#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
签名服务客户端
"""
from typing import Dict, Optional
import httpx
from loguru import logger

from core.config import settings


class SignatureClient:
    """签名服务客户端"""
    
    def __init__(self):
        self.base_url = settings.SIGNATURE_SERVICE_URL
        self.timeout = settings.SIGNATURE_SERVICE_TIMEOUT
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def get_xhs_sign(
        self, 
        url: str, 
        method: str = "GET",
        data: Optional[Dict] = None, 
        a1: str = "",
        b1: str = "",
        cookie: str = "",
        debug_port: Optional[int] = None,
        auto_fetch_b1: bool = False
    ) -> Dict[str, str]:
        """
        获取小红书签名（完整版）
        
        Args:
            url: 请求URL
            method: 请求方法 GET/POST
            data: 请求数据（GET请求为params，POST请求为body）
            a1: Cookie中的a1值
            b1: localStorage中的b1值（可选，用于生成x-s-common）
            
        返回: {"x-s": "xxx", "x-t": "xxx", "x-s-common": "xxx", "x-b3-traceid": "xxx"}
        """
        try:
            logger.info(f"🔑 请求签名服务:")
            logger.info(f"   服务地址: {self.base_url}/sign/xhs")
            logger.info(f"   URL: {url[:100]}...")
            logger.info(f"   Method: {method}")
            logger.info(f"   有a1: {'是' if a1 else '否'}")
            logger.info(f"   有b1: {'是' if b1 else '否'}")
            logger.info(f"   有data: {'是' if data else '否'}")
            logger.info(f"   有cookie: {'是' if cookie else '否'}")
            logger.info(f"   debug_port: {debug_port if debug_port else '无'}")
            
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout
                )
                logger.info(f"✅ 签名服务客户端初始化完成")
            
            payload = {
                "url": url, 
                "method": method,
                "data": data,
                "a1": a1,
                "b1": b1,
                "cookie": cookie,
                "debugPort": debug_port,
                "auto_fetch_b1": auto_fetch_b1
            }
            logger.info(f"📤 签名请求载荷: {str(payload)[:200]}...")
            
            response = await self.client.post(
                "/sign/xhs",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ 签名服务响应: {result}")
            
            sign_data = result.get("data", {})
            if sign_data:
                logger.info(f"🎯 获取到签名:")
                logger.info(f"   x-s: {sign_data.get('x-s', '')[:30]}...")
                logger.info(f"   x-t: {sign_data.get('x-t', '')}")
                if sign_data.get('x-s-common'):
                    logger.info(f"   x-s-common: {sign_data.get('x-s-common', '')[:30]}...")
                if sign_data.get('x-b3-traceid'):
                    logger.info(f"   x-b3-traceid: {sign_data.get('x-b3-traceid', '')}")
            else:
                logger.warning(f"⚠️ 签名服务返回空数据")
            
            return sign_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 签名服务HTTP错误: {e.response.status_code}")
            logger.error(f"   响应内容: {e.response.text}")
            return {}
        except httpx.ConnectError as e:
            logger.error(f"❌ 签名服务连接失败: {e}")
            logger.error(f"   请确保签名服务正在运行: {self.base_url}")
            return {}
        except Exception as e:
            logger.error(f"❌ 小红书签名失败: {type(e).__name__} - {e}")
            return {}
    
    async def get_douyin_sign(self, url: str, data: Optional[Dict] = None) -> Dict[str, str]:
        """
        获取抖音签名
        返回: {"X-Bogus": "xxx"}
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            
            response = await self.client.post(
                "/sign/douyin",
                json={"url": url, "data": data}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"✅ 抖音签名成功")
            return result.get("data", {})
            
        except Exception as e:
            logger.error(f"❌ 抖音签名失败: {e}")
            return {}
    
    async def get_kuaishou_sign(self, url: str, data: Optional[Dict] = None) -> Dict[str, str]:
        """
        获取快手签名
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            
            response = await self.client.post(
                "/sign/kuaishou",
                json={"url": url, "data": data}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"✅ 快手签名成功")
            return result.get("data", {})
            
        except Exception as e:
            logger.error(f"❌ 快手签名失败: {e}")
            return {}
    
    async def get_bilibili_sign(self, params: Dict) -> Dict[str, str]:
        """
        获取B站 wbi 签名
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            
            response = await self.client.post(
                "/sign/bilibili",
                json={"params": params}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"✅ B站签名成功")
            return result.get("data", {})
            
        except Exception as e:
            logger.error(f"❌ B站签名失败: {e}")
            return {}


# 全局签名客户端实例
signature_client = SignatureClient()



