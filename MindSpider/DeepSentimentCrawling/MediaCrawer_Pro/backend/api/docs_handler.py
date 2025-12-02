#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 文档页面 - 交互式文档
"""
import tornado.web


class DocsHandler(tornado.web.RequestHandler):
    """API 文档处理器 - 类似 FastAPI 的 Swagger UI"""
    
    def get(self):
        """返回交互式 API 文档 HTML 页面"""
        html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediaCrawer Pro API 文档</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 40px; }
        
        .endpoint {
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s;
        }
        .endpoint:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .endpoint-header {
            padding: 15px 20px;
            background: #fafafa;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .endpoint-header:hover {
            background: #f0f0f0;
        }
        .method {
            padding: 6px 14px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85em;
            min-width: 60px;
            text-align: center;
        }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
        .delete { background: #f93e3e; color: white; }
        .put { background: #fca130; color: white; }
        .path {
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            flex: 1;
        }
        .description {
            color: #666;
            font-size: 0.9em;
        }
        
        .endpoint-details {
            display: none;
            padding: 20px;
            border-top: 1px solid #e0e0e0;
        }
        .endpoint-details.active {
            display: block;
        }
        
        .section-title {
            font-weight: bold;
            color: #667eea;
            margin: 15px 0 10px 0;
            font-size: 1.1em;
        }
        
        .param-list {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
        }
        .param-item {
            margin: 10px 0;
        }
        .param-name {
            font-family: 'Courier New', monospace;
            color: #e83e8c;
            font-weight: bold;
        }
        .param-type {
            color: #6c757d;
            font-size: 0.9em;
        }
        .param-required {
            color: #f93e3e;
            font-size: 0.85em;
        }
        
        .try-it {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 20px;
            margin-top: 15px;
        }
        .try-it h4 {
            margin-bottom: 15px;
            color: #667eea;
        }
        .input-group {
            margin-bottom: 15px;
        }
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        .input-group input,
        .input-group textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        .input-group textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .response {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .response.success {
            border-left-color: #49cc90;
            background: #f0fdf4;
        }
        .response.error {
            border-left-color: #f93e3e;
            background: #fef2f2;
        }
        .response-code {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .response-body {
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 0.9em;
        }
        
        .toggle-icon {
            transition: transform 0.3s;
        }
        .toggle-icon.active {
            transform: rotate(90deg);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MediaCrawer Pro API</h1>
            <p>交互式 API 文档 - 点击端点展开并测试</p>
        </div>
        
        <div class="content">
            <!-- 健康检查 -->
            <div class="endpoint" data-method="GET" data-path="/health">
                <div class="endpoint-header" onclick="toggleEndpoint(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="method get">GET</span>
                    <span class="path">/health</span>
                    <span class="description">健康检查</span>
                </div>
                <div class="endpoint-details">
                    <div class="section-title">📝 说明</div>
                    <p>检查服务健康状态，返回版本号和服务信息</p>
                    
                    <div class="try-it">
                        <h4>🧪 试一试</h4>
                        <button onclick="executeRequest('GET', '/health', null)">执行</button>
                        <div id="response-GET-/health" class="response" style="display:none;">
                            <div class="response-code"></div>
                            <div class="response-body"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 获取任务列表 -->
            <div class="endpoint" data-method="GET" data-path="/api/v1/tasks">
                <div class="endpoint-header" onclick="toggleEndpoint(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="method get">GET</span>
                    <span class="path">/api/v1/tasks</span>
                    <span class="description">获取任务列表</span>
                </div>
                <div class="endpoint-details">
                    <div class="section-title">📝 说明</div>
                    <p>获取任务列表，支持分页和筛选</p>
                    
                    <div class="section-title">📋 查询参数</div>
                    <div class="param-list">
                        <div class="param-item">
                            <span class="param-name">page</span>
                            <span class="param-type">integer</span> - 页码，默认 1
                        </div>
                        <div class="param-item">
                            <span class="param-name">page_size</span>
                            <span class="param-type">integer</span> - 每页数量，默认 20
                        </div>
                        <div class="param-item">
                            <span class="param-name">status</span>
                            <span class="param-type">string</span> - 状态筛选 (pending/running/completed/failed)
                        </div>
                        <div class="param-item">
                            <span class="param-name">platform</span>
                            <span class="param-type">string</span> - 平台筛选 (xhs/douyin/kuaishou/bilibili)
                        </div>
                    </div>
                    
                    <div class="try-it">
                        <h4>🧪 试一试</h4>
                        <div class="input-group">
                            <label>page:</label>
                            <input type="number" id="param-page" value="1">
                        </div>
                        <div class="input-group">
                            <label>page_size:</label>
                            <input type="number" id="param-page_size" value="20">
                        </div>
                        <button onclick="executeTaskListRequest()">执行</button>
                        <div id="response-GET-/api/v1/tasks" class="response" style="display:none;">
                            <div class="response-code"></div>
                            <div class="response-body"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 创建任务 -->
            <div class="endpoint" data-method="POST" data-path="/api/v1/tasks">
                <div class="endpoint-header" onclick="toggleEndpoint(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="method post">POST</span>
                    <span class="path">/api/v1/tasks</span>
                    <span class="description">创建任务</span>
                </div>
                <div class="endpoint-details">
                    <div class="section-title">📝 说明</div>
                    <p>创建新的采集任务</p>
                    
                    <div class="section-title">📋 请求体参数</div>
                    <div class="param-list">
                        <div class="param-item">
                            <span class="param-name">platform</span>
                            <span class="param-type">string</span>
                            <span class="param-required">* 必填</span> - 平台名称 (xhs/douyin/kuaishou/bilibili)
                        </div>
                        <div class="param-item">
                            <span class="param-name">type</span>
                            <span class="param-type">string</span>
                            <span class="param-required">* 必填</span> - 任务类型 (search/homefeed/note)
                        </div>
                        <div class="param-item">
                            <span class="param-name">keywords</span>
                            <span class="param-type">array</span> - 关键词列表
                        </div>
                        <div class="param-item">
                            <span class="param-name">max_count</span>
                            <span class="param-type">integer</span> - 最大采集数量
                        </div>
                        <div class="param-item">
                            <span class="param-name">enable_comment</span>
                            <span class="param-type">boolean</span> - 是否爬取评论
                        </div>
                        <div class="param-item">
                            <span class="param-name">enable_download</span>
                            <span class="param-type">boolean</span> - 是否下载视频/图片
                        </div>
                    </div>
                    
                    <div class="try-it">
                        <h4>🧪 试一试</h4>
                        <div class="input-group">
                            <label>请求体 (JSON):</label>
                            <textarea id="body-POST-/api/v1/tasks">{
  "platform": "xhs",
  "type": "search",
  "keywords": ["测试"],
  "max_count": 10,
  "enable_comment": true,
  "enable_download": false
}</textarea>
                        </div>
                        <button onclick="executeCreateTask()">执行</button>
                        <div id="response-POST-/api/v1/tasks" class="response" style="display:none;">
                            <div class="response-code"></div>
                            <div class="response-body"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 获取账号列表 -->
            <div class="endpoint" data-method="GET" data-path="/api/v1/accounts">
                <div class="endpoint-header" onclick="toggleEndpoint(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="method get">GET</span>
                    <span class="path">/api/v1/accounts</span>
                    <span class="description">获取账号列表</span>
                </div>
                <div class="endpoint-details">
                    <div class="section-title">📝 说明</div>
                    <p>获取平台账号列表</p>
                    
                    <div class="try-it">
                        <h4>🧪 试一试</h4>
                        <button onclick="executeRequest('GET', '/api/v1/accounts', null)">执行</button>
                        <div id="response-GET-/api/v1/accounts" class="response" style="display:none;">
                            <div class="response-code"></div>
                            <div class="response-body"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 获取代理列表 -->
            <div class="endpoint" data-method="GET" data-path="/api/v1/proxies">
                <div class="endpoint-header" onclick="toggleEndpoint(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="method get">GET</span>
                    <span class="path">/api/v1/proxies</span>
                    <span class="description">获取代理列表</span>
                </div>
                <div class="endpoint-details">
                    <div class="section-title">📝 说明</div>
                    <p>获取IP代理列表</p>
                    
                    <div class="try-it">
                        <h4>🧪 试一试</h4>
                        <button onclick="executeRequest('GET', '/api/v1/proxies', null)">执行</button>
                        <div id="response-GET-/api/v1/proxies" class="response" style="display:none;">
                            <div class="response-code"></div>
                            <div class="response-body"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 获取推荐流 -->
            <div class="endpoint" data-method="GET" data-path="/api/v1/homefeed">
                <div class="endpoint-header" onclick="toggleEndpoint(this)">
                    <span class="toggle-icon">▶</span>
                    <span class="method get">GET</span>
                    <span class="path">/api/v1/homefeed</span>
                    <span class="description">获取首页推荐流</span>
                </div>
                <div class="endpoint-details">
                    <div class="section-title">📝 说明</div>
                    <p>获取指定平台的首页推荐内容</p>
                    
                    <div class="section-title">📋 查询参数</div>
                    <div class="param-list">
                        <div class="param-item">
                            <span class="param-name">platform</span>
                            <span class="param-type">string</span> - 平台，默认 xhs
                        </div>
                        <div class="param-item">
                            <span class="param-name">page</span>
                            <span class="param-type">integer</span> - 页码，默认 1
                        </div>
                    </div>
                    
                    <div class="try-it">
                        <h4>🧪 试一试</h4>
                        <button onclick="executeRequest('GET', '/api/v1/homefeed?platform=xhs&page=1', null)">执行</button>
                        <div id="response-GET-/api/v1/homefeed" class="response" style="display:none;">
                            <div class="response-code"></div>
                            <div class="response-body"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function toggleEndpoint(header) {
            const endpoint = header.parentElement;
            const details = endpoint.querySelector('.endpoint-details');
            const icon = header.querySelector('.toggle-icon');
            
            details.classList.toggle('active');
            icon.classList.toggle('active');
        }

        async function executeRequest(method, path, body) {
            const responseId = `response-${method}-${path.split('?')[0]}`;
            const responseEl = document.getElementById(responseId);
            const codeEl = responseEl.querySelector('.response-code');
            const bodyEl = responseEl.querySelector('.response-body');
            
            responseEl.style.display = 'block';
            responseEl.className = 'response';
            codeEl.textContent = '⏳ 请求中...';
            bodyEl.textContent = '';
            
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                if (body) {
                    options.body = JSON.stringify(body);
                }
                
                const response = await fetch(path, options);
                const data = await response.json();
                
                responseEl.className = response.ok ? 'response success' : 'response error';
                codeEl.textContent = `HTTP ${response.status} ${response.statusText}`;
                bodyEl.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                responseEl.className = 'response error';
                codeEl.textContent = '❌ 请求失败';
                bodyEl.textContent = error.message;
            }
        }

        async function executeTaskListRequest() {
            const page = document.getElementById('param-page').value;
            const pageSize = document.getElementById('param-page_size').value;
            const path = `/api/v1/tasks?page=${page}&page_size=${pageSize}`;
            await executeRequest('GET', path, null);
        }

        async function executeCreateTask() {
            const bodyText = document.getElementById('body-POST-/api/v1/tasks').value;
            try {
                const body = JSON.parse(bodyText);
                await executeRequest('POST', '/api/v1/tasks', body);
            } catch (error) {
                const responseId = 'response-POST-/api/v1/tasks';
                const responseEl = document.getElementById(responseId);
                const codeEl = responseEl.querySelector('.response-code');
                const bodyEl = responseEl.querySelector('.response-body');
                
                responseEl.style.display = 'block';
                responseEl.className = 'response error';
                codeEl.textContent = '❌ JSON 格式错误';
                bodyEl.textContent = error.message;
            }
        }
    </script>
</body>
</html>
        """
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.write(html)
