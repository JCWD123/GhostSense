#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务模块 - 全局单例
"""
from typing import Optional

# 全局服务实例（延迟初始化）
_task_service: Optional['TaskService'] = None
_account_service: Optional['AccountService'] = None
_proxy_service: Optional['ProxyService'] = None
_checkpoint_service: Optional['CheckpointService'] = None
_download_service: Optional['DownloadService'] = None
_homefeed_service: Optional['HomeFeedService'] = None


def get_task_service():
    """获取任务服务单例"""
    global _task_service
    if _task_service is None:
        from .task_service import TaskService
        _task_service = TaskService()
    return _task_service


def get_account_service():
    """获取账号服务单例"""
    global _account_service
    if _account_service is None:
        from .account_service import AccountService
        _account_service = AccountService()
    return _account_service


def get_proxy_service():
    """获取代理服务单例"""
    global _proxy_service
    if _proxy_service is None:
        from .proxy_service import ProxyService
        _proxy_service = ProxyService()
    return _proxy_service


def get_checkpoint_service():
    """获取断点服务单例"""
    global _checkpoint_service
    if _checkpoint_service is None:
        from .checkpoint_service import CheckpointService
        _checkpoint_service = CheckpointService()
    return _checkpoint_service


def get_download_service():
    """获取下载服务单例"""
    global _download_service
    if _download_service is None:
        from .download_service import DownloadService
        _download_service = DownloadService()
    return _download_service


def get_homefeed_service():
    """获取首页推荐服务单例"""
    global _homefeed_service
    if _homefeed_service is None:
        from .homefeed_service import HomeFeedService
        _homefeed_service = HomeFeedService()
    return _homefeed_service
