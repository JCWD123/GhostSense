#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中已存在的空 note_id 记录
通过重新爬取或从其他字段提取
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from core.config import settings
from crawler.xhs_client import XHSClient


async def fix_empty_note_ids():
    """修复空的 note_id"""
    print("=" * 60)
    print("🔧 修复数据库中的空 note_id")
    print("=" * 60)
    print()
    
    # 连接数据库
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    notes_collection = db.notes
    
    try:
        # 1. 统计空 note_id 的记录
        empty_count = await notes_collection.count_documents({"note_id": ""})
        total_count = await notes_collection.count_documents({})
        
        print(f"📊 统计信息:")
        print(f"   总记录数: {total_count}")
        print(f"   空 note_id: {empty_count}")
        print(f"   有效 note_id: {total_count - empty_count}")
        print()
        
        if empty_count == 0:
            print("✅ 没有空 note_id，无需修复！")
            return
        
        # 2. 方案选择
        print("🔧 修复方案:")
        print("   方案 1: 删除空 note_id 记录（推荐）")
        print("   方案 2: 尝试从其他字段提取")
        print("   方案 3: 保持不变，仅提示")
        print()
        
        choice = input("请选择方案 (1/2/3) [默认: 1]: ").strip() or "1"
        
        if choice == "1":
            # 删除空 note_id 的记录
            print(f"\n🗑️  准备删除 {empty_count} 条空 note_id 记录...")
            confirm = input("确认删除？(yes/no) [默认: no]: ").strip().lower()
            
            if confirm == "yes":
                result = await notes_collection.delete_many({"note_id": ""})
                print(f"✅ 已删除 {result.deleted_count} 条记录")
                print("💡 建议重新运行爬取任务获取完整数据")
            else:
                print("❌ 已取消删除操作")
        
        elif choice == "2":
            # 尝试从 _id 生成 note_id
            print("\n🔄 尝试从其他字段生成 note_id...")
            empty_notes = notes_collection.find({"note_id": ""})
            
            updated = 0
            async for note in empty_notes:
                # 尝试从 MongoDB _id 生成一个唯一标识
                generated_id = f"generated_{str(note['_id'])}"
                await notes_collection.update_one(
                    {"_id": note["_id"]},
                    {"$set": {"note_id": generated_id, "note_id_generated": True}}
                )
                updated += 1
            
            print(f"✅ 已更新 {updated} 条记录")
            print("⚠️  注意: 这些是生成的 ID，不是真实的小红书 note_id")
        
        elif choice == "3":
            print("\n📋 保持不变，仅记录问题")
            async for note in notes_collection.find({"note_id": ""}).limit(5):
                print(f"   - _id: {note['_id']}")
                print(f"     title: {note.get('title', 'N/A')[:40]}")
                print(f"     user: {note.get('nickname', 'N/A')}")
                print()
        
        # 3. 最终统计
        print("\n" + "=" * 60)
        final_empty = await notes_collection.count_documents({"note_id": ""})
        final_total = await notes_collection.count_documents({})
        print(f"✅ 修复完成")
        print(f"   剩余空 note_id: {final_empty}/{final_total}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(fix_empty_note_ids())


