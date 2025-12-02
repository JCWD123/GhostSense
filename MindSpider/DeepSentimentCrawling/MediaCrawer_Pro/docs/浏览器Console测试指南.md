# 🌐 浏览器Console测试指南

## ✅ 问题已解决

我已经修复了CORS问题并添加了通用的 `/sign` 路由。

---

## 🚀 使用步骤

### 第1步：重启签名服务

```bash
# 停止旧服务（Ctrl+C）
# 然后重新启动

cd signature-service
npm start

# 应该看到：
# Server listening at http://[::]:3000
# 或
# Server listening at http://localhost:3000
```

**验证服务运行**：
```bash
# 在另一个终端测试
curl http://localhost:3000/health

# 应该返回：
# {"code":0,"message":"MediaCrawer Pro Signature Service is running",...}
```

---

### 第2步：在小红书网站打开Console

```
1. 打开 https://www.xiaohongshu.com
2. 按 F12 打开开发者工具
3. 切换到 "Console" 标签
```

---

### 第3步：执行测试代码

#### 完整测试代码（复制粘贴）

```javascript
// ========================================
// 小红书API完整测试（包含签名）
// ========================================

console.log('🔍 开始测试小红书API...\n');

// 1. 获取Cookie中的a1值
const cookies = document.cookie.split(';').reduce((acc, cookie) => {
  const [key, value] = cookie.trim().split('=');
  acc[key] = value;
  return acc;
}, {});

const a1 = cookies.a1;
console.log('✅ a1 Cookie:', a1);

if (!a1) {
  console.error('❌ 错误：未找到a1 Cookie，请先登录小红书');
} else {
  // 2. 获取签名
  console.log('\n📝 步骤1：获取签名...');
  
  fetch('http://localhost:3000/sign', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      url: '/api/sns/web/v1/search/notes',
      method: 'POST',
      data: {
        keyword: '测试',
        page: 1,
        page_size: 10,
        search_id: '',
        sort: 'general',
        note_type: 0
      },
      a1: a1
    })
  })
  .then(res => res.json())
  .then(signData => {
    console.log('✅ 签名获取成功:', signData);
    
    if (signData.code === 0) {
      const { 'x-s': xs, 'x-t': xt } = signData.data;
      console.log('   x-s:', xs);
      console.log('   x-t:', xt);
      
      // 3. 使用签名调用小红书API
      console.log('\n📡 步骤2：调用小红书API...');
      
      return fetch('https://edith.xiaohongshu.com/api/sns/web/v1/search/notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-s': xs,
          'x-t': xt
        },
        body: JSON.stringify({
          keyword: '测试',
          page: 1,
          page_size: 10,
          search_id: '',
          sort: 'general',
          note_type: 0
        }),
        credentials: 'include'
      })
      .then(res => {
        console.log('✅ API响应状态:', res.status);
        return res.json();
      })
      .then(data => {
        console.log('✅ API响应数据:', data);
        
        if (data.success && data.data && data.data.items) {
          console.log(`\n🎉 成功！搜索到 ${data.data.items.length} 条笔记`);
          console.log('前3条笔记标题:');
          data.data.items.slice(0, 3).forEach((item, index) => {
            console.log(`   ${index + 1}. ${item.note_card?.display_title || '无标题'}`);
          });
        } else {
          console.warn('⚠️ API返回数据但可能有问题:', data);
        }
      });
    } else {
      console.error('❌ 签名获取失败:', signData.message);
    }
  })
  .catch(error => {
    console.error('❌ 错误:', error);
    console.error('\n可能的原因:');
    console.error('1. 签名服务未启动（运行: cd signature-service && npm start）');
    console.error('2. 端口被占用（检查3000端口）');
    console.error('3. Cookie已失效（重新登录小红书）');
  });
}

console.log('\n⏳ 请等待...');
```

---

### 预期输出

#### ✅ 成功情况

```
🔍 开始测试小红书API...

✅ a1 Cookie: 19a92737f1ceciaeebuhrkxyur39uxnus50ph3n8e50000209062

📝 步骤1：获取签名...
✅ 签名获取成功: {code: 0, message: 'success', data: {...}}
   x-s: XYS_2UQhPsHCH0c1Pjh9HjIj2erjwjQhyoPTqBPT49pj...
   x-t: 1763519646469

📡 步骤2：调用小红书API...
✅ API响应状态: 200
✅ API响应数据: {success: true, data: {...}}

🎉 成功！搜索到 20 条笔记
前3条笔记标题:
   1. GPT降智恢复指南
   2. 如何高效使用ChatGPT
   3. AI工具推荐
```

---

#### ❌ 失败情况及解决方案

**错误1：CORS错误**
```
❌ Access to fetch at 'http://localhost:3000/sign' from origin 'https://www.xiaohongshu.com' 
   has been blocked by CORS policy
```

**解决方案**：
```bash
# 确保签名服务已重启（新代码包含CORS支持）
cd signature-service
npm start
```

---

**错误2：连接被拒绝**
```
❌ Failed to fetch
   TypeError: NetworkError when attempting to fetch resource
```

**解决方案**：
```bash
# 检查签名服务是否运行
curl http://localhost:3000/health

# 如果失败，启动服务
cd signature-service
npm start
```

---

