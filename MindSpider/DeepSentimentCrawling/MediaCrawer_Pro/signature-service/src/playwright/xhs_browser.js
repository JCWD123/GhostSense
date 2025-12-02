/**
 * 使用 Playwright 从真实浏览器获取小红书请求头
 * 
 * 功能：
 * - 自动获取 x-s, x-t, x-s-common
 * - 处理 Cookie 续期
 * - 绕过反爬检测
 */

const { chromium } = require('playwright');

class XhsBrowserClient {
  constructor(options = {}) {
    this.headless = options.headless !== false;
    this.debugPort = options.debugPort || null;  // 如果指定，连接到已有浏览器
    this.browser = null;
    this.context = null;
    this.page = null;
    this.interceptedHeaders = null;
  }

  /**
   * 初始化浏览器
   * @param {string} cookie - Cookie字符串
   */
  async init(cookie = "") {
    try {
      // 如果指定了调试端口，连接到已有浏览器（如 Electron）
      if (this.debugPort) {
        console.log(`🔗 尝试连接到 Electron，调试端口: ${this.debugPort}`);
        
        try {
          // 使用 CDP 协议连接
          const cdpUrl = `http://localhost:${this.debugPort}`;
          console.log(`📡 CDP URL: ${cdpUrl}`);
          
          this.browser = await chromium.connectOverCDP(cdpUrl);
          console.log('✅ CDP 连接成功');
          
          // 获取所有上下文
          const contexts = this.browser.contexts();
          console.log(`📋 找到 ${contexts.length} 个浏览器上下文`);
          
          // 尝试找到小红书窗口（通过 URL 或标题判断）
          let xhsPage = null;
          
          for (const context of contexts) {
            const pages = context.pages();
            console.log(`🔍 检查上下文 (${pages.length} 个页面)`);
            
            for (const page of pages) {
              const url = page.url();
              const title = await page.title();
              console.log(`   📄 页面: ${title || 'Untitled'} | ${url}`);
              
              // 判断是否是小红书窗口
              if (url.includes('xiaohongshu.com') || 
                  title.includes('小红书') ||
                  title.includes('RED')) {
                xhsPage = page;
                this.context = context;
                console.log(`🎯 找到小红书窗口: ${title}`);
                break;
              }
            }
            
            if (xhsPage) break;
          }
          
          if (xhsPage) {
            // 找到了小红书窗口
            this.page = xhsPage;
            console.log('✅ 成功连接到小红书窗口');
          } else if (contexts.length > 0) {
            // 没找到小红书窗口，使用第一个可用页面
            console.log('⚠️  未找到小红书窗口，尝试使用第一个可用窗口');
            this.context = contexts[0];
            const pages = this.context.pages();
            
            if (pages.length > 0) {
              this.page = pages[0];
              console.log(`✅ 使用第一个窗口: ${await this.page.title()}`);
            } else {
              this.page = await this.context.newPage();
              console.log('✅ 创建新页面');
            }
          } else {
            // 没有任何上下文
            console.log('⚠️  没有找到上下文，创建新的');
            this.context = await this.browser.newContext({
              viewport: { width: 1920, height: 1080 }
            });
            this.page = await this.context.newPage();
          }
          
          console.log('✅ Electron 浏览器连接完成');
        } catch (cdpError) {
          console.error(`❌ CDP连接失败: ${cdpError.message}`);
          console.log('💡 提示：确保 Electron 应用正在运行，且开启了调试端口');
          console.log(`   验证命令: curl http://localhost:${this.debugPort}/json/version`);
          throw new Error(`无法连接到Electron浏览器（端口${this.debugPort}）: ${cdpError.message}`);
        }
      } else {
        // 启动新的浏览器实例
        console.log('🚀 启动新的 Chromium 浏览器...');
        this.browser = await chromium.launch({
          headless: this.headless,
          args: [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-web-security'
          ]
        });

        this.context = await this.browser.newContext({
          viewport: { width: 1920, height: 1080 },
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });

        this.page = await this.context.newPage();
        console.log('✅ 浏览器启动成功');
      }

      // 注入 Cookie
      if (cookie) {
        await this._injectCookie(cookie);
      }

      // 导航到小红书（增加错误处理）
      try {
        console.log('🌐 正在导航到小红书...');
        await this.page.goto('https://www.xiaohongshu.com/explore', {
          waitUntil: 'domcontentloaded',  // 改为更快的加载策略
          timeout: 30000
        });
        console.log('✅ 页面加载完成');
      } catch (navError) {
        console.warn(`⚠️  页面导航警告: ${navError.message}`);
        // 不抛出错误，继续执行
      }

      return true;
    } catch (error) {
      console.error('❌ 浏览器初始化失败:', error.message);
      console.error('详细错误:', error);
      throw error;
    }
  }

