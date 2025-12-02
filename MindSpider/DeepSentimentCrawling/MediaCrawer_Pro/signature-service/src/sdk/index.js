/**
 * MediaCrawler 签名算法 SDK
 * 
 * 支持三种模式：
 * 1. 纯JS逆向（快速、轻量）
 * 2. Playwright浏览器（完整、慢）
 * 3. 混合模式（自动选择）
 */

const { XhsSignature } = require('../core/xhs_signature');
const { XhsBrowserClient, getXhsHeaders } = require('../playwright/xhs_browser');

/**
 * 混合签名客户端
 * 
 * 根据需求自动选择最优方案
 */
class HybridSignatureClient {
  constructor(options = {}) {
    this.jsClient = new XhsSignature();
    this.browserClient = null;
    this.defaultMode = options.mode || 'auto';  // 'js', 'browser', 'auto'
    this.debugPort = options.debugPort || null;  // 连接 Electron
  }

  /**
   * 获取签名头
   * 
   * @param {Object} options
   * @param {string} options.platform - 平台名称 (xhs, douyin, 等)
   * @param {string} options.url - 请求URL
   * @param {string} options.method - HTTP方法
   * @param {Object} options.data - 请求数据
   * @param {string} options.a1 - Cookie中的a1值
   * @param {string} options.cookie - 完整Cookie字符串（浏览器模式需要）
   * @param {string} options.mode - 模式选择 ('js', 'browser', 'auto')
   * @returns {Object} 签名头对象
   */
  async getHeaders(options = {}) {
    const {
      platform = 'xhs',
      url,
      method = 'GET',
      data = null,
      a1 = '',
      cookie = '',
      mode = this.defaultMode
    } = options;

    if (platform !== 'xhs') {
      throw new Error(`暂不支持平台: ${platform}`);
    }

    // 模式选择
    let actualMode = mode;
    if (mode === 'auto') {
      // 自动模式：优先使用JS，如果需要x-s-common则使用浏览器
      actualMode = options.needXsCommon ? 'browser' : 'js';
    }

    if (actualMode === 'js') {
      // 纯JS逆向模式
      return await this._getHeadersWithJS({ url, method, data, a1 });
    } else if (actualMode === 'browser') {
      // Playwright 浏览器模式
      return await this._getHeadersWithBrowser({ url, method, data, cookie });
    } else {
      throw new Error(`未知模式: ${mode}`);
    }
  }

  /**
   * 纯JS逆向获取签名
   * @private
   */
  async _getHeadersWithJS({ url, method, data, a1 }) {
    const { xs, xt } = this.jsClient.sign({
      method,
      url,
      data,
      a1
    });

    return {
      'x-s': xs,
      'x-t': xt,
      'x-s-common': '',  // JS逆向暂不支持
      mode: 'js'
    };
  }

  /**
   * Playwright 浏览器获取完整请求头
   * @private
   */
  async _getHeadersWithBrowser({ url, method, data, cookie }) {
    // 如果没有初始化浏览器客户端，创建一个
    if (!this.browserClient) {
      this.browserClient = new XhsBrowserClient({
        headless: true,
        debugPort: this.debugPort
      });
      await this.browserClient.init(cookie);
    }

    const headers = await this.browserClient.getHeaders(url, method, data);
    return {
      ...headers,
      mode: 'browser'
    };
  }

  /**
   * 关闭客户端
   */
  async close() {
    if (this.browserClient) {
      await this.browserClient.close();
      this.browserClient = null;
    }
  }
}

/**
 * 快速获取签名（函数式API）
 */
async function getSignature(options = {}) {
  const client = new HybridSignatureClient({
    debugPort: options.debugPort
  });

  try {
    return await client.getHeaders(options);
  } finally {
    await client.close();
  }
}

// ==================== 导出 ====================
module.exports = {
  // 核心类
  HybridSignatureClient,
  XhsSignature,
  XhsBrowserClient,
  
  // 便捷函数
  getSignature,
  getXhsHeaders,
  
  // 平台特定
  xhs: {
    Signature: XhsSignature,
    BrowserClient: XhsBrowserClient,
    getHeaders: getXhsHeaders
  }
};





