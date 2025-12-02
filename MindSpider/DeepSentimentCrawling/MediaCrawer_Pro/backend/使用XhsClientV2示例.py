#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 XhsClientV2 获取完整签名（包括 x-s-common）
"""
import asyncio
from crawler.xhs_client_v2 import XhsClientV2

async def test_search():
    # 你的完整Cookie
    cookie = """
    a1=your_a1_value;
    webId=your_webid;
    web_session=your_web_session;
    xsecappid=xhs-pc-web
    """
    
    # 使用 XhsClientV2，启用Electron浏览器模式
    async with XhsClientV2(cookie=cookie, use_electron=True) as client:
        # 使用浏览器模式获取完整签名（包括x-s-common）
        result = await client.search_notes(
            keyword="美食",
            page=1,
            page_size=20,
            signature_mode="browser"  # 🔑 关键：使用浏览器模式
        )
        
        print(f"✅ 搜索成功，找到 {len(result.get('data', {}).get('items', []))} 条笔记")
        return result

if __name__ == "__main__":
    asyncio.run(test_search())



