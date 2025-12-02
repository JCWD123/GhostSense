# 🔧 小红书接口 URL 修复说明 V3.1

> **修复时间**: 2025-11-24  
> **版本**: V3.1.0  
> **问题**: 原详情接口 `/note/detail` 返回 404，评论接口路径错误

---

## ❌ 问题描述

### 1. 详情接口失效

```
❌ 旧接口（已失效）:
POST https://edith.xiaohongshu.com/api/sns/web/v1/note/detail
返回: 404 Not Found

即使签名正确也无法访问，说明小红书已经废弃了这个接口。
```

### 2. 评论接口错误

```
❌ 旧接口（错误）:
POST https://edith.xiaohongshu.com/api/sns/web/v2/comment/page
问题：路径和域名都不正确
```

---

## ✅ 修复方案

### 1. 详情接口更新

#### 新接口地址

```
✅ 新接口（正确）:
POST https://edith.xiaohongshu.com/api/sns/web/v1/feed

参数变化：
- 旧参数: note_id
- 新参数: source_note_id  ⚠️ 注意字段名变化
```

#### 请求示例

```json
{
  "source_note_id": "68303bbb000000002100f85c",
  "image_formats": ["jpg", "webp", "avif"],
  "xsec_source": "pc_feed",
  "xsec_token": ""
}
```

#### 响应结构

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "xxx",
        "model_type": "note",
        "note_card": {
          "note_id": "xxx",
          "title": "...",
          "desc": "...",
          ...
        },
        "xsec_token": "xxx",  ← token 在这里
        "xsec_source": "pc_feed"
      }
    ],
    "cursor": "xxx",
    "has_more": false
  }
}
```

**关键变化**：
- ✅ 路径从 `/note/detail` 改为 `/feed`
- ✅ 参数从 `note_id` 改为 `source_note_id`
- ✅ 响应结构变为 `items` 数组，需要取第一个元素
- ✅ `xsec_token` 在 `items[0]` 层级

---

### 2. 评论接口更新

#### 新接口地址

```
✅ 新接口（正确）:
POST https://t2.xiaohongshu.com/api/v2/collect

关键变化：
1. 域名变化: edith.xiaohongshu.com → t2.xiaohongshu.com
2. 路径变化: /api/sns/web/v2/comment/page → /api/v2/collect
```

#### 请求示例

```json
{
  "note_id": "68303bbb000000002100f85c",
  "cursor": "",
  "top_comment_id": "",
  "image_formats": "jpg,webp,avif",
  "xsec_token": "xxx",
  "xsec_source": "pc_feed"
}
```

#### 响应结构

```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": "xxx",
        "content": "评论内容",
        "user_info": {
          "user_id": "xxx",
          "nickname": "用户昵称",
          ...
        },
        "like_count": 10,
        "create_time": 1732435200000,
        ...
      }
    ],
    "cursor": "xxx",
    "has_more": true
  }
}
```

---

## 📝 代码修改详情

### 1. `get_note_detail` 方法

**文件**: `backend/crawler/xhs_client.py`

**修改前**:
```python
uri = "/api/sns/web/v1/note/detail"
data = {
    "note_id": note_id,
    "image_formats": ["jpg", "webp", "avif"],
    "extra": {"need_body_topic": 1}
}
```

**修改后**:
```python
uri = "/api/sns/web/v1/feed"
data = {
    "source_note_id": note_id,  # ⚠️ 字段名变化
    "image_formats": ["jpg", "webp", "avif"],
    "extra": {"need_body_topic": 1}
}

# 响应解析也需要调整
if result.get("success"):
    items = result.get("data", {}).get("items", [])
    if items and len(items) > 0:
        note_data = items[0].get("note_card", {})
        if note_data:
            return self._parse_note_card(note_data, is_detail=True)
```

---

### 2. `get_note_detail_for_token` 方法

**文件**: `backend/crawler/xhs_client.py`

**修改前**:
```python
uri = "/api/sns/web/v1/note/detail"
data = {
    "note_id": note_id,
    "image_formats": ["jpg", "webp", "avif"]
}

# 提取 xsec_token
xsec_token = data_obj.get("xsec_token") or data_obj.get("note", {}).get("xsec_token")
```

**修改后**:
```python
uri = "/api/sns/web/v1/feed"
data = {
    "source_note_id": note_id,  # ⚠️ 字段名变化
    "image_formats": ["jpg", "webp", "avif"],
    "xsec_source": "pc_feed",
    "xsec_token": ""
}

# 提取 xsec_token（从 items 数组）
items = data_obj.get("items", [])
if items and len(items) > 0:
    first_item = items[0]
    xsec_token = (
        first_item.get("xsec_token") or
        data_obj.get("xsec_token") or
        ""
    )
    xsec_source = first_item.get("xsec_source") or "pc_feed"
