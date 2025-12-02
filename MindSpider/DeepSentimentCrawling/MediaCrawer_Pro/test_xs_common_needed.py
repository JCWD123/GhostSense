#!/usr/bin/env python3
"""
增强版：补全小红书 Web 端所有关键风控字段（x-b3-traceid / x-xray-traceid）
确保 API 返回真实数据，而不是 0 条或空列表
"""
import asyncio
import httpx
import random
import uuid
from loguru import logger

# 你的 Cookie
COOKIE_STRING = """
abRequestId=d2934dac-d798-5d19-9ef6-a9fc4527fe27; a1=199e3b169bbs36kx94cq4rrb6p7ghvgpd9msa3rtt50000173588; webId=8a849dade1cb0a26b1b1f29450cb9a7a; gid=yjjdqDyj8Sf2yjjdqDyKjjqFDDMqKTCj4SA4699FFDKUWM28kxhkU0888yWq2YY8qifW0y8y; customerClientId=755235804483889; x-user-id-pro.xiaohongshu.com=66795aeb0000000007006fad; x-user-id-ruzhu.xiaohongshu.com=66795aeb0000000007006fad; x-user-id-creator.xiaohongshu.com=684d4c33000000001b02099b; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517566117115826470913mrqpl3mxhpgtycrl; galaxy_creator_session_id=PsmtkxBFSkkhTQbxV6dJ1aiXPTUXPM66x3fq; galaxy.creator.beaker.session.id=1761623918372019715250; xsecappid=xhs-pc-web; webBuild=4.85.2; loadts=1763536498419; web_session=040069b9390f7b3c59cd8626283b4b9f0688fa; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=d128ec37-3740-4599-8f49-b009a36171af; acw_tc=0a0b135b17635383814414076e71b0173cc89eaf089067a7d7a5e29ecec004; unread={%22ub%22:%226915bca800000000040177e9%22,%22ue%22:%22690c06b00000000004006b05%22,%22uc%22:28}
""".strip()

SIGN_URL = "http://localhost:3000/sign"
API_URL = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"


def extract_a1(cookie: str) -> str:
    """提取 a1"""
    for kv in cookie.split(";"):
        kv = kv.strip()
        if kv.startswith("a1="):
            return kv.split("=", 1)[1].strip()
    return ""


def gen_trace_id():
    """x-b3-traceid：16 hex"""
    return ''.join(random.choices("0123456789abcdef", k=16))


def gen_xray_id():
    """x-xray-traceid：32 hex"""
    return uuid.uuid4().hex


async def get_signature(keyword="美食"):
    """从签名服务获取 x-s/x-t"""
    a1 = extract_a1(COOKIE_STRING)

    logger.info("📝 正在获取签名...")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            SIGN_URL,
            json={
                "url": "/api/sns/web/v1/search/notes",
                "method": "POST",
                "data": {
                    "keyword": keyword,
                    "page": 1,
                    "page_size": 10,
                    "sort": "general",
                    "note_type": 0,
                },
                "a1": a1
            },
            timeout=15
        )

        if resp.status_code != 200:
            logger.error(f"❌ 签名服务错误: {resp.status_code}")
            return None

        js = resp.json()
        if js.get("code") != 0:
            logger.error(f"❌ 签名返回异常: {js}")
            return None

        logger.success("✅ 签名成功")
        return js["data"]


async def test_without_xs_common(sign_data, keyword="美食"):
    """美食是否能返回真实搜索结果"""
    logger.info("\n🧪 开始请求（带完整风控字段）...")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",

        "Referer": "https://www.xiaohongshu.com/",
        "Origin": "https://www.xiaohongshu.com",

        # 必须是浏览器 UA
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),

        # Cookie 与浏览器一致
        "Cookie": COOKIE_STRING,

        # 签名
        "x-s": sign_data["x-s"],
        "x-t": str(sign_data["x-t"]),

        # 两个关键防爬字段（最重要）
        "x-b3-traceid": gen_trace_id(),
        "x-xray-traceid": gen_xray_id(),
    }

    payload = {
        "keyword": keyword,
        "page": 1,
        "page_size": 10,
        "sort": "general",
        "note_type": 0
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(API_URL, json=payload, headers=headers, timeout=15)

        logger.info(f"📡 状态码: {resp.status_code}")

        if resp.status_code == 200:
            js = resp.json()
            logger.info(f"响应: {js}")

            if js.get("code") == 0:
                items = js.get("data", {}).get("items", [])
                logger.success(f"🎉 成功返回 {len(items)} 条结果")
                return True, "OK"

            logger.warning("⚠️ API返回 code != 0")
            return False, "API_ERROR"

        if resp.status_code in (401, 403):
            logger.error("❌ Cookie 失效/账号异常")
            return False, "COOKIE_INVALID"

        if resp.status_code in (406, 461):
            logger.warning("⚠️ 风控，需要 x-s-common 或 traceid 伪造更专业")
            return False, "NEED_XS_COMMON"

        logger.error(f"❌ 未知错误: {resp.text}")
        return False, "UNKNOWN"


async def main():
    print("=" * 80)
    print("🔬 小红书 API 美食（增强版）")
    print("=" * 80)

    # 1. 获取签名
    sign_data = await get_signature()
    if not sign_data:
        return

    # 2. 请求 API
    ok, info = await test_without_xs_common(sign_data)

    print("\n" + "=" * 80)
    print("📊 最终结论")
    print("=" * 80)

    if ok:
        print("✅ API 返回真实数据，x-s + x-t + traceid 完全可用！")
    elif info == "COOKIE_INVALID":
        print("❌ Cookie 无效或被封，请更换 Cookie")
    elif info == "NEED_XS_COMMON":
        print("⚠️ 需要 x-s-common 或更真实的 traceid")
    else:
        print("❓ 其他未知问题")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
