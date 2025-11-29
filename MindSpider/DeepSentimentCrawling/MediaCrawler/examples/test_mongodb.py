#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 存储测试脚本
用于测试 MongoDB 连接和数据存储功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from database.mongodb_session import (
    test_mongodb_connection,
    init_mongodb_indexes,
    get_mongodb_database,
    close_mongodb_connection
)
from store.xhs.mongodb_store import XhsMongoDBStoreImplement
from tools import utils


async def test_connection():
    """测试 MongoDB 连接"""
    print("=" * 60)
    print("🔌 测试 MongoDB 连接...")
    print("=" * 60)
    
    result = await test_mongodb_connection()
    if result:
        print("✅ MongoDB 连接成功！\n")
        return True
    else:
        print("❌ MongoDB 连接失败，请检查配置\n")
        return False


async def test_indexes():
    """测试索引创建"""
    print("=" * 60)
    print("📊 创建 MongoDB 索引...")
    print("=" * 60)
    
    result = await init_mongodb_indexes()
    if result:
        print("✅ 索引创建成功！\n")
        return True
    else:
        print("❌ 索引创建失败\n")
        return False


async def test_store_data():
    """测试数据存储"""
    print("=" * 60)
    print("💾 测试数据存储...")
    print("=" * 60)
    
    try:
        # 创建存储实例
        store = XhsMongoDBStoreImplement()
        
        # 测试数据
        test_note = {
            "note_id": "test_note_001",
            "type": "normal",
            "title": "MongoDB 测试笔记",
            "desc": "这是一条测试数据，用于验证 MongoDB 存储功能",
            "video_url": "",
            "time": 1700000000000,
            "last_update_time": 1700000000000,
            "user_id": "test_user_001",
            "nickname": "测试用户",
            "avatar": "https://example.com/avatar.jpg",
            "liked_count": "100",
            "collected_count": "50",
            "comment_count": "20",
            "share_count": "10",
            "ip_location": "北京",
            "image_list": "https://img1.jpg,https://img2.jpg",
            "tag_list": "测试,MongoDB,爬虫",
            "note_url": "https://www.xiaohongshu.com/explore/test_note_001",
            "source_keyword": "测试",
            "xsec_token": "test_token"
        }
        
        test_comment = {
            "comment_id": "test_comment_001",
            "note_id": "test_note_001",
            "content": "这是一条测试评论",
            "create_time": 1700000000000,
            "user_id": "test_user_002",
            "nickname": "评论用户",
            "avatar": "https://example.com/avatar2.jpg",
            "sub_comment_count": "5",
            "like_count": "10",
            "pictures": "",
            "parent_comment_id": "",
            "ip_location": "上海"
        }
        
        test_creator = {
            "user_id": "test_user_001",
            "nickname": "测试创作者",
            "avatar": "https://example.com/creator.jpg",
            "desc": "这是一个测试创作者账号",
            "gender": "女",
            "ip_location": "广州",
            "follows": "1000",
            "fans": "5000",
            "interaction": "10000",
            "tag_list": {"type1": "美食", "type2": "旅游"}
        }
        
        # 存储笔记
        print("📝 存储测试笔记...")
        await store.store_content(test_note)
        
        # 存储评论
        print("💬 存储测试评论...")
        await store.store_comment(test_comment)
        
        # 存储创作者
        print("👤 存储测试创作者...")
        await store.store_creator(test_creator)
        
        print("✅ 数据存储测试成功！\n")
        return True
        
    except Exception as e:
        print(f"❌ 数据存储测试失败: {e}\n")
        return False


async def test_query_data():
    """测试数据查询"""
    print("=" * 60)
    print("🔍 测试数据查询...")
    print("=" * 60)
    
    try:
        db = get_mongodb_database()
        
        # 查询笔记
        note = await db.xhs_notes.find_one({"note_id": "test_note_001"})
        if note:
            print(f"✅ 成功查询到笔记: {note.get('title')}")
        else:
            print("⚠️  未找到测试笔记")
        
        # 查询评论
        comment = await db.xhs_comments.find_one({"comment_id": "test_comment_001"})
        if comment:
            print(f"✅ 成功查询到评论: {comment.get('content')}")
        else:
            print("⚠️  未找到测试评论")
        
        # 查询创作者
        creator = await db.xhs_creators.find_one({"user_id": "test_user_001"})
        if creator:
            print(f"✅ 成功查询到创作者: {creator.get('nickname')}")
        else:
            print("⚠️  未找到测试创作者")
        
        # 统计数据
        note_count = await db.xhs_notes.count_documents({})
        comment_count = await db.xhs_comments.count_documents({})
        creator_count = await db.xhs_creators.count_documents({})
        
        print(f"\n📊 数据统计:")
        print(f"   笔记总数: {note_count}")
        print(f"   评论总数: {comment_count}")
        print(f"   创作者总数: {creator_count}")
        
        print("\n✅ 数据查询测试成功！\n")
        return True
        
    except Exception as e:
        print(f"❌ 数据查询测试失败: {e}\n")
        return False


async def cleanup_test_data():
    """清理测试数据"""
    print("=" * 60)
    print("🗑️  清理测试数据...")
    print("=" * 60)
    
    try:
        db = get_mongodb_database()
        
        # 删除测试数据
        await db.xhs_notes.delete_one({"note_id": "test_note_001"})
        await db.xhs_comments.delete_one({"comment_id": "test_comment_001"})
        await db.xhs_creators.delete_one({"user_id": "test_user_001"})
        
        print("✅ 测试数据清理完成！\n")
        return True
        
    except Exception as e:
        print(f"❌ 清理测试数据失败: {e}\n")
        return False


async def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("🚀 BettaFish MongoDB 存储测试")
    print("=" * 60 + "\n")
    
    try:
        # 1. 测试连接
        if not await test_connection():
            print("❌ 连接失败，请检查 MongoDB 配置")
            print("\n配置方法：")
            print("1. 编辑 .env 文件，设置 MongoDB 连接参数")
            print("2. 或设置环境变量: MONGODB_HOST, MONGODB_PORT 等")
            return
        
        # 2. 创建索引
        await test_indexes()
        
        # 3. 测试存储
        if not await test_store_data():
            return
        
        # 4. 测试查询
        await test_query_data()
        
        # 5. 清理测试数据
        await cleanup_test_data()
        
        print("=" * 60)
        print("🎉 所有测试通过！MongoDB 存储功能正常")
        print("=" * 60)
        print("\n💡 提示：")
        print("   - 现在可以使用 --save_data_option mongodb 参数运行爬虫")
        print("   - 查看详细文档: docs/MongoDB使用指南.md")
        print("   - 数据库: bettafish")
        print("   - 集合: xhs_notes, xhs_comments, xhs_creators, ...")
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭连接
        await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(main())





