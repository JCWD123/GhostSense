# 小红书签名服务

基于 [xhshow](https://github.com/Cloxl/xhshow) 项目的完整签名算法实现。

## 快速开始

### 1. 安装依赖

```bash
cd MediaCrawer_Pro/signature-service
npm install
```

### 2. 启动服务

```bash
npm start
```

服务将在 `http://localhost:3000` 启动。

### 3. 测试签名算法

```bash
node test_xhs_sign.js
```

## API 接口

### 健康检查

```http
GET /health
```

**响应：**
```json
{
  "code": 0,
  "message": "MediaCrawer Pro Signature Service is running",
  "data": {
    "version": "1.0.0",
    "platforms": ["xhs", "douyin", "kuaishou", "bilibili"]
  }
}
```

### 小红书签名

```http
POST /sign/xhs
Content-Type: application/json

{
  "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
  "method": "GET",
  "data": {
    "keyword": "美食",
    "page": "1"
  },
  "a1": "your_a1_cookie_value"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "x-s": "XYS_xxxxxxxxxxxxxx",
    "x-t": "1700000000000"
  }
}
```

## 使用示例

### Node.js 调用

```javascript
const axios = require('axios');

async function getXhsSign() {
  const response = await axios.post('http://localhost:3000/sign/xhs', {
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    method: 'GET',
    data: {
      keyword: '美食',
      page: '1'
    },
    a1: 'your_a1_cookie_value'
  });
  
  console.log(response.data);
}
```

### Python 调用

```python
import httpx
import asyncio

async def get_xhs_sign():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:3000/sign/xhs',
            json={
                'url': 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
                'method': 'GET',
                'data': {
                    'keyword': '美食',
                    'page': '1'
                },
                'a1': 'your_a1_cookie_value'
            }
        )
        print(response.json())

asyncio.run(get_xhs_sign())
```

### curl 调用

```bash
curl -X POST http://localhost:3000/sign/xhs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes",
    "method": "GET",
    "data": {
      "keyword": "美食",
      "page": "1"
    },
    "a1": "your_a1_cookie_value"
  }'
```

## 参数说明

### 小红书签名参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | ✅ | 请求的完整 URL 或 URI |
| method | string | ❌ | 请求方法，默认 "GET" |
| data | object | ❌ | GET 请求为 params，POST 请求为 body |
| a1 | string | ❌ | Cookie 中的 a1 值（强烈推荐） |

## 配置选项

编辑 `src/server.js` 修改服务配置：

```javascript
const port = process.env.PORT || 3000;  // 端口号
```

## 环境变量

- `PORT`: 服务端口，默认 3000

## Docker 部署

```bash
# 构建镜像
docker build -t mediacrawer-signature .

# 运行容器
docker run -d -p 3000:3000 mediacrawer-signature
```

## 开发说明

### 项目结构

```
signature-service/
├── src/
│   ├── platforms/
│   │   ├── xhs.js          # 小红书签名算法
│   │   ├── douyin.js       # 抖音签名算法
│   │   ├── kuaishou.js     # 快手签名算法
│   │   └── bilibili.js     # B站签名算法
│   └── server.js           # 主服务
├── test_xhs_sign.js        # 测试脚本
├── package.json
└── README.md
```

### 签名算法实现

小红书签名算法基于 xhshow 项目，包含以下核心组件：

1. **Base58 编码器** - 自定义字母表的 Base58 编解码
2. **Base64 编码器** - 自定义字母表的 Base64 编解码
3. **位运算工具** - XOR 转换数组
4. **加密处理器** - 构建 payload 数组
5. **签名生成器** - 完整的签名生成流程

详细说明请参考：[小红书签名算法完善说明.md](../docs/小红书签名算法完善说明.md)

## 常见问题

### Q1: 签名验证失败？

**A:** 确保以下几点：
- 传入了正确的 `a1` cookie 值
- URL 格式正确
- `method` 参数与实际请求方法一致
- GET 请求的参数放在 `data` 中，POST 请求的 body 也放在 `data` 中

### Q2: 如何获取 a1 cookie？

**A:** 
1. 打开小红书网站
2. 登录账号
3. 打开浏览器开发者工具（F12）
4. 切换到 Application/存储 -> Cookies
5. 找到 `a1` 字段，复制其值

### Q3: 签名每次都不同是正常的吗？

**A:** 是的。签名算法包含随机化机制，每次生成的签名都不同，这是为了增加安全性。

### Q4: 支持其他平台吗？

**A:** 目前支持：
- ✅ 小红书（完整实现）
- 🚧 抖音（待完善）
- 🚧 快手（待完善）
- 🚧 B站（待完善）

## 注意事项

1. **a1 cookie 很重要**：虽然不传 a1 也能生成签名，但可能无法通过小红书的验证
2. **请求频率控制**：合理控制请求频率，避免被封禁
3. **代理使用**：建议配合代理池使用
4. **遵守规则**：仅供学习研究使用，不得用于商业用途

## 许可证

本项目仅供学习和研究使用。使用者应遵守：
- 不得用于任何商业用途
- 遵守目标平台的使用条款和 robots.txt 规则
- 不得进行大规模爬取或对平台造成运营干扰
- 合理控制请求频率
- 不得用于任何非法或不当的用途

## 参考资料

- [xhshow](https://github.com/Cloxl/xhshow) - 小红书签名算法 Python 实现
- [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) - 原始项目

## 更新日志

### v1.0.0 (2024-11-16)
- ✨ 基于 xhshow 完整实现小红书签名算法
- ✨ 支持 GET 和 POST 请求
- ✨ Base58/Base64 自定义编解码
- ✨ 完整的测试脚本
- 📝 详细的文档说明

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2024-11-16

























