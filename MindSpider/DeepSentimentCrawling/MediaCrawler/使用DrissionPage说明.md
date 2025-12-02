# 使用 DrissionPage 爬取小红书说明

## 📝 简介

DrissionPage 是一个强大的 Python 网页自动化工具，相比 Playwright 有以下优势：

- ✅ **不基于 webdriver**，更难被检测
- ✅ **运行速度更快**
- ✅ **语法简洁优雅**，对新手友好
- ✅ **可直接使用已打开的浏览器**
- ✅ **支持跨 iframe 操作**
- ✅ **内置无数人性化设计**

官方仓库：https://github.com/g1879/DrissionPage

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install DrissionPage>=4.0.0
```

或者使用项目的 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 配置启用

修改 `config/base_config.py`：

```python
# 启用 DrissionPage 模式
USE_DRISSION_PAGE = True

# 其他配置保持不变
PLATFORM = "xhs"
KEYWORDS = "体测猝死"
LOGIN_TYPE = "qrcode"
CRAWLER_TYPE = "search"
HEADLESS = False  # 建议设置为 False，方便调试
```

### 3. 运行爬虫

```bash
python main.py --platform xhs --lt qrcode --type search
```

---

## 🔧 配置说明

### DrissionPage 特定配置

```python
# 在 config/base_config.py 中

# 是否使用 DrissionPage（仅支持小红书平台）
USE_DRISSION_PAGE = True  # 设置为 True 启用

# 是否无头模式（建议设为 False）
HEADLESS = False

# 登录方式
LOGIN_TYPE = "qrcode"  # 支持 qrcode | phone | cookie
```

---

## 🆚 DrissionPage vs Playwright

| 特性 | DrissionPage | Playwright |
|------|-------------|-----------|
| 反检测能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 运行速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 语法简洁性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 稳定性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 社区支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 💡 何时使用 DrissionPage

### ✅ 推荐使用场景

1. **账号被检测到异常**
   ```
   错误信息：检测到账号异常，请稍后重启试试
   解决方案：启用 USE_DRISSION_PAGE = True
   ```

2. **遇到 Verifytype 错误**
   ```
   错误信息：KeyError: 'Verifytype'
   解决方案：已在代码中修复，但建议配合 DrissionPage 使用
   ```

3. **登录二维码找不到**
   ```
   错误信息：Timeout waiting for qrcode
   解决方案：DrissionPage 对元素查找更稳定
   ```

4. **频繁触发验证码**
   ```
   现象：需要频繁滑动验证码
   解决方案：DrissionPage 的反检测能力更强
   ```

### ❌ 不推荐使用场景

1. **需要最高稳定性**
   - Playwright 经过长期验证，更稳定

2. **跨平台爬取**
   - 目前 DrissionPage 只适配了小红书平台

---

## 📖 代码结构

### 新增文件

```
media_platform/xhs/
├── drission_login.py        # 基于 DrissionPage 的登录模块
├── drission_core.py          # 基于 DrissionPage 的核心爬虫
├── client.py                 # 已添加 update_cookies_from_drission 方法
└── 使用DrissionPage说明.md   # 本文档
```

### 核心实现

1. **drission_login.py**
   - 二维码登录：`login_by_qrcode()`
   - 手机号登录：`login_by_mobile()`
   - Cookie 登录：`login_by_cookies()`

2. **drission_core.py**
   - 继承自 `AbstractCrawler`
   - 兼容原有的搜索、详情、创作者三种模式
   - 自动管理浏览器生命周期

3. **main.py**
   - 自动根据 `USE_DRISSION_PAGE` 配置选择爬虫类型

---

## 🐛 常见问题

### Q1: 如何切换回 Playwright？

A: 修改配置文件：

```python
USE_DRISSION_PAGE = False
```

### Q2: DrissionPage 支持无头模式吗？

A: 支持，但建议设为 False：

```python
HEADLESS = False  # 有头模式，方便调试
```

### Q3: 如何查看浏览器操作过程？

A: 设置 `HEADLESS = False`，会打开浏览器窗口展示操作过程。

### Q4: 遇到 "检测到账号异常" 错误怎么办？

A: 尝试以下步骤：

1. 启用 DrissionPage：`USE_DRISSION_PAGE = True`
2. 关闭无头模式：`HEADLESS = False`
3. 删除浏览器缓存：`rm -rf browser_data/xhs_user_data_dir`
4. 重新运行爬虫

### Q5: xpath 语法需要改吗？

A: 不需要！DrissionPage 完全兼容原有的 xpath 语法。

---

## 📚 参考资料

- [DrissionPage 官方文档](https://DrissionPage.cn)
- [DrissionPage GitHub](https://github.com/g1879/DrissionPage)
- [MediaCrawler 原项目](https://github.com/NanmiCoder/MediaCrawler)

---

## 🎯 使用示例

### 示例 1：搜索关键词并爬取

```bash
# 1. 修改配置
vim config/base_config.py
# 设置 USE_DRISSION_PAGE = True
# 设置 KEYWORDS = "体测猝死"

# 2. 运行爬虫
python main.py --platform xhs --lt qrcode --type search

# 3. 扫码登录后自动开始爬取
```

### 示例 2：爬取指定笔记详情

```bash
# 1. 修改配置
vim config/base_config.py
# 设置 USE_DRISSION_PAGE = True
# 设置 CRAWLER_TYPE = "detail"
# 设置 XHS_SPECIFIED_NOTE_LIST

# 2. 运行爬虫
python main.py --platform xhs --lt qrcode --type detail
```

### 示例 3：Cookie 登录

```bash
# 1. 在浏览器中手动登录小红书，获取 Cookie
# 2. 修改配置
vim config/base_config.py
# 设置 USE_DRISSION_PAGE = True
# 设置 LOGIN_TYPE = "cookie"
# 设置 COOKIES = "你的cookie字符串"

# 3. 运行爬虫
python main.py --platform xhs --lt cookie --type search
```

---

## ⚠️ 注意事项

1. **遵守爬虫礼仪**
   - 合理控制并发数：`MAX_CONCURRENCY_NUM = 1`
   - 添加随机延迟避免过于频繁

2. **账号安全**
   - 不要使用主要账号进行爬取
   - 建议使用小号测试

3. **法律合规**
   - 仅用于学习和研究目的
   - 遵守平台的使用条款和 robots.txt
   - 不得用于商业用途

4. **数据保护**
   - 妥善保管爬取的数据
   - 不要公开分享他人隐私信息

---

## 📞 支持

如有问题，请：

1. 查看本文档的常见问题部分
2. 查看 DrissionPage 官方文档
3. 提交 Issue 到项目仓库

---

**祝你爬取顺利！** 🎉

