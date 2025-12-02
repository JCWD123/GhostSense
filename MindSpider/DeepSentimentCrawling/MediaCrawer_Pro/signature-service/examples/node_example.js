/**
 * Node.js 使用示例
 * 
 * 展示如何在 Node.js 项目中使用签名SDK
 */

const { 
  HybridSignatureClient, 
  XhsSignature,
  getSignature 
} = require('../src/sdk/index');

// ==================== 示例1：纯JS签名（最快） ====================
async function example1_jsSignature() {
  console.log('\n📝 示例1：纯JS签名');
  console.log('================================');
  
  const client = new XhsSignature();
  
  const { xs, xt } = client.sign({
    method: 'GET',
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    data: { keyword: '美食', page: 1 },
    a1: 'your_a1_cookie'
  });
  
  console.log('签名结果:');
  console.log('x-s:', xs.substring(0, 50) + '...');
  console.log('x-t:', xt);
  
  // 使用签名发起请求
  const response = await fetch(
    'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes?keyword=美食&page=1',
    {
      headers: {
        'x-s': xs,
        'x-t': xt,
        'cookie': 'a1=your_a1_cookie; ...'
      }
    }
  );
  
  console.log('请求状态:', response.status);
}

// ==================== 示例2：Playwright浏览器获取 ====================
async function example2_browserSignature() {
  console.log('\n🌐 示例2：Playwright浏览器获取（完整）');
  console.log('================================');
  
  // 快速获取（单次使用）
  const headers = await getSignature({
    platform: 'xhs',
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    method: 'GET',
    data: { keyword: '美食', page: 1 },
    cookie: 'a1=xxx; webId=xxx; web_session=xxx',
    mode: 'browser'
  });
  
  console.log('完整请求头:');
  console.log('x-s:', headers['x-s']?.substring(0, 30) + '...');
  console.log('x-t:', headers['x-t']);
  console.log('x-s-common:', headers['x-s-common']?.substring(0, 30) + '...');
  console.log('模式:', headers.mode);
}

// ==================== 示例3：混合模式（推荐） ====================
async function example3_hybridMode() {
  console.log('\n🎯 示例3：混合模式（推荐）');
  console.log('================================');
  
  const client = new HybridSignatureClient();
  
  // 自动模式：默认使用JS，需要时自动切换到浏览器
  const headers = await client.getHeaders({
    platform: 'xhs',
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    method: 'GET',
    data: { keyword: '美食', page: 1 },
    a1: 'your_a1_cookie',
    cookie: 'complete_cookie_string',
    mode: 'auto'  // 自动选择
  });
  
  console.log('获取的签名:');
  console.log('x-s:', headers['x-s']?.substring(0, 30) + '...');
  console.log('x-t:', headers['x-t']);
  console.log('使用的模式:', headers.mode);
  
  await client.close();
}

// ==================== 示例4：连接到Electron ====================
async function example4_electronIntegration() {
  console.log('\n🔗 示例4：连接到Electron浏览器');
  console.log('================================');
  
  // 连接到Electron的调试端口（9222）
  const client = new HybridSignatureClient({
    debugPort: 9222  // Electron 调试端口
  });
  
  try {
    const headers = await client.getHeaders({
      platform: 'xhs',
      url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
      method: 'GET',
      data: { keyword: '美食' },
      cookie: 'your_cookie',
      mode: 'browser'
    });
    
    console.log('✅ 成功从Electron获取签名');
    console.log('x-s:', headers['x-s']?.substring(0, 30) + '...');
    
    await client.close();
  } catch (error) {
    console.error('❌ 连接Electron失败:', error.message);
    console.log('💡 确保Electron应用正在运行，且启用了调试端口9222');
  }
}

// ==================== 示例5：HTTP API调用 ====================
async function example5_httpApi() {
  console.log('\n🌐 示例5：通过HTTP API调用');
  console.log('================================');
  
  // 启动签名服务: npm start
  const API_URL = 'http://localhost:3100';
  
  // 5.1 纯JS签名
  const jsResponse = await fetch(`${API_URL}/sign/xhs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
      method: 'GET',
      data: { keyword: '美食' },
      a1: 'your_a1_cookie'
    })
  });
  
  const jsResult = await jsResponse.json();
  console.log('JS签名结果:', jsResult);
  
  // 5.2 浏览器模式
  const browserResponse = await fetch(`${API_URL}/sign/xhs/browser`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
      method: 'GET',
      data: { keyword: '美食' },
      cookie: 'complete_cookie_string'
    })
  });
  
  const browserResult = await browserResponse.json();
  console.log('浏览器模式结果:', browserResult);
}

// ==================== 运行所有示例 ====================
async function runAllExamples() {
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║  MediaCrawler 签名SDK 使用示例        ║');
  console.log('╚════════════════════════════════════════╝');
  
  try {
    await example1_jsSignature();
    // await example2_browserSignature();  // 取消注释以运行
    await example3_hybridMode();
    // await example4_electronIntegration();  // 需要Electron运行
    // await example5_httpApi();  // 需要签名服务运行
    
    console.log('\n✅ 所有示例运行完成');
  } catch (error) {
    console.error('\n❌ 示例运行出错:', error);
  }
}

if (require.main === module) {
  runAllExamples();
}

module.exports = {
  example1_jsSignature,
  example2_browserSignature,
  example3_hybridMode,
  example4_electronIntegration,
  example5_httpApi
};





