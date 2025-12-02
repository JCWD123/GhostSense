#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爬虫客户端（不使用 Playwright）
"""
from typing import Dict, List, Optional
import uuid
import json
import httpx
from loguru import logger

from core.config import settings
from .base_client import BaseHttpClient
from .signature_client import signature_client
from .xhs_helper import parse_note_info_from_note_url, extract_note_id_from_url


class XHSClient(BaseHttpClient):
    """小红书客户端"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://edith.xiaohongshu.com"
        self.headers = {
            "User-Agent": settings.XHS_USER_AGENT,
            "Referer": "https://www.xiaohongshu.com/",
            "Origin": "https://www.xiaohongshu.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.b1: str = ""

    def set_b1(self, b1: Optional[str]):
        self.b1 = (b1 or "").strip()

    async def sign_request(self, url: str, data: Optional[Dict] = None, use_browser: bool = True) -> Dict[str, str]:
        """
        调用签名服务获取完整签名（x-s, x-t, x-s-common, X-B3-Traceid）

        Args:
            url: 请求URL
            data: 请求数据
            use_browser: 是否使用浏览器模式获取完整签名（推荐）

        Returns:
            包含签名的 headers 字典
        """
        # 从 cookies 中提取 a1 值
        a1 = self.cookies.get("a1", "")

        # 判断请求方法（根据 URL 和数据判断）
        method = "POST" if data else "GET"
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()]) if self.cookies else ""
        debug_port = settings.ELECTRON_DEBUG_PORT if settings.USE_ELECTRON_BROWSER else None

        # 🔑 如果启用浏览器模式，使用 /sign/xhs/browser 端点获取完整签名
        if use_browser:
            logger.info("🌐 使用浏览器模式获取完整签名（包括 x-s-common）")

            try:
                if not signature_client.client:
                    signature_client.client = httpx.AsyncClient(
                        base_url=signature_client.base_url,
                        timeout=30.0  # 浏览器模式需要更长超时
                    )

                # 获取当前设置的 UserAgent
                user_agent = self.headers.get("User-Agent", "")
                
                logger.debug(
                    "🚀 调用签名服务浏览器模式: cookie_len=%s debug_port=%s ua_len=%s",
                    len(cookie_str),
                    debug_port or "无",
                    len(user_agent)
                )
                response = await signature_client.client.post(
                    "/sign/xhs/browser",
                    json={
                        "url": url,
                        "method": method,
                        "data": data,
                        "cookie": cookie_str,
                        "userAgent": user_agent,
                        "debugPort": debug_port
                    }
                )
                response.raise_for_status()

                result = response.json()
                if result.get("success"):
                    headers = result.get("data", {})
                    logger.info("✅ 浏览器模式获取签名成功:")
                    logger.info(f"   x-s: {headers.get('x-s', '')[:30]}...")
                    logger.info(f"   x-t: {headers.get('x-t', '')}")
                    logger.info(f"   x-s-common: {headers.get('x-s-common', '')[:30]}...")
                    logger.info(f"   x-b3-traceid: {headers.get('x-b3-traceid', '')}")
                    return self._normalize_signature_headers(headers)
                else:
                    logger.error("❌ 浏览器模式失败，降级到纯JS模式")
                    content = result.get("error") or result
                    logger.error(f"   签名服务返回: {content}")
                    return await self._get_js_signature(url, method, data, a1, cookie_str, debug_port)
            except httpx.HTTPStatusError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                body = http_err.response.text[:500] if http_err.response else ""
                logger.error(
                    f"❌ 浏览器模式 HTTP 错误: {status} - {http_err}，降级到纯JS模式"
                )
                if body:
                    logger.error(f"   签名服务响应体: {body}")
                return await self._get_js_signature(url, method, data, a1, cookie_str, debug_port)
            except httpx.TimeoutException as timeout_err:
                logger.error(
                    "❌ 浏览器模式请求超时(%ss): %s，降级到纯JS模式",
                    signature_client.timeout,
                    repr(timeout_err)
                )
                logger.info("   建议检查 Electron 调试端口与网络连通性")
                return await self._get_js_signature(url, method, data, a1, cookie_str, debug_port)
            except Exception as e:
                logger.exception("❌ 浏览器模式出错，降级到纯JS模式")
                return await self._get_js_signature(url, method, data, a1, cookie_str, debug_port)
        else:
            # 纯JS模式（只返回 x-s, x-t）
            logger.warning("⚠️ 使用纯JS模式，可能缺少 x-s-common 导致请求失败")
            return await self._get_js_signature(url, method, data, a1, cookie_str, debug_port)

    async def _get_js_signature(
            self,
            url: str,
            method: str,
            data: Optional[Dict],
            a1: str,
            cookie_str: str,
            debug_port: Optional[int]
    ) -> Dict[str, str]:
        headers = await signature_client.get_xhs_sign(
            url,
            method,
            data,
            a1,
            self.b1,
            cookie=cookie_str,
            debug_port=debug_port,
            auto_fetch_b1=True
        )
        return self._normalize_signature_headers(headers)

    def _normalize_signature_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        if not headers:
            return {}
        normalized = {k: v for k, v in headers.items() if v is not None}
        for key in ["x-s", "x-t", "x-s-common", "x-b3-traceid"]:
            value = normalized.get(key) or normalized.get(key.upper())
            if value:
                normalized[key] = value
            normalized.pop(key.upper(), None)
        return normalized

    async def search_notes(
            self,
            keyword: str,
            page: int = 1,
            page_size: int = 20,
            sort: str = "general"
    ) -> List[Dict]:
        """
        搜索笔记

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort: 排序方式 (general: 综合, time_descending: 最新, popularity_descending: 最热)

        Returns:
            笔记列表
        """
        logger.info(f"🔍 开始搜索笔记:")
        logger.info(f"   关键词: {keyword}")
        logger.info(f"   页码: {page}")
        logger.info(f"   每页数量: {page_size}")
        logger.info(f"   排序: {sort}")

        uri = "/api/sns/web/v1/search/notes"
        url = f"{self.base_url}{uri}"

        # ⭐ 小红书使用 POST 请求，参数放在 Body 中，不是 URL 参数！
        data = {
            "keyword": keyword,
            "page": page,  # 改为整数，不是字符串
            "page_size": page_size,  # 改为整数，不是字符串
            "search_id": uuid.uuid4().hex,
            "sort": sort,
            "note_type": 0,  # 0: 全部, 1: 视频, 2: 图文
        }

        logger.info(f"📋 POST Body: {data}")
        logger.info(f"🌐 URL: {url}")

        try:
            # 改用 POST 请求，参数作为 JSON body
            result = await self.post(url, json=data)

            if result.get("success"):
                items = result.get("data", {}).get("items", [])
                notes = []

                for item in items:
                    note_card = item.get("note_card", {})
                    if note_card:
                        # ⚠️ 重要：id 在 item 层级，不在 note_card 层级
                        # 将 id 注入到 note_card 中
                        if "id" in item and not note_card.get("note_id"):
                            note_card["note_id"] = item["id"]

                        notes.append(self._parse_note_card(note_card))

                logger.info(f"✅ 搜索到 {len(notes)} 条笔记: {keyword}")
                return notes
            else:
                logger.error(f"❌ 搜索失败: {result}")
                return []

        except Exception as e:
            logger.error(f"❌ 搜索笔记失败: {e}")
            return []

    async def get_note_detail(self, note_id: str) -> Optional[Dict]:
        """
        获取笔记详情
        
        ✅ 使用正确的接口：POST /api/sns/web/v1/feed
        传递 source_note_id 参数（注意不是 note_id）

        Args:
            note_id: 笔记 ID

        Returns:
            笔记详情
        """
        # ✅ 正确的接口路径
        uri = "/api/sns/web/v1/feed"

        # ✅ 使用 source_note_id 参数
        data = {
            "source_note_id": note_id,  # 注意是 source_note_id 而不是 note_id
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": 1}
        }

        url = f"{self.base_url}{uri}"

        try:
            logger.debug(f"📝 请求笔记详情: {note_id}")
            result = await self.post(url, json=data)

            if result.get("success"):
                # feed 接口返回的数据结构可能略有不同
                items = result.get("data", {}).get("items", [])
                if items and len(items) > 0:
                    # 取第一个 item
                    note_data = items[0].get("note_card", {})
                    if note_data:
                        return self._parse_note_card(note_data, is_detail=True)

            logger.error(f"❌ 获取笔记详情失败: {note_id}, 响应: {result}")
            return None

        except Exception as e:
            logger.error(f"❌ 获取笔记详情失败: {e}")
            return None

    async def get_note_detail_for_token(self, note_id: str) -> Optional[Dict]:
        """
        获取笔记详情页（用于提取 xsec_token）

        ✅ 正确的详情接口：POST /api/sns/web/v1/feed
        这个接口会返回笔记的完整信息，包括 xsec_token 和 xsec_source
        用于后续请求评论接口时的认证

        Args:
            note_id: 笔记 ID

        Returns:
            包含 xsec_token 的详情数据
            {
                "note_id": "xxx",
                "xsec_token": "xxx",
                "xsec_source": "pc_note",
                "title": "...",
                ...
            }
        """
        # ✅ 正确的详情接口：/feed
        uri = "/api/sns/web/v1/feed"

        # ✅ 使用 POST，参数放在 body 中，传递 source_note_id
        data = {
            "source_note_id": note_id,  # 注意是 source_note_id
            "image_formats": ["jpg", "webp", "avif"],
            "xsec_source": "pc_feed",
            "xsec_token": ""
        }

        url = f"{self.base_url}{uri}"

        try:
            logger.debug(f"🔍 获取笔记详情以提取 xsec_token: {note_id}")
            logger.debug(f"   POST {url}")
            logger.debug(f"   Body: {data}")

            # ✅ 使用 POST 请求
            result = await self.post(url, json=data)

            if result.get("success"):
                data_obj = result.get("data", {})

                # feed 接口的响应结构
                # {
                #   "success": true,
                #   "data": {
                #     "items": [
                #       {
                #         "id": "xxx",
                #         "model_type": "note",
                #         "note_card": { ... },
                #         "xsec_token": "xxx",  ← token 在这里
                #         ...
                #       }
                #     ],
                #     "cursor": "xxx"
                #   }
                # }

                # 提取 xsec_token（从 items 数组的第一个元素）
                items = data_obj.get("items", [])
                xsec_token = ""
                xsec_source = "pc_feed"  # feed 接口默认是 pc_feed
                
                if items and len(items) > 0:
                    first_item = items[0]
                    # 尝试多个可能的位置
                    xsec_token = (
                        first_item.get("xsec_token") or  # 优先：item 层级
                        data_obj.get("xsec_token") or  # 备用：data 层级
                        first_item.get("note_card", {}).get("xsec_token") or  # 备用：note_card 层级
                        ""
                    )
                    
                    # xsec_source 也可能在 item 中
                    xsec_source = (
                        first_item.get("xsec_source") or
                        data_obj.get("xsec_source") or
                        "pc_feed"
                    )

                if xsec_token:
                    logger.info(f"✅ 成功获取 xsec_token: {note_id}")
                    logger.debug(f"   xsec_token: {xsec_token[:30]}...")
                    logger.debug(f"   xsec_source: {xsec_source}")

                    # 返回包含 token 的简化数据
                    return {
                        "note_id": note_id,
                        "xsec_token": xsec_token,
                        "xsec_source": xsec_source,
                        "title": items[0].get("note_card", {}).get("title", "") if items else "",
                        "type": items[0].get("note_card", {}).get("type", "") if items else "",
                    }
                else:
                    logger.warning(f"⚠️ feed 接口响应中未找到 xsec_token: {note_id}")
                    logger.debug(f"   响应结构: {list(data_obj.keys())}")
                    logger.debug(f"   items 数量: {len(items)}")

                    # 即使没有 token，也返回基本信息
                    return {
                        "note_id": note_id,
                        "xsec_token": "",
                        "xsec_source": "pc_note",
                    }
            else:
                error_msg = result.get("msg", "Unknown error")
                logger.error(f"❌ 获取详情页失败: {note_id}, {error_msg}")
                return None

        except Exception as e:
            logger.error(f"❌ 获取详情页异常: {note_id} - {e}")
            import traceback
            logger.debug(f"详细错误: {traceback.format_exc()}")
            return None

    async def execute_in_browser(self, url: str, method: str = "POST", data: Optional[Dict] = None) -> Dict:
        """
        在浏览器上下文内执行请求（最高安全性，自动带真实指纹）
        
        适用于最敏感的接口，如评论接口，直接在 Electron 浏览器中执行 fetch，
        自动带上 WebGL/Canvas 指纹、完整签名等。
        
        Args:
            url: 请求 URL
            method: 请求方法
            data: 请求数据
            
        Returns:
            API 响应数据
        """
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()]) if self.cookies else ""
        debug_port = settings.ELECTRON_DEBUG_PORT if settings.USE_ELECTRON_BROWSER else None
        
        if not signature_client.client:
            signature_client.client = httpx.AsyncClient(
                base_url=signature_client.base_url,
                timeout=60.0  # 浏览器内执行需要更长时间
            )
        
        try:
            logger.info(f"🌐 使用浏览器内执行模式: {method} {url}")
            logger.debug(f"   Cookie长度: {len(cookie_str)}, 调试端口: {debug_port}")
            
            response = await signature_client.client.post(
                "/execute/xhs/browser",
                json={
                    "url": url,
                    "method": method,
                    "data": data,
                    "cookie": cookie_str,
                    "debugPort": debug_port
                }
            )
            
            if response.status_code != 200:
                logger.error(f"❌ 浏览器内执行失败: HTTP {response.status_code}")
                logger.error(f"   响应: {response.text[:200]}")
                raise Exception(f"浏览器内执行失败: {response.status_code}")
            
            result = response.json()
            if not result.get("success"):
                raise Exception(result.get("message", "未知错误"))
            
            logger.success(f"✅ 浏览器内执行成功: {url}")
            return result.get("data", {})
            
        except Exception as e:
            logger.error(f"❌ 浏览器内执行异常: {e}")
            raise

    async def get_note_comments(
            self,
            note_id: str,
            cursor: str = "",
            top_comment_id: str = "",
            xsec_token: str = "",
            xsec_source: str = "pc_search",
            referer: str = ""
    ) -> Dict:
        """
        获取笔记评论（修复版 - 使用正确的接口）

        ✅ 正确的评论接口：POST https://t2.xiaohongshu.com/api/v2/collect
        注意：域名变了，从 edith 变成了 t2

        Args:
            note_id: 笔记 ID
            cursor: 游标（用于翻页）
            top_comment_id: 置顶评论 ID
            xsec_token: 安全令牌（必需，从搜索结果或笔记URL中获取）
            xsec_source: 来源标识（默认 pc_search）
            referer: Referer 头（模拟从详情页访问评论）

        Returns:
            评论数据
        """
        # ✅ 正确的评论接口（注意域名也变了）
        comment_base_url = "https://t2.xiaohongshu.com"
        uri = "/api/v2/collect"

        data = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": top_comment_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
            "xsec_source": xsec_source
        }

        # ⚠️ 注意：评论接口使用不同的域名
        url = f"{comment_base_url}{uri}"
        
        # 🌟 如果启用了浏览器内执行模式，使用最高安全性方案
        if settings.USE_BROWSER_EXECUTE_FOR_COMMENTS and settings.USE_ELECTRON_BROWSER:
            logger.info(f"🔒 使用浏览器内执行模式获取评论（最高安全性）")
            try:
                result = await self.execute_in_browser(url, method="POST", data=data)
                
                # 浏览器内执行返回的就是 API 响应，直接解析
                if result.get("success"):
                    comments_data = result.get("data", {}).get("comments", [])
                    comments = []
                    for comment in comments_data:
                        comments.append({
                            "comment_id": comment.get("id", ""),
                            "content": comment.get("content", ""),
                            "user_id": comment.get("user_info", {}).get("user_id", ""),
                            "user_name": comment.get("user_info", {}).get("nickname", ""),
                            "likes": comment.get("like_count", 0),
                            "sub_comment_count": comment.get("sub_comment_count", 0),
                            "create_time": comment.get("create_time", 0),
                        })
                    
                    logger.success(f"✅ 成功获取评论: {note_id} ({len(comments)} 条)")
                    return {
                        "success": True,
                        "comments": comments,
                        "cursor": result.get("data", {}).get("cursor", ""),
                        "has_more": result.get("data", {}).get("has_more", False)
                    }
                else:
                    error_msg = result.get("msg", "Unknown error")
                    logger.error(f"❌ 获取评论失败: {note_id}, {error_msg}")
                    return {"success": False, "comments": [], "error": error_msg}
                    
            except Exception as e:
                logger.warning(f"⚠️ 浏览器内执行失败，降级到普通模式: {e}")
                # 降级到普通模式（继续下面的代码）
        
        # 普通模式：使用 HTTP 客户端 + 签名服务
        # 设置正确的 referer（模拟从详情页过来）
        custom_headers = {}
        if referer:
            custom_headers["Referer"] = referer
            logger.debug(f"🔗 设置 Referer: {referer}")
        else:
            # 默认使用笔记详情页作为 referer
            custom_headers["Referer"] = f"https://www.xiaohongshu.com/explore/{note_id}"

        try:
            # 评论接口需要使用 POST，并将参数放在 JSON body 中
            result = await self.post(url, json=data, headers=custom_headers)

            if result.get("success"):
                comments_data = result.get("data", {}).get("comments", [])
                comments = []

                for comment in comments_data:
                    comments.append(self._parse_comment(comment))

                logger.info(f"✅ 获取到 {len(comments)} 条评论: {note_id}")

                return {
                    "comments": comments,
                    "cursor": result.get("data", {}).get("cursor", ""),
                    "has_more": result.get("data", {}).get("has_more", False)
                }
            else:
                logger.error(f"❌ 获取评论失败: {result}")
                return {"comments": [], "cursor": "", "has_more": False}

        except Exception as e:
            logger.error(f"❌ 获取评论失败: {e}")
            return {"comments": [], "cursor": "", "has_more": False}

    async def get_homefeed(self, cursor: str = "") -> Dict:
        """
        获取首页推荐流

        Args:
            cursor: 游标（用于翻页）

        Returns:
            推荐笔记列表
        """
        uri = "/api/sns/web/v1/homefeed"

        data = {
            "cursor_score": cursor,
            "num": 20,
            "refresh_type": 1,
            "note_index": 0,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": "homefeed_recommend"
        }

        url = f"{self.base_url}{uri}"

        try:
            result = await self.post(url, json=data)

            if result.get("success"):
                items = result.get("data", {}).get("items", [])
                notes = []

                for item in items:
                    note_card = item.get("note_card", {})
                    if note_card:
                        notes.append(self._parse_note_card(note_card))

                logger.info(f"✅ 获取到 {len(notes)} 条推荐笔记")

                return {
                    "notes": notes,
                    "cursor": result.get("data", {}).get("cursor_score", "")
                }
            else:
                logger.error(f"❌ 获取推荐流失败: {result}")
                return {"notes": [], "cursor": ""}

        except Exception as e:
            logger.error(f"❌ 获取推荐流失败: {e}")
            return {"notes": [], "cursor": ""}

    async def get_video_play_url(self, video_id: str, note_id: str = "") -> Optional[str]:
        """
        获取视频播放地址（修复版 - 使用正确的API路径）

        Args:
            video_id: 视频 ID (originVideoKey)
            note_id: 笔记 ID（可选，用于日志）

        Returns:
            视频播放地址（真实流URL或BD降级链接）
        """
        # 使用正确的API路径（与老仓库一致）
        uri = "/api/sns/v1/resource/video/play"

        data = {
            "video_id": video_id,
            "source": "pc"  # 使用 "pc" 而不是 "pc_web"
        }

        url = f"{self.base_url}{uri}"

        try:
            logger.info(f"🎬 获取视频播放地址:")
            logger.info(f"   video_id: {video_id}")
            logger.info(f"   note_id: {note_id}")
            logger.info(f"   API: {uri}")

            result = await self.post(url, json=data)

            logger.info(f"📡 API响应: {str(result)[:200]}...")

            # 检查响应结构
            if result.get("data"):
                video_data = result["data"].get("video", {})
                stream_list = video_data.get("stream", [])

                logger.info(f"📺 找到 {len(stream_list)} 个视频流")

                if stream_list:
                    # 按分辨率排序，获取最高清晰度
                    stream_list_sorted = sorted(
                        stream_list,
                        key=lambda x: x.get("height", 0),
                        reverse=True
                    )
                    best_stream = stream_list_sorted[0]
                    real_url = best_stream.get("url", "")

                    if real_url:
                        logger.info(
                            f"✅ 获取到真实视频流: {real_url[:80]}... "
                            f"(分辨率: {best_stream.get('width')}x{best_stream.get('height')})"
                        )
                        return real_url
                    else:
                        logger.warning(f"⚠️ 视频流URL为空")
                else:
                    logger.warning(f"⚠️ 响应中没有视频流")
            else:
                logger.warning(f"⚠️ 响应中没有data字段")

            # 降级到BD链接
            fallback_url = f"http://sns-video-bd.xhscdn.com/{video_id}"
            logger.warning(f"⚠️ 使用降级BD链接: {fallback_url}")
            return fallback_url

        except Exception as e:
            logger.error(f"❌ 获取视频地址异常: {type(e).__name__} - {e}")
            import traceback
            logger.error(f"   详细堆栈: {traceback.format_exc()}")

            # 出错时返回降级链接
            fallback_url = f"http://sns-video-bd.xhscdn.com/{video_id}"
            logger.info(f"🔄 返回降级链接: {fallback_url}")
            return fallback_url

    def _parse_note_card(self, note_card: Dict, is_detail: bool = False) -> Dict:
        """解析笔记数据"""
        note_id = (
                note_card.get("note_id")
                or note_card.get("id")
                or note_card.get("note", {}).get("note_id")
                or note_card.get("note", {}).get("id")
        )

        if not note_id:
            share_info = note_card.get("share_info") or {}
            candidate_urls = [
                share_info.get("link"),
                share_info.get("url"),
                share_info.get("copy_url"),
                share_info.get("share_url"),
            ]
            for url in candidate_urls:
                if not url:
                    continue
                try:
                    note_id = extract_note_id_from_url(url)
                    break
                except Exception:
                    continue

        if not note_id:
            logger.warning("⚠️ search result note_card 未包含 note_id，使用空字符串保存")
            note_id = ""

        # 基础信息
        parsed = {
            "note_id": note_id,
            "title": note_card.get("title", ""),
            "desc": note_card.get("desc", ""),
            "type": note_card.get("type", ""),  # normal, video
            "user_id": note_card.get("user", {}).get("user_id", ""),
            "nickname": note_card.get("user", {}).get("nickname", ""),
            "avatar": note_card.get("user", {}).get("avatar", ""),
            "liked_count": note_card.get("interact_info", {}).get("liked_count", "0"),
            "collected_count": note_card.get("interact_info", {}).get("collected_count", "0"),
            "comment_count": note_card.get("interact_info", {}).get("comment_count", "0"),
            "share_count": note_card.get("interact_info", {}).get("share_count", "0"),
            "ip_location": note_card.get("ip_location", ""),
            "note_url": f"https://www.xiaohongshu.com/explore/{note_id}",
        }

        security_info = self._extract_xsec_from_card(note_card, parsed["note_url"])
        parsed["xsec_token"] = security_info.get("xsec_token", "")
        parsed["xsec_source"] = security_info.get("xsec_source", "pc_search")

        # 图片列表
        image_list = note_card.get("image_list", [])
        if image_list:
            parsed["image_list"] = [img.get("url_default", "") for img in image_list]

        # 视频信息
        video_data = note_card.get("video", {})
        if video_data:
            video_id = video_data.get("consumer", {}).get("origin_video_key", "")
            if video_id:
                parsed["video_id"] = video_id
                parsed["video_url"] = f"http://sns-video-bd.xhscdn.com/{video_id}"  # BD链接，需要后续转换

        # 标签
        tag_list = note_card.get("tag_list", [])
        if tag_list:
            parsed["tags"] = [tag.get("name", "") for tag in tag_list]

        # 时间戳
        if is_detail:
            parsed["time"] = note_card.get("time", 0)
            parsed["last_update_time"] = note_card.get("last_update_time", 0)

        return parsed

    def _extract_xsec_from_card(self, note_card: Dict, default_url: str = "") -> Dict[str, str]:
        result = {
            "xsec_token": note_card.get("xsec_token", ""),
            "xsec_source": note_card.get("xsec_source", "pc_search") or "pc_search"
        }

        if result["xsec_token"]:
            return result

        candidate_urls: List[str] = []
        share_info = note_card.get("share_info") or {}
        for key in ("url", "link", "copy_url", "share_url"):
            value = share_info.get(key)
            if value:
                candidate_urls.append(value)

        if note_card.get("note_url"):
            candidate_urls.append(note_card["note_url"])
        if default_url:
            candidate_urls.append(default_url)

        for url in candidate_urls:
            try:
                info = parse_note_info_from_note_url(url)
            except Exception:
                continue
            if info and info.xsec_token:
                result["xsec_token"] = info.xsec_token
                result["xsec_source"] = info.xsec_source or result["xsec_source"]
                break

        return result

    def _parse_comment(self, comment: Dict) -> Dict:
        """解析评论数据"""
        return {
            "comment_id": comment.get("id", ""),
            "content": comment.get("content", ""),
            "user_id": comment.get("user_info", {}).get("user_id", ""),
            "nickname": comment.get("user_info", {}).get("nickname", ""),
            "avatar": comment.get("user_info", {}).get("image", ""),
            "ip_location": comment.get("ip_location", ""),
            "liked_count": comment.get("like_count", "0"),
            "sub_comment_count": comment.get("sub_comment_count", "0"),
            "create_time": comment.get("create_time", 0),
        }
