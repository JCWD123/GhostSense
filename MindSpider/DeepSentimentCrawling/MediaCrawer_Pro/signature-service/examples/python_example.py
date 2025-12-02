"""
Python 使用示例
展示如何在 Python 项目中调用签名服务
"""

import httpx
import asyncio


# ==================== 示例1：HTTP API 调用 ====================
async def example1_http_api():
    """通过HTTP API调用签名服务"""
    print("\n📝 示例1：HTTP API调用")
    print("================================")
    
    API_URL = "http://localhost:3100"
    
    async with httpx.AsyncClient() as client:
        # 1.1 纯JS签名
        response = await client.post(
            f"{API_URL}/sign/xhs",
            json={
                "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
                "method": "GET",
                "data": {"keyword": "美食", "page": 1},
                "a1": "your_a1_cookie_value"
            }
        )
        
        result = response.json()
        print("JS签名结果:")
        print(f"  x-s: {result['data']['x-s'][:30]}...")
        print(f"  x-t: {result['data']['x-t']}")
        print(f"  模式: {result.get('mode', 'unknown')}")


# ==================== 示例2：浏览器模式 ====================
async def example2_browser_mode():
    """Playwright浏览器模式获取完整签名"""
    print("\n🌐 示例2：Playwright浏览器模式")
    print("================================")
    
    API_URL = "http://localhost:3100"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_URL}/sign/xhs/browser",
            json={
                "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
                "method": "GET",
                "data": {"keyword": "美食"},
                "cookie": "a1=xxx; webId=xxx; web_session=xxx"
            }
        )
        
        result = response.json()
        if result.get("success"):
            headers = result["data"]
            print("浏览器模式结果:")
            print(f"  x-s: {headers.get('x-s', '')[:30]}...")
            print(f"  x-t: {headers.get('x-t', '')}")
            print(f"  x-s-common: {headers.get('x-s-common', '')[:30]}...")
            print(f"  模式: {result.get('mode', 'unknown')}")


# ==================== 示例3：混合模式（推荐） ====================
async def example3_hybrid_mode():
    """混合模式：自动选择最优方案"""
    print("\n🎯 示例3：混合模式（推荐）")
    print("================================")
    
    API_URL = "http://localhost:3100"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 自动模式
        response = await client.post(
            f"{API_URL}/sign/xhs/hybrid",
            json={
                "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
                "method": "GET",
                "data": {"keyword": "美食"},
                "a1": "your_a1_value",
                "cookie": "complete_cookie_string",
                "mode": "auto"  # 自动选择
            }
        )
        
        result = response.json()
        if result.get("success"):
            headers = result["data"]
            print("混合模式结果:")
            print(f"  使用的模式: {headers.get('mode', 'unknown')}")
            print(f"  x-s: {headers.get('x-s', '')[:30]}...")
            print(f"  x-t: {headers.get('x-t', '')}")


# ==================== 示例4：完整的爬虫示例 ====================
async def example4_full_crawler():
    """完整的爬虫示例：获取签名 + 请求API"""
    print("\n🕷️  示例4：完整爬虫示例")
    print("================================")
    
    API_URL = "http://localhost:3100"
    XHS_API_URL = "https://edith.xiaohongshu.com"
    
    # 配置
    keyword = "美食"
    cookie = "a1=xxx; webId=xxx; web_session=xxx"  # 替换为真实Cookie
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 获取签名
        print("步骤1: 获取签名...")
        sign_response = await client.post(
            f"{API_URL}/sign/xhs/hybrid",
            json={
                "url": f"{XHS_API_URL}/api/sns/web/v1/search/notes",
                "method": "GET",
                "data": {"keyword": keyword, "page": 1},
                "cookie": cookie,
                "mode": "auto"
            }
        )
        
        sign_result = sign_response.json()
        if not sign_result.get("success"):
            print("❌ 签名获取失败")
            return
        
        headers = sign_result["data"]
        print(f"✅ 签名获取成功 (模式: {headers.get('mode', 'unknown')})")
        
        # 2. 使用签名请求小红书API
        print("\n步骤2: 请求小红书API...")
        
        xhs_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": cookie,
            "x-s": headers.get("x-s", ""),
            "x-t": headers.get("x-t", ""),
            "Referer": "https://www.xiaohongshu.com/",
            "Origin": "https://www.xiaohongshu.com"
        }
        
        # 如果有x-s-common，也加上
        if headers.get("x-s-common"):
            xhs_headers["x-s-common"] = headers["x-s-common"]
        
        xhs_response = await client.get(
            f"{XHS_API_URL}/api/sns/web/v1/search/notes",
            params={"keyword": keyword, "page": 1, "page_size": 20},
            headers=xhs_headers
        )
        
        if xhs_response.status_code == 200:
            result = xhs_response.json()
            items = result.get("data", {}).get("items", [])
            print(f"✅ 搜索成功！找到 {len(items)} 条笔记")
            
            # 打印前3条
            for i, item in enumerate(items[:3], 1):
                note = item.get("note_card", {})
                print(f"\n{i}. {note.get('display_title', 'N/A')}")
                print(f"   作者: {note.get('user', {}).get('nickname', 'N/A')}")
                print(f"   点赞: {note.get('interact_info', {}).get('liked_count', 0)}")
        else:
            print(f"❌ 请求失败: {xhs_response.status_code}")
            print(f"响应: {xhs_response.text[:200]}")


# ==================== 示例5：连接Electron ====================
async def example5_electron_integration():
    """连接到Electron浏览器"""
    print("\n🔗 示例5：连接Electron浏览器")
    print("================================")
    print("⚠️  需要Electron应用运行在端口9222")
    print("💡 启动方式: cd frontend && npm run electron:dev\n")
    
    API_URL = "http://localhost:3100"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_URL}/sign/xhs/browser",
                json={
                    "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
                    "method": "GET",
                    "data": {"keyword": "美食"},
                    "cookie": "a1=xxx; webId=xxx",
                    "debugPort": 9222  # Electron调试端口
                }
            )
            
            result = response.json()
            if result.get("success"):
                print("✅ 成功连接到Electron浏览器")
                headers = result["data"]
                print(f"  x-s: {headers.get('x-s', '')[:30]}...")
                print(f"  x-s-common: {headers.get('x-s-common', '')[:30]}...")
            else:
                print(f"❌ 连接失败: {result.get('message')}")
        except Exception as e:
            print(f"❌ 错误: {e}")
            print("💡 确保Electron应用正在运行")


# ==================== 运行所有示例 ====================
async def main():
    print("\n╔════════════════════════════════════════╗")
    print("║  MediaCrawler 签名服务 Python示例     ║")
    print("╚════════════════════════════════════════╝")
    
    try:
        await example1_http_api()
        # await example2_browser_mode()  # 取消注释以运行
        await example3_hybrid_mode()
        await example4_full_crawler()
        # await example5_electron_integration()  # 需要Electron运行
        
        print("\n✅ 所有示例运行完成")
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        print("💡 确保签名服务正在运行: cd signature-service && npm start")


if __name__ == "__main__":
    asyncio.run(main())






