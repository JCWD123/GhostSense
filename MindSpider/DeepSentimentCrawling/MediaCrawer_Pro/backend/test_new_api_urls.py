#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的小红书接口 URL

验证以下接口：
1. POST /api/sns/web/v1/feed - 详情接口
2. POST /api/v2/collect - 评论接口（t2 域名）
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from crawler.xhs_client import XHSClient
from loguru import logger


async def test_detail_api():
    """测试详情接口（feed）"""
    print("\n" + "=" * 70)
    print("📝 测试详情接口: /api/sns/web/v1/feed")
    print("=" * 70)
    
    client = XHSClient()
    
    # 使用一个已知的 note_id（替换为实际的）
    test_note_id = "68303bbb000000002100f85c"
    
    try:
        logger.info(f"测试 note_id: {test_note_id}")
        
        detail = await client.get_note_detail(test_note_id)
        
        if detail:
            print("\n✅ 详情接口测试成功!")
            print(f"   📌 Note ID: {detail.get('note_id', 'N/A')}")
            print(f"   📝 标题: {detail.get('title', 'N/A')[:50]}...")
            print(f"   👤 作者: {detail.get('user_name', 'N/A')}")
            print(f"   ❤️  点赞: {detail.get('liked_count', 0)}")
            print(f"   💬 评论: {detail.get('comments_count', 0)}")
            return True
        else:
            print("\n❌ 详情接口测试失败")
            print("   可能原因:")
            print("   1. note_id 不存在或已删除")
            print("   2. 需要登录状态")
            print("   3. 接口 URL 仍然不正确")
            return False
            
    except Exception as e:
        print(f"\n❌ 详情接口测试异常: {e}")
        logger.error(f"详情接口异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()


async def test_token_api():
    """测试获取 xsec_token"""
    print("\n" + "=" * 70)
    print("🔑 测试获取 xsec_token: /api/sns/web/v1/feed")
    print("=" * 70)
    
    client = XHSClient()
    
    test_note_id = "68303bbb000000002100f85c"
    
    try:
        logger.info(f"测试 note_id: {test_note_id}")
        
        token_data = await client.get_note_detail_for_token(test_note_id)
        
        if token_data and token_data.get("xsec_token"):
            print("\n✅ xsec_token 获取成功!")
            print(f"   🔑 Token: {token_data['xsec_token'][:40]}...")
            print(f"   📍 Source: {token_data.get('xsec_source', 'N/A')}")
            print(f"   📝 Title: {token_data.get('title', 'N/A')[:50]}...")
            return token_data
        else:
            print("\n❌ xsec_token 获取失败")
            print("   可能原因:")
            print("   1. 响应结构发生变化")
            print("   2. token 在其他位置")
            print("   3. 需要登录状态")
            return None
            
    except Exception as e:
        print(f"\n❌ xsec_token 获取异常: {e}")
        logger.error(f"xsec_token 获取异常: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await client.close()


async def test_comment_api(xsec_token: str, xsec_source: str):
    """测试评论接口（collect）"""
    print("\n" + "=" * 70)
    print("💬 测试评论接口: https://t2.xiaohongshu.com/api/v2/collect")
    print("=" * 70)
    
    client = XHSClient()
    
    test_note_id = "68303bbb000000002100f85c"
    
    try:
        logger.info(f"测试 note_id: {test_note_id}")
        logger.info(f"使用 token: {xsec_token[:30]}...")
        
        # 先设置一个 cookie（如果有的话）
        # client.set_cookie("your_cookie_here")
        
        comments_result = await client.get_note_comments(
            note_id=test_note_id,
            xsec_token=xsec_token,
            xsec_source=xsec_source,
            cursor="",
            referer=f"https://www.xiaohongshu.com/explore/{test_note_id}"
        )
        
        if comments_result.get("success"):
            comments = comments_result.get("comments", [])
            print("\n✅ 评论接口测试成功!")
            print(f"   💬 评论数: {len(comments)}")
            print(f"   📄 游标: {comments_result.get('cursor', 'N/A')}")
            print(f"   ➡️  更多: {comments_result.get('has_more', False)}")
            
            if comments:
                print(f"\n   前 3 条评论:")
                for i, comment in enumerate(comments[:3], 1):
                    content = comment.get("content", "N/A")
                    user = comment.get("user_name", "匿名")
                    likes = comment.get("likes", 0)
                    print(f"   {i}. [{user}] {content[:40]}... (👍 {likes})")
            
            return True
        else:
            error = comments_result.get("error", "Unknown")
            print(f"\n❌ 评论接口测试失败: {error}")
            print("   可能原因:")
            print("   1. xsec_token 无效或过期")
            print("   2. 需要登录状态")
            print("   3. 接口 URL 不正确")
            print("   4. 缺少必需的 headers")
            return False
            
    except Exception as e:
        print(f"\n❌ 评论接口测试异常: {e}")
        logger.error(f"评论接口异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()


async def main():
    """主测试流程"""
    print("\n" + "🧪" * 35)
    print("🔬 小红书新接口 URL 测试")
    print("🧪" * 35)
    
    print("\n📋 测试说明:")
    print("   1. 详情接口: POST /api/sns/web/v1/feed (参数: source_note_id)")
    print("   2. 评论接口: POST https://t2.xiaohongshu.com/api/v2/collect")
    print("   3. 注意：评论接口需要 xsec_token，从详情接口获取")
    
    # 测试1: 详情接口
    detail_ok = await test_detail_api()
    
    # 测试2: 获取 xsec_token
    token_data = await test_token_api()
    
    # 测试3: 评论接口（如果成功获取了 token）
    comment_ok = False
    if token_data and token_data.get("xsec_token"):
        comment_ok = await test_comment_api(
            xsec_token=token_data["xsec_token"],
            xsec_source=token_data.get("xsec_source", "pc_feed")
        )
    else:
        print("\n⚠️ 跳过评论接口测试（因为未能获取 xsec_token）")
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    print(f"   {'✅' if detail_ok else '❌'} 详情接口: {'通过' if detail_ok else '失败'}")
    print(f"   {'✅' if token_data else '❌'} Token 获取: {'通过' if token_data else '失败'}")
    print(f"   {'✅' if comment_ok else '❌'} 评论接口: {'通过' if comment_ok else '失败'}")
    
    if detail_ok and token_data and comment_ok:
        print("\n🎉 所有接口测试通过！")
        print("   新的接口 URL 已正确配置，可以正常使用。")
    else:
        print("\n⚠️ 部分接口测试失败")
        print("   请检查:")
        print("   1. note_id 是否有效")
        print("   2. 是否需要登录（Cookie）")
        print("   3. 签名服务是否正常")
        print("   4. Electron 是否运行（浏览器内执行模式）")
    
    print("\n💡 提示:")
    print("   - 如果所有测试都失败，请先确保签名服务正常运行")
    print("   - 评论接口可能需要有效的登录状态")
    print("   - 可以先在 Electron 中扫码登录，然后重新测试")
    print("   - 详细日志请查看: backend/logs/app.log")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

