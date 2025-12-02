/**
 * 签名服务 HTTP API
 * 
 * 端口: 3100
 * 
 * 路由：
 * POST /sign/xhs          - 纯JS签名（x-s, x-t）
 * POST /sign/xhs/browser  - Playwright获取完整头（包括x-s-common）
 * POST /sign/xhs/hybrid   - 混合模式
 */

const fastify = require('fastify')({ logger: true });
const { XhsSignature } = require('../core/xhs_signature');
const { getXhsHeaders, getB1Value, executeInBrowser } = require('../playwright/xhs_browser');
const { HybridSignatureClient } = require('../sdk/index');
const { sign: enhanceSign } = require('../utils/xhs_sign_enhanced');

// 初始化签名客户端
const jsClient = new XhsSignature();
let hybridClient = null;

const B1_CACHE_TTL = parseInt(process.env.B1_CACHE_TTL || '1800000', 10);
const b1Cache = new Map();

function getB1Cache(key) {
  if (!key) key = 'default';
  const cached = b1Cache.get(key);
  if (!cached) return '';
  if (Date.now() - cached.timestamp > B1_CACHE_TTL) {
    b1Cache.delete(key);
    return '';
  }
  return cached.value || '';
}

function setB1Cache(key, value) {
  if (!value) return;
  if (!key) key = 'default';
  b1Cache.set(key, { value, timestamp: Date.now() });
}

// ==================== 路由 ====================

/**
 * 健康检查
 */
fastify.get('/health', async (request, reply) => {
  return {
    success: true,
    service: 'MediaCrawler Signature Service',
    version: '2.0.0',
    timestamp: Date.now()
  };
});

/**
 * 在浏览器上下文内执行请求（最高安全性，带真实指纹）
 * 
 * POST /execute/xhs/browser
 * Body: {
 *   url: string,
 *   method: string,
 *   data: object,
 *   cookie: string,
 *   debugPort: number
 * }
 */
fastify.post('/execute/xhs/browser', async (request, reply) => {
  try {
    const {
      url,
      method = 'POST',
      data = null,
      cookie = '',
      debugPort = null
    } = request.body;

    if (!url) {
      return reply.code(400).send({
        success: false,
        message: '缺少必需参数: url'
      });
    }

    fastify.log.info(`🌐 浏览器内执行请求: ${method} ${url}`);
    fastify.log.info(`   调试端口: ${debugPort || '未指定'}`);
    fastify.log.info(`   Cookie长度: ${cookie ? cookie.length : 0}`);

    const result = await executeInBrowser({
      url,
      method,
      data,
      cookie,
      debugPort,
      headless: true
    });

    fastify.log.info('✅ 浏览器内请求成功');

    return {
      success: true,
      data: result,
      mode: 'browser-execute',
      note: '请求在真实浏览器环境中执行，自动带上完整指纹和签名',
      timestamp: Date.now()
    };
  } catch (error) {
    fastify.log.error('❌ 浏览器内执行失败:');
    fastify.log.error(`   错误: ${error.message}`);
    
    return reply.code(500).send({
      success: false,
      message: error.message || '浏览器内执行请求失败',
      timestamp: Date.now()
    });
  }
});

/**
 * 纯JS签名（快速）
 * 
 * POST /sign/xhs
 * Body: {
 *   url: string,
 *   method: string,
 *   data: object,
 *   a1: string,
 *   b1: string (可选，用于生成 x-s-common)
 * }
 */
