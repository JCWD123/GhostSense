#!/usr/bin/env python3
"""
使用从浏览器抓取的真实请求头测试
"""
import asyncio
import httpx
from loguru import logger

# 从浏览器抓取的完整Cookie
REAL_COOKIE = """
abRequestId=2bcf34b8-02b2-580f-ab56-ef89a36d9697; a1=19a92737f1ceciaeebuhrkxyur39uxnus50ph3n8e50000209062; webId=8eb92737ce4a022d797f34748852a1f5; gid=yj0jJWqYj8MKyj0jJWqWi2qIySdS30ddD7xF8YdTCv7FqU28j7CI7x888J8j8KJ8jJ8jSDiq; websectiga=6169c1e84f393779a5f7de7303038f3b47a78e47be716e7bec57ccce17d45f99; sec_poison_id=306254bc-609d-4161-a516-0cf31f39ebfc; acw_tc=0a0bb1ff17635421075367378e1bb3936fc1a3d4b0c83eb465332210a66603; webBuild=4.86.0; xsecappid=xhs-pc-web; loadts=1763542138313; web_session=040069b9390f7b3c59cdf7cc283b4bf3ec2f02; unread={%22ub%22:%226919ad8b00000000040218f7%22%2C%22ue%22:%22690eadc20000000007033836%22%2C%22uc%22:29}
""".strip()

# 从浏览器抓取的真实请求头
REAL_HEADERS = {
    "x-s-common": "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1Pjh9HjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjHFN0W9N0ZjNsQh+aHCH0rEG/DU+AP780b08n+kGnpSGdpiqfTh2gpUPASM2BEMqALIqBWAJ0YS+/ZIPeZUPeDI+0HjNsQh+jHCHjHVHdW7H0ijHjIj2eWjwjQQPAYUaBzdq9k6qB4Q4fpA8b878FSet9RQzLlTcSiM8/+n4MYP8F8LagY/P9Ql4FpUzfpS2BcI8nT1GFbC/L88JdbFyrSiafp/cDMra7pFLDDAa7+8J7QgabmFz7Qjp0mcwp4fanD68p40+fp8qgzELLbILrDA+9p3JpH9LLI3+LSk+d+DJfpSL98lnLYl49IUqgcMc0mrcDShtMmozBD6qM8FyFSh8o+h4g4U+obFyLSi4nbQz/+SPFlnPrDApSzQcA4SPopFJeQmzBMA/o8Szb+NqM+c4ApQzg8Ayp8FaDRl4AYs4g4fLomD8pzBpFRQ2ezLanSM+Skc47Qc4gcMag8VGLlj87PAqgzhagYSqAbn4FYQy7pTanTQ2npx87+8NM4L89L78p+l4BL6ze4AzB+IygmS8Bp8qDzFaLP98Lzn4AQQzLEAL7bFJBEVL7pwyS8Fag868nTl4e+0n04ApfuF8FSbL7SQyrpotASrpLS92dDFa/YOanS0+Mkc4FbQ4fSe+Bu6qFzP8oP9Lo4naLP78p+D+7+DPbHFaLp9qA+QzFMFpd4panSDqA+AN7+hnDESyp8FGf+p8np8pd4iag8Vqokm+fpDqg4eqBEtqFzn4MmQ2BlFagYyL9RM4FRdpd4Iq7HFyBppN9L9/o8Szbm7zDS987PlqfRAPLzyyLSk+7+xGfRAP94UzDSbPBLALoz9anSjLDRl4FROqgziagYSq7Yc4A4QyrbSpSmFyrSiN7+8qgz/z7b72nMc4FzQ4DS3a/+Q4ezYzMPFnaRSygpFyDSkJgQQzLRALM8F2DQ6zDF6wg8Sy0Sy4DSkzLEo4gzCqdpFJrS94fLALozp/7mN8nS0/d+kagkSanYdqA86+d+L4gzCqop7arS9+9LIpd4fanDM8/8x4gSQcFTA8B8O8Lzn4b+Q2B4A2op74/QfpFQQzpqFaL+dqM8++d+/8aRA8rD98p4M494QcFpGag8kpfbl49zQ2bmfanS68/bT+rMCqFkSp7pFJLSk2dQILo4QJpkS8nz+PBp8pdzI8Mm7nDSh4/FjNsQhwaHCN/LAPAW9+0WUPaIj2erIH0ilwsIj2erlH0ijJfRUJnbVHdF=",
    "x-b3-traceid": "a3d82dbfa1d5c8b4",
    "x-xray-traceid": "cd4da75e053c1b6c9f750e6c0924ad61",
    "x-s": "XYS_2UQhPsHCH0c1Pjh9HjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg98yGLTlLgmBpp8F+bkwt9l1LjR9p7+9qDz0pFMawepnPDTx2bSx/rDUy0bT+FDF8bYiaLLhPgLA8/c7LgSI+bp/LBGAJnQV4ebT4SSaPFY7pop+8SQQwBz1nfRnpDEd4SpicFYnzBR82/mYzL8nL/8DaMmmPrkHaMY/PbSp4pq7Pn8+c9EIqMQCLDkcpnbLP9IIqDT/Jfznnfl0yLLIaSQQyAmOarGROaHVHdWFH0ijJ9Qx8n+FHdF=",
    "x-t": "1763542219809",
}

