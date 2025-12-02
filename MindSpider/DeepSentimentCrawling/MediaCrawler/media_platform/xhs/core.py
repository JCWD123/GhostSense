# 声明:本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

import asyncio
import os
import random
import subprocess
import sys
from asyncio import Task
from typing import Dict, List, Optional

from DrissionPage import ChromiumPage, ChromiumOptions
from tenacity import RetryError
from websocket import WebSocketException

import config
from base.base_crawler import AbstractCrawler
from config import CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES
from model.m_xiaohongshu import NoteUrlInfo, CreatorUrlInfo
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import xhs as xhs_store
from tools import utils
from var import crawler_type_var, source_keyword_var

from .client import XiaoHongShuClient
from .login import XiaoHongShuLogin
from .exception import DataFetchError
from .field import SearchSortType
from .help import parse_note_info_from_note_url, parse_creator_info_from_url, get_search_id


class XiaoHongShuCrawler(AbstractCrawler):
    """基于 DrissionPage 的小红书爬虫"""
    
    page: ChromiumPage
    xhs_client: XiaoHongShuClient

    def __init__(self) -> None:
        self.index_url = "https://www.xiaohongshu.com"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.page = None

    async def start(self) -> None:
        """启动爬虫"""
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(ip_proxy_info)

        if getattr(config, "DRISSION_ATTACH_TO_BROWSER", False):
            co = self._build_existing_browser_options()
            utils.logger.info("[XiaoHongShuCrawler] 通过 CDP 连接到已运行浏览器")
            try:
                self.page = ChromiumPage(addr_or_opts=co)
            except Exception as exc:
                raise RuntimeError(
                    "无法连接到已运行的浏览器，请确认远程调试端口已打开且可访问。"
                ) from exc
        else:
            last_launch_error: Optional[Exception] = None
            for browser_path in self._iter_browser_paths():
                co = ChromiumOptions()

                if browser_path:
                    co.set_browser_path(browser_path)
                    utils.logger.info("[XiaoHongShuCrawler] 尝试使用浏览器路径: %s", browser_path)
                else:
                    utils.logger.info("[XiaoHongShuCrawler] 尝试使用系统默认浏览器路径")
                
                # 设置用户数据目录
                user_data_dir = os.path.join(os.getcwd(), "browser_data", "xhs_user_data_dir")
                co.set_user_data_path(user_data_dir)
                
                # 设置 User-Agent
                co.set_user_agent(self.user_agent)
                
                # 设置代理（如果需要）
                if httpx_proxy_format:
                    co.set_proxy(httpx_proxy_format)
                
                # 设置无头模式
                if config.HEADLESS:
                    co.headless()
                
                # 禁用自动化检测特征
                co.set_argument('--disable-blink-features=AutomationControlled')
                co.set_argument('--disable-dev-shm-usage')
                co.set_argument('--no-sandbox')
                
                # 创建浏览器页面
                utils.logger.info("[XiaoHongShuCrawler] 使用 DrissionPage 启动浏览器")
                try:
                    self.page = ChromiumPage(addr_or_opts=co)
                    break
                except (WebSocketException, RuntimeError, OSError, AttributeError) as exc:
                    last_launch_error = exc
                    utils.logger.error(
                        "[XiaoHongShuCrawler] 浏览器启动失败: %s，尝试下一个候选路径...",
                        exc,
                        exc_info=True,
                    )
                    self.page = None
                    continue
                except Exception as exc:
                    last_launch_error = exc
                    utils.logger.error(
                        "[XiaoHongShuCrawler] 浏览器启动遇到未知异常: %s，尝试下一个候选路径...",
                        exc,
                        exc_info=True,
                    )
                    self.page = None
                    continue

            if not self.page:
                raise RuntimeError("所有候选浏览器均无法启动，请检查浏览器安装或配置。") from last_launch_error
        
        # 访问首页
        self.page.get(self.index_url)
        await asyncio.sleep(2)

        # 创建 HTTP 客户端
        self.xhs_client = await self.create_xhs_client(httpx_proxy_format)
        
        # 检查登录状态
        if not await self.xhs_client.pong():
            if getattr(config, "DRISSION_ATTACH_TO_BROWSER", False):
                await self._wait_for_manual_login()
            else:
                login_obj = XiaoHongShuLogin(
                    login_type=config.LOGIN_TYPE,
                    page=self.page,
                    login_phone="",  # input your phone number
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
                await self.xhs_client.update_cookies_from_drission(self.page)

        crawler_type_var.set(config.CRAWLER_TYPE)
        if config.CRAWLER_TYPE == "search":
            # Search for notes and retrieve their comment information.
            await self.search()
        elif config.CRAWLER_TYPE == "detail":
            # Get the information and comments of the specified post
            await self.get_specified_notes()
        elif config.CRAWLER_TYPE == "creator":
            # Get creator's information and their notes and comments
            await self.get_creators_and_notes()
        else:
            pass

        utils.logger.info("[XiaoHongShuCrawler.start] Xhs Crawler finished ...")

    async def search(self) -> None:
        """搜索笔记并获取评论信息"""
        utils.logger.info("[XiaoHongShuCrawler.search] Begin search xiaohongshu keywords")
        xhs_limit_count = 20  # xhs limit page fixed value
        if config.CRAWLER_MAX_NOTES_COUNT < xhs_limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = xhs_limit_count
        start_page = config.START_PAGE
        
        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(f"[XiaoHongShuCrawler.search] Current search keyword: {keyword}")
            page = 1
            search_id = get_search_id()
            
            while (page - start_page + 1) * xhs_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[XiaoHongShuCrawler.search] Skip page {page}")
                    page += 1
                    continue

                try:
                    utils.logger.info(f"[XiaoHongShuCrawler.search] search xhs keyword: {keyword}, page: {page}")
                    note_ids: List[str] = []
                    xsec_tokens: List[str] = []
                    notes_res = await self.xhs_client.get_note_by_keyword(
                        keyword=keyword,
                        search_id=search_id,
                        page=page,
                        sort=(SearchSortType(config.SORT_TYPE) if config.SORT_TYPE != "" else SearchSortType.GENERAL),
                    )
                    utils.logger.info(f"[XiaoHongShuCrawler.search] Search notes res:{notes_res}")
                    if not notes_res or not notes_res.get("has_more", False):
                        utils.logger.info("No more content!")
                        break
                    
                    semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
                    task_list = [
                        self.get_note_detail_async_task(
                            note_id=post_item.get("note_id"),
                            xsec_token=post_item.get("xsec_token"),
                            xsec_source=post_item.get("xsec_source"),
                            semaphore=semaphore
                        ) for post_item in notes_res.get("items", {})
                        if post_item.get("note_id") not in config.CRAWLER_NOTE_ID_LIST
                    ]
                    note_details = await asyncio.gather(*task_list)
                    for note_detail in note_details:
                        if note_detail:
                            await xhs_store.update_xhs_note(note_detail)
                            await self.get_note_comments(note_detail, page_comments=config.ENABLE_GET_COMMENTS)
                    page += 1
                    await self.batch_get_note_comments(note_details)
                except DataFetchError:
                    utils.logger.error("[XiaoHongShuCrawler.search] Get note detail error")
                    break

    async def get_specified_notes(self):
        """获取指定笔记的详情"""
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_note_detail_async_task(
                note_info.note_id, note_info.xsec_token, note_info.xsec_source, semaphore
            ) for note_info in config.XHS_SPECIFIED_NOTE_LIST
        ]

        note_details = await asyncio.gather(*task_list)
        for note_detail in note_details:
            if note_detail:
                await xhs_store.update_xhs_note(note_detail)
        await self.batch_get_note_comments(note_details)

    async def get_creators_and_notes(self) -> None:
        """获取创作者信息和笔记"""
        utils.logger.info("[XiaoHongShuCrawler.get_creators_and_notes] Begin get xiaohongshu creators")
        for user_url in config.XHS_CREATOR_URL_LIST:
            creator_info: CreatorUrlInfo = parse_creator_info_from_url(user_url)
            if creator_info is None:
                utils.logger.info(f"[XiaoHongShuCrawler.get_creators_and_notes] Invalid creator url: {user_url}")
                continue

            await self.get_creator_notes_by_creator_id(creator_info.user_id)
            await self.get_creator_info(creator_info.user_id)

    async def get_creator_notes_by_creator_id(self, user_id: str) -> None:
        """根据创作者ID获取笔记"""
        utils.logger.info(f"[XiaoHongShuCrawler.get_creator_notes_by_creator_id] Begin get note list by user_id: {user_id}")
        
        cursor = ""
        page = 0
        while page * 30 <= config.CRAWLER_MAX_NOTES_COUNT:
            notes_res = await self.xhs_client.get_note_by_creator(user_id=user_id, cursor=cursor)
            if not notes_res or not notes_res.get("has_more", False):
                utils.logger.info("No more content!")
                break
            
            note_list: List[str] = notes_res.get("notes", [])
            utils.logger.info(f"[XiaoHongShuCrawler.get_creator_notes_by_creator_id] got note list: {note_list}")
            
            semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
            task_list = [
                self.get_note_detail_async_task(
                    note_id=note_item.get("note_id"),
                    xsec_token=note_item.get("xsec_token"),
                    xsec_source=note_item.get("xsec_source"),
                    semaphore=semaphore
                ) for note_item in note_list
                if note_item.get("note_id") not in config.CRAWLER_NOTE_ID_LIST
            ]
            note_details = await asyncio.gather(*task_list)
            for note_detail in note_details:
                if note_detail:
                    await xhs_store.update_xhs_note(note_detail)
            await self.batch_get_note_comments(note_details)
            
            cursor = notes_res.get("cursor", "")
            page += 1
            utils.logger.info(f"[XiaoHongShuCrawler.get_creator_notes_by_creator_id] creator user_id:{user_id}, note page: {page}")
            await asyncio.sleep(random.randint(1, 3))

    async def get_creator_info(self, user_id: str) -> None:
        """获取创作者信息"""
        utils.logger.info(f"[XiaoHongShuCrawler.get_creator_info] Begin get creator info, user_id: {user_id}")
        user_info: Dict = await self.xhs_client.get_creator_info(user_id=user_id)
        if user_info:
            await xhs_store.save_creator(user_id, user_info)

    async def get_note_detail_async_task(
        self, note_id: str, xsec_token: str, xsec_source: str, semaphore: asyncio.Semaphore
    ) -> Optional[Dict]:
        """异步获取笔记详情"""
        async with semaphore:
            try:
                result = await self.xhs_client.get_note_by_id(note_id, xsec_token, xsec_source)
                return result
            except DataFetchError as ex:
                utils.logger.error(f"[XiaoHongShuCrawler.get_note_detail_async_task] Get note detail error: {ex}")
                return None
            except KeyError as ex:
                utils.logger.error(
                    f"[XiaoHongShuCrawler.get_note_detail_async_task] have not fund note detail note_id:{note_id}, err: {ex}")
                return None

    async def batch_get_note_comments(self, note_list: List[Dict]):
        """批量获取笔记评论"""
        if not config.ENABLE_GET_COMMENTS:
            return
        
        task_list: List[Task] = []
        for note_item in note_list:
            task = asyncio.create_task(self.get_note_comments(note_item), name=note_item.get("note_id"))
            task_list.append(task)
        await asyncio.gather(*task_list)

    async def get_note_comments(self, note_item: Dict, page_comments: bool = False):
        """获取笔记的评论"""
        if not config.ENABLE_GET_COMMENTS:
            return
        
        note_id = note_item.get("note_id")
        xsec_token = note_item.get("xsec_token", "")
        xsec_source = note_item.get("xsec_source", "")
        
        utils.logger.info(f"[XiaoHongShuCrawler.get_note_comments] Begin get note id comments {note_id}")
        
        all_comments = []
        crawled_count = 0
        comments_has_more = True
        comments_cursor = ""
        
        while crawled_count < CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES and comments_has_more:
            try:
                comments_res = await self.xhs_client.get_note_comments(
                    note_id=note_id,
                    xsec_token=xsec_token,
                    xsec_source=xsec_source,
                    cursor=comments_cursor
                )
                comments_has_more = comments_res.get("has_more", False)
                comments_cursor = comments_res.get("cursor", "")
                
                if "comments" not in comments_res:
                    utils.logger.info(
                        f"[XiaoHongShuCrawler.get_note_comments] No 'comments' key found in response for note_id: {note_id}")
                    break
                
                comments = comments_res["comments"]
                if not comments:
                    break
                
                if page_comments:
                    await xhs_store.batch_update_xhs_note_comments(note_id, comments)
                    crawled_count += len(comments)
                else:
                    all_comments.extend(comments)
                    crawled_count += len(comments)
            except DataFetchError as ex:
                utils.logger.error(f"[XiaoHongShuCrawler.get_note_comments] get note_id: {note_id} comment error: {ex}")
                break
            except Exception as e:
                utils.logger.error(f"[XiaoHongShuCrawler.get_note_comments] An error occurred: {e}")
                break
        
        if not page_comments:
            await xhs_store.batch_update_xhs_note_comments(note_id, all_comments)
        
        utils.logger.info(f"[XiaoHongShuCrawler.get_note_comments] note_id: {note_id} comments have all been obtained.")

    async def create_xhs_client(self, httpx_proxy: Optional[str]) -> XiaoHongShuClient:
        """创建小红书客户端"""
        utils.logger.info("[XiaoHongShuCrawler.create_xhs_client] Begin create xiaohongshu API client ...")
        
        # 从 DrissionPage 获取 cookies
        cookie_str, cookie_dict = self.get_cookies_from_drission()
        
        xhs_client = XiaoHongShuClient(
            proxy=httpx_proxy,
            headers={
                "User-Agent": self.user_agent,
                "Cookie": cookie_str,
                "Origin": "https://www.xiaohongshu.com",
                "Referer": "https://www.xiaohongshu.com",
                "Content-Type": "application/json;charset=UTF-8"
            },
            playwright_page=None,  # DrissionPage 不需要 playwright_page
            cookie_dict=cookie_dict,
        )
        return xhs_client

    def get_cookies_from_drission(self):
        """从 DrissionPage 获取 cookies"""
        cookies = self.page.cookies(all_domains=True, all_info=True)
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        return cookie_str, cookie_dict

    async def _wait_for_manual_login(self, timeout: int = 180):
        """在附着浏览器模式下等待用户手动登录"""
        utils.logger.info(
            "[XiaoHongShuCrawler] 请在已连接的浏览器窗口中手动完成登录，程序将在后台检测登录状态（剩余 %ss）",
            timeout,
        )
        remaining = timeout
        while remaining > 0:
            await asyncio.sleep(3)
            remaining -= 3
            try:
                await self.xhs_client.update_cookies_from_drission(self.page)
                if await self.xhs_client.pong():
                    utils.logger.info("[XiaoHongShuCrawler] 检测到登录成功，继续执行任务。")
                    return
            except Exception as exc:
                utils.logger.debug(
                    "[XiaoHongShuCrawler] 手动登录检测异常: %s（剩余 %ss）",
                    exc,
                    remaining,
                )

            if remaining % 30 == 0 or remaining < 30:
                utils.logger.info(
                    "[XiaoHongShuCrawler] 请尽快完成登录，剩余 %ss。",
                    max(remaining, 0),
                )

        raise RuntimeError("等待用户手动登录超时，请确认已经在浏览器中完成登录。")

    async def launch_browser(self, *args, **kwargs):
        """保留接口兼容性"""
        pass

    async def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()

    def _build_existing_browser_options(self) -> ChromiumOptions:
        """构建连接到已运行浏览器的 DrissionPage 配置"""
        co = ChromiumOptions()
        co.existing_only(True)

        debug_host = getattr(config, "DRISSION_REMOTE_DEBUG_HOST", "127.0.0.1")
        debug_port = getattr(config, "DRISSION_REMOTE_DEBUG_PORT", 9222) or 9222
        address = f"{debug_host}:{debug_port}"
        co.set_address(address)

        utils.logger.info(
            "[XiaoHongShuCrawler] 将连接到远程调试浏览器: %s",
            address,
        )
        return co

    def _iter_browser_paths(self) -> List[Optional[str]]:
        """按优先级返回可尝试的浏览器路径列表"""
        checked_paths: List[str] = []
        result: List[Optional[str]] = []

        configured_path = getattr(config, "DRISSION_BROWSER_PATH", "").strip()
        normalized_config_path = os.path.expanduser(configured_path) if configured_path else ""
        if configured_path:
            if self._is_browser_available(normalized_config_path):
                result.append(normalized_config_path)
                checked_paths.append(normalized_config_path)
            else:
                utils.logger.warning(
                    "[XiaoHongShuCrawler] 配置的浏览器路径不可用: %s，请检查是否已安装或具备执行权限。",
                    normalized_config_path,
                )

        for candidate in self._default_browser_candidates():
            normalized_candidate = os.path.expanduser(candidate)
            if normalized_candidate in checked_paths:
                continue
            if self._is_browser_available(normalized_candidate):
                utils.logger.info("[XiaoHongShuCrawler] 自动检测到浏览器路径: %s", normalized_candidate)
                result.append(normalized_candidate)
                checked_paths.append(normalized_candidate)

        # 最后尝试使用系统默认浏览器
        result.append(None)
        return result

    def _default_browser_candidates(self) -> List[str]:
        """默认尝试的浏览器路径"""
        linux_candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
        windows_candidates = [
            "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
            "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe",
            "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        ]

        if sys.platform.startswith("linux"):
            candidates: List[str] = []
            if self._is_wsl_environment():
                candidates.extend(windows_candidates)
            candidates.extend(linux_candidates)
            return candidates
        elif sys.platform.startswith("win"):
            return [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            ]
        return []

    @staticmethod
    def _is_wsl_environment() -> bool:
        """判断是否运行在 WSL 中"""
        return "WSL_DISTRO_NAME" in os.environ or os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop")

    def _is_browser_available(self, path: str) -> bool:
        """尝试执行浏览器的 --version 以判断是否可用"""
        if not path:
            return False
        if not os.path.exists(path):
            return False

        try:
            result = subprocess.run(
                [path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except OSError as exc:
            utils.logger.debug("[XiaoHongShuCrawler] 运行浏览器检测命令失败: %s", exc)
            return False

        if result.returncode == 0:
            return True

        err_msg = result.stderr.decode(errors="ignore").strip()
        if not err_msg:
            err_msg = result.stdout.decode(errors="ignore").strip()
        utils.logger.warning(
            "[XiaoHongShuCrawler] 浏览器 '%s' 无法执行 --version（返回码 %s，信息：%s）",
            path,
            result.returncode,
            err_msg or "未知错误",
        )
        return False
