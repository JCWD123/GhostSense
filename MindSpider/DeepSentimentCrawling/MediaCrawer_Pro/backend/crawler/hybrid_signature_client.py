#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合签名客户端
支持三种模式：
1. 纯JS逆向（快速）
2. Playwright浏览器（完整，包括x-s-common）
3. 自动模式（智能选择）
"""
from typing import Dict, Optional, Literal
import httpx
from loguru import logger

from core.config import settings


class HybridSignatureClient:
    """
    混合签名客户端
    
    优先使用纯JS逆向（快速），需要时自动切换到Playwright浏览器模式（获取x-s-common）
    """
    
    def __init__(self):
        self.base_url = settings.SIGNATURE_SERVICE_URL
        self.timeout = settings.SIGNATURE_SERVICE_TIMEOUT
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """异步上下文管理器"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
    
    async def get_xhs_headers(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        a1: str = "",
        cookie: str = "",
        mode: Literal["js", "browser", "auto"] = "auto",
        use_electron: bool = False
    ) -> Dict[str, str]:
        """
        获取小红书请求头
        
        Args:
            url: 请求URL
            method: HTTP方法
            data: 请求数据
            a1: Cookie中的a1值（JS模式需要）
            cookie: 完整Cookie字符串（浏览器模式需要）
            mode: 模式选择
                - "js": 纯JS逆向，只返回 x-s, x-t
                - "browser": Playwright浏览器，返回完整头包括 x-s-common
                - "auto": 自动选择（默认）
            use_electron: 是否连接到Electron浏览器（仅在browser模式有效）
            
        Returns:
            请求头字典 {"x-s": "...", "x-t": "...", "x-s-common": "..."}
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            
            # 根据模式选择API端点
            if mode == "js":
                return await self._get_js_signature(url, method, data, a1)
            elif mode == "browser":
                return await self._get_browser_signature(url, method, data, cookie, use_electron)
            else:  # auto
                # 自动模式：先尝试JS，失败则用浏览器
                try:
                    headers = await self._get_js_signature(url, method, data, a1)
                    logger.info("✅ 使用纯JS签名模式")
                    return headers
                except Exception as e:
                    logger.warning(f"⚠️ JS签名失败，切换到浏览器模式: {e}")
                    return await self._get_browser_signature(url, method, data, cookie, use_electron)
                    
        except Exception as e:
            logger.error(f"❌ 获取签名失败: {e}")
            return {}
    
    async def _get_js_signature(
        self, 
        url: str, 
        method: str, 
        data: Optional[Dict], 
        a1: str
    ) -> Dict[str, str]:
        """
        纯JS签名模式（快速）
        """
        logger.info("🚀 使用纯JS签名模式")
        
        response = await self.client.post(
            "/sign/xhs",
            json={
                "url": url,
                "method": method,
                "data": data,
                "a1": a1
            }
        )
        response.raise_for_status()
        
        result = response.json()
        if not result.get("success"):
            raise Exception(result.get("message", "签名失败"))
        
        sign_data = result.get("data", {})
        logger.info(f"✅ JS签名成功: x-s={sign_data.get('x-s', '')[:30]}...")
        
        return sign_data
    
    async def _get_browser_signature(
        self,
        url: str,
        method: str,
        data: Optional[Dict],
        cookie: str,
        use_electron: bool = False
    ) -> Dict[str, str]:
        """
        Playwright浏览器模式（完整，包括x-s-common）
        """
        logger.info("🌐 使用Playwright浏览器模式")
        
        payload = {
            "url": url,
            "method": method,
            "data": data,
            "cookie": cookie
        }
        
        # 如果使用Electron，添加调试端口
        if use_electron:
            payload["debugPort"] = 9222
            logger.info("🔗 将连接到Electron浏览器（端口9222）")
        
        response = await self.client.post(
            "/sign/xhs/browser",
            json=payload,
            timeout=30.0  # 浏览器模式需要更长超时
        )
        response.raise_for_status()
        
        result = response.json()
        if not result.get("success"):
            raise Exception(result.get("message", "浏览器获取签名失败"))
        
        headers = result.get("data", {})
        logger.info("✅ 浏览器模式成功:")
        logger.info(f"   x-s: {headers.get('x-s', '')[:30]}...")
        logger.info(f"   x-t: {headers.get('x-t', '')}")
        logger.info(f"   x-s-common: {headers.get('x-s-common', '')[:30]}...")
        
        return headers
    
    async def get_xhs_sign_hybrid(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        a1: str = "",
        cookie: str = "",
        mode: str = "auto"
    ) -> Dict[str, str]:
        """
        混合模式API（调用签名服务的hybrid端点）
        
        Args:
            url: 请求URL
            method: HTTP方法
            data: 请求数据
            a1: Cookie中的a1值
            cookie: 完整Cookie字符串
            mode: 模式选择 (js/browser/auto)
            
        Returns:
            完整的请求头
        """
        try:
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout
                )
            
            logger.info(f"🎯 调用混合模式API (mode={mode})")
            
            response = await self.client.post(
                "/sign/xhs/hybrid",
                json={
                    "url": url,
                    "method": method,
                    "data": data,
                    "a1": a1,
                    "cookie": cookie,
                    "mode": mode,
                    "debugPort": 9222 if settings.USE_ELECTRON_BROWSER else None
                },
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            if not result.get("success"):
                raise Exception(result.get("message", "混合模式签名失败"))
            
            headers = result.get("data", {})
            logger.info(f"✅ 混合模式成功 (使用: {headers.get('mode', 'unknown')})")
            
            return headers
            
        except Exception as e:
            logger.error(f"❌ 混合模式签名失败: {e}")
            return {}


# 全局实例
hybrid_signature_client = HybridSignatureClient()


# ==================== 便捷函数 ====================

async def get_xhs_headers_auto(
    url: str,
    method: str = "GET",
    data: Optional[Dict] = None,
    cookie: str = "",
    use_electron: bool = False
) -> Dict[str, str]:
    """
    快速获取小红书请求头（自动模式）
    
    优先使用JS签名，需要时自动切换到浏览器模式
    """
    async with HybridSignatureClient() as client:
        # 从cookie中提取a1
        a1 = ""
        if cookie:
            for item in cookie.split(";"):
                if "a1=" in item:
                    a1 = item.split("a1=")[1].strip()
                    break
        
        return await client.get_xhs_headers(
            url=url,
            method=method,
            data=data,
            a1=a1,
            cookie=cookie,
            mode="auto",
            use_electron=use_electron
        )