API_URL = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"


async def test_with_real_headers():
    """使用真实请求头测试"""
    print("=" * 80)
    print("🧪 使用浏览器真实请求头测试")
    print("=" * 80)
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Referer": "https://www.xiaohongshu.com/",
        "Origin": "https://www.xiaohongshu.com",
        "Cookie": REAL_COOKIE,
        **REAL_HEADERS
    }
    
    payload = {
        "keyword": "美食",
        "page": 1,
        "page_size": 20,
        "sort": "general",
        "note_type": 0
    }
    
    logger.info("📝 请求参数:")
    logger.info(f"  - 关键词: {payload['keyword']}")
    logger.info(f"  - 页码: {payload['page']}")
    logger.info(f"  - 每页: {payload['page_size']}")
    
    logger.info("\n🔑 关键请求头:")
    logger.info(f"  - x-s-common: {headers['x-s-common'][:50]}... ({len(headers['x-s-common'])} 字符)")
    logger.info(f"  - x-b3-traceid: {headers['x-b3-traceid']}")
    logger.info(f"  - x-xray-traceid: {headers['x-xray-traceid']}")
    logger.info(f"  - x-s: {headers['x-s'][:50]}...")
    logger.info(f"  - x-t: {headers['x-t']}")
    logger.info(f"  - Cookie: {len(headers['Cookie'])} 字符")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info("\n🚀 发送请求...")
            response = await client.post(API_URL, json=payload, headers=headers, timeout=15)
            
            logger.info(f"📡 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"\n📦 响应数据:")
                logger.info(f"  - code: {data.get('code')}")
                logger.info(f"  - success: {data.get('success')}")
                logger.info(f"  - msg: {data.get('msg')}")
                
                if data.get('success'):
                    items = data.get('data', {}).get('items', [])
                    has_more = data.get('data', {}).get('has_more', False)
                    
                    logger.success(f"\n🎉 成功返回 {len(items)} 条结果！")
                    logger.info(f"  - has_more: {has_more}")
                    
                    if items:
                        logger.info("\n📝 前3条笔记:")
                        for i, item in enumerate(items[:3], 1):
                            note = item.get('note_card', {})
                            logger.info(f"  {i}. {note.get('display_title', 'N/A')}")
                            logger.info(f"     ID: {note.get('note_id', 'N/A')}")
                            logger.info(f"     作者: {note.get('user', {}).get('nickname', 'N/A')}")
                        
                        print("\n" + "=" * 80)
                        print("✅ 测试成功！真实请求头有效！")
                        print("=" * 80)
                        return True
                    else:
                        logger.warning("\n⚠️ 返回0条结果（即使有真实请求头）")
                        logger.warning("可能原因：")
                        logger.warning("  1. Cookie已过期（重新登录）")
                        logger.warning("  2. IP被风控（更换IP）")
                        logger.warning("  3. 请求头已失效（刷新页面重新抓取）")
                        return False
                else:
                    logger.error(f"\n❌ API返回失败: {data}")
                    return False
            else:
                logger.error(f"\n❌ HTTP错误: {response.status_code}")
                logger.error(f"响应: {response.text}")
                return False
                
        except Exception as e:
            logger.exception(f"\n❌ 请求异常: {e}")
            return False


async def main():
    success = await test_with_real_headers()
    
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    if success:
        print("\n✅ 完美！真实请求头可以获取数据！")
        print("\n📝 下一步：")
        print("  1. 分析 x-s-common 的生成逻辑")
        print("  2. 逆向相关JS代码")
        print("  3. 在签名服务中实现 x-s-common")
        print("  4. 更新 traceid 生成算法（去除连字符）")
    else:
        print("\n⚠️ 即使使用真实请求头，仍然返回空数据")
        print("\n可能原因：")
        print("  1. Cookie已过期（请重新登录小红书）")
        print("  2. IP被风控（请更换IP或使用代理）")
        print("  3. 请求头包含时效性字段（x-s, x-t, x-s-common 都有时效性）")
        print("\n💡 建议：")
        print("  - 在浏览器中重新搜索，立即复制新的请求头")
        print("  - 在30秒内运行本脚本")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())







