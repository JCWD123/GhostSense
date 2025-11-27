# -*- coding: utf-8 -*-
"""
小红书 MongoDB 存储实现
"""
from typing import Dict, List
from datetime import datetime

from base.base_crawler import AbstractStore
from database.mongodb_session import get_mongodb_database
from tools import utils
from tools.time_util import get_current_timestamp


class XhsMongoDBStoreImplement(AbstractStore):
    """小红书 MongoDB 存储实现"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = get_mongodb_database()
        if not self.db:
            raise RuntimeError("MongoDB connection failed. Please install motor: pip install motor")
        
        # 集合名称
        self.notes_collection = self.db["xhs_notes"]
        self.comments_collection = self.db["xhs_comments"]
        self.creators_collection = self.db["xhs_creators"]
    
    async def store_content(self, content_item: Dict):
        """
        存储小红书笔记到 MongoDB
        Args:
            content_item: 笔记数据字典
        """
        note_id = content_item.get("note_id")
        if not note_id:
            utils.logger.warning("[XhsMongoDBStore.store_content] note_id is empty")
            return
        
        try:
            # 准备存储数据
            mongo_doc = self._prepare_note_document(content_item)
            
            # 使用 upsert 更新或插入
            result = await self.notes_collection.update_one(
                {"note_id": note_id},
                {"$set": mongo_doc},
                upsert=True
            )
            
            if result.upserted_id:
                utils.logger.info(f"[XhsMongoDBStore] Inserted new note: {note_id}")
            else:
                utils.logger.info(f"[XhsMongoDBStore] Updated note: {note_id}")
                
        except Exception as e:
            utils.logger.error(f"[XhsMongoDBStore.store_content] Error: {e}, note_id: {note_id}")
    
    async def store_comment(self, comment_item: Dict):
        """
        存储小红书评论到 MongoDB
        Args:
            comment_item: 评论数据字典
        """
        comment_id = comment_item.get("comment_id")
        if not comment_id:
            utils.logger.warning("[XhsMongoDBStore.store_comment] comment_id is empty")
            return
        
        try:
            # 准备存储数据
            mongo_doc = self._prepare_comment_document(comment_item)
            
            # 使用 upsert 更新或插入
            result = await self.comments_collection.update_one(
                {"comment_id": comment_id},
                {"$set": mongo_doc},
                upsert=True
            )
            
            if result.upserted_id:
                utils.logger.info(f"[XhsMongoDBStore] Inserted new comment: {comment_id}")
            else:
                utils.logger.info(f"[XhsMongoDBStore] Updated comment: {comment_id}")
                
        except Exception as e:
            utils.logger.error(f"[XhsMongoDBStore.store_comment] Error: {e}, comment_id: {comment_id}")
    
    async def store_creator(self, creator_item: Dict):
        """
        存储小红书创作者到 MongoDB
        Args:
            creator_item: 创作者数据字典
        """
        user_id = creator_item.get("user_id")
        if not user_id:
            utils.logger.warning("[XhsMongoDBStore.store_creator] user_id is empty")
            return
        
        try:
            # 准备存储数据
            mongo_doc = self._prepare_creator_document(creator_item)
            
            # 使用 upsert 更新或插入
            result = await self.creators_collection.update_one(
                {"user_id": user_id},
                {"$set": mongo_doc},
                upsert=True
            )
            
            if result.upserted_id:
                utils.logger.info(f"[XhsMongoDBStore] Inserted new creator: {user_id}")
            else:
                utils.logger.info(f"[XhsMongoDBStore] Updated creator: {user_id}")
                
        except Exception as e:
            utils.logger.error(f"[XhsMongoDBStore.store_creator] Error: {e}, user_id: {user_id}")
    
    def _prepare_note_document(self, content_item: Dict) -> Dict:
        """
        准备笔记文档（MongoDB 格式）
        """
        current_ts = int(get_current_timestamp())
        
        # 将字符串格式的图片列表和标签列表转换为数组
        image_list = content_item.get("image_list", "")
        if isinstance(image_list, str):
            images = [img.strip() for img in image_list.split(",") if img.strip()]
        else:
            images = image_list if image_list else []
        
        tag_list = content_item.get("tag_list", "")
        if isinstance(tag_list, str):
            tags = [tag.strip() for tag in tag_list.split(",") if tag.strip()]
        else:
            tags = tag_list if tag_list else []
        
        # 构建 MongoDB 文档
        doc = {
            "note_id": content_item.get("note_id"),
            "type": content_item.get("type"),
            "title": content_item.get("title"),
            "desc": content_item.get("desc"),
            "video_url": content_item.get("video_url"),
            "note_url": content_item.get("note_url"),
            "source_keyword": content_item.get("source_keyword", ""),
            "xsec_token": content_item.get("xsec_token"),
            
            # 用户信息（嵌套文档）
            "user": {
                "user_id": content_item.get("user_id"),
                "nickname": content_item.get("nickname"),
                "avatar": content_item.get("avatar"),
            },
            
            # 互动数据（嵌套文档）
            "interact": {
                "liked_count": int(content_item.get("liked_count", 0)) if content_item.get("liked_count") else 0,
                "collected_count": int(content_item.get("collected_count", 0)) if content_item.get("collected_count") else 0,
                "comment_count": int(content_item.get("comment_count", 0)) if content_item.get("comment_count") else 0,
                "share_count": int(content_item.get("share_count", 0)) if content_item.get("share_count") else 0,
            },
            
            # 内容数据（数组）
            "images": images,
            "tags": tags,
            
            # 位置信息
            "ip_location": content_item.get("ip_location"),
            
            # 时间戳
            "time": content_item.get("time"),  # 发布时间
            "last_update_time": content_item.get("last_update_time"),
            "add_ts": content_item.get("add_ts", current_ts),
            "last_modify_ts": current_ts,
            
            # MongoDB 特有字段
            "created_at": datetime.fromtimestamp(content_item.get("time", current_ts) / 1000) if content_item.get("time") else datetime.now(),
            "updated_at": datetime.now(),
        }
        
        return doc
    
    def _prepare_comment_document(self, comment_item: Dict) -> Dict:
        """
        准备评论文档（MongoDB 格式）
        """
        current_ts = int(get_current_timestamp())
        
        # 处理评论图片
        pictures = comment_item.get("pictures", "")
        if isinstance(pictures, str):
            picture_list = [pic.strip() for pic in pictures.split(",") if pic.strip()]
        else:
            picture_list = pictures if pictures else []
        
        # 构建 MongoDB 文档
        doc = {
            "comment_id": comment_item.get("comment_id"),
            "note_id": comment_item.get("note_id"),
            "content": comment_item.get("content"),
            "pictures": picture_list,
            
            # 用户信息（嵌套文档）
            "user": {
                "user_id": comment_item.get("user_id"),
                "nickname": comment_item.get("nickname"),
                "avatar": comment_item.get("avatar"),
            },
            
            # 互动数据
            "sub_comment_count": int(comment_item.get("sub_comment_count", 0)),
            "like_count": int(comment_item.get("like_count", 0)) if comment_item.get("like_count") else 0,
            
            # 父评论ID（用于二级评论）
            "parent_comment_id": comment_item.get("parent_comment_id"),
            
            # 位置信息
            "ip_location": comment_item.get("ip_location"),
            
            # 时间戳
            "create_time": comment_item.get("create_time"),
            "add_ts": comment_item.get("add_ts", current_ts),
            "last_modify_ts": current_ts,
            
            # MongoDB 特有字段
            "created_at": datetime.fromtimestamp(comment_item.get("create_time", current_ts) / 1000) if comment_item.get("create_time") else datetime.now(),
            "updated_at": datetime.now(),
        }
        
        return doc
    
    def _prepare_creator_document(self, creator_item: Dict) -> Dict:
        """
        准备创作者文档（MongoDB 格式）
        """
        current_ts = int(get_current_timestamp())
        
        # 处理标签列表
        tag_list = creator_item.get("tag_list", {})
        if isinstance(tag_list, str):
            import json
            try:
                tags = json.loads(tag_list)
            except:
                tags = {}
        else:
            tags = tag_list if tag_list else {}
        
        # 构建 MongoDB 文档
        doc = {
            "user_id": creator_item.get("user_id"),
            "nickname": creator_item.get("nickname"),
            "avatar": creator_item.get("avatar"),
            "desc": creator_item.get("desc"),
            "gender": creator_item.get("gender"),
            "ip_location": creator_item.get("ip_location"),
            
            # 粉丝数据
            "follows": int(creator_item.get("follows", 0)) if creator_item.get("follows") else 0,
            "fans": int(creator_item.get("fans", 0)) if creator_item.get("fans") else 0,
            "interaction": int(creator_item.get("interaction", 0)) if creator_item.get("interaction") else 0,
            
            # 标签（嵌套文档）
            "tags": tags,
            
            # 时间戳
            "add_ts": creator_item.get("add_ts", current_ts),
            "last_modify_ts": current_ts,
            
            # MongoDB 特有字段
            "created_at": datetime.fromtimestamp(current_ts / 1000),
            "updated_at": datetime.now(),
        }
        
        return doc




