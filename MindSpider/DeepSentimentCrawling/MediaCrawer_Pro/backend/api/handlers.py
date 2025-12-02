#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 请求处理器
"""
import tornado.web
import orjson
from loguru import logger
from typing import Optional

from core.config import settings
from services import (
    get_task_service,
    get_download_service,
    get_account_service,
    get_proxy_service,
    get_checkpoint_service,
    get_homefeed_service
)
from services.cookie_refresh_service import get_cookie_refresh_service


class BaseHandler(tornado.web.RequestHandler):
    """基础处理器"""
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    
    def options(self, *args):
        """处理 OPTIONS 请求"""
        self.set_status(204)
        self.finish()
    
    def write_json(self, data: dict, status_code: int = 200):
        """写入 JSON 响应"""
        self.set_status(status_code)
        self.write(orjson.dumps(data))
    
    def write_success(self, data=None, message: str = "success"):
        """成功响应"""
        self.write_json({
            "code": 0,
            "message": message,
            "data": data
        })
    
    def write_error_response(self, message: str, code: int = 1, status_code: int = 400):
        """错误响应"""
        self.write_json({
            "code": code,
            "message": message,
            "data": None
        }, status_code)
    
    def get_json_body(self) -> dict:
        """获取 JSON 请求体"""
        try:
            return orjson.loads(self.request.body)
        except Exception as e:
            logger.error(f"解析请求体失败: {e}")
            return {}


class HealthHandler(BaseHandler):
    """健康检查"""
    
    async def get(self):
        """GET /health"""
        self.write_success({
            "status": "healthy",
            "version": settings.APP_VERSION,
            "app_name": settings.APP_NAME
        })


class TaskHandler(BaseHandler):
    """任务管理"""
    
    async def get(self):
        """GET /api/v1/tasks - 获取任务列表"""
        try:
            page = int(self.get_argument("page", "1"))
            page_size = int(self.get_argument("page_size", "20"))
            status = self.get_argument("status", None)
            platform = self.get_argument("platform", None)
            
            task_service = get_task_service()
            result = await task_service.list_tasks(
                page=page,
                page_size=page_size,
                status=status,
                platform=platform
            )
            
            self.write_success(result)
            
        except Exception as e:
            logger.exception("获取任务列表失败")
            self.write_error_response(str(e), status_code=500)
    
    async def post(self):
        """POST /api/v1/tasks - 创建任务"""
        try:
            logger.info("📥 收到创建任务请求")
            body = self.get_json_body()
            logger.info(f"📦 请求体: {body}")
            
            # 验证必填参数
            required_fields = ["platform", "type"]
            for field in required_fields:
                if field not in body:
                    self.write_error_response(f"缺少必填参数: {field}")
                    return
            
            logger.info("🔧 正在获取 TaskService 实例...")
            task_service = get_task_service()
            logger.info("✅ TaskService 实例获取成功")
            
            logger.info("📝 正在调用 create_task 方法...")
            task = await task_service.create_task(body)
            logger.info("✅ create_task 方法执行成功")
            
            self.write_success(task, "任务创建成功")
            
        except Exception as e:
            logger.exception(f"❌ 创建任务失败，错误类型: {type(e).__name__}，错误信息: {str(e)}")
            import traceback
            logger.error(f"📍 错误堆栈:\n{traceback.format_exc()}")
            self.write_error_response(str(e), status_code=500)


class TaskDetailHandler(BaseHandler):
    """任务详情"""
    
    async def get(self, task_id: str):
        """GET /api/v1/tasks/{task_id} - 获取任务详情"""
        try:
            task_service = get_task_service()
            task = await task_service.get_task(task_id)
            
            if not task:
                self.write_error_response("任务不存在", status_code=404)
                return
            
            self.write_success(task)
            
        except Exception as e:
            logger.exception("获取任务详情失败")
            self.write_error_response(str(e), status_code=500)
    
    async def put(self, task_id: str):
        """PUT /api/v1/tasks/{task_id} - 启动任务"""
        try:
            task_service = get_task_service()
            success = await task_service.start_task(task_id)
            
            if not success:
                self.write_error_response("任务启动失败（任务不存在或状态不正确）", status_code=400)
                return
            
            self.write_success(message="任务已提交执行")
            
        except Exception as e:
            logger.exception("启动任务失败")
            self.write_error_response(str(e), status_code=500)
    
    async def delete(self, task_id: str):
        """DELETE /api/v1/tasks/{task_id} - 删除任务"""
        try:
            task_service = get_task_service()
            success = await task_service.delete_task(task_id)
            
            if not success:
                self.write_error_response("任务不存在", status_code=404)
                return
            
            self.write_success(message="任务删除成功")
            
        except Exception as e:
            logger.exception("删除任务失败")
            self.write_error_response(str(e), status_code=500)


class DownloadHandler(BaseHandler):
    """下载处理"""
    
    async def post(self):
        """POST /api/v1/download - 下载视频/图片"""
        try:
            body = self.get_json_body()
            
            url = body.get("url")
            if not url:
                self.write_error_response("缺少 URL 参数")
                return
            
            download_service = get_download_service()
            result = await download_service.download(
                url=url,
                save_path=body.get("save_path"),
                filename=body.get("filename")
            )
            
            self.write_success(result, "下载成功")
            
        except Exception as e:
            logger.exception("下载失败")
            self.write_error_response(str(e), status_code=500)


class AccountHandler(BaseHandler):
    """账号管理"""
    
    async def get(self, account_id: Optional[str] = None):
        """GET /api/v1/accounts - 获取账号列表"""
        try:
            account_service = get_account_service()
            
            if account_id:
                account = await account_service.get_account(account_id)
                if not account:
                    self.write_error_response("账号不存在", status_code=404)
                    return
                self.write_success(account)
            else:
                platform = self.get_argument("platform", None)
                status = self.get_argument("status", None)
                accounts = await account_service.list_accounts(platform, status)
                self.write_success(accounts)
            
        except Exception as e:
            logger.exception("获取账号失败")
            self.write_error_response(str(e), status_code=500)
    
    async def post(self):
        """POST /api/v1/accounts - 添加账号"""
        try:
            body = self.get_json_body()
            account_service = get_account_service()
            account = await account_service.add_account(body)
            self.write_success(account, "账号添加成功")
            
        except Exception as e:
            logger.exception("添加账号失败")
            self.write_error_response(str(e), status_code=500)
    
    async def delete(self, account_id: str):
        """DELETE /api/v1/accounts/{account_id} - 删除账号"""
        try:
            account_service = get_account_service()
            success = await account_service.delete_account(account_id)
            
            if not success:
                self.write_error_response("账号不存在", status_code=404)
                return
            
            self.write_success(message="账号删除成功")
            
        except Exception as e:
            logger.exception("删除账号失败")
            self.write_error_response(str(e), status_code=500)


class CookieRefreshHandler(BaseHandler):
    """Cookie刷新管理"""
    
    async def post(self):
        """POST /api/v1/cookies/check - 检查所有Cookie"""
        try:
            cookie_service = get_cookie_refresh_service()
            await cookie_service.check_all_cookies()
            self.write_success(message="Cookie检查完成")
        except Exception as e:
            logger.exception("Cookie检查失败")
            self.write_error_response(str(e), status_code=500)
    
    async def put(self, account_id: str):
        """PUT /api/v1/cookies/{account_id} - 手动更新Cookie"""
        try:
            body = self.get_json_body()
            new_cookie = body.get("cookie")
            
            if not new_cookie:
                self.write_error_response("Cookie不能为空", status_code=400)
                return
            
            cookie_service = get_cookie_refresh_service()
            success = await cookie_service.manual_refresh_cookie(account_id, new_cookie)
            
            if success:
                self.write_success(message="Cookie更新成功")
            else:
                self.write_error_response("Cookie更新失败", status_code=500)
        except Exception as e:
            logger.exception("更新Cookie失败")
            self.write_error_response(str(e), status_code=500)
    
    async def get(self, account_id: str):
        """GET /api/v1/cookies/{account_id}/info - 获取Cookie过期信息"""
        try:
            cookie_service = get_cookie_refresh_service()
            info = await cookie_service.get_cookie_expiry_info(account_id)
            
            if "error" in info:
                self.write_error_response(info["error"], status_code=404)
                return
            
            self.write_success(info)
        except Exception as e:
            logger.exception("获取Cookie信息失败")
            self.write_error_response(str(e), status_code=500)


class ProxyHandler(BaseHandler):
    """代理管理"""
    
    async def get(self, proxy_id: Optional[str] = None):
        """GET /api/v1/proxies - 获取代理列表"""
        try:
            proxy_service = get_proxy_service()
            
            if proxy_id:
                proxy = await proxy_service.get_proxy(proxy_id)
                if not proxy:
                    self.write_error_response("代理不存在", status_code=404)
                    return
                self.write_success(proxy)
            else:
                status = self.get_argument("status", None)
                proxies = await proxy_service.list_proxies(status)
                self.write_success(proxies)
            
        except Exception as e:
            logger.exception("获取代理失败")
            self.write_error_response(str(e), status_code=500)
    
    async def post(self):
        """POST /api/v1/proxies - 添加代理"""
        try:
            body = self.get_json_body()
            proxy_service = get_proxy_service()
            proxy = await proxy_service.add_proxy(body)
            self.write_success(proxy, "代理添加成功")
            
        except Exception as e:
            logger.exception("添加代理失败")
            self.write_error_response(str(e), status_code=500)


class CheckpointHandler(BaseHandler):
    """断点续爬"""
    
    async def get(self, task_id: Optional[str] = None):
        """GET /api/v1/checkpoints - 获取断点信息"""
        try:
            checkpoint_service = get_checkpoint_service()
            
            if task_id:
                checkpoint = await checkpoint_service.get_checkpoint(task_id)
                if not checkpoint:
                    self.write_error_response("断点不存在", status_code=404)
                    return
                self.write_success(checkpoint)
            else:
                checkpoints = await checkpoint_service.list_checkpoints()
                self.write_success(checkpoints)
            
        except Exception as e:
            logger.exception("获取断点失败")
            self.write_error_response(str(e), status_code=500)


class HomeFeedHandler(BaseHandler):
    """首页推荐流"""
    
    async def get(self):
        """GET /api/v1/homefeed - 获取首页推荐"""
        try:
            platform = self.get_argument("platform", "xhs")
            page = int(self.get_argument("page", "1"))
            
            homefeed_service = get_homefeed_service()
            result = await homefeed_service.get_homefeed(platform, page)
            
            self.write_success(result)
            
        except Exception as e:
            logger.exception("获取推荐流失败")
            self.write_error_response(str(e), status_code=500)



