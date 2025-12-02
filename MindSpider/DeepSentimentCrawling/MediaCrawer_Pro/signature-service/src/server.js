#!/usr/bin/env node
/**
 * MediaCrawer Pro - 签名服务
 * 
 * 提供各平台的签名算法实现
 */

const fastify = require('fastify')({ logger: true });
const { XhsSignature } = require('./core/xhs_signature');
const douyinSign = require('./platforms/douyin');
const kuaishouSign = require('./platforms/kuaishou');
const biliSign = require('./platforms/bilibili');

// 初始化小红书签名实例（纯 JS 逆向）
const xhsSignature = new XhsSignature();

// 处理跨域请求（增强版）
fastify.addHook('onRequest', (request, reply, done) => {
  // 获取请求来源
  const origin = request.headers.origin || '*';
  
  // 设置CORS响应头
  reply.header('Access-Control-Allow-Origin', origin);
  reply.header('Access-Control-Allow-Credentials', 'true');
  reply.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  reply.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  reply.header('Access-Control-Max-Age', '86400'); // 24小时

  // 处理OPTIONS预检请求
  if (request.method === 'OPTIONS') {
    reply.code(204).send();
    return;
  }

  done();
});

// 健康检查
fastify.get('/health', async (request, reply) => {
  return {
    code: 0,
    message: 'MediaCrawer Pro Signature Service is running',
    data: {
      version: '1.0.0',
      platforms: ['xhs', 'douyin', 'kuaishou', 'bilibili']
    }
  };
});

// CORS测试端点
fastify.get('/cors-test', async (request, reply) => {
  return {
    code: 0,
    message: 'CORS配置正常',
    data: {
      origin: request.headers.origin || 'no origin',
      method: request.method,
      timestamp: Date.now()
    }
  };
});

// 通用签名接口（默认小红书）- 兼容旧版本
fastify.post('/sign', async (request, reply) => {
  try {
    const { url, method = 'GET', data = null, a1 = '' } = request.body;
    
    if (!url) {
      return reply.code(400).send({
        code: 1,
        message: '缺少 url 参数',
        data: null
      });
    }
    
    // 新的签名算法需要传入 method、data 和 a1
    const { xs, xt } = xhsSignature.sign({
      method,
      url,
      data,
      a1
    });
    
    return {
      code: 0,
      message: 'success',
      data: {
        'x-s': xs,
        'x-t': xt
      }
    };
  } catch (error) {
    request.log.error(error);
    return reply.code(500).send({
      code: 1,
      message: error.message,
      data: null
    });
  }
});

// 小红书签名（显式指定平台）
fastify.post('/sign/xhs', async (request, reply) => {
  try {
    const { url, method = 'GET', data = null, a1 = '', b1 = '' } = request.body;
    
    if (!url) {
      return reply.code(400).send({
        code: 1,
        message: '缺少 url 参数',
        data: null
      });
    }
    
    // 新的签名算法需要传入 method、data 和 a1
    const { xs, xt } = xhsSignature.sign({
      method,
      url,
      data,
      a1
    });
    
    // 如果提供了 b1，生成完整签名（包括 x-s-common 和 X-B3-Traceid）
    if (b1) {
      const { sign } = require('./utils/xhs_sign_enhanced');
      const fullSign = sign(a1, b1, xs, xt);
      
      return {
        code: 0,
        message: 'success',
        data: fullSign
      };
    }
    
    // 否则只返回基础签名
    return {
      code: 0,
      message: 'success',
      data: {
        'x-s': xs,
        'x-t': xt
      }
    };
  } catch (error) {
    request.log.error(error);
    return reply.code(500).send({
      code: 1,
      message: error.message,
      data: null
    });
  }
});

// 抖音签名
fastify.post('/sign/douyin', async (request, reply) => {
  try {
    const { url, data } = request.body;
    
    if (!url) {
      return reply.code(400).send({
        code: 1,
        message: '缺少 url 参数',
        data: null
      });
    }
    
    const sign = douyinSign.getSign(url, data);
    
    return {
      code: 0,
      message: 'success',
      data: sign
    };
  } catch (error) {
    request.log.error(error);
    return reply.code(500).send({
      code: 1,
      message: error.message,
      data: null
    });
  }
});

// 快手签名
fastify.post('/sign/kuaishou', async (request, reply) => {
  try {
    const { url, data } = request.body;
    
    if (!url) {
      return reply.code(400).send({
        code: 1,
        message: '缺少 url 参数',
        data: null
      });
    }
    
    const sign = kuaishouSign.getSign(url, data);
    
    return {
      code: 0,
      message: 'success',
      data: sign
    };
  } catch (error) {
    request.log.error(error);
    return reply.code(500).send({
      code: 1,
      message: error.message,
      data: null
    });
  }
});

// B站签名
fastify.post('/sign/bilibili', async (request, reply) => {
  try {
    const { params } = request.body;
    
    if (!params) {
      return reply.code(400).send({
        code: 1,
        message: '缺少 params 参数',
        data: null
      });
    }
    
    const sign = await biliSign.getSign(params);
    
    return {
      code: 0,
      message: 'success',
      data: sign
    };
  } catch (error) {
    request.log.error(error);
    return reply.code(500).send({
      code: 1,
      message: error.message,
      data: null
    });
  }
});

// 启动服务
const start = async () => {
  try {
    const port = process.env.PORT || 3000;
    await fastify.listen({ port, host: '0.0.0.0' });
    console.log(`✅ 签名服务启动成功！监听端口: ${port}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();

