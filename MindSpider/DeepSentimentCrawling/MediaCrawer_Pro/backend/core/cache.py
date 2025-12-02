#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis 缓存管理
"""
from typing import Optional, Any
import redis.asyncio as aioredis
from loguru import logger
import orjson

from .config import settings


class RedisCache:
    """Redis 缓存管理器"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """连接 Redis"""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True
            )
            
            # 测试连接
            await self.redis.ping()
            
            logger.success(f"✅ Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"❌ Redis 连接失败: {e}")
            raise
    
    async def close(self):
        """关闭 Redis 连接"""
        if self.redis:
            await self.redis.close()
            logger.info("👋 Redis 连接已关闭")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = await self.redis.get(key)
            if value:
                return orjson.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET 错误: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """设置缓存"""
        try:
            json_value = orjson.dumps(value)
            await self.redis.setex(key, expire, json_value)
            return True
        except Exception as e:
            logger.error(f"Redis SET 错误: {e}")
            return False
    
    async def delete(self, key: str):
        """删除缓存"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE 错误: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 错误: {e}")
            return False
    
    async def expire(self, key: str, seconds: int):
        """设置过期时间"""
        try:
            await self.redis.expire(key, seconds)
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE 错误: {e}")
            return False
    
    async def incr(self, key: str) -> int:
        """自增"""
        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR 错误: {e}")
            return 0
    
    async def decr(self, key: str) -> int:
        """自减"""
        try:
            return await self.redis.decr(key)
        except Exception as e:
            logger.error(f"Redis DECR 错误: {e}")
            return 0
    
    async def lpush(self, key: str, *values):
        """列表左推"""
        try:
            serialized = [orjson.dumps(v) for v in values]
            return await self.redis.lpush(key, *serialized)
        except Exception as e:
            logger.error(f"Redis LPUSH 错误: {e}")
            return 0
    
    async def rpop(self, key: str) -> Optional[Any]:
        """列表右弹"""
        try:
            value = await self.redis.rpop(key)
            if value:
                return orjson.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis RPOP 错误: {e}")
            return None
    
    async def llen(self, key: str) -> int:
        """列表长度"""
        try:
            return await self.redis.llen(key)
        except Exception as e:
            logger.error(f"Redis LLEN 错误: {e}")
            return 0


# 全局缓存实例
redis_cache = RedisCache()


async def init_cache():
    """初始化缓存"""
    await redis_cache.connect()


async def close_cache():
    """关闭缓存"""
    await redis_cache.close()


def get_cache() -> RedisCache:
    """获取缓存实例"""
    if redis_cache.redis is None:
        raise RuntimeError("Redis 未连接")
    return redis_cache




