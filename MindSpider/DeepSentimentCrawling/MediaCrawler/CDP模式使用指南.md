# DrissionPage CDP模式使用指南 (外挂浏览器模式)

## 🎯 什么是CDP模式?

CDP (Chrome DevTools Protocol) 模式让程序"外挂"连接到你手动打开的Chrome浏览器:

**工作流程:**
```
你手动打开Chrome → 手动登录小红书 → 程序连接这个浏览器 → 开始爬取
```

## ⭐ CDP模式的优势

✅ **不带 WebDriver 特征** - 使用真实浏览器环境  
✅ **不带 Playwright Runtime** - 不会被检测  
✅ **不改指纹** - 使用你本机的真实浏览器指纹  
✅ **不注入脚本** - 只通过 CDP 协议通信  
✅ **风控触发概率最低** - 和手动操作几乎无异  

---

## 📋 完整使用步骤

### 步骤0: 配置文件

确认 `config/base_config.py` 中的配置:

```python
# 启用DrissionPage
USE_DRISSION_PAGE = True

# ⭐ 关键配置:启用外挂模式
DRISSION_ATTACH_TO_BROWSER = True
DRISSION_REMOTE_DEBUG_HOST = "127.0.0.1"
DRISSION_REMOTE_DEBUG_PORT = 9222

# 浏览器路径
DRISSION_BROWSER_PATH = "/usr/bin/google-chrome-stable"
```

### 步骤1: 手动启动Chrome浏览器

打开**第一个终端窗口**,执行:

```bash
/usr/bin/google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug_profile
```

**参数说明:**
- `--remote-debugging-port=9222`: 开启端口,让程序可以连接
- `--user-data-dir=/tmp/chrome_debug_profile`: 独立配置文件夹

**验证:** 访问 http://localhost:9222/json 能看到JSON数组 ✅

### 步骤2: 手动登录小红书

在刚才打开的Chrome中:

1. 访问 https://www.xiaohongshu.com
2. 点击登录按钮
3. 扫码登录
4. 确认登录成功

⚠️ **保持浏览器窗口开着!**

### 步骤3: 运行爬虫

打开**第二个终端窗口**:

```bash
cd /mnt/c/Users/HP/Desktop/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler
source ~/BettaFish/bin/activate
python main.py --platform xhs --lt qrcode --type search
```

### 步骤4: 观察运行

正常日志:
```
[XiaoHongShuCrawler] 通过 CDP 连接到已运行浏览器
[XiaoHongShuCrawler] 将连接到远程调试浏览器: 127.0.0.1:9222
[XiaoHongShuCrawler] 检测到登录成功,继续执行任务。
```

如果未登录,会提示:
```
[XiaoHongShuCrawler] 请在已连接的浏览器窗口中手动完成登录,程序将在后台检测登录状态(剩余 180s)
```

此时在浏览器中完成登录即可。

---

## 🚀 一键启动脚本

创建文件 `start_cdp.sh`:

```bash
#!/bin/bash

echo "===== DrissionPage CDP模式启动 ====="

# 检查端口
if lsof -Pi :9222 -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ Chrome已在9222端口运行"
else
    echo "→ 启动Chrome..."
    /usr/bin/google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug_profile &
    sleep 3
fi

echo ""
echo "请在浏览器中:"
echo "1. 访问 https://www.xiaohongshu.com"
echo "2. 扫码登录"
echo "3. 确认登录成功"
echo ""
echo "完成后按任意键继续..."
read -n 1

echo ""
echo "→ 启动爬虫..."
cd /mnt/c/Users/HP/Desktop/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler
source ~/BettaFish/bin/activate
python main.py --platform xhs --lt qrcode --type search
