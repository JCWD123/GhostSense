#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库诊断脚本
检查 MongoDB 连接、表结构和数据
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import sys

from core.config import settings


async def check_mongodb():
    """检查 MongoDB 连接和数据"""
    print("=" * 60)
    print("📊 MediaCrawer Pro - 数据库诊断")
    print("=" * 60)
    
    # 1. 显示配置
    print("\n1️⃣ 当前配置:")
    print(f"   MongoDB URL: {settings.MONGODB_URL}")
    print(f"   数据库名称: {settings.DATABASE_NAME}")
    print()
    
    try:
        # 2. 连接数据库
        print("2️⃣ 连接数据库...")
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        
        # 测试连接
        await client.admin.command('ping')
        print("   ✅ MongoDB 连接成功")
        
        db = client[settings.DATABASE_NAME]
        
        # 3. 列出所有集合
        print("\n3️⃣ 数据库集合:")
        collections = await db.list_collection_names()
        if collections:
            for col in collections:
                count = await db[col].count_documents({})
                print(f"   📦 {col}: {count} 条记录")
        else:
            print("   ⚠️  数据库中没有集合")
        
        # 4. 检查 notes 集合
        print("\n4️⃣ notes 集合详情:")
        if 'notes' in collections:
            # 统计信息
            total_notes = await db.notes.count_documents({})
            empty_note_id = await db.notes.count_documents({"note_id": ""})
            valid_note_id = await db.notes.count_documents({"note_id": {"$ne": ""}})
            
            print(f"   总笔记数: {total_notes}")
            print(f"   有效 note_id: {valid_note_id}")
            print(f"   空 note_id: {empty_note_id}")
            
            # 显示最新的几条记录
            if total_notes > 0:
                print("\n   📝 最新 5 条记录:")
                async for note in db.notes.find().sort("_id", -1).limit(5):
                    print(f"      - note_id: {note.get('note_id', 'N/A')[:20]}")
                    print(f"        title: {note.get('title', 'N/A')[:40]}")
                    print(f"        user: {note.get('nickname', 'N/A')}")
                    print()
            
            # 索引信息
            print("   🔍 索引:")
            indexes = await db.notes.list_indexes().to_list(length=100)
            for idx in indexes:
                print(f"      - {idx.get('name')}: {idx.get('key')}")
        else:
            print("   ⚠️  notes 集合不存在")
        
        # 5. 检查其他集合
        print("\n5️⃣ 其他集合:")
        for col_name in ['comments', 'tasks', 'accounts', 'checkpoints']:
            if col_name in collections:
                count = await db[col_name].count_documents({})
                print(f"   ✅ {col_name}: {count} 条记录")
                
                # 显示示例
                if count > 0:
                    sample = await db[col_name].find_one()
                    print(f"      示例字段: {list(sample.keys())[:10]}")
            else:
                print(f"   ⚠️  {col_name}: 集合不存在")
        
        print("\n" + "=" * 60)
        print("✅ 诊断完成")
        print("=" * 60)
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_mongodb())



