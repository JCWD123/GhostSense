# -*- coding: utf-8 -*-
"""
MongoDB 异步会话管理
"""
from typing import Optional
from contextlib import asynccontextmanager

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    AsyncIOMotorClient = None
    AsyncIOMotorDatabase = None

from config.mongodb_config import get_mongodb_uri, mongodb_config
from tools import utils

# 全局 MongoDB 客户端
_mongodb_client: Optional[AsyncIOMotorClient] = None
_mongodb_database: Optional[AsyncIOMotorDatabase] = None


def get_mongodb_client() -> Optional[AsyncIOMotorClient]:
    """
    获取 MongoDB 客户端（单例模式）
    """
    global _mongodb_client
    
    if not MONGODB_AVAILABLE:
        utils.logger.error("[MongoDB] motor package not installed. Please install: pip install motor")
        return None
    
    if _mongodb_client is None:
        try:
            mongodb_uri = get_mongodb_uri()
            utils.logger.info(f"[MongoDB] Connecting to {mongodb_config['host']}:{mongodb_config['port']}")
            
            _mongodb_client = AsyncIOMotorClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5秒超时
                connectTimeoutMS=10000,         # 10秒连接超时
                socketTimeoutMS=30000,          # 30秒socket超时
            )
            utils.logger.info("[MongoDB] Connected successfully")
        except Exception as e:
            utils.logger.error(f"[MongoDB] Connection failed: {e}")
            return None
    
    return _mongodb_client


def get_mongodb_database() -> Optional[AsyncIOMotorDatabase]:
    """
    获取 MongoDB 数据库实例
    """
    global _mongodb_database
    
    if _mongodb_database is None:
        client = get_mongodb_client()
        if client:
            _mongodb_database = client[mongodb_config["db_name"]]
            utils.logger.info(f"[MongoDB] Using database: {mongodb_config['db_name']}")
    
    return _mongodb_database


async def close_mongodb_connection():
    """
    关闭 MongoDB 连接
    """
    global _mongodb_client, _mongodb_database
    
    if _mongodb_client:
        _mongodb_client.close()
        _mongodb_client = None
        _mongodb_database = None
        utils.logger.info("[MongoDB] Connection closed")


async def init_mongodb_indexes():
    """
    初始化 MongoDB 索引
    """
    if not MONGODB_AVAILABLE:
        utils.logger.error("[MongoDB] Cannot init indexes: motor not installed")
        return False
    
    try:
        db = get_mongodb_database()
        if not db:
            return False
        
        utils.logger.info("[MongoDB] Initializing indexes...")
        
        # 小红书笔记索引
        await db.xhs_notes.create_index([("note_id", 1)], unique=True)
        await db.xhs_notes.create_index([("publish_time", -1)])
        await db.xhs_notes.create_index([("user.user_id", 1)])
        await db.xhs_notes.create_index([("source_keyword", 1)])
        await db.xhs_notes.create_index([("add_ts", -1)])
        
        # 小红书评论索引
        await db.xhs_comments.create_index([("comment_id", 1)], unique=True)
        await db.xhs_comments.create_index([("note_id", 1)])
        await db.xhs_comments.create_index([("create_time", -1)])
        await db.xhs_comments.create_index([("user.user_id", 1)])
        
        # 小红书创作者索引
        await db.xhs_creators.create_index([("user_id", 1)], unique=True)
        
        # 抖音索引
        await db.douyin_aweme.create_index([("aweme_id", 1)], unique=True)
        await db.douyin_aweme.create_index([("create_time", -1)])
        await db.douyin_comments.create_index([("comment_id", 1)], unique=True)
        await db.douyin_comments.create_index([("aweme_id", 1)])
        
        # B站索引
        await db.bilibili_videos.create_index([("video_id", 1)], unique=True)
        await db.bilibili_videos.create_index([("create_time", -1)])
        await db.bilibili_comments.create_index([("comment_id", 1)], unique=True)
        await db.bilibili_comments.create_index([("video_id", 1)])
        
        # 快手索引
        await db.kuaishou_videos.create_index([("video_id", 1)], unique=True)
        await db.kuaishou_videos.create_index([("create_time", -1)])
        await db.kuaishou_comments.create_index([("comment_id", 1)], unique=True)
        
        # 微博索引
        await db.weibo_notes.create_index([("note_id", 1)], unique=True)
        await db.weibo_notes.create_index([("create_time", -1)])
        await db.weibo_comments.create_index([("comment_id", 1)], unique=True)
        await db.weibo_comments.create_index([("note_id", 1)])
        
        # 贴吧索引
        await db.tieba_notes.create_index([("note_id", 1)], unique=True)
        await db.tieba_notes.create_index([("publish_time", -1)])
        await db.tieba_comments.create_index([("comment_id", 1)], unique=True)
        await db.tieba_comments.create_index([("note_id", 1)])
        
        # 知乎索引
        await db.zhihu_contents.create_index([("content_id", 1)], unique=True)
        await db.zhihu_contents.create_index([("created_time", -1)])
        await db.zhihu_comments.create_index([("comment_id", 1)], unique=True)
        await db.zhihu_comments.create_index([("content_id", 1)])
        
        utils.logger.info("[MongoDB] Indexes created successfully")
        return True
        
    except Exception as e:
        utils.logger.error(f"[MongoDB] Failed to create indexes: {e}")
        return False


async def test_mongodb_connection() -> bool:
    """
    测试 MongoDB 连接
    """
    try:
        client = get_mongodb_client()
        if not client:
            return False
        
        # 尝试 ping 数据库
        await client.admin.command('ping')
        utils.logger.info("[MongoDB] Connection test successful")
        return True
    except Exception as e:
        utils.logger.error(f"[MongoDB] Connection test failed: {e}")
        return False


@asynccontextmanager
async def get_mongodb_session():
    """
    获取 MongoDB 会话（用于事务支持，可选）
    注意：事务需要副本集支持
    """
    client = get_mongodb_client()
    if not client:
        yield None
        return
    
    async with await client.start_session() as session:
        yield session





