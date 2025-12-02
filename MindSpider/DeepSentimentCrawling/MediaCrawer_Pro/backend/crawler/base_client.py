#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础 HTTP 客户端（不使用 Playwright）
"""
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from urllib.parse import urlencode
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings


class BaseHttpClient(ABC):
    """基础 HTTP 客户端"""
    
    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url: str = ""
        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}
        self.timeout = settings.REQUEST_TIMEOUT
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.init_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def init_client(self):
        """初始化客户端"""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=self.headers,
            cookies=self.cookies,
        )
        logger.info(f"✅ HTTP 客户端初始化成功: {self.__class__.__name__}")
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            logger.info(f"👋 HTTP 客户端已关闭: {self.__class__.__name__}")
    
    def set_cookie(self, cookie: str):
        """设置 Cookie"""
        # 解析 cookie 字符串
        for item in cookie.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                self.cookies[key.strip()] = value.strip()
        
        if self.client:
            self.client.cookies.update(self.cookies)
    
    def set_proxy(self, proxy: Optional[str]):
        """设置代理"""
        if proxy and self.client:
            self.client._mounts.clear()
            self.client._mounts[b'http://'] = httpx.AsyncHTTPTransport(proxy=proxy)
            self.client._mounts[b'https://'] = httpx.AsyncHTTPTransport(proxy=proxy)
    
    @abstractmethod
    async def sign_request(self, url: str, data: Optional[Dict] = None) -> Dict[str, str]:
        """
        签名请求（调用签名服务）
        返回签名后的 headers
        """
        pass
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通用请求方法
        """
        if not self.client:
            await self.init_client()
        
        # 构造带查询参数的完整 URL，用于签名和实际请求
        request_url = url
        if params:
            query_str = urlencode(params, doseq=True)
            separator = '&' if '?' in request_url else '?'
            request_url = f"{request_url}{separator}{query_str}"
        
        # 调用签名服务（确保与实际请求 URL 完全一致）
        logger.info(f"🔐 准备签名请求:")
        logger.info(f"   URL: {request_url}")
        logger.info(f"   Method: {method}")
        if params:
            logger.info(f"   Params: {params}")
        if data or json:
            logger.info(f"   Body: {data or json}")
        
        sign_headers = await self.sign_request(request_url, data or json)
        logger.info(f"✅ 签名服务返回 headers: {list(sign_headers.keys())}")
        
        # 合并 headers
        final_headers = {**self.headers, **(headers or {}), **sign_headers}
        
        # 打印最终请求头（隐藏敏感信息）
        safe_headers = {k: v if k.lower() not in ['cookie', 'authorization'] else '***' for k, v in final_headers.items()}
        logger.info(f"📤 最终请求头: {safe_headers}")
        
        try:
            logger.info(f"🔄 发送请求: {method} {request_url}")
            
            response = await self.client.request(
                method=method,
                url=request_url,
                params=None,
                data=data,
                json=json,
                headers=final_headers,
                **kwargs
            )
            
            response.raise_for_status()
            
            logger.info(f"✅ 响应成功: {response.status_code}")
            
            # 尝试解析 JSON
            try:
                result = response.json()
                logger.info(f"📦 响应数据: {str(result)[:200]}...")
                return result
            except Exception:
                logger.info(f"📦 响应文本: {response.text[:200]}...")
                return {"text": response.text}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP 错误: {e.response.status_code} - {url}")
            logger.error(f"   完整URL: {request_url}")
            logger.error(f"   响应体: {e.response.text[:500]}")
            raise
        except httpx.TimeoutException:
            logger.error(f"⏱️ 请求超时: {url}")
            raise
        except Exception as e:
            logger.error(f"❌ 请求失败: {url} - {e}")
            raise
    
    async def get(self, url: str, **kwargs) -> Dict:
        """GET 请求"""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Dict:
        """POST 请求"""
        return await self.request("POST", url, **kwargs)



