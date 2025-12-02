#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页推荐流服务
"""
from typing import Dict
from loguru import logger

from crawler.xhs_client import XHSClient
from .account_service import AccountService
from .proxy_service import ProxyService


class HomeFeedService:
    """首页推荐流服务"""
    
    def __init__(self):
        self._account_service = None
        self._proxy_service = None
    
    @property
    def account_service(self):
        if self._account_service is None:
            self._account_service = AccountService()
        return self._account_service
    
    @property
    def proxy_service(self):
        if self._proxy_service is None:
            self._proxy_service = ProxyService()
        return self._proxy_service
    
    async def get_homefeed(self, platform: str, page: int = 1) -> Dict:
        """
        获取首页推荐流
        
        Args:
            platform: 平台（xhs, douyin, kuaishou, bilibili）
            page: 页码
        
        Returns:
            推荐内容
        """
        try:
            if platform == "xhs":
                return await self._get_xhs_homefeed(page)
            elif platform == "douyin":
                # TODO: 实现抖音推荐流
                return {"items": [], "message": "抖音推荐流暂未实现"}
            elif platform == "kuaishou":
                # TODO: 实现快手推荐流
                return {"items": [], "message": "快手推荐流暂未实现"}
            elif platform == "bilibili":
                # TODO: 实现B站推荐流
                return {"items": [], "message": "B站推荐流暂未实现"}
            else:
                return {"items": [], "message": f"不支持的平台: {platform}"}
                
        except Exception as e:
            logger.exception(f"❌ 获取推荐流失败: {platform}")
            return {"items": [], "message": str(e)}
    
    async def _get_xhs_homefeed(self, page: int) -> Dict:
        """获取小红书推荐流"""
        # 获取账号
        account = await self.account_service.get_available_account("xhs")
        
        # 获取代理
        proxy = await self.proxy_service.get_available_proxy()
        
        async with XHSClient() as client:
            # 设置 cookie
            if account:
                client.set_cookie(account.get("cookie", ""))
            
            # 设置代理
            if proxy:
                client.set_proxy(proxy)
            
            # 获取推荐流
            # TODO: 实现分页逻辑（需要保存 cursor）
            result = await client.get_homefeed()
            
            return {
                "platform": "xhs",
                "items": result.get("notes", []),
                "cursor": result.get("cursor", ""),
                "has_more": len(result.get("notes", [])) > 0
            }




