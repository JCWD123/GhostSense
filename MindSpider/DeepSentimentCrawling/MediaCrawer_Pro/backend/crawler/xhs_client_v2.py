#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫客户端 V2
使用混合签名模式（纯JS + Playwright）
"""
from typing import Dict, List, Optional
import httpx
from loguru import logger
from urllib.parse import urlencode

from core.config import settings
from crawler.base_client import BaseHttpClient
from crawler.hybrid_signature_client import HybridSignatureClient


class XhsClientV2(BaseHttpClient):
    """
    小红书爬虫客户端 V2
    
    特性：
    - 混合签名模式：纯JS（快） + Playwright（完整）
    - 自动降级：JS失败自动切换到浏览器模式
    - Electron集成：可连接到Electron浏览器
    """
    
    def __init__(self, cookie: str = "", use_electron: bool = False):
        """
        初始化
        
        Args:
            cookie: Cookie字符串
            use_electron: 是否使用Electron浏览器（仅在browser模式有效）
        """
        super().__init__()
        self.base_url = settings.XHS_BASE_URL
        self.web_url = settings.XHS_WEB_URL
        self.use_electron = use_electron
        
        # 初始化签名客户端
        self.signature_client = HybridSignatureClient()
        
        # 设置基础请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": self.web_url,
            "Origin": self.web_url,
        }
        
        # 设置Cookie
        if cookie:
            self.set_cookie(cookie)
            self.headers["Cookie"] = cookie
        
        # 提取a1（用于JS签名）
        self.a1 = self._extract_a1(cookie)
        self.cookie_string = cookie
    
    def _extract_a1(self, cookie: str) -> str:
        """从Cookie中提取a1值"""
        for item in cookie.split(";"):
            if "a1=" in item:
                return item.split("a1=")[1].strip()
        return ""
    
    async def init_client(self):
        """初始化客户端"""
        await super().init_client()
        # 初始化签名客户端
        await self.signature_client.__aenter__()
        logger.info("✅ 小红书客户端V2初始化成功（混合签名模式）")
    
    async def close(self):
        """关闭客户端"""
        if self.signature_client:
            await self.signature_client.__aexit__(None, None, None)
        await super().close()
    
    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        signature_mode: str = "auto"
    ) -> Dict:
        """
        发起请求（自动添加签名）
        
        Args:
            method: HTTP方法
            url: 请求URL
            params: 查询参数
            data: 请求体数据
            signature_mode: 签名模式 (js/browser/auto)
            
        Returns:
            响应数据
        """
        try:
            # 构建完整URL
            full_url = url if url.startswith("http") else f"{self.base_url}{url}"
            
            # 获取签名
            logger.info(f"🔑 获取签名 (mode={signature_mode})")
            
            sign_headers = await self.signature_client.get_xhs_headers(
                url=full_url,
                method=method,
                data=params if method == "GET" else data,
                a1=self.a1,
                cookie=self.cookie_string,
                mode=signature_mode,
                use_electron=self.use_electron
            )
            
            if not sign_headers:
                raise Exception("签名获取失败")
            
            # 更新请求头
            request_headers = {**self.headers}
            request_headers["x-s"] = sign_headers.get("x-s", "")
            request_headers["x-t"] = sign_headers.get("x-t", "")
            
            # 如果是浏览器模式，还有x-s-common
            if sign_headers.get("x-s-common"):
                request_headers["x-s-common"] = sign_headers["x-s-common"]
                logger.info("✅ 使用完整签名（包括x-s-common）")
            
            # 发起请求
            logger.info(f"📤 {method} {full_url}")
            
            if method == "GET":
                response = await self.client.get(
                    full_url,
                    params=params,
                    headers=request_headers
                )
            else:
                response = await self.client.post(
                    full_url,
                    json=data,
                    headers=request_headers
                )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ 请求成功: {response.status_code}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP错误: {e.response.status_code}")
            logger.error(f"   响应内容: {e.response.text[:200]}")
            raise
        except Exception as e:
            logger.error(f"❌ 请求失败: {e}")
            raise
    
    async def search_notes(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: str = "general",
        signature_mode: str = "auto"
    ) -> Dict:
        """
        搜索笔记
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort: 排序方式 (general/popularity_descending/time_descending)
            signature_mode: 签名模式 (js/browser/auto)
            
        Returns:
            搜索结果
        """
        logger.info(f"🔍 搜索笔记: {keyword} (page={page}, mode={signature_mode})")
        
        params = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": self._generate_search_id(),
            "sort": sort,
            "note_type": 0,
            "ext_flags": []
        }
        
        result = await self._make_request(
            method="GET",
            url="/api/sns/web/v1/search/notes",
            params=params,
            signature_mode=signature_mode
        )
        
        return result
    
    async def get_note_detail(
        self,
        note_id: str,
        signature_mode: str = "auto"
    ) -> Dict:
        """
        获取笔记详情
        
        Args:
            note_id: 笔记ID
            signature_mode: 签名模式
            
        Returns:
            笔记详情
        """
        logger.info(f"📄 获取笔记详情: {note_id}")
        
        params = {
            "source_note_id": note_id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": 1},
            "xsec_source": "pc_search",
            "xsec_token": ""
        }
        
        result = await self._make_request(
            method="GET",
            url="/api/sns/web/v1/feed",
            params=params,
            signature_mode=signature_mode
        )
        
        return result
    
    async def get_user_info(
        self,
        user_id: str,
        signature_mode: str = "auto"
    ) -> Dict:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            signature_mode: 签名模式
            
        Returns:
            用户信息
        """
        logger.info(f"👤 获取用户信息: {user_id}")
        
        params = {
            "user_id": user_id
        }
        
        result = await self._make_request(
            method="GET",
            url="/api/sns/web/v1/user/otherinfo",
            params=params,
            signature_mode=signature_mode
        )
        
        return result
    
    async def get_user_notes(
        self,
        user_id: str,
        cursor: str = "",
        page_size: int = 30,
        signature_mode: str = "auto"
    ) -> Dict:
        """
        获取用户笔记列表
        
        Args:
            user_id: 用户ID
            cursor: 游标（翻页用）
            page_size: 每页数量
            signature_mode: 签名模式
            
        Returns:
            笔记列表
        """
        logger.info(f"📝 获取用户笔记: {user_id}")
        
        params = {
            "user_id": user_id,
            "cursor": cursor,
            "num": page_size,
            "image_formats": "jpg,webp,avif"
        }
        
        result = await self._make_request(
            method="GET",
            url="/api/sns/web/v1/user_posted",
            params=params,
            signature_mode=signature_mode
        )
        
        return result
    
    def _generate_search_id(self) -> str:
        """生成搜索ID"""
        import time
        import random
        timestamp = int(time.time() * 1000)
        random_str = ''.join(random.choices('0123456789abcdef', k=8))
        return f"{timestamp}_{random_str}"


# ==================== 使用示例 ====================

async def example_usage():
    """使用示例"""
    
    # 示例Cookie（请替换为真实Cookie）
    cookie = """
    a1=your_a1_value;
    webId=your_webid;
    web_session=your_session;
    xsecappid=xhs-pc-web
    """
    
    # 初始化客户端
    async with XhsClientV2(cookie=cookie, use_electron=True) as client:
        
        # 1. 搜索笔记（自动模式）
        search_result = await client.search_notes(
            keyword="美食",
            page=1,
            signature_mode="auto"  # 自动选择最优方案
        )
        logger.info(f"搜索结果: {len(search_result.get('data', {}).get('items', []))} 条")
        
        # 2. 获取笔记详情（强制使用浏览器模式）
        note_detail = await client.get_note_detail(
            note_id="note_id_here",
            signature_mode="browser"  # 强制使用浏览器获取完整签名
        )
        
        # 3. 获取用户信息（纯JS模式）
        user_info = await client.get_user_info(
            user_id="user_id_here",
            signature_mode="js"  # 纯JS签名，最快
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())




