# 🔐 小红书 x-s-common 逆向实战指南

## 📋 目录

1. [什么是 x-s-common](#什么是-x-s-common)
2. [为什么需要 x-s-common](#为什么需要-x-s-common)
3. [逆向分析步骤](#逆向分析步骤)
4. [实现方案](#实现方案)
5. [测试验证](#测试验证)
6. [常见问题](#常见问题)

---

## 什么是 x-s-common？

### 定义

`x-s-common` 是小红书API请求中的**设备指纹签名**header，用于：

1. **标识客户端环境**：浏览器类型、版本、操作系统等
2. **防止爬虫**：验证请求来自真实的浏览器
3. **风控识别**：检测异常行为

---

## 为什么需要 x-s-common？

###  完整的请求Headers

小红书API需要3个关键headers：

| Header | 作用 | 生成方式 | 有效期 |
|--------|------|----------|--------|
| `x-s` | 请求签名 | 动态生成 | 一次性 |
| `x-t` | 时间戳 | 当前时间 | 一次性 |
| `x-s-common` | 设备指纹 | 相对固定 | 长期有效 |

**目前状态**：
- ✅ `x-s` - 已实现
- ✅ `x-t` - 已实现  
- ❌ `x-s-common` - **需要实现** ← 你在这里

---

## 逆向分析步骤

### 第1步：确认是否真的需要

#### 测试方法

```bash
# 使用curl测试（不带x-s-common）
curl -X POST 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes' \
  -H 'Content-Type: application/json' \
  -H 'x-s: XYS_xxx...' \
  -H 'x-t: 1763536910' \
  -H 'Cookie: a1=xxx; web_session=xxx' \
  -d '{"keyword":"测试","page":1,"page_size":10}' \
  -v
```

**结果判断**：
- ❌ `406 Not Acceptable` → **需要 x-s-common**
- ❌ `461` → **需要 x-s-common**
- ✅ `200 OK` → 不需要，当前签名已足够
- ❌ `401` → Cookie问题
- ❌ `403` → 可能被风控

---

### 第2步：浏览器抓包获取真实值

#### 2.1 打开Chrome DevTools

```
1. 访问 https://www.xiaohongshu.com
2. F12 → Network标签
3. 清空（点击🚫）
4. 在搜索框输入任意关键词，搜索
5. 找到 search/notes 请求
6. 查看 Request Headers
```

#### 2.2 找到 x-s-common

```http
Request Headers:
  x-s: XYS_2UQhPsHCH0c1Pjh9HjIj2erjwjQhyoPTqBPT49pj...
  x-t: 1763536910750
  x-s-common: 2UQAPsHC+aIjqArjqArqrqwYr+rtwYrtqAwz=+0nZ8J/m0ZeZLdHjHjIj2erjwjQhyoPTqBPT49pjw/HVHjIj2erjwjQhyoPTqBPT49pjHjIj2erjwjQhyoPTqBPT49pjHjIj2erjwjQh+0lqeFpZcMkh+0rqrtqArGrMU7qAFH0
  ^^^^^^^^^^^^^ 找到它！
```

**关键信息**：
- 长度：通常100-200字符
- 格式：通常以固定前缀开头（如 `2UQAPsHC`）
- 变化频率：相对固定，不像x-s每次都变

---

### 第3步：分析生成逻辑

#### 3.1 搜索JS文件

在Chrome DevTools中：

```javascript
// Sources标签 → 全局搜索（Ctrl+Shift+F）
// 搜索关键词：
"x-s-common"
"xsCommon"
"x_s_common"
"common"
```

**可能找到的文件**：
- `shield.xxx.js` - 小红书的加密库
- `commons.xxx.js` - 公共库
- `app.xxx.js` - 主应用

---

#### 3.2 定位关键函数

找到类似这样的代码：

```javascript
// 示例1：简单实现
function getXsCommon() {
  var platform = "PC";
  var version = "1.0.0";
  var deviceId = getDeviceId();
  var timestamp = Date.now();
  
  return sign([platform, version, deviceId, timestamp].join("|"));
}

// 示例2：复杂实现
function generateXsCommon(a1, webId) {
  var e = {
    s0: 3,  // 平台类型
    s1: "1.0.0",  // 版本
    x0: "1",  // 某个标识
    x1: getMachineId(),  // 机器ID
    x2: "Mac OS",  // 操作系统
    x3: "xhs-pc-web",  // 应用ID
    x4: "4.44.0",  // 应用版本
    x5: webId,  // WebID
    x6: timestamp(),  // 时间戳
    x7: a1,  // a1 Cookie
    x8: window.screen.width + "x" + window.screen.height,  // 屏幕分辨率
    x9: navigator.userAgent,  // User-Agent
    x10: ""  // 预留
  };
  
  return encodeXsCommon(e);
}

function encodeXsCommon(data) {
  // 1. JSON字符串化
  var jsonStr = JSON.stringify(data);
  
  // 2. Base64编码
  var base64 = btoa(jsonStr);
  
  // 3. 添加前缀
  return "2UQAPsHC+" + base64;
}
```

---

#### 3.3 使用Console Hook拦截

如果找不到源码，用Hook方法：

```javascript
// 在Chrome Console中执行

// Hook XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;

const headers = {};

XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
  if (name.toLowerCase().includes('x-s')) {
    console.log(`捕获Header: ${name} = ${value}`);
    headers[name] = value;
  }
  return originalSetRequestHeader.apply(this, arguments);
};

XMLHttpRequest.prototype.open = function() {
  this.addEventListener('load', function() {
    console.log('请求Headers:', headers);
  });
  return originalOpen.apply(this, arguments);
};

// 然后执行一次搜索，查看Console输出
```

---

#### 3.4 使用Frida Hook（高级）

如果是App端或加密复杂，用Frida：

```python
import frida
import sys

# Frida脚本
script_code = """
Java.perform(function() {
    // 找到XsCommon相关的类
    var XsCommonUtil = Java.use("com.xingin.xhs.shield.XsCommonUtil");
    
    // Hook生成函数
    XsCommonUtil.generate.implementation = function(arg1, arg2) {
        console.log("XsCommon Input:", arg1, arg2);
        var result = this.generate(arg1, arg2);
        console.log("XsCommon Output:", result);
        return result;
    };
});
"""

# 连接设备并注入
device = frida.get_usb_device()
session = device.attach("小红书")  # 替换为实际进程名
script = session.create_script(script_code)
script.load()
sys.stdin.read()
```

---

### 第4步：提取算法

#### 4.1 分析数据结构

根据逆向结果，x-s-common通常包含：

```javascript
{
  "s0": 3,                    // 平台类型（1=iOS, 2=Android, 3=Web）
  "s1": "1.0.0",             // SDK版本
  "x0": "1",                 // 未知标识
  "x1": "19a92737...",       // 从a1提取
  "x2": "Windows",           // 操作系统
  "x3": "xhs-pc-web",        // 应用ID
  "x4": "4.85.2",            // 应用版本
  "x5": "8eb92737...",       // webId
  "x6": 1763536910750,       // 时间戳
  "x7": "zh-CN",             // 语言
  "x8": "1920x1080",         // 屏幕分辨率
  "x9": "GMT+0800",          // 时区
  "x10": "Mozilla/5.0..."    // User-Agent
}
```

#### 4.2 编码算法

常见的编码方式：

**方案A：简单Base64**
```javascript
const data = JSON.stringify(commonData);
const base64 = Buffer.from(data).toString('base64');
const xsCommon = "2UQAPsHC+" + base64;
```

**方案B：自定义编码**
```javascript
function customEncode(data) {
  // 1. JSON序列化
  const jsonStr = JSON.stringify(data);
  
  // 2. 使用密钥加密
  const encrypted = encryptWithKey(jsonStr, SECRET_KEY);
  
  // 3. Base64
  const base64 = Buffer.from(encrypted).toString('base64');
  
  // 4. 添加前缀和校验码
  const checksum = md5(base64).substring(0, 8);
  return `2UQAPsHC+${base64}+${checksum}`;
}
```

---

## 实现方案

### 方案1：完整实现（推荐）

创建 `signature-service/src/platforms/xs_common.js`：

```javascript
/**
 * 小红书 x-s-common 生成器
 */
const crypto = require('crypto');

class XsCommonGenerator {
  constructor(options = {}) {
    this.version = options.version || '1.0.0';
    this.appVersion = options.appVersion || '4.85.2';
  }
  
  /**
   * 生成 x-s-common
   * 
   * @param {Object} params
   * @param {string} params.a1 - a1 Cookie值
   * @param {string} params.webId - webId Cookie值
   * @param {string} params.userAgent - User-Agent
   * @returns {string} x-s-common值
   */
  generate(params) {
    const {
      a1 = '',
      webId = '',
      userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    } = params;
    
    // 1. 构建数据对象
    const commonData = {
      s0: 3,  // Web平台
      s1: this.version,
      x0: "1",
      x1: a1 ? a1.substring(0, 32) : '',
      x2: this.detectOS(userAgent),
      x3: "xhs-pc-web",
      x4: this.appVersion,
      x5: webId || '',
      x6: Date.now(),
      x7: "zh-CN",
      x8: "1920x1080",
      x9: "GMT+0800",
      x10: userAgent.substring(0, 100)
    };
    
    // 2. 编码
    return this.encode(commonData);
  }
  
  /**
   * 编码数据
   */
  encode(data) {
    // JSON序列化
    const jsonStr = JSON.stringify(data);
    
    // Base64编码
    const base64 = Buffer.from(jsonStr).toString('base64');
    
    // 添加前缀（根据实际抓包结果调整）
    return `2UQAPsHC+${base64}`;
  }
  
  /**
   * 从User-Agent检测操作系统
   */
  detectOS(userAgent) {
    if (userAgent.includes('Windows')) return 'Windows';
    if (userAgent.includes('Mac')) return 'Mac OS';
    if (userAgent.includes('Linux')) return 'Linux';
    return 'Unknown';
  }
}

module.exports = { XsCommonGenerator };
```

---

### 方案2：模拟真实浏览器（如果上述不行）

使用Puppeteer或Playwright获取真实x-s-common：

```javascript
// signature-service/src/platforms/xs_common_browser.js

const puppeteer = require('puppeteer');

class XsCommonBrowserGenerator {
  async generate(a1, webId) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // 设置Cookie
    await page.setCookie({
      name: 'a1',
      value: a1,
      domain: '.xiaohongshu.com'
    }, {
      name: 'webId',
      value: webId,
      domain: '.xiaohongshu.com'
    });
    
    // 访问小红书
    await page.goto('https://www.xiaohongshu.com/explore');
    
    // 拦截网络请求，获取x-s-common
    let xsCommon = '';
    
    page.on('request', request => {
      const headers = request.headers();
      if (headers['x-s-common']) {
        xsCommon = headers['x-s-common'];
      }
    });
    
    // 触发搜索请求
    await page.evaluate(() => {
      // 模拟搜索
      fetch('/api/sns/web/v1/search/notes', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({keyword: 'test', page: 1})
      });
    });
    
    // 等待请求完成
    await page.waitForTimeout(2000);
    
    await browser.close();
    
    return xsCommon;
  }
}

module.exports = { XsCommonBrowserGenerator };
```

---

### 集成到签名服务

修改 `signature-service/src/platforms/xhs.js`：

```javascript
const { XsCommonGenerator } = require('./xs_common');

const xsCommonGen = new XsCommonGenerator();

function getSign(url, options = {}) {
  const { method = 'GET', data = null, a1 = '', webId = '' } = options;
  
  // 生成 x-s 和 x-t（已有）
  const xs = /* ... 现有的x-s生成逻辑 ... */;
  const xt = String(Date.now());
  
  // 生成 x-s-common（新增）
  const xsCommon = xsCommonGen.generate({
    a1,
    webId,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  
  return {
    'x-s': xs,
    'x-t': xt,
    'x-s-common': xsCommon  // ← 新增
  };
}
```

---

## 测试验证

### 第1步：单元测试

创建 `signature-service/test/xs_common.test.js`：

```javascript
const { XsCommonGenerator } = require('../src/platforms/xs_common');

const generator = new XsCommonGenerator();

// 测试生成
const result = generator.generate({
  a1: '19a92737f1ceciaeebuhrkxyur39uxnus50ph3n8e50000209062',
  webId: '8eb92737ce4a022d797f34748852a1f5'
});

console.log('生成的 x-s-common:', result);
console.log('长度:', result.length);
console.log('格式:', result.startsWith('2UQAPsHC+') ? '✅' : '❌');
```

---

### 第2步：API测试

```bash
# 完整请求测试
curl -X POST 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes' \
  -H 'Content-Type: application/json' \
  -H 'x-s: XYS_xxx...' \
  -H 'x-t: 1763536910' \
  -H 'x-s-common: 2UQAPsHC+xxx...' \
  -H 'Cookie: a1=xxx; web_session=xxx' \
  -d '{"keyword":"测试","page":1,"page_size":10}' \
  -v
```

**预期结果**：
- ✅ `200 OK` + 返回数据 → 成功！
- ❌ `406` → x-s-common格式/算法有问题
- ❌ `461` → x-s-common过期或无效

---

### 第3步：对比验证

```javascript
// 对比浏览器真实值和生成值

// 真实值（从浏览器抓包）
const realXsCommon = "2UQAPsHC+eyJzMCI6MywiczEiOiIxLjAuMCIsIngwIjoiMSIsIngxIjoiMTlhOTI3MzdmMWNl...";

// 生成值
const generatedXsCommon = generator.generate({a1: 'xxx', webId: 'xxx'});

// 解码对比
const realDecoded = Buffer.from(realXsCommon.substring(9), 'base64').toString();
const genDecoded = Buffer.from(generatedXsCommon.substring(9), 'base64').toString();

console.log('真实值解码:', realDecoded);
console.log('生成值解码:', genDecoded);

// 对比差异
console.log('是否一致:', realDecoded === genDecoded);
```

---

## 常见问题

### Q1：x-s-common 是动态的还是固定的？

**答**：相对固定，但会包含时间戳。

- 固定部分：平台、版本、设备ID、a1、webId
- 动态部分：时间戳
- 有效期：通常24小时或更长

**建议**：
- ✅ 可以缓存一段时间（如1小时）
- ✅ 定期更新（检测到失效时）

---

### Q2：如果算法很复杂怎么办？

**方案A**：使用真实浏览器

```javascript
// 用Puppeteer/Playwright打开真实浏览器
// 让浏览器自己生成x-s-common
// 拦截并返回给Python
```

**方案B**：调用Node.js的原始代码

```javascript
// 如果你逆向到了小红书的原始JS代码
// 可以直接eval执行
const xhsShieldCode = fs.readFileSync('shield.min.js', 'utf8');
eval(xhsShieldCode);
const xsCommon = window.getXsCommon(a1, webId);
```

---

### Q3：406错误一定是因为缺少x-s-common吗？

**不一定**！406可能的原因：

1. ❌ 缺少 x-s-common
2. ❌ x-s签名错误
3. ❌ Cookie失效
4. ❌ User-Agent不对
5. ❌ Content-Type错误
6. ❌ 被风控

**诊断方法**：
```bash
# 逐个添加header测试
curl ... -H 'x-s: xxx' -H 'x-t: xxx'  # 406
curl ... -H 'x-s: xxx' -H 'x-t: xxx' -H 'x-s-common: xxx'  # 200？
```

---

### Q4：目前是否确认需要x-s-common？

**需要实际测试**！

**测试代码**（Python）：

```python
import httpx

url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

# 测试1：不带x-s-common
response1 = httpx.post(
    url,
    json={"keyword": "测试", "page": 1, "page_size": 10},
    headers={
        "x-s": "XYS_xxx...",
        "x-t": "1763536910",
        "Cookie": "a1=xxx; web_session=xxx"
    }
)
print(f"不带x-s-common: {response1.status_code}")

# 测试2：带x-s-common
response2 = httpx.post(
    url,
    json={"keyword": "测试", "page": 1, "page_size": 10},
    headers={
        "x-s": "XYS_xxx...",
        "x-t": "1763536910",
        "x-s-common": "2UQAPsHC+xxx...",  # 从浏览器抓包
        "Cookie": "a1=xxx; web_session=xxx"
    }
)
print(f"带x-s-common: {response2.status_code}")
```

**结果判断**：
- 两个都200 → 不需要x-s-common
- 第一个406，第二个200 → **需要x-s-common**

---

## 📊 总结

### 逆向流程图

```
1. 浏览器抓包
   ↓
2. 找到 x-s-common 真实值
   ↓
3. 搜索JS源码
   ↓
4. 定位生成函数
   ↓
5. 分析数据结构和算法
   ↓
6. Node.js实现
   ↓
7. 测试验证
   ↓
8. 集成到签名服务
```

### 实现优先级

1. **优先**：测试是否真的需要（5分钟）
2. **次要**：浏览器抓包获取真实值（10分钟）
3. **核心**：逆向JS找到生成逻辑（1-3小时）
4. **实现**：Node.js编码实现（30分钟）
5. **测试**：验证是否有效（10分钟）

### 下一步行动

1. **立即**：用curl或Python测试当前签名是否已经够用
2. **如果不够**：浏览器抓包获取真实x-s-common值
3. **然后**：搜索JS源码找生成函数
4. **最后**：一起实现算法！

---

**我们一起加油！** 🚀

如果你已经测试确认需要x-s-common，把：
1. 浏览器抓包的真实x-s-common值
2. 测试的错误信息
3. JS搜索到的相关代码片段

发给我，我们一起分析实现！💪







