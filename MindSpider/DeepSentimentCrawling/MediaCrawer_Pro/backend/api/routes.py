#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 路由配置
"""
import tornado.web
from .handlers import (
    HealthHandler,
    TaskHandler,
    TaskDetailHandler,
    DownloadHandler,
    AccountHandler,
    ProxyHandler,
    CheckpointHandler,
    HomeFeedHandler,
    CookieRefreshHandler,
)
from .docs_handler import DocsHandler


def make_app() -> tornado.web.Application:
    """创建 Tornado 应用"""
    return tornado.web.Application(
        [
            # 健康检查
            (r"/health", HealthHandler),
            (r"/", HealthHandler),
            
            # API 文档
            (r"/docs", DocsHandler),
            
            # 任务管理
            (r"/api/v1/tasks", TaskHandler),
            (r"/api/v1/tasks/([^/]+)", TaskDetailHandler),
            
            # 下载
            (r"/api/v1/download", DownloadHandler),
            
            # 账号管理
            (r"/api/v1/accounts", AccountHandler),
            (r"/api/v1/accounts/([^/]+)", AccountHandler),
            
            # Cookie刷新
            (r"/api/v1/cookies/check", CookieRefreshHandler),
            (r"/api/v1/cookies/([^/]+)", CookieRefreshHandler),
            (r"/api/v1/cookies/([^/]+)/info", CookieRefreshHandler),
            
            # 代理管理
            (r"/api/v1/proxies", ProxyHandler),
            (r"/api/v1/proxies/([^/]+)", ProxyHandler),
            
            # 断点续爬
            (r"/api/v1/checkpoints", CheckpointHandler),
            (r"/api/v1/checkpoints/([^/]+)", CheckpointHandler),
            
            # HomeFeed 推荐流
            (r"/api/v1/homefeed", HomeFeedHandler),
        ],
        debug=False,
        autoreload=False,
    )




