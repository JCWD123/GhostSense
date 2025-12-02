#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫辅助函数
移植自 MediaCrawler 老仓库的 help.py
"""

from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass


@dataclass
class NoteUrlInfo:
    """笔记URL信息"""
    note_id: str
    xsec_token: str
    xsec_source: str


@dataclass
class CreatorUrlInfo:
    """创作者URL信息"""
    user_id: str
    xsec_token: str
    xsec_source: str


def extract_url_params_to_dict(url: str) -> Dict[str, str]:
    """
    从URL中提取查询参数
    
    Args:
        url: URL字符串
        
    Returns:
        参数字典
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    # 将列表值转换为单个值
    return {k: v[0] if isinstance(v, list) and len(v) > 0 else v for k, v in params.items()}


def parse_note_info_from_note_url(url: str) -> NoteUrlInfo:
    """
    从小红书笔记URL中解析出笔记信息
    
    Args:
        url: 笔记URL
        例如: "https://www.xiaohongshu.com/explore/66fad51c000000001b0224b8?xsec_token=AB3rO-QopW5sgrJ41GwN01WCXh6yWPxjSoFI9D5JIMgKw=&xsec_source=pc_search"
    
    Returns:
        NoteUrlInfo: 包含 note_id, xsec_token, xsec_source 的对象
    """
    # 提取 note_id（从路径最后一段，去除查询参数）
    note_id = url.split("/")[-1].split("?")[0]
    
    # 提取查询参数
    params = extract_url_params_to_dict(url)
    xsec_token = params.get("xsec_token", "")
    xsec_source = params.get("xsec_source", "")
    
    return NoteUrlInfo(
        note_id=note_id,
        xsec_token=xsec_token,
        xsec_source=xsec_source
    )


def parse_creator_info_from_url(url: str) -> CreatorUrlInfo:
    """
    从小红书创作者主页URL中解析出创作者信息
    
    支持以下格式:
    1. 完整URL: "https://www.xiaohongshu.com/user/profile/5eb8e1d400000000010075ae?xsec_token=AB1nWBKCo1vE2HEkfoJUOi5B6BE5n7wVrbdpHoWIj5xHw=&xsec_source=pc_feed"
    2. 纯ID: "5eb8e1d400000000010075ae"
    
    Args:
        url: 创作者主页URL或user_id
        
    Returns:
        CreatorUrlInfo: 包含user_id, xsec_token, xsec_source的对象
    """
    import re
    
    # 如果是纯ID格式(24位十六进制字符),直接返回
    if len(url) == 24 and all(c in "0123456789abcdef" for c in url.lower()):
        return CreatorUrlInfo(user_id=url, xsec_token="", xsec_source="")
    
    # 从URL中提取user_id: /user/profile/xxx
    user_pattern = r'/user/profile/([^/?]+)'
    match = re.search(user_pattern, url)
    if match:
        user_id = match.group(1)
        # 提取xsec_token和xsec_source参数
        params = extract_url_params_to_dict(url)
        xsec_token = params.get("xsec_token", "")
        xsec_source = params.get("xsec_source", "")
        return CreatorUrlInfo(user_id=user_id, xsec_token=xsec_token, xsec_source=xsec_source)
    
    raise ValueError(f"无法从URL中解析出创作者信息: {url}")


def extract_note_id_from_url(url: str) -> str:
    """
    从笔记URL中快速提取 note_id
    
    Args:
        url: 笔记URL
        
    Returns:
        note_id
    """
    return url.split("/")[-1].split("?")[0]


# ==================== 测试 ====================

if __name__ == '__main__':
    print("🧪 测试小红书辅助函数\n")
    
    # 测试1: 解析笔记URL
    print("1️⃣ 解析笔记URL:")
    test_note_url = "https://www.xiaohongshu.com/explore/66fad51c000000001b0224b8?xsec_token=AB3rO-QopW5sgrJ41GwN01WCXh6yWPxjSoFI9D5JIMgKw=&xsec_source=pc_search"
    note_info = parse_note_info_from_note_url(test_note_url)
    print(f"   note_id: {note_info.note_id}")
    print(f"   xsec_token: {note_info.xsec_token[:30]}...")
    print(f"   xsec_source: {note_info.xsec_source}")
    
    # 测试2: 解析创作者URL
    print("\n2️⃣ 解析创作者URL:")
    test_creator_url = "https://www.xiaohongshu.com/user/profile/5eb8e1d400000000010075ae?xsec_token=AB1nWBKCo1vE2HEkfoJUOi5B6BE5n7wVrbdpHoWIj5xHw=&xsec_source=pc_feed"
    creator_info = parse_creator_info_from_url(test_creator_url)
    print(f"   user_id: {creator_info.user_id}")
    print(f"   xsec_token: {creator_info.xsec_token[:30]}...")
    print(f"   xsec_source: {creator_info.xsec_source}")
    
    # 测试3: 纯ID
    print("\n3️⃣ 解析纯ID:")
    test_user_id = "5eb8e1d400000000010075ae"
    creator_info2 = parse_creator_info_from_url(test_user_id)
    print(f"   user_id: {creator_info2.user_id}")
    print(f"   xsec_token: {creator_info2.xsec_token or '(空)'}")
    print(f"   xsec_source: {creator_info2.xsec_source or '(空)'}")
    
    print("\n✅ 测试完成")