**错误3：未找到a1 Cookie**
```
❌ 错误：未找到a1 Cookie，请先登录小红书
```

**解决方案**：
```
1. 确保已登录小红书
2. 刷新页面
3. 重新执行测试代码
```

---

**错误4：406 Not Acceptable**
```
✅ API响应状态: 406
```

**可能原因**：
1. Cookie已失效 → 重新登录
2. 签名不正确 → 检查签名服务
3. 请求被风控 → 降低请求频率

---

## 📊 CORS配置说明

### 什么是CORS？

**CORS（Cross-Origin Resource Sharing）**：跨域资源共享

```
同源策略：
https://www.xiaohongshu.com  ← 你在这里
    ↓ 请求
http://localhost:3000        ← 签名服务

不同的：
- 协议（https vs http）
- 域名（xiaohongshu.com vs localhost）
- 端口（443 vs 3000）

结果：浏览器阻止请求（安全措施）
```

---

### 签名服务的CORS配置

```javascript
// signature-service/src/server.js

// 处理跨域请求
fastify.addHook('onRequest', (request, reply, done) => {
  // ⭐ 允许任何域名访问
  reply.header('Access-Control-Allow-Origin', '*');
  
  // ⭐ 允许的HTTP方法
  reply.header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  
  // ⭐ 允许的请求头
  reply.header('Access-Control-Allow-Headers', 'Content-Type,Authorization');
  
  // ⭐ 预检请求缓存时间（10分钟）
  reply.header('Access-Control-Max-Age', '600');

  // ⭐ 处理OPTIONS预检请求
  if (request.method === 'OPTIONS') {
    reply.code(204).send();
    return;
  }

  done();
});
```

**配置说明**：
- `Access-Control-Allow-Origin: *` - 允许所有来源
- `Access-Control-Allow-Methods` - 允许的HTTP方法
- `Access-Control-Allow-Headers` - 允许的请求头
- OPTIONS预检请求处理 - 浏览器会先发送OPTIONS请求检查权限

---

## 🔧 高级用法

### 测试不同关键词

```javascript
// 修改关键词
const keyword = '你想搜索的内容';  // ← 修改这里

// 然后执行完整测试代码
```

---

### 获取更多结果

```javascript
// 修改分页参数
const searchParams = {
  keyword: '测试',
  page: 1,        // ← 第几页
  page_size: 20,  // ← 每页数量（最大20）
  search_id: '',
  sort: 'general',
  note_type: 0
};
```

---

### 保存结果到变量

```javascript
// 使用async/await版本
let searchResults;

(async () => {
  // ... 完整测试代码 ...
  searchResults = data.data.items;
  console.log('结果已保存到变量 searchResults');
})();

// 之后可以使用
console.log(searchResults);
```

---

## ⚠️ 重要提醒

### 1. 仅用于测试

浏览器Console测试仅适合：
- ✅ 快速验证API
- ✅ 调试签名算法
- ✅ 学习理解流程

**生产环境请使用**：
- ✅ 项目中的XHSClient（自动签名）
- ✅ 后端API接口
- ✅ 前端应用

---

### 2. 请求频率

不要频繁请求，避免：
- ❌ 被小红书风控
- ❌ IP被封禁
- ❌ 账号被限制

**建议**：
- ✅ 每次测试间隔3-5秒
- ✅ 一天测试不超过50次
- ✅ 使用项目的自动延迟功能

---

### 3. Cookie安全

- ❌ 不要在公共场合执行（暴露Cookie）
- ❌ 不要分享包含Cookie的代码
- ✅ 测试完成后关闭浏览器
- ✅ 定期更换Cookie

---

## 🎯 总结

### 步骤回顾

```
1. 启动签名服务
   └─> npm start

2. 打开小红书网站
   └─> https://www.xiaohongshu.com

3. 打开Console（F12）
   └─> 粘贴测试代码

4. 观察结果
   └─> 成功 or 失败

5. 如果失败
   └─> 查看错误信息
   └─> 对照解决方案
```

---

### 为什么推荐使用项目而不是Console？

| 对比项 | Console测试 | 项目使用 |
|--------|------------|----------|
| 操作复杂度 | ⚠️ 复杂（多步骤） | ✅ 简单（一键） |
| 自动签名 | ❌ 手动获取 | ✅ 自动添加 |
| 错误处理 | ⚠️ 需要自己判断 | ✅ 完整的错误处理 |
| Cookie管理 | ❌ 手动提取 | ✅ 自动管理 |
| 请求延迟 | ❌ 需要手动控制 | ✅ 自动延迟 |
| 数据保存 | ❌ 需要复制粘贴 | ✅ 自动存储到数据库 |
| 适合场景 | 调试、学习 | 生产使用 |

---

### 推荐的工作流

```
学习阶段:
  Console测试 → 理解原理 → 了解流程

开发阶段:
  项目API → 功能开发 → 业务逻辑

生产阶段:
  前端应用 → 自动化任务 → 数据采集
```

---

## 📚 相关文档

- `docs/Cookie验证与保持指南.md` - Cookie管理
- `docs/签名算法与HTTP方法的关系.md` - 签名原理
- `docs/浏览器抓包教程.md` - 抓包分析
- `docs/API接口修复说明.md` - API变化

---

**最后更新**: 2025-11-19  
**维护者**: AI Assistant