  /**
   * 注入 Cookie
   */
  async _injectCookie(cookieString) {
    const cookies = [];
    for (const item of cookieString.split(';')) {
      const trimmed = item.trim();
      if (trimmed && trimmed.includes('=')) {
        const [name, value] = trimmed.split('=', 2);
        cookies.push({
          name: name.trim(),
          value: value.trim(),
          domain: '.xiaohongshu.com',
          path: '/'
        });
      }
    }

    if (cookies.length > 0) {
      await this.context.addCookies(cookies);
      console.log(`✅ 已注入 ${cookies.length} 个 Cookie`);
    }
  }

  /**
   * 获取完整的请求头（包括 x-s-common）
   * 
   * @param {string} targetUrl - 目标API URL
   * @param {string} method - HTTP方法
   * @param {Object} data - 请求数据
   * @returns {Object} 完整的请求头
   */
  async getHeaders(targetUrl, method = "GET", data = null) {
    try {
      this.interceptedHeaders = null;

      const routeHandler = async (route, request) => {
        const url = request.url();
        
        // 拦截目标 API 请求
        if (url.includes('/api/sns/')) {
          console.log(`🎯 拦截到目标请求: ${url}`);
          
          // 获取完整请求头（包括 X-B3-Traceid）
          this.interceptedHeaders = {
            'x-s': request.headers()['x-s'] || '',
            'x-t': request.headers()['x-t'] || '',
            'x-s-common': request.headers()['x-s-common'] || '',
            'x-b3-traceid': request.headers()['x-b3-traceid'] || '',
            'cookie': request.headers()['cookie'] || '',
            'user-agent': request.headers()['user-agent'] || '',
            'referer': request.headers()['referer'] || 'https://www.xiaohongshu.com/',
            'origin': 'https://www.xiaohongshu.com'
          };
          
          console.log('✅ 已捕获请求头');
        }
        
        // 继续请求
        await route.continue();
      };

      await this.page.route('**/*', routeHandler);

      const maxAttempts = 3;
      for (let attempt = 0; attempt < maxAttempts && !this.interceptedHeaders; attempt++) {
        if (attempt > 0) {
          console.log(`🔁 第 ${attempt + 1} 次重试触发请求`);
          await this._sleep(500);
        }

        console.log(`⏰ 开始等待拦截 (最多 15 秒)...`);
        const triggerPromise = this._triggerRequest(targetUrl, method, data);

        let retries = 0;
        const maxRetries = 30;
        while (!this.interceptedHeaders && retries < maxRetries) {
          await this._sleep(500);
          retries++;
          if (retries % 5 === 0) {
            console.log(`⏳ 等待中... (${retries}/${maxRetries})`);
          }
        }

        try {
          await triggerPromise;
        } catch (err) {
          console.warn(`⚠️ 触发请求时出错: ${err.message}`);
        }
      }

      await this.page.unroute('**/*', routeHandler);

      if (!this.interceptedHeaders) {
        throw new Error('未能捕获到目标请求头');
      }

      console.log('✅ 成功捕获请求头');
      return this.interceptedHeaders;
    } catch (error) {
      console.error('❌ 获取请求头失败:', error.message);
      throw error;
    }
  }

  /**
   * 获取 localStorage 中的值
   * @param {string} key
   * @returns {Promise<string>}
   */
  async getLocalStorageValue(key) {
    if (!this.page) {
      throw new Error('浏览器页面尚未初始化');
    }

    try {
      await this.page.waitForLoadState('domcontentloaded', { timeout: 5000 });
    } catch (error) {
      console.warn(`⚠️ 等待页面加载以获取 localStorage(${key}) 超时: ${error.message}`);
    }

    return await this.page.evaluate((storageKey) => {
      return window.localStorage.getItem(storageKey) || '';
    }, key);
  }

  /**
   * 获取 b1 值
   */
  async getB1Value() {
    return await this.getLocalStorageValue('b1');
  }

  /**
   * 触发请求（通过在页面中执行 JavaScript）
   * 改进版：添加详细日志和错误处理
   */
  async _triggerRequest(url, method, data) {
    console.log(`🚀 触发请求: ${method} ${url}`);
    if (data) {
      console.log(`   Body: ${JSON.stringify(data).substring(0, 100)}...`);
    }
    
    try {
      const result = await this.page.evaluate(async ({ url, method, data }) => {
        console.log(`[页面内] 开始请求: ${method} ${url}`);
        
        try {
          const options = {
            method: method,
            headers: {
              'Content-Type': 'application/json'
            },
            credentials: 'include'
          };
          
          if (data) {
            options.body = JSON.stringify(data);
          }
          
          console.log(`[页面内] Fetch 选项:`, options);
          const response = await fetch(url, options);
          console.log(`[页面内] 响应状态: ${response.status}`);
          
          const json = await response.json();
          console.log(`[页面内] 响应成功:`, json);
          
          return { success: true, status: response.status, data: json };
        } catch (error) {
          console.error(`[页面内] 请求失败:`, error.message);
          return { success: false, error: error.message };
        }
      }, { url, method, data });
      
      if (result.success) {
        console.log(`✅ 请求触发成功，状态: ${result.status}`);
      } else {
        console.warn(`⚠️ 请求触发失败: ${result.error}`);
      }
      
      return result;
    } catch (error) {
      console.error(`❌ 触发请求时出错: ${error.message}`);
      throw error;
    }
  }