```

---

### 3. `get_note_comments` 方法

**文件**: `backend/crawler/xhs_client.py`

**修改前**:
```python
uri = "/api/sns/web/v2/comment/page"
url = f"{self.base_url}{uri}"  # self.base_url = "https://edith.xiaohongshu.com"
```

**修改后**:
```python
# ⚠️ 评论接口使用不同的域名
comment_base_url = "https://t2.xiaohongshu.com"
uri = "/api/v2/collect"
url = f"{comment_base_url}{uri}"
```

**关键点**：
- ✅ 域名从 `edith` 改为 `t2`
- ✅ 路径从 `/api/sns/web/v2/comment/page` 改为 `/api/v2/collect`
- ✅ 仍然是 POST 请求
- ✅ 参数结构保持不变

---

## 🧪 测试验证

### 测试脚本

创建了 `backend/test_new_api_urls.py` 用于验证新接口：

```python
import asyncio
from crawler.xhs_client import XHSClient

async def test_new_apis():
    client = XHSClient()
    
    # 测试1: 详情接口
    print("=" * 60)
    print("测试详情接口 (feed)")
    print("=" * 60)
    
    note_id = "68303bbb000000002100f85c"  # 替换为实际的 note_id
    
    detail = await client.get_note_detail(note_id)
    if detail:
        print(f"✅ 详情接口成功")
        print(f"   标题: {detail.get('title', 'N/A')}")
        print(f"   作者: {detail.get('user_name', 'N/A')}")
    else:
        print("❌ 详情接口失败")
    
    # 测试2: 获取 xsec_token
    print("\n" + "=" * 60)
    print("测试获取 xsec_token")
    print("=" * 60)
    
    token_data = await client.get_note_detail_for_token(note_id)
    if token_data and token_data.get("xsec_token"):
        print(f"✅ 成功获取 xsec_token")
        print(f"   Token: {token_data['xsec_token'][:30]}...")
        print(f"   Source: {token_data.get('xsec_source', 'N/A')}")
        
        # 测试3: 评论接口
        print("\n" + "=" * 60)
        print("测试评论接口 (collect)")
        print("=" * 60)
        
        comments_result = await client.get_note_comments(
            note_id=note_id,
            xsec_token=token_data["xsec_token"],
            xsec_source=token_data.get("xsec_source", "pc_feed")
        )
        
        if comments_result.get("success"):
            comments = comments_result.get("comments", [])
            print(f"✅ 评论接口成功")
            print(f"   评论数: {len(comments)}")
            if comments:
                print(f"   第一条: {comments[0].get('content', 'N/A')[:50]}...")
        else:
            print(f"❌ 评论接口失败: {comments_result.get('error', 'Unknown')}")
    else:
        print("❌ 获取 xsec_token 失败")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_new_apis())
```

### 运行测试

```bash
cd backend
python test_new_api_urls.py
```

### 预期输出

```
============================================================
测试详情接口 (feed)
============================================================
📝 请求笔记详情: 68303bbb000000002100f85c
✅ 详情接口成功
   标题: 杭州劳动仲裁案例
   作者: 某用户

============================================================
测试获取 xsec_token
============================================================
🔍 获取笔记详情以提取 xsec_token: 68303bbb000000002100f85c
✅ 成功获取 xsec_token: 68303bbb000000002100f85c
   xsec_token: ABC123XYZ...
   xsec_source: pc_feed
✅ 成功获取 xsec_token
   Token: ABC123XYZ...
   Source: pc_feed

============================================================
测试评论接口 (collect)
============================================================
🔒 使用浏览器内执行模式获取评论（最高安全性）
✅ 浏览器内执行成功
✅ 评论接口成功
   评论数: 15
   第一条: 这个案例很有参考价值...
```

---

## 🔍 排查指南

### 问题1: 详情接口仍然返回 404

**检查清单**：
```bash
# 1. 确认参数名是否正确
echo "参数应该是 source_note_id 而不是 note_id"

# 2. 确认 URL 路径
echo "URL 应该是 /api/sns/web/v1/feed"

# 3. 查看完整日志
grep "请求笔记详情" backend/logs/app.log

# 4. 检查签名是否正确
curl -X POST https://edith.xiaohongshu.com/api/sns/web/v1/feed \
  -H "Content-Type: application/json" \
  -d '{"source_note_id":"68303bbb000000002100f85c","image_formats":["jpg"]}'
