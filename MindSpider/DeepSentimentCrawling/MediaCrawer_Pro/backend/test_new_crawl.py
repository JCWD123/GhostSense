#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的爬取功能（验证 note_id 修复）
"""
import asyncio
from loguru import logger
from crawler.xhs_client import XHSClient


async def test_search_with_fixed_note_id():
    """测试搜索功能，验证 note_id 是否正确提取"""
    print("=" * 60)
    print("🧪 测试新的爬取功能")
    print("=" * 60)
    print()
    
    # 创建客户端
    client = XHSClient()
    
    try:
        print("📋 测试参数:")
        print("   关键词: 测试")
        print("   数量: 5 条")
        print()
        
        # 搜索笔记
        print("🔍 开始搜索...")
        notes = await client.search_notes(
            keyword="测试",
            page=1,
            page_size=5
        )
        
        print(f"\n✅ 搜索完成，获取到 {len(notes)} 条笔记\n")
        
        # 验证 note_id
        print("=" * 60)
        print("📊 验证结果:")
        print("=" * 60)
        
        valid_count = 0
        empty_count = 0
        
        for i, note in enumerate(notes, 1):
            note_id = note.get("note_id", "")
            title = note.get("title", "无标题")[:30]
            
            if note_id:
                valid_count += 1
                status = "✅"
            else:
                empty_count += 1
                status = "❌"
            
            print(f"{status} [{i}] note_id: {note_id or '(空)'}")
            print(f"      标题: {title}")
            print(f"      用户: {note.get('nickname', 'N/A')}")
            print()
        
        print("=" * 60)
        print(f"✅ 有效 note_id: {valid_count}/{len(notes)}")
        print(f"❌ 空 note_id: {empty_count}/{len(notes)}")
        print("=" * 60)
        
        if empty_count == 0:
            print("\n🎉 完美！所有 note_id 都已正确提取！")
            print("✅ 修复成功，可以正常使用了！")
        else:
            print("\n⚠️  仍有空 note_id，请检查:")
            print("   1. 确保使用最新的 xhs_client.py (第187-194行的修复)")
            print("   2. 查看完整响应数据结构")
        
        return notes
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_search_with_fixed_note_id())