  /**
   * 搜索笔记（便捷方法）
   */
  async searchNotes(keyword, page = 1, pageSize = 20, sort = "general") {
    const apiUrl = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes';
    const params = {
      keyword,
      page,
      page_size: pageSize,
      search_id: this._generateSearchId(),
      sort
    };

    const fullUrl = `${apiUrl}?${new URLSearchParams(params).toString()}`;
    const headers = await this.getHeaders(fullUrl, 'GET');

    // 使用捕获的请求头发起真实请求
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers
    });

    return await response.json();
  }

  /**
   * 生成搜索ID
   */
  _generateSearchId() {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 15);
    return `${timestamp}_${random}`;
  }

  /**
   * 关闭浏览器
   */
  async close() {
    try {
      if (this.page && !this.debugPort) {
        await this.page.close();
      }
      
      // 如果是连接到 Electron，不关闭浏览器
      if (this.browser && !this.debugPort) {
        await this.browser.close();
        console.log('👋 浏览器已关闭');
      } else if (this.debugPort) {
        console.log('👋 已断开与 Electron 的连接');
      }
    } catch (error) {
      console.error('关闭浏览器时出错:', error.message);
    }
  }

  /**
   * 工具：延迟
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ==================== 便捷函数 ====================

/**
 * 快速获取小红书请求头（单次使用）
 * 
 * @param {Object} options
 * @param {string} options.url - 目标URL
 * @param {string} options.method - HTTP方法
 * @param {Object} options.data - 请求数据
 * @param {string} options.cookie - Cookie字符串
 * @param {number} options.debugPort - Electron调试端口（可选）
 * @returns {Object} 完整请求头
 */
async function getXhsHeaders(options = {}) {
  const client = new XhsBrowserClient({
    headless: options.headless !== false,
    debugPort: options.debugPort
  });

  try {
    await client.init(options.cookie);
    const headers = await client.getHeaders(options.url, options.method, options.data);
    return headers;
  } finally {
    await client.close();
  }
}

/**
 * 快速获取 b1
 */
async function getB1Value(options = {}) {
  const client = new XhsBrowserClient({
    headless: options.headless !== false,
    debugPort: options.debugPort || null
  });

  try {
    await client.init(options.cookie || '');
    const value = await client.getB1Value();
    return value || '';
  } finally {
    await client.close();
  }
}

/**
 * 在浏览器上下文内执行请求（带真实指纹）
 * 
 * @param {Object} options - 配置选项
 * @param {string} options.url - 请求 URL
 * @param {string} [options.method='GET'] - 请求方法
 * @param {Object} [options.data] - 请求数据
 * @param {string} [options.cookie] - Cookie
 * @param {number} [options.debugPort] - Electron 调试端口
 * @returns {Promise<Object>} API响应数据
 */
async function executeInBrowser(options = {}) {
  const client = new XhsBrowserClient({
    headless: options.headless !== false,
    debugPort: options.debugPort
  });

  try {
    await client.init(options.cookie || '');
    
    console.log(`🌐 在浏览器内执行请求: ${options.method || 'GET'} ${options.url}`);
    
    // 在页面上下文内执行 fetch
    const result = await client.page.evaluate(async ({ url, method, data }) => {
      try {
        const options = {
          method: method || 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*'
          },
          credentials: 'include'  // 自动带上 cookie
        };
        
        if (data) {
          options.body = JSON.stringify(data);
        }
        
        console.log('[浏览器内] 发起请求:', url);
        const response = await fetch(url, options);
        const json = await response.json();
        
        console.log('[浏览器内] 响应状态:', response.status);
        console.log('[浏览器内] 响应数据:', json);
        
        return {
          success: response.ok,
          status: response.status,
          data: json
        };
      } catch (error) {
        console.error('[浏览器内] 请求失败:', error.message);
        return {
          success: false,
          error: error.message
        };
      }
    }, {
      url: options.url,
      method: options.method || 'GET',
      data: options.data
    });
    
    if (result.success) {
      console.log('✅ 浏览器内请求成功');
      return result.data;
    } else {
      throw new Error(result.error || '浏览器内请求失败');
    }
  } finally {
    await client.close();
  }
}

// ==================== 导出 ====================
module.exports = {
  XhsBrowserClient,
  getXhsHeaders,
  getB1Value,
  executeInBrowser
};


