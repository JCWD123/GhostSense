"""
测试评论爬取（自动获取 xsec_token）
"""
import asyncio
from loguru import logger
from crawler.xhs_client import XHSClient
from core.database import Database
from services.account_service import AccountService

async def test():
    """测试评论爬取流程"""
    logger.info("╔════════════════════════════════════════╗")
    logger.info("║  测试评论爬取 - xsec_token 自动获取   ║")
    logger.info("╚════════════════════════════════════════╝\n")
    
    # 连接数据库
    db = Database()
    await db.connect()
    
    try:
        # 获取账号
        account_service = AccountService(db)
        account = await account_service.get_available_account("xhs")
        if not account:
            logger.error("❌ 没有可用的小红书账号")
            return
        
        logger.info(f"✅ 使用账号: {account.get('username', 'unknown')}")
        
        # 初始化客户端
        client = XHSClient()
        await client.init_client(
            cookies=account.get("cookies", {}),
            headers=account.get("headers", {})
        )
        
        # 1. 搜索笔记
        logger.info("\n📝 步骤1: 搜索笔记")
        notes = await client.search_notes(keyword="美食", page=1, page_size=1)
        
        if not notes:
            logger.error("❌ 未搜索到笔记")
            return
        
        note = notes[0]
        note_id = note.get("note_id")
        logger.info(f"   找到笔记: {note_id}")
        logger.info(f"   标题: {note.get('title', 'N/A')}")
        
        # 2. 检查笔记中是否有 xsec_token
        xsec_token = note.get("xsec_token", "")
        if xsec_token:
            logger.info(f"   ✅ 笔记已包含 xsec_token: {xsec_token[:30]}...")
        else:
            logger.warning("   ⚠️ 笔记未包含 xsec_token，需要从详情页获取")
        
        # 3. 获取详情页的 xsec_token
        logger.info("\n🔑 步骤2: 获取 xsec_token")
        detail = await client.get_note_detail_for_token(note_id)
        
        if not detail:
            logger.error("❌ 无法获取笔记详情")
            return
        
        xsec_token = detail.get("xsec_token", "")
        xsec_source = detail.get("xsec_source", "pc_search")
        
        if not xsec_token:
            logger.error("❌ 详情页未返回 xsec_token")
            return
        
        logger.success(f"   ✅ 成功获取 xsec_token: {xsec_token[:30]}...")
        logger.info(f"   xsec_source: {xsec_source}")
        
        # 4. 使用 token 获取评论
        logger.info("\n💬 步骤3: 获取评论")
        result = await client.get_note_comments(
            note_id=note_id,
            xsec_token=xsec_token,
            xsec_source=xsec_source
        )
        
        comments = result.get("comments", [])
        logger.success(f"   ✅ 成功获取 {len(comments)} 条评论")
        
        if comments:
            logger.info("\n   📋 评论示例:")
            for i, comment in enumerate(comments[:3], 1):
                logger.info(f"      {i}. {comment.get('user', {}).get('nickname', 'Unknown')}: {comment.get('content', '')[:50]}...")
        
        logger.info("\n✅ 测试完成！所有步骤成功")
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
    
    finally:
        await client.close()
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(test())


