#!/usr/bin/env python3
"""
快速检查Cookie是否完整

用法：
    python check_cookie.py
"""

# 从 test_xs_common_needed.py 导入的Cookie
from test_xs_common_needed import COOKIE_STRING

# 必需字段
REQUIRED_FIELDS = [
    "a1",
    "webId",
    "web_session",  # 最关键！HttpOnly
    "xsecappid",
    "websectiga",
    "sec_poison_id",
]

# 推荐字段
RECOMMENDED_FIELDS = [
    "gid",
    "abRequestId",
    "acw_tc",
]

print("=" * 80)
print("🍪 Cookie 完整性检查")
print("=" * 80)

print(f"\n📊 Cookie 长度: {len(COOKIE_STRING)} 字符")
print(f"📊 Cookie 字段数: {len(COOKIE_STRING.split(';'))} 个\n")

# 检查必需字段
print("✅ 必需字段检查:")
missing_required = []
for field in REQUIRED_FIELDS:
    if f"{field}=" in COOKIE_STRING:
        # 提取值
        value = ""
        for kv in COOKIE_STRING.split(";"):
            kv = kv.strip()
            if kv.startswith(f"{field}="):
                value = kv.split("=", 1)[1]
                break
        
        # 截断显示
        display_value = value[:40] + "..." if len(value) > 40 else value
        print(f"  ✅ {field:<20} = {display_value}")
    else:
        print(f"  ❌ {field:<20} 缺失！")
        missing_required.append(field)

# 检查推荐字段
print("\n📝 推荐字段检查:")
for field in RECOMMENDED_FIELDS:
    if f"{field}=" in COOKIE_STRING:
        value = ""
        for kv in COOKIE_STRING.split(";"):
            kv = kv.strip()
            if kv.startswith(f"{field}="):
                value = kv.split("=", 1)[1]
                break
        display_value = value[:40] + "..." if len(value) > 40 else value
        print(f"  ✅ {field:<20} = {display_value}")
    else:
        print(f"  ⚠️  {field:<20} 未找到（非必需）")

# 结论
print("\n" + "=" * 80)
print("📊 检查结果")
print("=" * 80)

if not missing_required:
    print("\n✅ Cookie 完整！包含所有必需字段。")
    print("\n✅ 可以进行API测试。")
    print("\n🔍 如果API仍返回0条结果，可能原因：")
    print("  1. Cookie已过期（重新登录获取）")
    print("  2. 缺少 x-s-common 或其他请求头")
    print("  3. IP被风控（使用代理）")
    print("  4. traceid 格式不真实")
else:
    print(f"\n❌ Cookie 不完整！缺少 {len(missing_required)} 个必需字段：")
    for field in missing_required:
        print(f"  - {field}")
    
    print("\n📖 获取完整Cookie的方法：")
    print("  1. 打开 https://www.xiaohongshu.com")
    print("  2. 确保已登录")
    print("  3. F12 → Network → 搜索任意关键词")
    print("  4. 找到 POST .../search/notes 请求")
    print("  5. Headers → Request Headers → Cookie → 右键复制")
    print("\n📖 详细教程：docs/从浏览器获取真实请求头.md")

print("\n" + "=" * 80)







