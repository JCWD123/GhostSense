#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP 代理池管理服务
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import random
import httpx
from loguru import logger

from core.database import get_db
from core.config import settings


class ProxyService:
    """IP 代理池管理服务"""
    
    def __init__(self):
        self._db = None
        self._collection = None
        self.enabled = settings.PROXY_ENABLED
        self.pool_size = settings.PROXY_POOL_SIZE
        self.retry = settings.PROXY_RETRY
        self._current_index = 0
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.proxies
        return self._collection
    
    async def add_proxy(self, proxy_data: Dict) -> Dict:
        """
        添加代理
        
        Args:
            proxy_data: 代理数据
                {
                    "protocol": "http",  # http, https, socks5
                    "host": "127.0.0.1",
                    "port": 7890,
                    "username": "",
                    "password": "",
                    "provider": "custom",  # custom, kuaidaili, wandou 等
                    "status": "active"
                }
        
        Returns:
            添加的代理
        """
        try:
            # 构建代理 URL
            if proxy_data.get("username") and proxy_data.get("password"):
                proxy_url = (
                    f"{proxy_data['protocol']}://"
                    f"{proxy_data['username']}:{proxy_data['password']}@"
                    f"{proxy_data['host']}:{proxy_data['port']}"
                )
            else:
                proxy_url = f"{proxy_data['protocol']}://{proxy_data['host']}:{proxy_data['port']}"
            
            proxy = {
                **proxy_data,
                "proxy_url": proxy_url,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "use_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "success_rate": 100.0,
                "last_used_at": None,
                "last_check_at": None,
            }
            
            # 检查代理是否可用
            is_available = await self._check_proxy(proxy_url)
            proxy["status"] = "active" if is_available else "inactive"
            
            result = await self.collection.insert_one(proxy)
            proxy["_id"] = str(result.inserted_id)
            
            logger.success(f"✅ 添加代理成功: {proxy_url} ({'可用' if is_available else '不可用'})")
            return proxy
            
        except Exception as e:
            logger.error(f"❌ 添加代理失败: {e}")
            raise
    
    async def get_proxy(self, proxy_id: str) -> Optional[Dict]:
        """获取代理"""
        try:
            from bson import ObjectId
            proxy = await self.collection.find_one({"_id": ObjectId(proxy_id)})
            if proxy:
                proxy["_id"] = str(proxy["_id"])
            return proxy
        except Exception as e:
            logger.error(f"❌ 获取代理失败: {e}")
            return None
    
    async def list_proxies(self, status: Optional[str] = None) -> List[Dict]:
        """
        获取代理列表
        
        Args:
            status: 状态（active, inactive, banned）
        
        Returns:
            代理列表
        """
        try:
            query = {}
            if status:
                query["status"] = status
            
            cursor = self.collection.find(query).sort([("success_rate", -1), ("created_at", -1)])
            proxies = await cursor.to_list(length=1000)
            
            for proxy in proxies:
                proxy["_id"] = str(proxy["_id"])
            
            logger.info(f"✅ 获取到 {len(proxies)} 个代理")
            return proxies
            
        except Exception as e:
            logger.error(f"❌ 获取代理列表失败: {e}")
            return []
    
    async def delete_proxy(self, proxy_id: str) -> bool:
        """删除代理"""
        try:
            from bson import ObjectId
            result = await self.collection.delete_one({"_id": ObjectId(proxy_id)})
            logger.info(f"✅ 删除代理成功: {proxy_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"❌ 删除代理失败: {e}")
            return False
    
    async def get_available_proxy(self) -> Optional[str]:
        """
        获取可用代理
        
        Returns:
            代理 URL
        """
        if not self.enabled:
            return None
        
        try:
            # 获取所有活跃代理
            proxies = await self.list_proxies(status="active")
            
            if not proxies:
                logger.warning("⚠️ 没有可用的代理")
                return None
            
            # 按成功率排序，优先使用成功率高的代理
            proxies_sorted = sorted(
                proxies,
                key=lambda x: (x.get("success_rate", 0), -x.get("use_count", 0)),
                reverse=True
            )
            
            # 从前 N 个高质量代理中随机选择
            top_proxies = proxies_sorted[:min(5, len(proxies_sorted))]
            proxy = random.choice(top_proxies)
            
            # 更新使用记录
            await self._update_proxy_usage(proxy["_id"])
            
            logger.info(f"✅ 选择代理: {proxy['proxy_url']} (成功率: {proxy.get('success_rate', 0):.2f}%)")
            return proxy["proxy_url"]
            
        except Exception as e:
            logger.error(f"❌ 获取可用代理失败: {e}")
            return None
    
    async def _update_proxy_usage(self, proxy_id: str):
        """更新代理使用记录"""
        try:
            from bson import ObjectId
            await self.collection.update_one(
                {"_id": ObjectId(proxy_id)},
                {
                    "$inc": {"use_count": 1},
                    "$set": {
                        "last_used_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                }
            )
        except Exception as e:
            logger.error(f"❌ 更新代理使用记录失败: {e}")
    
    async def update_proxy_status(
        self,
        proxy_url: str,
        is_success: bool
    ):
        """
        更新代理状态
        
        Args:
            proxy_url: 代理 URL
            is_success: 本次使用是否成功
        """
        try:
            proxy = await self.collection.find_one({"proxy_url": proxy_url})
            if not proxy:
                return
            
            if is_success:
                await self.collection.update_one(
                    {"proxy_url": proxy_url},
                    {
                        "$inc": {"success_count": 1},
                        "$set": {"updated_at": datetime.now()}
                    }
                )
            else:
                await self.collection.update_one(
                    {"proxy_url": proxy_url},
                    {
                        "$inc": {"fail_count": 1},
                        "$set": {"updated_at": datetime.now()}
                    }
                )
            
            # 重新计算成功率
            proxy = await self.collection.find_one({"proxy_url": proxy_url})
            total = proxy["success_count"] + proxy["fail_count"]
            success_rate = (proxy["success_count"] / total * 100) if total > 0 else 100.0
            
            await self.collection.update_one(
                {"proxy_url": proxy_url},
                {"$set": {"success_rate": success_rate}}
            )
            
            # 如果成功率过低，标记为不可用
            if success_rate < 30 and total > 10:
                await self.collection.update_one(
                    {"proxy_url": proxy_url},
                    {"$set": {"status": "inactive"}}
                )
                logger.warning(f"⚠️ 代理成功率过低，已标记为不可用: {proxy_url}")
            
        except Exception as e:
            logger.error(f"❌ 更新代理状态失败: {e}")
    
    async def _check_proxy(self, proxy_url: str, timeout: int = 10) -> bool:
        """
        检查代理是否可用
        
        Args:
            proxy_url: 代理 URL
            timeout: 超时时间
        
        Returns:
            是否可用
        """
        try:
            async with httpx.AsyncClient(proxies=proxy_url, timeout=timeout) as client:
                response = await client.get("https://httpbin.org/ip")
                if response.status_code == 200:
                    logger.debug(f"✅ 代理可用: {proxy_url}")
                    return True
                else:
                    logger.warning(f"⚠️ 代理不可用: {proxy_url}")
                    return False
        except Exception as e:
            logger.warning(f"⚠️ 代理检查失败: {proxy_url} - {e}")
            return False
    
    async def health_check(self):
        """定时健康检查"""
        logger.info("🔍 开始代理健康检查...")
        
        proxies = await self.list_proxies()
        
        for proxy in proxies:
            # 超过 1 小时未检查的代理才检查
            last_check = proxy.get("last_check_at")
            if last_check and (datetime.now() - last_check) < timedelta(hours=1):
                continue
            
            is_available = await self._check_proxy(proxy["proxy_url"])
            
            await self.collection.update_one(
                {"_id": proxy["_id"]},
                {
                    "$set": {
                        "status": "active" if is_available else "inactive",
                        "last_check_at": datetime.now()
                    }
                }
            )
        
        logger.info("✅ 代理健康检查完成")




