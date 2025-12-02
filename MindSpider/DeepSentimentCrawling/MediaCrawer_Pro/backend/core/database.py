#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger

from .config import settings


class MongoDB:
    """MongoDB 连接管理器"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """连接数据库"""
        try:
            import asyncio
            # 获取当前事件循环
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=10000,
                io_loop=loop  # 显式指定事件循环
            )
            
            # 测试连接
            await self.client.admin.command('ping')
            
            self.db = self.client[settings.DATABASE_NAME]
            
            logger.success(f"✅ MongoDB 连接成功: {settings.DATABASE_NAME}")
            
            # 创建索引
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ MongoDB 连接失败: {e}")
            raise
    
    async def _create_indexes(self):
        """创建数据库索引"""
        try:
            # 笔记集合索引
            await self.db.notes.create_index("note_id", unique=True)
            await self.db.notes.create_index("platform")
            await self.db.notes.create_index("user_id")
            await self.db.notes.create_index([("create_time", -1)])
            
            # 评论集合索引
            await self.db.comments.create_index("comment_id", unique=True)
            await self.db.comments.create_index("note_id")
            await self.db.comments.create_index("platform")
            
            # 任务集合索引
            await self.db.tasks.create_index("task_id", unique=True)
            await self.db.tasks.create_index("status")
            await self.db.tasks.create_index([("created_at", -1)])
            
            # 账号池索引
            await self.db.accounts.create_index([("platform", 1), ("status", 1)])
            
            # 代理池索引
            await self.db.proxies.create_index([("status", 1), ("success_rate", -1)])
            
            # 断点续爬索引
            await self.db.checkpoints.create_index([("task_id", 1), ("checkpoint_time", -1)])
            
            logger.info("✅ 数据库索引创建完成")
            
        except Exception as e:
            logger.warning(f"⚠️ 创建索引时出现警告: {e}")
    
    async def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("👋 MongoDB 连接已关闭")
    
    def get_collection(self, name: str):
        """获取集合"""
        if self.db is None:
            raise RuntimeError("数据库未连接")
        return self.db[name]


# 全局数据库实例
mongo_db = MongoDB()


async def init_database():
    """初始化数据库"""
    await mongo_db.connect()


async def close_database():
    """关闭数据库"""
    await mongo_db.close()


def get_db() -> AsyncIOMotorDatabase:
    """获取数据库实例"""
    if mongo_db.db is None:
        raise RuntimeError("数据库未连接")
    return mongo_db.db



