#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Playwright 的小红书爬虫客户端
使用真实浏览器环境，自动处理所有签名
"""
import asyncio
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Page, Browser
from loguru import logger


class PlaywrightXHSClient:
    """
    使用 Playwright 的小红书客户端
    
    优势：
    1. 真实浏览器环境，完全绕过签名检测
    2. 自动处理 Cookie、x-s、x-t、x-s-common
    3. 不需要逆向任何算法
    4. 稳定性高
    """
    
    def __init__(self, cookie: str = "", headless: bool = True):
        """
        初始化
        
        Args:
            cookie: 完整的Cookie字符串
            headless: 是否无头模式
        """
        self.cookie = cookie
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._playwright = None
    
    async def __aenter__(self):
        """异步上下文管理器"""
        await self.init()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """关闭"""
        await self.close()
    
    async def init(self):
        """初始化浏览器"""
        logger.info("🚀 启动 Playwright 浏览器...")
        
        self._playwright = await async_playwright().start()
        
        # 启动浏览器
        self.browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        
        # 创建上下文
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 注入Cookie
        if self.cookie:
            cookies = self._parse_cookie_string(self.cookie)
            await context.add_cookies(cookies)
            logger.info("✅ Cookie 已注入")
        
        # 创建页面
        self.page = await context.new_page()
        
        # 导航到小红书
        await self.page.goto('https://www.xiaohongshu.com')
        await self.page.wait_for_load_state('networkidle')
        
        logger.success("✅ 浏览器初始化完成")
    
    def _parse_cookie_string(self, cookie_str: str) -> List[Dict]:
        """解析Cookie字符串为Playwright格式"""
        cookies = []
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                name, value = item.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip(),
                    'domain': '.xiaohongshu.com',
                    'path': '/'
                })
        return cookies
    
    async def search_notes(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
        sort: str = "general"
    ) -> Dict:
        """
        搜索笔记
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort: 排序方式
        
        Returns:
            搜索结果
        """
        logger.info(f"🔍 搜索笔记: {keyword}, 页码: {page}")
        
        try:
            # 拦截API响应
            search_result = None
            
            async def handle_response(response):
                nonlocal search_result
                if '/api/sns/web/v1/search/notes' in response.url:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            search_result = data
                            logger.success(f"✅ 捕获到搜索结果: {len(data.get('data', {}).get('items', []))} 条")
                        except Exception as e:
                            logger.error(f"解析响应失败: {e}")
            
            # 监听响应
            self.page.on('response', handle_response)
            
            # 在搜索框输入关键词
            search_input = await self.page.query_selector('input[placeholder*="搜索"]')
            if search_input:
                await search_input.fill(keyword)
                await search_input.press('Enter')
                
                # 等待API响应（最多10秒）
                for _ in range(20):
                    if search_result:
                        break
                    await asyncio.sleep(0.5)
                
                if search_result:
                    return search_result
                else:
                    logger.warning("⚠️ 未捕获到API响应，尝试直接请求")
            
            # 如果监听失败，直接导航到搜索页面并解析
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
            await self.page.goto(search_url)
            await self.page.wait_for_load_state('networkidle')
            
            # 从页面中提取笔记数据
            notes = await self.page.evaluate('''() => {
                const items = document.querySelectorAll('section');
                return Array.from(items).slice(0, 20).map(item => ({
                    title: item.textContent.substring(0, 100),
                }));
            }''')
            
            return {
                "success": True,
                "data": {
                    "items": notes,
                    "has_more": True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return {
                "success": False,
                "msg": str(e)
            }
    
    async def get_note_detail(self, note_id: str) -> Dict:
        """获取笔记详情"""
        logger.info(f"📖 获取笔记详情: {note_id}")
        
        try:
            url = f"https://www.xiaohongshu.com/explore/{note_id}"
            await self.page.goto(url)
            await self.page.wait_for_load_state('networkidle')
            
            # 提取笔记信息
            note_data = await self.page.evaluate('''() => {
                return {
                    title: document.querySelector('meta[property="og:title"]')?.content || '',
                    description: document.querySelector('meta[property="og:description"]')?.content || '',
                    images: Array.from(document.querySelectorAll('img')).map(img => img.src).filter(src => src.includes('sns-')),
                };
            }''')
            
            return {
                "success": True,
                "data": note_data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取详情失败: {e}")
            return {
                "success": False,
                "msg": str(e)
            }
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            logger.info("👋 浏览器已关闭")
        
        if self._playwright:
            await self._playwright.stop()


# 测试
async def test():
    """测试函数"""
    # 使用你的Cookie
    cookie = """
    abRequestId=d2934dac-d798-5d19-9ef6-a9fc4527fe27; 
    a1=199e3b169bbs36kx94cq4rrb6p7ghvgpd9msa3rtt50000173588; 
    webId=8a849dade1cb0a26b1b1f29450cb9a7a; 
    web_session=040069b9390f7b3c59cd8626283b4b9f0688fa;
    xsecappid=xhs-pc-web;
    """
    
    async with PlaywrightXHSClient(cookie=cookie, headless=False) as client:
        # 搜索
        result = await client.search_notes("美食", page=1, page_size=20)
        
        if result.get("success"):
            items = result.get("data", {}).get("items", [])
            print(f"\n✅ 搜索成功！找到 {len(items)} 条笔记")
            
            for i, item in enumerate(items[:3], 1):
                print(f"{i}. {item}")
        else:
            print(f"\n❌ 搜索失败: {result.get('msg')}")


if __name__ == "__main__":
    asyncio.run(test())





