#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie 自动续期服务
支持多种续期策略：
1. 定期检测Cookie有效性
2. RefreshToken自动刷新（需要逆向）
3. Cookie即将过期时自动刷新
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import httpx
from loguru import logger

from core.config import settings
from services.account_service import AccountService
from crawler.xhs_client import XHSClient


class CookieRefreshService:
    """Cookie自动续期服务"""
    
    def __init__(self):
        self.account_service = AccountService()
        self.check_interval = 6 * 3600  # 6小时检查一次
        self.cookie_lifetime = {
            "a1": 90 * 24 * 3600,  # 90天
            "web_session": 30 * 24 * 3600,  # 30天
            "acw_tc": 5 * 60,  # 5分钟
        }
        self._running = False
    
    async def start_monitoring(self):
        """启动Cookie监控服务"""
        if self._running:
            logger.warning("⚠️ Cookie监控服务已在运行中")
            return
        
        self._running = True
        logger.success("🚀 Cookie监控服务已启动")
        
        while self._running:
            try:
                await self.check_all_cookies()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Cookie监控服务错误: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再重试
    
    async def stop_monitoring(self):
        """停止Cookie监控服务"""
        self._running = False
        logger.info("👋 Cookie监控服务已停止")
    
    async def check_all_cookies(self):
        """检查所有账号的Cookie状态"""
        logger.info("🔍 开始检查所有账号Cookie...")
        
        try:
            # 获取所有活跃账号
            accounts = await self.account_service.list_accounts(
                platform="xhs",
                status="active"
            )
            
            if not accounts:
                logger.warning("⚠️ 没有活跃账号需要检查")
                return
            
            for account in accounts:
                account_id = account["_id"]
                logger.info(f"检查账号: {account_id}")
                
                # 检查并刷新Cookie
                is_valid = await self.refresh_cookie_if_needed(account_id)
                
                if not is_valid:
                    logger.warning(f"⚠️ 账号 {account_id} Cookie已失效")
            
            logger.success(f"✅ Cookie检查完成，共检查 {len(accounts)} 个账号")
            
        except Exception as e:
            logger.error(f"❌ 检查Cookie失败: {e}")
    
    async def refresh_cookie_if_needed(self, account_id: str) -> bool:
        """
        检查Cookie是否需要刷新
        
        Args:
            account_id: 账号ID
        
        Returns:
            bool: Cookie是否有效
        """
        try:
            # 1. 获取账号信息（完整Cookie）
            account = await self.account_service.get_account(account_id)
            if not account:
                logger.error(f"❌ 账号不存在: {account_id}")
                return False
            
            # 2. 测试Cookie是否有效
            is_valid = await self._test_cookie_validity(account)
            
            if is_valid:
                logger.success(f"✅ 账号 {account_id} Cookie有效")
                # 更新最后检查时间
                await self._update_last_checked(account_id)
                return True
            
            # 3. Cookie失效，尝试刷新
            logger.warning(f"⚠️ 账号 {account_id} Cookie已失效，尝试刷新...")
            
            # 方案1：尝试使用RefreshToken刷新（如果有）
            if await self._try_refresh_with_token(account):
                logger.success(f"✅ 使用RefreshToken刷新成功: {account_id}")
                return True
            
            # 方案2：标记账号为失效，通知管理员
            await self._mark_account_expired(account_id)
            await self._notify_admin(account)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 刷新Cookie失败: {e}")
            return False
    
    async def _test_cookie_validity(self, account: Dict) -> bool:
        """
        测试Cookie是否有效
        
        方法：调用一个简单的API接口，看是否返回成功
        """
        try:
            cookie_str = account.get("cookie", "")
            if not cookie_str:
                return False
            
            # 使用XHSClient测试搜索接口（不需要登录也能用）
            xhs_client = XHSClient()
            xhs_client.set_cookie(cookie_str)
            
            # 测试搜索功能
            result = await xhs_client.search_notes(
                keyword="测试",
                page=1,
                page_size=1
            )
            
            # 如果能正常返回数据，说明Cookie有效
            return result is not None and len(result.get("items", [])) > 0
            
        except Exception as e:
            logger.error(f"❌ Cookie验证失败: {e}")
            return False
    
    async def _try_refresh_with_token(self, account: Dict) -> bool:
        """
        尝试使用RefreshToken刷新Cookie
        
        ⚠️ 这需要逆向小红书的token刷新接口
        目前小红书的RefreshToken机制在Web端不明显
        
        可能的接口：
        - POST /api/sns/web/v1/user/refresh
        - POST /api/sns/web/v1/auth/refresh
        
        Args:
            account: 账号信息
        
        Returns:
            bool: 是否刷新成功
        """
        try:
            refresh_token = account.get("refresh_token")
            if not refresh_token:
                logger.warning("⚠️ 账号没有RefreshToken，无法自动刷新")
                return False
            
            # 尝试调用刷新接口
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://edith.xiaohongshu.com/api/sns/web/v1/auth/refresh",
                    json={"refresh_token": refresh_token},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Referer": "https://www.xiaohongshu.com/",
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        # 获取新的Cookie
                        new_cookies = data.get("data", {})
                        new_cookie_str = self._build_cookie_string(new_cookies)
                        
                        # 更新账号Cookie
                        from bson import ObjectId
                        await self.account_service.collection.update_one(
                            {"_id": ObjectId(account["_id"])},
                            {
                                "$set": {
                                    "cookie": new_cookie_str,
                                    "cookies": new_cookies,
                                    "updated_at": datetime.now(),
                                    "last_refreshed_at": datetime.now()
                                }
                            }
                        )
                        
                        logger.success(f"✅ RefreshToken刷新成功: {account['_id']}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ RefreshToken刷新失败: {e}")
            return False
    
    async def _mark_account_expired(self, account_id: str):
        """标记账号为失效"""
        try:
            await self.account_service.update_account_status(
                account_id=account_id,
                status="expired",
                is_success=False
            )
            logger.warning(f"⚠️ 账号已标记为失效: {account_id}")
        except Exception as e:
            logger.error(f"❌ 标记账号失效失败: {e}")
    
    async def _update_last_checked(self, account_id: str):
        """更新最后检查时间"""
        try:
            from bson import ObjectId
            await self.account_service.collection.update_one(
                {"_id": ObjectId(account_id)},
                {
                    "$set": {
                        "last_checked_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            )
        except Exception as e:
            logger.error(f"❌ 更新最后检查时间失败: {e}")
    
    async def _notify_admin(self, account: Dict):
        """
        通知管理员Cookie已失效
        
        可以通过多种方式通知：
        1. 邮件
        2. 企业微信
        3. 钉钉
        4. Telegram
        5. 数据库标记
        """
        logger.warning(f"📧 通知管理员：账号 {account['_id']} Cookie已失效")
        
        # TODO: 实现实际的通知逻辑
        # 示例：发送邮件
        # await self._send_email_notification(account)
        
        # 示例：发送企业微信消息
        # await self._send_wechat_notification(account)
        pass
    
    def _build_cookie_string(self, cookies: Dict[str, str]) -> str:
        """将Cookie字典转换为字符串"""
        return "; ".join(f"{k}={v}" for k, v in cookies.items())
    
    async def manual_refresh_cookie(
        self,
        account_id: str,
        new_cookie: str
    ) -> bool:
        """
        手动更新Cookie
        
        Args:
            account_id: 账号ID
            new_cookie: 新的Cookie字符串
        
        Returns:
            bool: 是否更新成功
        """
        try:
            from bson import ObjectId
            
            # 解析Cookie字符串为字典
            cookies_dict = {}
            for item in new_cookie.split(";"):
                item = item.strip()
                if "=" in item:
                    key, value = item.split("=", 1)
                    cookies_dict[key.strip()] = value.strip()
            
            # 更新数据库
            await self.account_service.collection.update_one(
                {"_id": ObjectId(account_id)},
                {
                    "$set": {
                        "cookie": new_cookie,
                        "cookies": cookies_dict,
                        "status": "active",
                        "updated_at": datetime.now(),
                        "last_refreshed_at": datetime.now()
                    }
                }
            )
            
            logger.success(f"✅ 手动更新Cookie成功: {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 手动更新Cookie失败: {e}")
            return False
    
    async def get_cookie_expiry_info(self, account_id: str) -> Dict[str, Any]:
        """
        获取Cookie过期信息
        
        Returns:
            {
                "is_valid": bool,
                "last_checked_at": datetime,
                "estimated_expiry": datetime,
                "days_remaining": int
            }
        """
        try:
            account = await self.account_service.get_account(account_id)
            if not account:
                return {"error": "账号不存在"}
            
            last_checked = account.get("last_checked_at")
            created_at = account.get("created_at")
            
            # 估算过期时间（基于创建时间 + 30天）
            if created_at:
                estimated_expiry = created_at + timedelta(days=30)
                days_remaining = (estimated_expiry - datetime.now()).days
            else:
                estimated_expiry = None
                days_remaining = None
            
            return {
                "is_valid": account.get("status") == "active",
                "last_checked_at": last_checked,
                "estimated_expiry": estimated_expiry,
                "days_remaining": days_remaining,
                "status": account.get("status")
            }
            
        except Exception as e:
            logger.error(f"❌ 获取Cookie过期信息失败: {e}")
            return {"error": str(e)}


# 单例模式
_cookie_refresh_service = None


def get_cookie_refresh_service() -> CookieRefreshService:
    """获取Cookie刷新服务单例"""
    global _cookie_refresh_service
    if _cookie_refresh_service is None:
        _cookie_refresh_service = CookieRefreshService()
    return _cookie_refresh_service





