#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaCrawer Pro - 后端服务入口
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

import tornado.web
from tornado.platform.asyncio import AsyncIOMainLoop
from loguru import logger

from api.routes import make_app
from core.config import settings
from core.database import init_database
from core.cache import init_cache


async def startup():
    """服务启动初始化"""
    logger.info("🚀 MediaCrawer Pro 正在启动...")
    
    # 初始化数据库
    logger.info("📦 正在连接数据库...")
    await init_database()
    
    # 初始化缓存
    logger.info("🗄️  正在连接 Redis...")
    await init_cache()
    
    # 启动Cookie监控服务
    logger.info("🍪 正在启动Cookie监控服务...")
    from services.cookie_refresh_service import get_cookie_refresh_service
    cookie_service = get_cookie_refresh_service()
    # 在后台启动监控（不阻塞）
    asyncio.create_task(cookie_service.start_monitoring())
    
    logger.info("✅ 所有服务初始化完成！")


async def shutdown():
    """服务关闭清理"""
    logger.info("👋 MediaCrawer Pro 正在关闭...")
    from core.database import close_database
    from core.cache import close_cache
    from services.cookie_refresh_service import get_cookie_refresh_service
    
    # 停止Cookie监控服务
    cookie_service = get_cookie_refresh_service()
    await cookie_service.stop_monitoring()
    
    await close_database()
    await close_cache()
    
    logger.info("✅ 服务已安全关闭")


def main():
    """主函数"""
    # 安装 AsyncIO 事件循环，确保 Tornado 与 asyncio 共用同一个 Loop
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    
    # 创建 Tornado 应用
    app = make_app()
    
    # 启动前初始化（运行在同一个事件循环中，避免 loop 被提前关闭）
    loop.run_until_complete(startup())
    
    # 启动服务器
    port = settings.API_PORT
    app.listen(port)
    logger.success(f"🌐 服务器启动成功！监听端口: {port}")
    logger.info(f"📖 API 文档: http://localhost:{port}/docs")
    logger.info(f"🎯 健康检查: http://localhost:{port}/health")
    
    try:
        # 启动事件循环
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("接收到中断信号...")
    finally:
        # 清理资源
        loop.run_until_complete(shutdown())
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()


if __name__ == "__main__":
    main()