fastify.post('/sign/xhs', async (request, reply) => {
  try {
    const {
      url,
      method = 'GET',
      data = null,
      a1 = '',
      b1 = '',
      cookie = '',
      debugPort = null,
      autoFetchB1 = true
    } = request.body;

    if (!url) {
      return reply.code(400).send({
        success: false,
        message: '缺少必需参数: url'
      });
    }

    const cacheKey = a1 || cookie;
    let resolvedB1 = b1 || getB1Cache(cacheKey);

    if (!resolvedB1 && autoFetchB1 && (cookie || debugPort)) {
      try {
        fastify.log.info('🔍 b1 未提供，尝试通过浏览器获取...');
        resolvedB1 = await getB1Value({ cookie, debugPort });
        if (resolvedB1) {
          fastify.log.info('✅ 成功自动获取 b1');
          setB1Cache(cacheKey, resolvedB1);
        } else {
          fastify.log.warn('⚠️ 自动获取 b1 失败，返回空值');
        }
      } catch (fetchError) {
        fastify.log.warn(`⚠️ 自动获取 b1 出错: ${fetchError.message}`);
      }
    }

    const { xs, xt } = jsClient.sign({
      method,
      url,
      data,
      a1
    });

    let headers = {
      'x-s': xs,
      'x-t': xt
    };

    // 如果提供了 b1，则返回完整签名（包括 x-s-common、X-B3-Traceid）
    if (resolvedB1) {
      const enhanced = enhanceSign(a1, resolvedB1, xs, xt);
      headers = {
        ...headers,
        'x-s-common': enhanced['x-s-common'],
        'x-b3-traceid': enhanced['x-b3-traceid']
      };
    } else {
      fastify.log.warn('⚠️ 未获取到 b1，返回基础签名（仅 x-s/x-t）');
    }

    return {
      success: true,
      data: headers,
      mode: resolvedB1 ? 'js-enhanced' : 'js',
      note: resolvedB1
        ? '基于 b1 生成完整签名（含 x-s-common、X-B3-Traceid）'
        : '如需完整签名（含x-s-common），请提供 b1 或使用 /sign/xhs/browser 端点',
      timestamp: Date.now()
    };
  } catch (error) {
    fastify.log.error(error);
    return reply.code(500).send({
      success: false,
      message: '签名生成失败',
      error: error.message
    });
  }
});

/**
 * Playwright 浏览器获取完整请求头
 * 
 * POST /sign/xhs/browser
 * Body: {
 *   url: string,
 *   method: string,
 *   data: object,
 *   cookie: string,
 *   userAgent: string,  // 可选，真实UA（从Electron获取）
 *   debugPort: number  // 可选，连接到Electron
 * }
 */
fastify.post('/sign/xhs/browser', async (request, reply) => {
  try {
    const {
      url,
      method = 'GET',
      data = null,
      cookie = '',
      userAgent = null,
      debugPort = null
    } = request.body;

    if (!url) {
      return reply.code(400).send({
        success: false,
        message: '缺少必需参数: url'
      });
    }

    fastify.log.info(`🌐 浏览器模式请求: ${url}`);
    fastify.log.info(`   调试端口: ${debugPort || '未指定（将启动新浏览器）'}`);
    fastify.log.info(`   Cookie长度: ${cookie ? cookie.length : 0}`);
    if (userAgent) {
      fastify.log.info(`   使用真实 UA: ${userAgent.substring(0, 50)}...`);
    }

    const headers = await getXhsHeaders({
      url,
      method,
      data,
      cookie,
      userAgent,
      debugPort,
      headless: true
    });

    fastify.log.info('✅ 浏览器模式成功获取请求头');
    fastify.log.info(`   包含字段: ${Object.keys(headers).join(', ')}`);

    return {
      success: true,
      data: headers,
      mode: 'browser',
      timestamp: Date.now()
    };
  } catch (error) {
    fastify.log.error('❌ 浏览器模式失败:');
    fastify.log.error(`   错误类型: ${error.name}`);
    fastify.log.error(`   错误信息: ${error.message}`);
    fastify.log.error(`   堆栈: ${error.stack}`);
    
    // 提供更详细的错误信息
    let userMessage = '浏览器获取请求头失败';
    let suggestions = [];

    if (error.message.includes('无法连接到Electron')) {
      userMessage = 'Electron浏览器连接失败';
      suggestions = [
        '1. 确保 Electron 应用正在运行',
        '2. 验证调试端口：curl http://localhost:9222/json/version',
        '3. 检查端口是否被占用：netstat -an | grep 9222'
      ];
    } else if (error.message.includes('timeout')) {
      userMessage = '浏览器操作超时';
      suggestions = [
        '1. 网络可能较慢，请重试',
        '2. 检查小红书网站是否可访问',
        '3. 考虑使用纯JS签名模式'
      ];
    } else if (error.message.includes('Executable')) {
      userMessage = 'Playwright浏览器未安装';
      suggestions = [
        '1. 运行: npx playwright install chromium',
        '2. 或使用Electron模式，指定debugPort: 9222'
      ];
    }

    return reply.code(500).send({
      success: false,
      message: userMessage,
      error: error.message,
      suggestions,
      timestamp: Date.now()
    });
  }
});

