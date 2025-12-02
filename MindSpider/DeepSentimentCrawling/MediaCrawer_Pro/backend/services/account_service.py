#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号池管理服务
"""
from typing import Optional, Dict, List
from datetime import datetime
import random
from loguru import logger

from core.database import get_db
from core.config import settings


class AccountService:
    """账号池管理服务"""
    
    def __init__(self):
        self._db = None
        self._collection = None
        self.enabled = settings.ACCOUNT_POOL_ENABLED
        self.rotation_strategy = settings.ACCOUNT_ROTATION_STRATEGY
        self._current_index = 0  # 轮询索引
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.accounts
        return self._collection
    
    async def add_account(self, account_data: Dict) -> Dict:
        """
        添加账号
        
        Args:
            account_data: 账号数据
                {
                    "platform": "xhs",
                    "cookie": "xxx",
                    "weight": 1,
                    "status": "active",
                    "note": "备注"
                }
        
        Returns:
            添加的账号
        """
        try:
            account_data = self._normalize_account_data(account_data)
            account = {
                **account_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "use_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "last_used_at": None,
            }
            
            result = await self.collection.insert_one(account)
            account["_id"] = str(result.inserted_id)
            
            logger.success(f"✅ 添加账号成功: {account_data.get('platform')}")
            return account
            
        except Exception as e:
            logger.error(f"❌ 添加账号失败: {e}")
            raise
    
    async def get_account(self, account_id: str) -> Optional[Dict]:
        """获取账号"""
        try:
            from bson import ObjectId
            account = await self.collection.find_one({"_id": ObjectId(account_id)})
            if account:
                account["_id"] = str(account["_id"])
            return account
        except Exception as e:
            logger.error(f"❌ 获取账号失败: {e}")
            return None
    
    async def list_accounts(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        获取账号列表
        
        Args:
            platform: 平台（xhs, douyin, kuaishou 等）
            status: 状态（active, inactive, banned）
        
        Returns:
            账号列表
        """
        try:
            query = {}
            if platform:
                query["platform"] = platform
            if status:
                query["status"] = status
            
            cursor = self.collection.find(query).sort("created_at", -1)
            accounts = await cursor.to_list(length=1000)
            
            for account in accounts:
                account["_id"] = str(account["_id"])
                # 隐藏完整 cookie，只显示前后各 20 个字符
                if account.get("cookie") and len(account["cookie"]) > 40:
                    account["cookie"] = account["cookie"][:20] + "..." + account["cookie"][-20:]
            
            logger.info(f"✅ 获取到 {len(accounts)} 个账号")
            return accounts
            
        except Exception as e:
            logger.error(f"❌ 获取账号列表失败: {e}")
            return []
    
    async def delete_account(self, account_id: str) -> bool:
        """删除账号"""
        try:
            from bson import ObjectId
            result = await self.collection.delete_one({"_id": ObjectId(account_id)})
            logger.info(f"✅ 删除账号成功: {account_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"❌ 删除账号失败: {e}")
            return False
    
    async def get_available_account(self, platform: str) -> Optional[Dict]:
        """
        获取可用账号（根据轮换策略）
        
        Args:
            platform: 平台名称
        
        Returns:
            账号数据
        """
        if not self.enabled:
            logger.warning("⚠️ 账号池未启用")
            return None
        
        try:
            # 获取所有活跃账号原始数据，避免被列表接口裁剪 Cookie
            cursor = self.collection.find({
                "platform": platform,
                "status": "active"
            }).sort("created_at", 1)
            accounts = await cursor.to_list(length=1000)
            for account in accounts:
                account["_id"] = str(account["_id"])
            
            if not accounts:
                logger.error(f"❌ 没有可用的 {platform} 账号")
                return None
            
            # 根据策略选择账号
            if self.rotation_strategy == "round_robin":
                # 轮询
                account = accounts[self._current_index % len(accounts)]
                self._current_index += 1
                
            elif self.rotation_strategy == "weighted":
                # 加权随机
                weights = [acc.get("weight", 1) for acc in accounts]
                account = random.choices(accounts, weights=weights, k=1)[0]
                
            elif self.rotation_strategy == "random":
                # 完全随机
                account = random.choice(accounts)
                
            else:
                # 默认轮询
                account = accounts[self._current_index % len(accounts)]
                self._current_index += 1
            
            # 更新使用记录
            await self._update_account_usage(account["_id"])
            
            logger.info(f"✅ 选择账号: {account['_id']} ({self.rotation_strategy})")
            return account
            
        except Exception as e:
            logger.error(f"❌ 获取可用账号失败: {e}")
            return None
    
    async def _update_account_usage(self, account_id: str):
        """更新账号使用记录"""
        try:
            from bson import ObjectId
            await self.collection.update_one(
                {"_id": ObjectId(account_id)},
                {
                    "$inc": {"use_count": 1},
                    "$set": {
                        "last_used_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            )
        except Exception as e:
            logger.error(f"❌ 更新账号使用记录失败: {e}")
    
    async def update_account_status(
        self,
        account_id: str,
        status: str,
        is_success: bool = True
    ):
        """
        更新账号状态
        
        Args:
            account_id: 账号 ID
            status: 状态（active, inactive, banned）
            is_success: 本次使用是否成功
        """
        try:
            from bson import ObjectId
            update_doc = {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now()
                }
            }
            
            if is_success:
                update_doc["$inc"] = {"success_count": 1}
            else:
                update_doc["$inc"] = {"fail_count": 1}
            
            await self.collection.update_one(
                {"_id": ObjectId(account_id)},
                update_doc
            )
            
            logger.info(f"✅ 更新账号状态: {account_id} -> {status}")
            
        except Exception as e:
            logger.error(f"❌ 更新账号状态失败: {e}")
    
    def _normalize_account_data(self, account_data: Dict) -> Dict:
        """确保账号记录包含可用的 cookie 字符串和字典"""
        normalized = {**account_data}
        cookie_str = normalized.get("cookie") or ""
        cookies_dict = normalized.get("cookies")
        
        if not cookie_str and isinstance(cookies_dict, dict):
            cookie_str = self._cookie_dict_to_str(cookies_dict)
        
        if cookie_str and not isinstance(cookies_dict, dict):
            cookies_dict = self._cookie_str_to_dict(cookie_str)
        
        normalized["cookie"] = cookie_str
        normalized["cookies"] = cookies_dict or {}
        if not normalized.get("status"):
            normalized["status"] = "active"
        return normalized
    
    def build_cookie_string(self, account: Dict) -> str:
        """根据账号记录生成完整的 cookie 字符串"""
        if not account:
            return ""
        cookie_str = account.get("cookie", "")
        if not cookie_str and isinstance(account.get("cookies"), dict):
            cookie_str = self._cookie_dict_to_str(account["cookies"])
        return cookie_str
    
    def _cookie_dict_to_str(self, cookies: Dict[str, str]) -> str:
        return "; ".join(f"{key}={value}" for key, value in cookies.items() if key and value)
    
    def _cookie_str_to_dict(self, cookie_str: str) -> Dict[str, str]:
        cookies: Dict[str, str] = {}
        for item in cookie_str.split(";"):
            item = item.strip()
            if not item or "=" not in item:
                continue
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
        return cookies


