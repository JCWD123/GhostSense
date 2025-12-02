#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断点续爬服务
"""
from typing import Optional, Dict, List
from datetime import datetime
from loguru import logger

from core.database import get_db
from core.config import settings


class CheckpointService:
    """断点续爬服务"""
    
    def __init__(self):
        self._db = None
        self._collection = None
        self.enabled = settings.CHECKPOINT_ENABLED
        self.save_interval = settings.CHECKPOINT_SAVE_INTERVAL
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.checkpoints
        return self._collection
    
    async def save_checkpoint(
        self,
        task_id: str,
        checkpoint_data: Dict
    ) -> bool:
        """
        保存断点
        
        Args:
            task_id: 任务 ID
            checkpoint_data: 断点数据
                {
                    "current_page": 1,
                    "current_cursor": "xxx",
                    "crawled_count": 100,
                    "last_item_id": "xxx",
                    "extra": {}
                }
        
        Returns:
            是否成功
        """
        if not self.enabled:
            return False
        
        try:
            checkpoint = {
                "task_id": task_id,
                "checkpoint_data": checkpoint_data,
                "checkpoint_time": datetime.now(),
                "status": "active"
            }
            
            await self.collection.update_one(
                {"task_id": task_id},
                {"$set": checkpoint},
                upsert=True
            )
            
            logger.debug(f"✅ 保存断点成功: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存断点失败: {e}")
            return False
    
    async def get_checkpoint(self, task_id: str) -> Optional[Dict]:
        """
        获取断点
        
        Args:
            task_id: 任务 ID
        
        Returns:
            断点数据
        """
        try:
            checkpoint = await self.collection.find_one(
                {"task_id": task_id, "status": "active"}
            )
            
            if checkpoint:
                logger.info(f"✅ 找到断点: {task_id}")
                logger.info(f"   当前关键词索引: {checkpoint.get('current_keyword_index', 0)}")
                logger.info(f"   当前页码: {checkpoint.get('current_page', 1)}")
                logger.info(f"   已爬取笔记数: {checkpoint.get('total_crawled', 0)}")
                return checkpoint
            else:
                logger.info(f"💡 未找到断点: {task_id}")
                logger.info(f"   说明: 这是任务首次执行，将从头开始爬取")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取断点失败: {e}")
            return None
    
    async def delete_checkpoint(self, task_id: str) -> bool:
        """
        删除断点
        
        Args:
            task_id: 任务 ID
        
        Returns:
            是否成功
        """
        try:
            result = await self.collection.update_one(
                {"task_id": task_id},
                {"$set": {"status": "deleted", "deleted_at": datetime.now()}}
            )
            
            logger.info(f"✅ 删除断点成功: {task_id}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ 删除断点失败: {e}")
            return False
    
    async def list_checkpoints(
        self,
        status: str = "active",
        limit: int = 100
    ) -> List[Dict]:
        """
        获取断点列表
        
        Args:
            status: 状态（active, deleted）
            limit: 数量限制
        
        Returns:
            断点列表
        """
        try:
            query = {"status": status} if status else {}
            
            cursor = self.collection.find(query).sort("checkpoint_time", -1).limit(limit)
            checkpoints = await cursor.to_list(length=limit)
            
            # 转换 ObjectId
            for checkpoint in checkpoints:
                checkpoint["_id"] = str(checkpoint["_id"])
            
            logger.info(f"✅ 获取到 {len(checkpoints)} 个断点")
            return checkpoints
            
        except Exception as e:
            logger.error(f"❌ 获取断点列表失败: {e}")
            return []
    
    async def resume_task(self, task_id: str) -> Optional[Dict]:
        """
        恢复任务（从断点继续）
        
        Args:
            task_id: 任务 ID
        
        Returns:
            断点数据
        """
        checkpoint = await self.get_checkpoint(task_id)
        
        if checkpoint:
            logger.success(f"🔄 恢复任务: {task_id}")
            logger.info(f"   爬取进度: {checkpoint['checkpoint_data'].get('crawled_count', 0)} 条")
            logger.info(f"   当前页码: {checkpoint['checkpoint_data'].get('current_page', 1)}")
            return checkpoint['checkpoint_data']
        else:
            logger.info(f"⚠️ 无断点，从头开始: {task_id}")
            return None
    
    async def should_save(self, crawled_count: int) -> bool:
        """
        判断是否应该保存断点
        
        Args:
            crawled_count: 已爬取数量
        
        Returns:
            是否应该保存
        """
        return crawled_count > 0 and crawled_count % self.save_interval == 0




