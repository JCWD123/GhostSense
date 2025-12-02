#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理服务
"""
from typing import Optional, Dict, List
from datetime import datetime
import uuid
import asyncio
from loguru import logger
import tornado.ioloop

from core.database import get_db
from core.config import settings
from crawler.xhs_client import XHSClient
from .checkpoint_service import CheckpointService
from .account_service import AccountService
from .proxy_service import ProxyService


class TaskService:
    """任务管理服务"""
    
    def __init__(self):
        # 延迟初始化，避免事件循环问题
        self._db = None
        self._collection = None
        self._checkpoint_service = None
        self._account_service = None
        self._proxy_service = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.db.tasks
        return self._collection
    
    @property
    def checkpoint_service(self):
        if self._checkpoint_service is None:
            self._checkpoint_service = CheckpointService()
        return self._checkpoint_service
    
    @property
    def account_service(self):
        if self._account_service is None:
            self._account_service = AccountService()
        return self._account_service
    
    @property
    def proxy_service(self):
        if self._proxy_service is None:
            self._proxy_service = ProxyService()
        return self._proxy_service
    
    async def create_task(self, task_data: Dict) -> Dict:
        """
        创建任务
        
        Args:
            task_data: 任务数据
                {
                    "platform": "xhs",
                    "type": "search",  # search, user, note, homefeed
                    "keywords": ["Python", "编程"],
                    "max_count": 100,
                    "enable_comment": true,
                    "enable_download": false
                }
        
        Returns:
            任务信息
        """
        try:
            task_id = str(uuid.uuid4())
            
            task = {
                "task_id": task_id,
                **task_data,
                "status": "pending",  # pending, running, completed, failed, cancelled
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "started_at": None,
                "completed_at": None,
                "progress": {
                    "total": task_data.get("max_count", 0),
                    "crawled": 0,
                    "success": 0,
                    "failed": 0
                },
                "error": None
            }
            
            await self.collection.insert_one(task)
            
            # 转换 ObjectId 为字符串
            task["_id"] = str(task["_id"])
            
            # 不自动执行任务，避免 Event Loop 问题
            # 任务将保持 pending 状态，需要通过其他方式启动
            # TODO: 实现任务调度器或通过单独的接口启动任务
            
            logger.success(f"✅ 任务创建成功: {task_id}")
            logger.info(f"💡 任务已创建，状态为 pending，等待执行")
            return task
            
        except Exception as e:
            logger.error(f"❌ 创建任务失败: {e}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务详情"""
        try:
            task = await self.collection.find_one({"task_id": task_id})
            if task:
                task["_id"] = str(task["_id"])
            return task
        except Exception as e:
            logger.error(f"❌ 获取任务失败: {e}")
            return None
    
    async def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        platform: Optional[str] = None
    ) -> Dict:
        """
        获取任务列表
        
        Returns:
            {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 20
            }
        """
        try:
            query = {}
            if status:
                query["status"] = status
            if platform:
                query["platform"] = platform
            
            # 总数
            total = await self.collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * page_size
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            tasks = await cursor.to_list(length=page_size)
            
            for task in tasks:
                task["_id"] = str(task["_id"])
            
            return {
                "items": tasks,
                "total": total,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"❌ 获取任务列表失败: {e}")
            return {"items": [], "total": 0, "page": page, "page_size": page_size}
    
    async def start_task(self, task_id: str) -> bool:
        """
        启动任务执行
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功启动
        """
        try:
            task = await self.get_task(task_id)
            if not task:
                logger.error(f"❌ 任务不存在: {task_id}")
                return False
            
            if task["status"] != "pending":
                logger.warning(f"⚠️  任务状态不是 pending，无法启动: {task_id}, 当前状态: {task['status']}")
                return False
            
            # 使用 tornado 的方式启动后台任务
            tornado.ioloop.IOLoop.current().add_callback(self._execute_task_wrapper, task)
            logger.info(f"🚀 任务已提交执行: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 启动任务失败: {e}")
            return False
    
    async def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            result = await self.collection.delete_one({"task_id": task_id})
            if result.deleted_count > 0:
                # 同时删除断点
                await self.checkpoint_service.delete_checkpoint(task_id)
                logger.info(f"✅ 删除任务成功: {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 删除任务失败: {e}")
            return False
    
    def _execute_task_wrapper(self, task: Dict):
        """
        任务执行包装器（同步方法）
        用于 Tornado IOLoop.add_callback
        """
        asyncio.ensure_future(self._execute_task(task))
    
    async def _execute_task(self, task: Dict):
        """执行任务（异步）"""
        task_id = task["task_id"]
        platform = task["platform"]
        task_type = task["type"]
        
        try:
            # 更新状态为运行中
            await self._update_task_status(task_id, "running", started_at=datetime.now())
            
            logger.info(f"🚀 开始执行任务: {task_id}")
            
            # 根据平台选择客户端
            if platform == "xhs":
                await self._execute_xhs_task(task)
            elif platform == "douyin":
                # TODO: 实现抖音爬取
                pass
            elif platform == "kuaishou":
                # TODO: 实现快手爬取
                pass
            else:
                raise ValueError(f"不支持的平台: {platform}")
            
            # 更新状态为完成
            await self._update_task_status(
                task_id,
                "completed",
                completed_at=datetime.now()
            )
            
            logger.success(f"✅ 任务完成: {task_id}")
            
        except Exception as e:
            logger.exception(f"❌ 任务执行失败: {task_id}")
            await self._update_task_status(
                task_id,
                "failed",
                error=str(e),
                completed_at=datetime.now()
            )
    
    async def _execute_xhs_task(self, task: Dict):
        """执行小红书任务"""
        task_id = task["task_id"]
        task_type = task["type"]
        max_count = task.get("max_count", 100)
        
        logger.info(f"📋 任务详情:")
        logger.info(f"   任务ID: {task_id}")
        logger.info(f"   任务类型: {task_type}")
        logger.info(f"   目标数量: {max_count}")
        logger.info(f"   关键词: {task.get('keywords', [])}")
        logger.info(f"   是否爬评论: {task.get('enable_comment', False)}")
        logger.info(f"   是否下载: {task.get('enable_download', False)}")
        
        # 获取账号
        logger.info(f"🔍 正在获取可用账号...")
        account = await self.account_service.get_available_account("xhs")
        if not account:
            logger.error(f"❌ 没有可用的小红书账号")
            raise ValueError("没有可用的小红书账号")
        logger.info(f"✅ 使用账号: {account.get('username', account.get('_id'))}")
        
        # 获取代理
        logger.info(f"🔍 正在获取代理...")
        proxy = await self.proxy_service.get_available_proxy()
        if proxy:
            logger.info(f"✅ 使用代理: {proxy.get('host')}:{proxy.get('port')}")
        else:
            logger.info(f"💡 不使用代理，直连")
        
        # 创建客户端
        async with XHSClient() as client:
            # 设置 cookie
            cookie_str = self.account_service.build_cookie_string(account) if account else ""
            if cookie_str:
                client.set_cookie(cookie_str)
            else:
                logger.warning("⚠️ 未获取到账号 Cookie，将以未登录状态访问")
            
            # 设置 User-Agent（从账号配置读取，保证签名 UA = 请求 UA）
            if account and account.get("user_agent"):
                client.set_user_agent(account["user_agent"])
                logger.info(f"✅ 使用账号真实 UA: {account['user_agent'][:50]}...")
            else:
                logger.warning(f"⚠️ 账号未提供 user_agent，使用默认 UA")
            
            # 设置代理
            if proxy:
                client.set_proxy(proxy)
            
            # 尝试从断点恢复
            checkpoint_data = await self.checkpoint_service.get_checkpoint(task_id)
            start_page = 1
            crawled_count = 0
            
            if checkpoint_data:
                start_page = checkpoint_data.get("current_page", 1)
                crawled_count = checkpoint_data.get("crawled_count", 0)
                logger.info(f"🔄 从断点恢复: 第 {start_page} 页, 已爬取 {crawled_count} 条")
            
            # 根据类型执行不同的爬取逻辑
            if task_type == "search":
                await self._execute_xhs_search(
                    client,
                    task,
                    start_page,
                    crawled_count
                )
            elif task_type == "homefeed":
                await self._execute_xhs_homefeed(
                    client,
                    task,
                    checkpoint_data
                )
            else:
                raise ValueError(f"不支持的任务类型: {task_type}")
    
    async def _execute_xhs_search(
        self,
        client: XHSClient,
        task: Dict,
        start_page: int,
        crawled_count: int
    ):
        """执行小红书搜索任务"""
        task_id = task["task_id"]
        keywords = task.get("keywords", [])
        max_count = task.get("max_count", 100)
        enable_comment = task.get("enable_comment", False)
        
        for keyword in keywords:
            page = start_page
            keyword_count = 0
            
            while keyword_count < max_count:
                try:
                    # 搜索笔记
                    notes = await client.search_notes(
                        keyword=keyword,
                        page=page,
                        page_size=20
                    )
                    
                    if not notes:
                        logger.info(f"⚠️ 关键词 '{keyword}' 已无更多数据")
                        break
                    
                    # 保存笔记
                    for note in notes:
                        # 保存到数据库
                        await self.db.notes.update_one(
                            {"note_id": note["note_id"]},
                            {"$set": {
                                **note,
                                "source_keyword": keyword,
                                "task_id": task_id,
                                "crawled_at": datetime.now()
                            }},
                            upsert=True
                        )
                        
                        # 获取评论
                        if enable_comment:
                            await self._crawl_comments(client, note["note_id"], task_id)
                        
                        keyword_count += 1
                        crawled_count += 1
                        
                        # 更新进度
                        await self._update_task_progress(
                            task_id,
                            total=max_count * len(keywords),
                            crawled=crawled_count
                        )
                        
                        # 保存断点
                        if await self.checkpoint_service.should_save(crawled_count):
                            await self.checkpoint_service.save_checkpoint(
                                task_id,
                                {
                                    "current_page": page,
                                    "current_keyword": keyword,
                                    "crawled_count": crawled_count,
                                    "keyword_count": keyword_count
                                }
                            )
                        
                        if keyword_count >= max_count:
                            break
                    
                    page += 1
                    
                    # 延时避免封禁
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ 爬取失败: {keyword} 第{page}页 - {e}")
                    await asyncio.sleep(5)
                    continue
    
    async def _execute_xhs_homefeed(
        self,
        client: XHSClient,
        task: Dict,
        checkpoint_data: Optional[Dict]
    ):
        """执行小红书首页推荐流任务"""
        task_id = task["task_id"]
        max_count = task.get("max_count", 100)
        
        cursor = ""
        if checkpoint_data:
            cursor = checkpoint_data.get("current_cursor", "")
        
        crawled_count = 0
        
        while crawled_count < max_count:
            try:
                result = await client.get_homefeed(cursor=cursor)
                notes = result.get("notes", [])
                cursor = result.get("cursor", "")
                
                if not notes:
                    logger.info("⚠️ 推荐流已无更多数据")
                    break
                
                for note in notes:
                    await self.db.notes.update_one(
                        {"note_id": note["note_id"]},
                        {"$set": {
                            **note,
                            "source": "homefeed",
                            "task_id": task_id,
                            "crawled_at": datetime.now()
                        }},
                        upsert=True
                    )
                    
                    crawled_count += 1
                    
                    await self._update_task_progress(
                        task_id,
                        total=max_count,
                        crawled=crawled_count
                    )
                    
                    if await self.checkpoint_service.should_save(crawled_count):
                        await self.checkpoint_service.save_checkpoint(
                            task_id,
                            {
                                "current_cursor": cursor,
                                "crawled_count": crawled_count
                            }
                        )
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ 爬取推荐流失败: {e}")
                await asyncio.sleep(5)
                continue
    
    async def _crawl_comments(self, client: XHSClient, note_id: str, task_id: str):
        """爬取评论（自动获取 xsec_token）"""
        try:
            # 1. 尝试从数据库获取已保存的 xsec_token
            note = await self.db.notes.find_one({"note_id": note_id})
            xsec_token = note.get("xsec_token", "") if note else ""
            xsec_source = note.get("xsec_source", "pc_search") if note else "pc_search"
            
            # 2. 如果数据库中没有 token，则调用详情接口获取
            if not xsec_token:
                logger.info(f"🔑 笔记 {note_id} 缺少 xsec_token，正在从详情页获取...")
                detail = await client.get_note_detail_for_token(note_id)
                if detail:
                    xsec_token = detail.get("xsec_token", "")
                    xsec_source = detail.get("xsec_source", "pc_search")
                    
                    # 更新数据库，缓存 token
                    if xsec_token:
                        await self.db.notes.update_one(
                            {"note_id": note_id},
                            {"$set": {
                                "xsec_token": xsec_token,
                                "xsec_source": xsec_source,
                                "updated_at": datetime.now()
                            }},
                            upsert=True
                        )
                        logger.info(f"✅ 成功获取并缓存 xsec_token: {note_id}")
                else:
                    logger.warning(f"⚠️ 无法获取笔记详情: {note_id}，跳过评论抓取")
                    return
            
            # 3. 如果仍然没有 token，跳过评论抓取
            if not xsec_token:
                logger.warning(f"⚠️ 笔记 {note_id} 无法获取 xsec_token，跳过评论抓取")
                return
            
            # 4. 模拟真实用户行为：延迟 + Referer 链
            # 参考老项目 media_platform/xhs/core.py 的做法：detail → sleep → comments
            detail_url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source={xsec_source}"
            logger.info(f"🔗 准备评论抓取，referer: {detail_url[:60]}...")
            
            # 延迟，模拟用户从详情页阅读到评论区的时间
            import asyncio
            sleep_time = settings.COMMENT_REQUEST_INTERVAL if hasattr(settings, 'COMMENT_REQUEST_INTERVAL') else settings.REQUEST_INTERVAL
            logger.debug(f"⏰ 模拟用户阅读详情页，等待 {sleep_time}s...")
            await asyncio.sleep(sleep_time)
            
            # 5. 使用 token 获取评论（带正确的 referer）
            logger.debug(f"💬 正在获取评论: {note_id} (token: {xsec_token[:20]}...)")
            result = await client.get_note_comments(
                note_id=note_id,
                xsec_token=xsec_token,
                xsec_source=xsec_source,
                referer=detail_url  # 传递详情页作为 referer
            )
            comments = result.get("comments", [])
            
            # 5. 保存评论到数据库
            for comment in comments:
                await self.db.comments.update_one(
                    {"comment_id": comment["comment_id"]},
                    {"$set": {
                        **comment,
                        "note_id": note_id,
                        "task_id": task_id,
                        "crawled_at": datetime.now()
                    }},
                    upsert=True
                )
            
            logger.success(f"✅ 成功爬取评论: {note_id} ({len(comments)} 条)")
            
        except Exception as e:
            logger.error(f"❌ 爬取评论失败: {note_id} - {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    async def _update_task_status(
        self,
        task_id: str,
        status: str,
        **kwargs
    ):
        """更新任务状态"""
        update_data = {
            "status": status,
            "updated_at": datetime.now(),
            **kwargs
        }
        
        await self.collection.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )
    
    async def _update_task_progress(
        self,
        task_id: str,
        total: int,
        crawled: int
    ):
        """更新任务进度"""
        await self.collection.update_one(
            {"task_id": task_id},
            {"$set": {
                "progress.total": total,
                "progress.crawled": crawled,
                "updated_at": datetime.now()
            }}
        )



