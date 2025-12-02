# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from playwright.async_api import BrowserContext, Page
from tenacity import retry, stop_after_attempt, wait_fixed
from xhshow import Xhshow

import config
from base.base_crawler import AbstractApiClient
from tools import utils

from .exception import DataFetchError, IPBlockError
from .field import SearchNoteType, SearchSortType
from .help import get_search_id, sign

PLAYWRIGHT_SIGN_SCRIPT = """
({a1, b1, x_s, x_t}) => {
    const lookup = [
        "Z", "m", "s", "e", "r", "b", "B", "o", "H", "Q", "t", "N",
        "P", "+", "w", "O", "c", "z", "a", "/", "L", "p", "n", "g",
        "G", "8", "y", "J", "q", "4", "2", "K", "W", "Y", "j", "0",
        "D", "S", "f", "d", "i", "k", "x", "3", "V", "T", "1", "6",
        "I", "l", "U", "A", "F", "M", "9", "7", "h", "E", "C", "v",
        "u", "R", "X", "5",
    ];
    const ie = [
        0, 1996959894, 3993919788, 2567524794, 124634137, 1886057615, 3915621685,
        2657392035, 249268274, 2044508324, 3772115230, 2547177864, 162941995,
        2125561021, 3887607047, 2428444049, 498536548, 1789927666, 4089016648,
        2227061214, 450548861, 1843258603, 4107580753, 2211677639, 325883990,
        1684777152, 4251122042, 2321926636, 335633487, 1661365465, 4195302755,
        2366115317, 997073096, 1281953886, 3579855332, 2724688242, 1006888145,
        1258607687, 3524101629, 2768942443, 901097722, 1119000684, 3686517206,
        2898065728, 853044451, 1172266101, 3705015759, 2882616665, 651767980,
        1373503546, 3369554304, 3218104598, 565507253, 1454621731, 3485111705,
        3099436303, 671266974, 1594198024, 3322730930, 2970347812, 795835527,
        1483230225, 3244367275, 3060149565, 1994146192, 31158534, 2563907772,
        4023717930, 1907459465, 112637215, 2680153253, 3904427059, 2013776290,
        251722036, 2517215374, 3775830040, 2137656763, 141376813, 2439277719,
        3865271297, 1802195444, 476864866, 2238001368, 4066508878, 1812370925,
        453092731, 2181625025, 4111451223, 1706088902, 314042704, 2344532202,
        4240017532, 1658658271, 366619977, 2362670323, 4224994405, 1303535960,
        984961486, 2747007092, 3569037538, 1256170817, 1037604311, 2765210733,
        3554079995, 1131014506, 879679996, 2909243462, 3663771856, 1141124467,
        855842277, 2852801631, 3708648649, 1342533948, 654459306, 3188396048,
        3373015174, 1466479909, 544179635, 3110523913, 3462522015, 1591671054,
        702138776, 2966460450, 3352799412, 1504918807, 783551873, 3082640443,
        3233442989, 3988292384, 2596254646, 62317068, 1957810842, 3939845945,
        2647816111, 81470997, 1943803523, 3814918930, 2489596804, 225274430,
        2053790376, 3826175755, 2466906013, 167816743, 2097651377, 4027552580,
        2265490386, 503444072, 1762050814, 4150417245, 2154129355, 426522225,
        1852507879, 4275313526, 2312317920, 282753626, 1742555852, 4189708143,
        2394877945, 397917763, 1622183637, 3604390888, 2714866558, 953729732,
        1340076626, 3518719985, 2797360999, 1068828381, 1219638859, 3624741850,
        2936675148, 906185462, 1090812512, 3747672003, 2825379669, 829329135,
        1181335161, 3412177804, 3160834842, 628085408, 1382605366, 3423369109,
        3138078467, 570562233, 1426400815, 3317316542, 2998733608, 733239954,
        1555261956, 3268935591, 3050360625, 752459403, 1541320221, 2607071920,
        3965973030, 1969922972, 40735498, 2617837225, 3943577151, 1913087877,
        83908371, 2512341634, 3803740692, 2075208622, 213261112, 2463272603,
        3855990285, 2094854071, 198958881, 2262029012, 4057260610, 1759359992,
        534414190, 2176718541, 4139329115, 1873836001, 414664567, 2282248934,
        4279200368, 1711684554, 285281116, 2405801727, 4167216745, 1634467795,
        376229701, 2685067896, 3608007406, 1308918612, 956543938, 2808555105,
        3495958263, 1231636301, 1047427035, 2932959818, 3654703836, 1088359270,
        936918000, 2847714899, 3736837829, 1202900863, 817233897, 3183342108,
        3401237130, 1404277552, 615818150, 3134207493, 3453421203, 1423857449,
        601450431, 3009837614, 3294710456, 1567103746, 711928724, 3020668471,
        3272380065, 1510334235, 755167117,
    ];
    const tripletToBase64 = (e) => (
        lookup[(e >> 18) & 63] +
        lookup[(e >> 12) & 63] +
        lookup[(e >> 6) & 63] +
        lookup[e & 63]
    );
    const encodeChunk = (e, t, r) => {
        const m = [];
        for (let b = t; b < r; b += 3) {
            const n = ((e[b] << 16) & 16711680) + ((e[b + 1] << 8) & 65280) + (e[b + 2] & 255);
            m.push(tripletToBase64(n));
        }
        return m.join("");
    };
    const b64Encode = (e) => {
        const P = e.length;
        const W = P % 3;
        const U = [];
        const z = 16383;
        let H = 0;
        const Z = P - W;
        while (H < Z) {
            const chunkEnd = H + z > Z ? Z : H + z;
            U.push(encodeChunk(e, H, chunkEnd));
            H += z;
        }
        if (W === 1) {
            const F = e[P - 1];
            U.push(lookup[F >> 2] + lookup[(F << 4) & 63] + "==");
        } else if (W === 2) {
            const F = (e[P - 2] << 8) + e[P - 1];
            U.push(lookup[F >> 10] + lookup[(F >> 4) & 63] + lookup[(F << 2) & 63] + "=");
        }
        return U.join("");
    };
    const encodeUtf8 = (val) => Array.from(new TextEncoder().encode(val));
    const rightWithoutSign = (num, bit = 0) => {
        const MAX32INT = 4294967295;
        const val = (num >>> bit) >>> 0;
        return ((val + (MAX32INT + 1)) % (2 * (MAX32INT + 1))) - MAX32INT - 1;
    };
    const mrc = (e) => {
        let o = -1;
        for (let n = 0; n < 57; n++) {
            o = ie[(o & 255) ^ e.charCodeAt(n)] ^ rightWithoutSign(o, 8);
        }
        return o ^ -1 ^ 3988292384;
    };
    const getTraceId = () => {
        const chars = "abcdef0123456789";
        let result = "";
        if (typeof crypto !== "undefined" && crypto.getRandomValues) {
            const randomVals = crypto.getRandomValues(new Uint32Array(16));
            for (let i = 0; i < randomVals.length; i++) {
                result += chars[randomVals[i] % chars.length];
            }
        } else {
            for (let i = 0; i < 16; i++) {
                result += chars[Math.floor(Math.random() * chars.length)];
            }
        }
        return result;
    };
    const common = {
        s0: 3,
        s1: "",
        x0: "1",
        x1: "4.2.2",
        x2: "Mac OS",
        x3: "xhs-pc-web",
        x4: "4.74.0",
        x5: a1,
        x6: x_t,
        x7: x_s,
        x8: b1,
        x9: mrc(x_t + x_s + b1),
        x10: 154,
        x11: "normal",
    };
    const encodeStr = encodeUtf8(JSON.stringify(common));
    const x_s_common = b64Encode(encodeStr);
    return {
        "x-s": x_s,
        "x-t": x_t,
        "x-s-common": x_s_common,
        "x-b3-traceid": getTraceId(),
    };
}
"""
from .extractor import XiaoHongShuExtractor