/**
 * 混合模式（自动选择）
 * 
 * POST /sign/xhs/hybrid
 * Body: {
 *   url: string,
 *   method: string,
 *   data: object,
 *   a1: string,
 *   cookie: string,
 *   mode: string,  // 'js', 'browser', 'auto'
 *   debugPort: number
 * }
 */
fastify.post('/sign/xhs/hybrid', async (request, reply) => {
  try {
    const {
      url,
      method = 'GET',
      data = null,
      a1 = '',
      cookie = '',
      mode = 'auto',
      debugPort = null
    } = request.body;

    if (!url) {
      return reply.code(400).send({
        success: false,
        message: '缺少必需参数: url'
      });
    }

    // 创建混合客户端（复用）
    if (!hybridClient) {
      hybridClient = new HybridSignatureClient({ debugPort });
    }

    const headers = await hybridClient.getHeaders({
      platform: 'xhs',
      url,
      method,
      data,
      a1,
      cookie,
      mode
    });

    return {
      success: true,
      data: headers,
      timestamp: Date.now()
    };
  } catch (error) {
    fastify.log.error(error);
    return reply.code(500).send({
      success: false,
      message: '混合模式签名失败',
      error: error.message
    });
  }
});

/**
 * 抖音签名（占位）
 */
fastify.post('/sign/douyin', async (request, reply) => {
  return reply.code(501).send({
    success: false,
    message: '抖音签名暂未实现'
  });
});

/**
 * 快手签名（占位）
 */
fastify.post('/sign/kuaishou', async (request, reply) => {
  return reply.code(501).send({
    success: false,
    message: '快手签名暂未实现'
  });
});

/**
 * B站签名（占位）
 */
fastify.post('/sign/bilibili', async (request, reply) => {
  return reply.code(501).send({
    success: false,
    message: 'B站签名暂未实现'
  });
});

// ==================== 启动服务 ====================

const PORT = process.env.PORT || 3100;
const HOST = process.env.HOST || '0.0.0.0';

async function start() {
  try {
    await fastify.listen({ port: PORT, host: HOST });
    console.log('');
    console.log('🚀 ========================================');
    console.log('📦 MediaCrawler 签名服务已启动');
    console.log('🌐 监听地址:', `http://${HOST}:${PORT}`);
    console.log('📚 API 文档:');
    console.log('   - 纯JS签名: POST /sign/xhs');
    console.log('   - 浏览器模式: POST /sign/xhs/browser');
    console.log('   - 混合模式: POST /sign/xhs/hybrid');
    console.log('   - 浏览器内执行: POST /execute/xhs/browser (最高安全性)');
    console.log('   - 健康检查: GET /health');
    console.log('🎯 版本: 2.0.0 (支持 Playwright + Electron + 浏览器内执行)');
    console.log('========================================');
    console.log('');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
}

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('\n👋 正在关闭服务...');
  if (hybridClient) {
    await hybridClient.close();
  }
  await fastify.close();
  console.log('✅ 服务已关闭');
  process.exit(0);
});

// 启动
if (require.main === module) {
  start();
}

module.exports = fastify;