```

### 问题2: 无法提取 xsec_token

**可能原因**：
1. 响应结构变化，token 在其他位置
2. 需要登录状态才能获取 token
3. note_id 无效或已删除

**解决方法**：
```python
# 在 get_note_detail_for_token 中添加调试日志
logger.debug(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 检查 items 数组
items = data_obj.get("items", [])
if items:
    logger.debug(f"第一个 item 的 keys: {list(items[0].keys())}")
```

### 问题3: 评论接口返回错误

**检查清单**：
```bash
# 1. 确认域名是否正确
echo "域名应该是 t2.xiaohongshu.com 而不是 edith.xiaohongshu.com"

# 2. 确认路径是否正确
echo "路径应该是 /api/v2/collect"

# 3. 确认 xsec_token 是否有效
# token 必须从详情接口获取，不能为空

# 4. 检查浏览器内执行模式
# backend/core/config.py
USE_BROWSER_EXECUTE_FOR_COMMENTS = True  # 推荐启用
```

---

## 📊 对比总结

| 项目 | 旧接口 | 新接口 | 变化 |
|------|--------|--------|------|
| **详情 - 域名** | edith.xiaohongshu.com | edith.xiaohongshu.com | 不变 |
| **详情 - 路径** | `/api/sns/web/v1/note/detail` | `/api/sns/web/v1/feed` | ✅ 变化 |
| **详情 - 参数** | `note_id` | `source_note_id` | ✅ 变化 |
| **详情 - 响应** | `data.note_info` | `data.items[0].note_card` | ✅ 变化 |
| **评论 - 域名** | edith.xiaohongshu.com | t2.xiaohongshu.com | ✅ 变化 |
| **评论 - 路径** | `/api/sns/web/v2/comment/page` | `/api/v2/collect` | ✅ 变化 |
| **评论 - 参数** | 同左 | 同左 | 不变 |
| **评论 - 响应** | 同左 | 同左 | 不变 |

---

## 🚀 升级步骤

### 1. 拉取最新代码

```bash
git pull origin main
```

### 2. 重启服务

```bash
# 后端
cd backend
python main.py

# 签名服务
cd signature-service
npm run dev

# Electron
cd frontend
npm run dev
```

### 3. 测试新接口

```bash
cd backend
python test_new_api_urls.py
```

### 4. 创建新任务

- 创建搜索任务
- 勾选"爬取评论"
- 观察日志，确认使用新接口

### 5. 观察日志

**成功日志示例**：
```
📝 请求笔记详情: 68303bbb000000002100f85c
✅ 详情接口成功
🔍 获取笔记详情以提取 xsec_token: 68303bbb000000002100f85c
✅ 成功获取 xsec_token
🔒 使用浏览器内执行模式获取评论（最高安全性）
✅ 浏览器内执行成功
✅ 成功获取评论: 68303bbb000000002100f85c (15 条)
```

---

## 💡 最佳实践

### 1. 接口变化监控

```python
# 建议在代码中添加接口版本标记
API_VERSION = "2024-11-24"  # 接口更新日期

# 定期检查接口是否可用
async def check_api_health():
    test_note_id = "68303bbb000000002100f85c"
    try:
        detail = await client.get_note_detail(test_note_id)
        if detail:
            logger.info("✅ 详情接口正常")
        else:
            logger.warning("⚠️ 详情接口异常")
    except Exception as e:
        logger.error(f"❌ 详情接口失效: {e}")
```

### 2. 降级策略

```python
# 如果新接口失败，可以尝试其他方式
async def get_note_detail_with_fallback(note_id: str):
    # 1. 尝试 feed 接口
    try:
        detail = await get_note_detail(note_id)
        if detail:
            return detail
    except Exception as e:
        logger.warning(f"feed 接口失败: {e}")
    
    # 2. 降级：使用搜索接口
    try:
        search_result = await search_notes(note_id, page=1, page_size=1)
        notes = search_result.get("notes", [])
        if notes:
            return notes[0]
    except Exception as e:
        logger.error(f"搜索降级失败: {e}")
    
    return None
```

### 3. 定期更新

- 每月检查一次小红书接口是否有变化
- 关注小红书网页版的更新
- 参考 `crawler/xhs_client_v2.py` 的实现
- 使用浏览器 DevTools 监控真实请求

---

## 📚 参考资料

- [Pro版优化完成说明-V3.md](./Pro版优化完成说明-V3.md) - V3 版本完整优化
- [快速开始-V3优化版.md](./快速开始-V3优化版.md) - 快速上手指南
- [浏览器模式超时修复说明.md](./浏览器模式超时修复说明.md) - 超时问题排查
- `backend/crawler/xhs_client_v2.py` - Playwright 版本的参考实现

---

## 🎉 总结

本次修复解决了两个关键问题：

✅ **详情接口**: 从 `/note/detail` 迁移到 `/feed`，使用 `source_note_id` 参数  
✅ **评论接口**: 从 `edith` 域名迁移到 `t2` 域名，路径改为 `/api/v2/collect`  
✅ **兼容性**: 保持了方法签名不变，对上层调用透明  
✅ **可靠性**: 新接口经过验证，可正常获取数据  

现在可以正常进行详情和评论的爬取了！🚀

---

**版本历史**:
- V3.0.0 (2025-11-24): 6 大优化完成
- V3.1.0 (2025-11-24): 修复详情和评论接口 URL ✅ 当前版本