class XiaoHongShuClient(AbstractApiClient):

    def __init__(
            self,
            timeout=60,  # 若开启爬取媒体选项，xhs 的长视频需要更久的超时时间
            proxy=None,
            *,
            headers: Dict[str, str],
            playwright_page: Page,
            cookie_dict: Dict[str, str],
    ):
        self.proxy = proxy
        self.timeout = timeout
        self.headers = headers
        self._host = "https://edith.xiaohongshu.com"
        self._domain = "https://www.xiaohongshu.com"
        self.IP_ERROR_STR = "网络连接异常，请检查网络设置或重启试试"
        self.IP_ERROR_CODE = 300012
        self.NOTE_ABNORMAL_STR = "笔记状态异常，请稍后查看"
        self.NOTE_ABNORMAL_CODE = -510001
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict
        self._extractor = XiaoHongShuExtractor()
        # 初始化 xhshow 客户端用于签名生成
        self._xhshow_client = Xhshow()

    async def _pre_headers(self, url: str, data=None) -> Dict:
        """
        请求头参数签名，使用 xhshow 库生成签名
        Args:
            url: 完整的 URI（GET 请求包含查询参数）
            data: POST 请求的请求体数据

        Returns:

        """
        # 获取 a1 cookie 值
        a1_value = self.cookie_dict.get("a1", "")

        # 根据请求类型使用不同的签名方法
        if data is None:
            # GET 请求：从 url 中提取参数
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url)
            params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
            # 使用完整的 URL（包含 host）
            full_url = f"{self._host}{url}"
            x_s = self._xhshow_client.sign_xs_get(uri=full_url, a1_value=a1_value, params=params)
        else:
            # POST 请求：使用 data 作为 payload
            full_url = f"{self._host}{url}"
            x_s = self._xhshow_client.sign_xs_post(uri=full_url, a1_value=a1_value, payload=data)

        x_t_value = str(int(time.time() * 1000))

        # 尝试获取 b1 值（从 localStorage），如果获取失败则使用空字符串
        b1_value = ""
        try:
            if self.playwright_page:
                local_storage = await self.playwright_page.evaluate("() => window.localStorage")
                b1_value = local_storage.get("b1", "")
        except Exception as e:
            utils.logger.warning(
                f"[XiaoHongShuClient._pre_headers] Failed to get b1 from localStorage: {e}, using empty string")

        signs = await self._generate_sign_headers(
            a1_value=a1_value,
            b1_value=b1_value,
            x_s=x_s,
            x_t=x_t_value,
        )

        headers = {
            "X-S": signs["x-s"],
            "X-T": signs["x-t"],
            "x-S-Common": signs["x-s-common"],
            "X-B3-Traceid": signs["x-b3-traceid"],
        }
        self.headers.update(headers)
        return self.headers

    async def _generate_sign_headers(self, *, a1_value: str, b1_value: str, x_s: str, x_t: str) -> Dict[str, str]:
        try:
            return sign(
                a1=a1_value,
                b1=b1_value,
                x_s=x_s,
                x_t=x_t,
            )
        except Exception as err:
            utils.logger.warning(
                f"[XiaoHongShuClient._generate_sign_headers] Local x-s-common generation failed: {err}. Trying Playwright fallback",
                exc_info=True,
            )
            if not self.playwright_page:
                raise
            return await self._generate_sign_with_playwright(
                a1_value=a1_value,
                b1_value=b1_value,
                x_s=x_s,
                x_t=x_t,
            )

    async def _generate_sign_with_playwright(self, *, a1_value: str, b1_value: str, x_s: str, x_t: str) -> Dict[
        str, str]:
        if not self.playwright_page:
            raise RuntimeError("Playwright page is required for fallback signature generation")

        payload = {
            "a1": a1_value or "",
            "b1": b1_value or "",
            "x_s": x_s or "",
            "x_t": x_t or "",
        }

        try:
            return await self.playwright_page.evaluate(PLAYWRIGHT_SIGN_SCRIPT, payload)
        except Exception as err:
            utils.logger.error(
                f"[XiaoHongShuClient._generate_sign_with_playwright] Playwright fallback failed: {err}",
                exc_info=True,
            )
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def request(self, method, url, **kwargs) -> Union[str, Any]:
        """
        封装httpx的公共请求方法，对请求响应做一些处理
        Args:
            method: 请求方法
            url: 请求的URL
            **kwargs: 其他请求参数，例如请求头、请求体等

        Returns:

        """
        # return response.text
        return_response = kwargs.pop("return_response", False)
        
        try:
            async with httpx.AsyncClient(proxy=self.proxy) as client:
                response = await client.request(method, url, timeout=self.timeout, **kwargs)
        except httpx.ConnectError as e:
            utils.logger.error(f"[XiaoHongShuClient.request] Network connection error: {e}")
            utils.logger.error(f"[XiaoHongShuClient.request] Failed to connect to {url}")
            return {}
        except httpx.TimeoutException as e:
            utils.logger.error(f"[XiaoHongShuClient.request] Request timeout: {e}")
            return {}
        except Exception as e:
            utils.logger.error(f"[XiaoHongShuClient.request] Unexpected error during request: {e}")
            return {}

        if response.status_code == 471 or response.status_code == 461:
            # someday someone maybe will bypass captcha
            verify_type = response.headers.get("Verifytype", "unknown")
            verify_uuid = response.headers.get("Verifyuuid", "unknown")
            msg = f"出现验证码，请求失败，Verifytype: {verify_type}，Verifyuuid: {verify_uuid}, Response: {response.text[:200]}"
            utils.logger.error(msg)
            raise Exception(msg)

        if return_response:
            return response.text

        # 先检查响应内容
        response_text = response.text
        if not response_text or response_text.strip() == "":
            utils.logger.error(f"[XiaoHongShuClient.request] Empty response received for {url}")
            raise DataFetchError("Empty response from API")

        # 尝试解析JSON
        try:
            data: Dict = response.json()
        except Exception as e:
            utils.logger.error(f"[XiaoHongShuClient.request] Failed to parse JSON response")
            utils.logger.error(f"[XiaoHongShuClient.request] Response status: {response.status_code}")
            utils.logger.error(f"[XiaoHongShuClient.request] Response headers: {dict(response.headers)}")
            utils.logger.error(f"[XiaoHongShuClient.request] Response text (first 500 chars): {response_text[:500]}")
            # 返回空数据而不是抛出异常
            return {}

        if data["success"]:
            return data.get("data", data.get("success", {}))
        elif data["code"] == self.IP_ERROR_CODE:
            raise IPBlockError(self.IP_ERROR_STR)
        else:
            err_msg = data.get("msg", None) or f"{response.text}"
            raise DataFetchError(err_msg)

    async def get(self, uri: str, params=None) -> Dict:
        """
        GET请求，对请求头签名
        Args:
            uri: 请求路由
            params: 请求参数

        Returns:

        """
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?" f"{urlencode(params)}"
        headers = await self._pre_headers(final_uri)
        return await self.request(
            method="GET", url=f"{self._host}{final_uri}", headers=headers
        )

    async def post(self, uri: str, data: dict, **kwargs) -> Dict:
        """
        POST请求，对请求头签名
        Args:
            uri: 请求路由
            data: 请求体参数

        Returns:

        """
        headers = await self._pre_headers(uri, data)
        json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return await self.request(
            method="POST",
            url=f"{self._host}{uri}",
            data=json_str,
            headers=headers,
            **kwargs,
        )

    async def get_video_play_url(self, video_id: str, note_id: str = "") -> Optional[str]:
        """
        获取真实的视频流播放URL（非BD链接）
        Args:
            video_id: 视频ID（origin_video_key）
            note_id: 笔记ID（可选，用于日志）

        Returns:
            真实的视频流URL，例如: http://sns-video-hs.xhscdn.com/stream/.../xxx.mp4
        """
        uri = "/api/sns/v1/resource/video/play"
        data = {
            "video_id": video_id,
            "source": "pc"
        }

        try:
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] ========== START ==========")
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] Fetching real video URL")
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] video_id: {video_id}")
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] note_id: {note_id}")
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] Calling API: {uri}")

            res = await self.post(uri, data)

            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] API Response: {res}")

            if res and res.get("data"):
                video_data = res["data"].get("video", {})
                stream_list = video_data.get("stream", [])

                utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] Found {len(stream_list)} stream(s)")

                if stream_list:
                    # 优先获取高清视频（按高度排序）
                    stream_list_sorted = sorted(stream_list, key=lambda x: x.get("height", 0), reverse=True)
                    best_stream = stream_list_sorted[0]
                    real_url = best_stream.get("url", "")

                    utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] Best stream: {best_stream}")

                    if real_url:
                        utils.logger.info(
                            f"[XiaoHongShuClient.get_video_play_url] ✓ SUCCESS! Got real video URL: {real_url} "
                            f"(resolution: {best_stream.get('width')}x{best_stream.get('height')})"
                        )
                        return real_url
                    else:
                        utils.logger.warning(f"[XiaoHongShuClient.get_video_play_url] Stream found but URL is empty")
                else:
                    utils.logger.warning(f"[XiaoHongShuClient.get_video_play_url] No streams in response")
            else:
                utils.logger.warning(f"[XiaoHongShuClient.get_video_play_url] Response data is empty or invalid")

            utils.logger.warning(
                f"[XiaoHongShuClient.get_video_play_url] ✗ Failed to get real video URL, using fallback")
            # 返回降级BD链接
            fallback_url = f"http://sns-video-bd.xhscdn.com/{video_id}"
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] ========== END (FALLBACK) ==========")
            return fallback_url

        except Exception as e:
            utils.logger.error(f"[XiaoHongShuClient.get_video_play_url] ✗ EXCEPTION occurred: {e}")
            import traceback
            utils.logger.error(f"[XiaoHongShuClient.get_video_play_url] Traceback: {traceback.format_exc()}")
            # 出错时返回BD链接作为降级
            fallback_url = f"http://sns-video-bd.xhscdn.com/{video_id}"
            utils.logger.info(f"[XiaoHongShuClient.get_video_play_url] ========== END (EXCEPTION) ==========")
            return fallback_url

    async def get_note_media(self, url: str) -> Union[bytes, None]:
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            try:
                response = await client.request("GET", url, timeout=self.timeout)
                response.raise_for_status()
                if not response.reason_phrase == "OK":
                    utils.logger.error(
                        f"[XiaoHongShuClient.get_note_media] request {url} err, res:{response.text}"
                    )
                    return None
                else:
                    return response.content
            except (
                    httpx.HTTPError
            ) as exc:  # some wrong when call httpx.request method, such as connection error, client error, server error or response status code is not 2xx
                utils.logger.error(
                    f"[XiaoHongShuClient.get_aweme_media] {exc.__class__.__name__} for {exc.request.url} - {exc}"
                )  # 保留原始异常类型名称，以便开发者调试
                return None

    async def pong(self) -> bool:
        """
        用于检查登录态是否失效了
        Returns:

        """
        """get a note to check if login state is ok"""
        utils.logger.info("[XiaoHongShuClient.pong] Begin to pong xhs...")
        ping_flag = False
        try:
            note_card: Dict = await self.get_note_by_keyword(keyword="小红书")
            if note_card.get("items"):
                ping_flag = True
        except Exception as e:
            utils.logger.error(
                f"[XiaoHongShuClient.pong] Ping xhs failed: {e}, and try to login again..."
            )
            ping_flag = False
        return ping_flag

    async def update_cookies(self, browser_context: BrowserContext):
        """
        API客户端提供的更新cookies方法，一般情况下登录成功后会调用此方法
        Args:
            browser_context: 浏览器上下文对象

        Returns:

        """
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def update_cookies_from_drission(self, page):
        """
        从 DrissionPage 更新 cookies
        Args:
            page: DrissionPage 的 ChromiumPage 对象

        Returns:

        """
        cookies = page.cookies(all_domains=True, all_info=True)
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict
        utils.logger.info("[XiaoHongShuClient.update_cookies_from_drission] Updated cookies from DrissionPage")

    async def get_note_by_keyword(
            self,
            keyword: str,
            search_id: str = get_search_id(),
            page: int = 1,
            page_size: int = 20,
            sort: SearchSortType = SearchSortType.GENERAL,
            note_type: SearchNoteType = SearchNoteType.ALL,
    ) -> Dict:
        """
        根据关键词搜索笔记
        Args:
            keyword: 关键词参数
            page: 分页第几页
            page_size: 分页数据长度
            sort: 搜索结果排序指定
            note_type: 搜索的笔记类型

        Returns:

        """
        uri = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": search_id,
            "sort": sort.value,
            "note_type": note_type.value,
        }
        return await self.post(uri, data)

    async def get_note_by_id(
            self,
            note_id: str,
            xsec_source: str,
            xsec_token: str,
    ) -> Dict:
        """
        获取笔记详情API
        Args:
            note_id:笔记ID
            xsec_source: 渠道来源
            xsec_token: 搜索关键字之后返回的比较列表中返回的token

        Returns:

        """
        if xsec_source == "":
            xsec_source = "pc_search"

        data = {
            "source_note_id": note_id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": 1},
            "xsec_source": xsec_source,
            "xsec_token": xsec_token,
        }
        uri = "/api/sns/web/v1/feed"
        res = await self.post(uri, data)
        if res and res.get("items"):
            res_dict: Dict = res["items"][0]["note_card"]
            return res_dict
        # 爬取频繁了可能会出现有的笔记能有结果有的没有
        utils.logger.error(
            f"[XiaoHongShuClient.get_note_by_id] get note id:{note_id} empty and res:{res}"
        )
        return dict()

    async def get_note_comments(
            self,
            note_id: str,
            xsec_token: str,
            cursor: str = "",
    ) -> Dict:
        """
        获取一级评论的API
        Args:
            note_id: 笔记ID
            xsec_token: 验证token
            cursor: 分页游标

        Returns:

        """
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif",
            "xsec_token": xsec_token,
        }
        return await self.get(uri, params)

    async def get_note_sub_comments(
            self,
            note_id: str,
            root_comment_id: str,
            xsec_token: str,
            num: int = 10,
            cursor: str = "",
    ):
        """
        获取指定父评论下的子评论的API
        Args:
            note_id: 子评论的帖子ID
            root_comment_id: 根评论ID
            xsec_token: 验证token
            num: 分页数量
            cursor: 分页游标

        Returns:

        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": num,
            "cursor": cursor,
            "image_formats": "jpg,webp,avif",
            "top_comment_id": "",
            "xsec_token": xsec_token,
        }
        return await self.get(uri, params)

    async def get_note_all_comments(
            self,
            note_id: str,
            xsec_token: str,
            crawl_interval: float = 1.0,
            callback: Optional[Callable] = None,
            max_count: int = 10,
    ) -> List[Dict]:
        """
        获取指定笔记下的所有一级评论，该方法会一直查找一个帖子下的所有评论信息
        Args:
            note_id: 笔记ID
            xsec_token: 验证token
            crawl_interval: 爬取一次笔记的延迟单位（秒）
            callback: 一次笔记爬取结束后
            max_count: 一次笔记爬取的最大评论数量
        Returns:

        """
        result = []
        comments_has_more = True
        comments_cursor = ""
        while comments_has_more and len(result) < max_count:
            comments_res = await self.get_note_comments(
                note_id=note_id, xsec_token=xsec_token, cursor=comments_cursor
            )
            comments_has_more = comments_res.get("has_more", False)
            comments_cursor = comments_res.get("cursor", "")
            if "comments" not in comments_res:
                utils.logger.info(
                    f"[XiaoHongShuClient.get_note_all_comments] No 'comments' key found in response: {comments_res}"
                )
                break
            comments = comments_res["comments"]
            if len(result) + len(comments) > max_count:
                comments = comments[: max_count - len(result)]
            if callback:
                await callback(note_id, comments)
            await asyncio.sleep(crawl_interval)
            result.extend(comments)
            sub_comments = await self.get_comments_all_sub_comments(
                comments=comments,
                xsec_token=xsec_token,
                crawl_interval=crawl_interval,
                callback=callback,
            )
            result.extend(sub_comments)
        return result

    async def get_comments_all_sub_comments(
            self,
            comments: List[Dict],
            xsec_token: str,
            crawl_interval: float = 1.0,
            callback: Optional[Callable] = None,
    ) -> List[Dict]:
        """
        获取指定一级评论下的所有二级评论, 该方法会一直查找一级评论下的所有二级评论信息
        Args:
            comments: 评论列表
            xsec_token: 验证token
            crawl_interval: 爬取一次评论的延迟单位（秒）
            callback: 一次评论爬取结束后

        Returns:

        """
        if not config.ENABLE_GET_SUB_COMMENTS:
            utils.logger.info(
                f"[XiaoHongShuCrawler.get_comments_all_sub_comments] Crawling sub_comment mode is not enabled"
            )
            return []

        result = []
        for comment in comments:
            note_id = comment.get("note_id")
            sub_comments = comment.get("sub_comments")
            if sub_comments and callback:
                await callback(note_id, sub_comments)

            sub_comment_has_more = comment.get("sub_comment_has_more")
            if not sub_comment_has_more:
                continue

            root_comment_id = comment.get("id")
            sub_comment_cursor = comment.get("sub_comment_cursor")

            while sub_comment_has_more:
                comments_res = await self.get_note_sub_comments(
                    note_id=note_id,
                    root_comment_id=root_comment_id,
                    xsec_token=xsec_token,
                    num=10,
                    cursor=sub_comment_cursor,
                )

                if comments_res is None:
                    utils.logger.info(
                        f"[XiaoHongShuClient.get_comments_all_sub_comments] No response found for note_id: {note_id}"
                    )
                    continue
                sub_comment_has_more = comments_res.get("has_more", False)
                sub_comment_cursor = comments_res.get("cursor", "")
                if "comments" not in comments_res:
                    utils.logger.info(
                        f"[XiaoHongShuClient.get_comments_all_sub_comments] No 'comments' key found in response: {comments_res}"
                    )
                    break
                comments = comments_res["comments"]
                if callback:
                    await callback(note_id, comments)
                await asyncio.sleep(crawl_interval)
                result.extend(comments)
        return result

    async def get_creator_info(
            self, user_id: str, xsec_token: str = "", xsec_source: str = ""
    ) -> Dict:
        """
        通过解析网页版的用户主页HTML，获取用户个人简要信息
        PC端用户主页的网页存在window.__INITIAL_STATE__这个变量上的，解析它即可

        Args:
            user_id: 用户ID
            xsec_token: 验证token (可选,如果URL中包含此参数则传入)
            xsec_source: 渠道来源 (可选,如果URL中包含此参数则传入)

        Returns:
            Dict: 创作者信息
        """
        # 构建URI,如果有xsec参数则添加到URL中
        uri = f"/user/profile/{user_id}"
        if xsec_token and xsec_source:
            uri = f"{uri}?xsec_token={xsec_token}&xsec_source={xsec_source}"

        html_content = await self.request(
            "GET", self._domain + uri, return_response=True, headers=self.headers
        )
        return self._extractor.extract_creator_info_from_html(html_content)

    async def get_notes_by_creator(
            self,
            creator: str,
            cursor: str,
            page_size: int = 30,
            xsec_token: str = "",
            xsec_source: str = "pc_feed",
    ) -> Dict:
        """
        获取博主的笔记
        Args:
            creator: 博主ID
            cursor: 上一页最后一条笔记的ID
            page_size: 分页数据长度
            xsec_token: 验证token
            xsec_source: 渠道来源

        Returns:

        """
        uri = f"/api/sns/web/v1/user_posted?num={page_size}&cursor={cursor}&user_id={creator}&xsec_token={xsec_token}&xsec_source={xsec_source}"
        return await self.get(uri)

    async def get_all_notes_by_creator(
            self,
            user_id: str,
            crawl_interval: float = 1.0,
            callback: Optional[Callable] = None,
            xsec_token: str = "",
            xsec_source: str = "pc_feed",
    ) -> List[Dict]:
        """
        获取指定用户下的所有发过的帖子，该方法会一直查找一个用户下的所有帖子信息
        Args:
            user_id: 用户ID
            crawl_interval: 爬取一次的延迟单位（秒）
            callback: 一次分页爬取结束后的更新回调函数
            xsec_token: 验证token
            xsec_source: 渠道来源

        Returns:

        """
        result = []
        notes_has_more = True
        notes_cursor = ""
        while notes_has_more and len(result) < config.CRAWLER_MAX_NOTES_COUNT:
            notes_res = await self.get_notes_by_creator(user_id, notes_cursor, xsec_token=xsec_token,
                                                        xsec_source=xsec_source)
            if not notes_res:
                utils.logger.error(
                    f"[XiaoHongShuClient.get_notes_by_creator] The current creator may have been banned by xhs, so they cannot access the data."
                )
                break

            notes_has_more = notes_res.get("has_more", False)
            notes_cursor = notes_res.get("cursor", "")
            if "notes" not in notes_res:
                utils.logger.info(
                    f"[XiaoHongShuClient.get_all_notes_by_creator] No 'notes' key found in response: {notes_res}"
                )
                break

            notes = notes_res["notes"]
            utils.logger.info(
                f"[XiaoHongShuClient.get_all_notes_by_creator] got user_id:{user_id} notes len : {len(notes)}"
            )

            remaining = config.CRAWLER_MAX_NOTES_COUNT - len(result)
            if remaining <= 0:
                break

            notes_to_add = notes[:remaining]
            if callback:
                await callback(notes_to_add)

            result.extend(notes_to_add)
            await asyncio.sleep(crawl_interval)

        utils.logger.info(
            f"[XiaoHongShuClient.get_all_notes_by_creator] Finished getting notes for user {user_id}, total: {len(result)}"
        )
        return result

    async def get_note_short_url(self, note_id: str) -> Dict:
        """
        获取笔记的短链接
        Args:
            note_id: 笔记ID

        Returns:

        """
        uri = f"/api/sns/web/short_url"
        data = {"original_url": f"{self._domain}/discovery/item/{note_id}"}
        return await self.post(uri, data=data, return_response=True)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def get_note_by_id_from_html(
            self,
            note_id: str,
            xsec_source: str,
            xsec_token: str,
            enable_cookie: bool = False,
    ) -> Optional[Dict]:
        """
        通过解析网页版的笔记详情页HTML，获取笔记详情, 该接口可能会出现失败的情况，这里尝试重试3次
        copy from https://github.com/ReaJason/xhs/blob/eb1c5a0213f6fbb592f0a2897ee552847c69ea2d/xhs/core.py#L217-L259
        thanks for ReaJason
        Args:
            note_id:
            xsec_source:
            xsec_token:
            enable_cookie:

        Returns:

        """
        url = (
                "https://www.xiaohongshu.com/explore/"
                + note_id
                + f"?xsec_token={xsec_token}&xsec_source={xsec_source}"
        )
        copy_headers = self.headers.copy()
        if not enable_cookie:
            del copy_headers["Cookie"]

        html = await self.request(
            method="GET", url=url, return_response=True, headers=copy_headers
        )

        return self._extractor.extract_note_detail_from_html(note_id, html)
