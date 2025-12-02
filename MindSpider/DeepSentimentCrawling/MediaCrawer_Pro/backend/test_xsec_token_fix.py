#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 xsec_token 获取修复
验证从详情页提取 xsec_token 的功能
"""
import asyncio
from loguru import logger
from crawler.xhs_client import XHSClient


async def test_xsec_token_extraction():
    """测试 xsec_token 提取"""
    print("=" * 60)
    print("🧪 测试 xsec_token 提取修复")
    print("=" * 60)
    print()
    
    client = XHSClient()
    
    try:
        # 1. 先搜索获取一些 note_id
        print("1️⃣ 搜索笔记...")
        notes = await client.search_notes(
            keyword="测试",
            page=1,
            page_size=3
        )
        
        if not notes:
            print("❌ 搜索失败，无法获取笔记")
            return
        
        print(f"✅ 获取到 {len(notes)} 条笔记\n")
        
        # 2. 对每个 note_id 测试获取 xsec_token
        print("2️⃣ 测试获取 xsec_token:")
        print("=" * 60)
        
        success_count = 0
        fail_count = 0
        
        for i, note in enumerate(notes, 1):
            note_id = note.get("note_id", "")
            title = note.get("title", "无标题")[:30]
            
            if not note_id:
                print(f"⚠️  [{i}] 跳过（note_id 为空）")
                continue
            
            print(f"\n📝 [{i}] 笔记: {note_id}")
            print(f"    标题: {title}")
            
            # 测试获取详情页
            try:
                detail = await client.get_note_detail_for_token(note_id)
                
                if detail:
                    xsec_token = detail.get("xsec_token", "")
                    xsec_source = detail.get("xsec_source", "")
                    
                    if xsec_token:
                        print(f"    ✅ xsec_token: {xsec_token[:30]}...")
                        print(f"    ✅ xsec_source: {xsec_source}")
                        success_count += 1
                        
                        # 尝试获取评论（验证 token 有效性）
                        print(f"    🔍 测试获取评论...")
                        comments_result = await client.get_note_comments(
                            note_id,
                            xsec_token=xsec_token,
                            xsec_source=xsec_source
                        )
                        
                        comments = comments_result.get("comments", [])
                        if comments:
                            print(f"    ✅ 成功获取 {len(comments)} 条评论")
                        else:
                            has_more = comments_result.get("has_more", False)
                            if has_more:
                                print(f"    ℹ️  无评论或需要翻页")
                            else:
                                print(f"    ℹ️  该笔记暂无评论")
                    else:
                        print(f"    ⚠️  详情页未包含 xsec_token")
                        fail_count += 1
                else:
                    print(f"    ❌ 获取详情页失败")
                    fail_count += 1
                    
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                fail_count += 1
            
            # 延迟，避免请求过快
            await asyncio.sleep(1)
        
        # 3. 统计结果
        print("\n" + "=" * 60)
        print("📊 测试结果:")
        print("=" * 60)
        print(f"✅ 成功获取 xsec_token: {success_count}/{len(notes)}")
        print(f"❌ 失败: {fail_count}/{len(notes)}")
        
        if success_count > 0:
            print("\n🎉 修复成功！可以正常获取 xsec_token 并抓取评论了！")
            print("\n💡 建议:")
            print("   1. 重新运行爬取任务，评论功能会自动生效")
            print("   2. 已有的 note_id 会自动从详情页获取 token")
            print("   3. token 会缓存到数据库，避免重复请求")
        else:
            print("\n⚠️  所有请求都失败了，可能原因:")
            print("   1. Cookie 已过期，需要重新登录")
            print("   2. 请求被限流，稍后再试")
            print("   3. API 接口可能发生变化")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


async def test_comment_crawl_with_auto_token():
    """测试完整的评论抓取流程（带自动 token 获取）"""
    print("\n" + "=" * 60)
    print("🧪 测试完整评论抓取流程")
    print("=" * 60)
    print()
    
    from services.task_service import TaskService
    from core.database import mongo_db
    
    try:
        # 连接数据库
        await mongo_db.connect()
        
        task_service = TaskService()
        client = XHSClient()
        
        # 搜索笔记
        print("1️⃣ 搜索笔记...")
        notes = await client.search_notes(keyword="测试", page=1, page_size=2)
        
        if not notes:
            print("❌ 搜索失败")
            return
        
        print(f"✅ 获取到 {len(notes)} 条笔记\n")
        
        # 测试评论抓取
        print("2️⃣ 测试评论抓取（带自动 token 获取）:")
        print("=" * 60)
        
        for i, note in enumerate(notes, 1):
            note_id = note.get("note_id", "")
            if not note_id:
                continue
            
            print(f"\n📝 [{i}] note_id: {note_id}")
            print(f"    标题: {note.get('title', '')[:30]}")
            
            # 调用 _crawl_comments（会自动获取 token）
            await task_service._crawl_comments(
                client,
                note_id,
                "test_task_id"
            )
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mongo_db.close()
        await client.close()


if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 测试 xsec_token 提取")
    print("2. 测试完整评论抓取流程")
    choice = input("\n请选择 (1/2) [默认: 1]: ").strip() or "1"
    
    if choice == "2":
        asyncio.run(test_comment_crawl_with_auto_token())
    else:
        asyncio.run(test_xsec_token_extraction())


