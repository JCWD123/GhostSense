# -*- coding: utf-8 -*-
"""
MongoDB 配置文件
兼容统一的 DB_* 配置参数，用户只需修改 DB_DIALECT=mongodb 即可切换
"""
import os
from typing import Optional

# 🔥 优先使用统一的 DB_* 配置（与 MySQL/PostgreSQL 保持一致）
# 如果有 MONGODB_* 专用配置则优先使用专用配置
MONGODB_HOST = os.getenv("MONGODB_HOST", os.getenv("DB_HOST", "localhost"))
MONGODB_PORT = int(os.getenv("MONGODB_PORT", os.getenv("DB_PORT", "27017")))
MONGODB_USER = os.getenv("MONGODB_USER", os.getenv("DB_USER", ""))
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", os.getenv("DB_PASSWORD", ""))
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", os.getenv("DB_NAME", "bettafish"))

# MongoDB 特有配置
MONGODB_AUTH_SOURCE = os.getenv("MONGODB_AUTH_SOURCE", os.getenv("DB_NAME", "admin"))

# MongoDB 连接配置
mongodb_config = {
    "host": MONGODB_HOST,
    "port": MONGODB_PORT,
    "user": MONGODB_USER,
    "password": MONGODB_PASSWORD,
    "db_name": MONGODB_DB_NAME,
    "auth_source": MONGODB_AUTH_SOURCE,
}

def get_mongodb_uri() -> str:
    """
    构建 MongoDB 连接 URI
    兼容统一的数据库配置参数
    """
    if MONGODB_USER and MONGODB_PASSWORD:
        return (
            f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@"
            f"{MONGODB_HOST}:{MONGODB_PORT}/"
            f"{MONGODB_DB_NAME}?authSource={MONGODB_AUTH_SOURCE}"
        )
    else:
        return f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB_NAME}"

