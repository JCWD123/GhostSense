#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 功能测试脚本

使用方法：
1. 确保已安装 DrissionPage: pip install DrissionPage>=4.0.0
2. 修改 config/base_config.py 中的 USE_DRISSION_PAGE = True
3. 运行本脚本: python test_drission_page.py
"""

import asyncio
from DrissionPage import ChromiumPage, ChromiumOptions


async def test_drission_page_basic():
    """测试 DrissionPage 基本功能"""
    print("=" * 60)
    print("测试 DrissionPage 基本功能")
    print("=" * 60)
    
    # 配置浏览器选项
    co = ChromiumOptions()
    co.set_argument('--disable-blink-features=AutomationControlled')
    
    # 创建浏览器页面
    page = ChromiumPage(addr_or_opts=co)
    
    try:
        # 访问小红书
        print("\n1. 正在访问小红书首页...")
        page.get("https://www.xiaohongshu.com")
        await asyncio.sleep(2)
        
        # 检查页面标题
        title = page.title
        print(f"   页面标题: {title}")
        
        # 检查是否能找到登录按钮
        print("\n2. 查找登录按钮...")
        login_button = page.ele("xpath://*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button", timeout=5)
        if login_button:
            print("   ✅ 找到登录按钮")
        else:
            print("   ⚠️ 未找到登录按钮（可能已登录）")
        
        # 检查 cookies
        print("\n3. 检查 Cookies...")
        cookies = page.cookies(all_domains=True, all_info=True)
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        print(f"   Cookie 数量: {len(cookie_dict)}")
        if 'web_session' in cookie_dict:
            print(f"   ✅ 找到 web_session: {cookie_dict['web_session'][:20]}...")
        else:
            print("   ℹ️ 未找到 web_session（未登录）")
        
        # 测试元素查找
        print("\n4. 测试 xpath 元素查找...")
        search_box = page.ele("xpath://input[@placeholder='搜索']", timeout=5)
        if search_box:
            print("   ✅ 找到搜索框")
        else:
            print("   ℹ️ 未找到搜索框")
        
        print("\n" + "=" * 60)
        print("✅ DrissionPage 基本功能测试完成！")
        print("=" * 60)
        
        # 等待用户查看
        print("\n浏览器将在 10 秒后关闭...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭浏览器
        page.quit()
        print("\n浏览器已关闭")


async def test_xpath_compatibility():
    """测试 xpath 语法兼容性"""
    print("\n" + "=" * 60)
    print("测试 xpath 语法兼容性")
    print("=" * 60)
    
    co = ChromiumOptions()
    co.set_argument('--disable-blink-features=AutomationControlled')
    page = ChromiumPage(addr_or_opts=co)
    
    try:
        page.get("https://www.xiaohongshu.com")
        await asyncio.sleep(2)
        
        # 测试各种 xpath 语法
        test_cases = [
            ("//img[@class='qrcode-img']", "二维码图片"),
            ("//div[@class='login-container']", "登录容器"),
            ("//*[@id='app']", "App根节点"),
            ("//input[@placeholder]", "搜索框（通过属性）"),
        ]
        
        print("\n测试 xpath 表达式:")
        for xpath, desc in test_cases:
            try:
                element = page.ele(f"xpath:{xpath}", timeout=2)
                status = "✅ 找到" if element else "⚠️ 未找到"
                print(f"   {status} - {desc}")
            except Exception as e:
                print(f"   ❌ 错误 - {desc}: {str(e)[:50]}")
        
        print("\n" + "=" * 60)
        print("✅ xpath 兼容性测试完成！")
        print("=" * 60)
        
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
    
    finally:
        page.quit()


async def test_anti_detection():
    """测试反检测能力"""
    print("\n" + "=" * 60)
    print("测试反检测能力")
    print("=" * 60)
    
    co = ChromiumOptions()
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--no-sandbox')
    
    page = ChromiumPage(addr_or_opts=co)
    
    try:
        page.get("https://www.xiaohongshu.com")
        await asyncio.sleep(2)
        
        # 执行 JavaScript 检测自动化特征
        print("\n1. 检测自动化特征...")
        
        # 检查 webdriver
        webdriver_check = page.run_js("return navigator.webdriver")
        print(f"   navigator.webdriver: {webdriver_check}")
        if not webdriver_check:
            print("   ✅ 成功隐藏 webdriver 特征")
        else:
            print("   ⚠️ webdriver 特征未被隐藏")
        
        # 检查 Chrome
        chrome_check = page.run_js("return typeof window.chrome !== 'undefined'")
        print(f"   window.chrome 存在: {chrome_check}")
        
        # 检查 plugins
        plugins_count = page.run_js("return navigator.plugins.length")
        print(f"   插件数量: {plugins_count}")
        
        print("\n" + "=" * 60)
        print("✅ 反检测能力测试完成！")
        print("=" * 60)
        
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
    
    finally:
        page.quit()


async def main():
    """主测试函数"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + " " * 12 + "DrissionPage 功能测试套件" + " " * 12 + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    try:
        # 测试 1: 基本功能
        await test_drission_page_basic()
        
        # 测试 2: xpath 兼容性
        await test_xpath_compatibility()
        
        # 测试 3: 反检测能力
        await test_anti_detection()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        print("=" * 60)
        print("\n如果所有测试都通过，可以开始使用 DrissionPage 进行爬取：")
        print("  1. 修改 config/base_config.py 设置 USE_DRISSION_PAGE = True")
        print("  2. 运行: python main.py --platform xhs --lt qrcode --type search")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

