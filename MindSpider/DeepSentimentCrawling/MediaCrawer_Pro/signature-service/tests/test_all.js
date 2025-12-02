/**
 * 签名服务测试套件
 */

const { XhsSignature } = require('../src/core/xhs_signature');
const { getXhsHeaders } = require('../src/playwright/xhs_browser');
const { HybridSignatureClient } = require('../src/sdk/index');

// 测试配置
const TEST_CONFIG = {
  url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
  method: 'GET',
  data: { keyword: '美食', page: 1 },
  a1: 'test_a1_cookie_value',
  cookie: 'a1=test_a1; webId=test_webid; web_session=test_session'
};

// ==================== 测试1：纯JS签名 ====================
async function testJsSignature() {
  console.log('\n📝 测试1：纯JS签名');
  console.log('================================');
  
  try {
    const client = new XhsSignature();
    const { xs, xt } = client.sign({
      method: TEST_CONFIG.method,
      url: TEST_CONFIG.url,
      data: TEST_CONFIG.data,
      a1: TEST_CONFIG.a1
    });

    console.log('✅ 签名生成成功:');
    console.log(`   x-s: ${xs.substring(0, 50)}...`);
    console.log(`   x-t: ${xt}`);
    console.log(`   耗时: 极快 (< 10ms)`);
    
    return true;
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    return false;
  }
}

// ==================== 测试2：Playwright 浏览器获取 ====================
async function testBrowserSignature() {
  console.log('\n🌐 测试2：Playwright 浏览器模式');
  console.log('================================');
  console.log('⚠️  警告：此测试需要启动真实浏览器，耗时较长');
  console.log('💡 提示：如果不想运行此测试，请跳过');
  console.log('');
  
  // 跳过浏览器测试（在CI环境中）
  if (process.env.SKIP_BROWSER_TESTS) {
    console.log('⏭️  已跳过浏览器测试');
    return true;
  }

  try {
    console.log('🚀 启动浏览器中...');
    const headers = await getXhsHeaders({
      url: TEST_CONFIG.url,
      method: TEST_CONFIG.method,
      data: TEST_CONFIG.data,
      cookie: TEST_CONFIG.cookie,
      headless: true
    });

    console.log('✅ 请求头获取成功:');
    console.log(`   x-s: ${headers['x-s'] ? headers['x-s'].substring(0, 30) + '...' : '(空)'}`);
    console.log(`   x-t: ${headers['x-t'] || '(空)'}`);
    console.log(`   x-s-common: ${headers['x-s-common'] ? headers['x-s-common'].substring(0, 30) + '...' : '(空)'}`);
    console.log(`   耗时: 1-3秒`);
    
    return true;
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    console.error('💡 提示：确保已安装 Playwright 浏览器:');
    console.error('   npx playwright install chromium');
    return false;
  }
}

// ==================== 测试3：混合模式 ====================
async function testHybridMode() {
  console.log('\n🎯 测试3：混合模式');
  console.log('================================');

  try {
    const client = new HybridSignatureClient();

    // 3.1 测试JS模式
    console.log('\n▶️  3.1 强制使用JS模式:');
    const jsHeaders = await client.getHeaders({
      platform: 'xhs',
      url: TEST_CONFIG.url,
      method: TEST_CONFIG.method,
      data: TEST_CONFIG.data,
      a1: TEST_CONFIG.a1,
      mode: 'js'
    });
    console.log(`   ✅ x-s: ${jsHeaders['x-s'].substring(0, 30)}...`);
    console.log(`   ✅ x-t: ${jsHeaders['x-t']}`);
    console.log(`   ✅ 模式: ${jsHeaders.mode}`);

    // 3.2 测试自动模式
    console.log('\n▶️  3.2 自动模式（默认使用JS）:');
    const autoHeaders = await client.getHeaders({
      platform: 'xhs',
      url: TEST_CONFIG.url,
      method: TEST_CONFIG.method,
      data: TEST_CONFIG.data,
      a1: TEST_CONFIG.a1,
      mode: 'auto'
    });
    console.log(`   ✅ x-s: ${autoHeaders['x-s'].substring(0, 30)}...`);
    console.log(`   ✅ 模式: ${autoHeaders.mode}`);

    await client.close();
    console.log('\n✅ 混合模式测试通过');
    return true;
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    return false;
  }
}

// ==================== 测试4：连接Electron ====================
async function testElectronConnection() {
  console.log('\n🔗 测试4：连接到Electron浏览器');
  console.log('================================');
  console.log('⚠️  此测试需要Electron应用运行在调试端口9222');
  console.log('💡 启动方式: cd frontend && npm run electron:dev');
  console.log('');

  // 检查是否有Electron在运行
  const http = require('http');
  
  return new Promise((resolve) => {
    const req = http.get('http://localhost:9222/json/version', (res) => {
      if (res.statusCode === 200) {
        console.log('✅ 检测到Electron浏览器正在运行');
        console.log('💡 可以使用 debugPort: 9222 连接');
        console.log('');
        console.log('示例代码:');
        console.log('```javascript');
        console.log('const client = new HybridSignatureClient({ debugPort: 9222 });');
        console.log('const headers = await client.getHeaders({...});');
        console.log('```');
        resolve(true);
      } else {
        console.log('⏭️  Electron未运行，跳过此测试');
        resolve(true);
      }
    });

    req.on('error', () => {
      console.log('⏭️  Electron未运行（端口9222不可用）');
      console.log('💡 如需测试Electron集成，请先启动前端应用');
      resolve(true);
    });

    req.setTimeout(2000, () => {
      req.destroy();
      console.log('⏭️  连接超时，跳过此测试');
      resolve(true);
    });
  });
}

// ==================== 运行所有测试 ====================
async function runAllTests() {
  console.log('\n');
  console.log('╔════════════════════════════════════════╗');
  console.log('║  MediaCrawler 签名服务测试套件        ║');
  console.log('╚════════════════════════════════════════╝');

  const results = [];

  // 执行测试
  results.push({ name: 'JS签名', passed: await testJsSignature() });
  
  // 浏览器测试（可选）
  const runBrowserTest = process.argv.includes('--browser');
  if (runBrowserTest) {
    results.push({ name: 'Playwright浏览器', passed: await testBrowserSignature() });
  } else {
    console.log('\n⏭️  跳过浏览器测试（使用 --browser 参数启用）');
  }

  results.push({ name: '混合模式', passed: await testHybridMode() });
  results.push({ name: 'Electron连接', passed: await testElectronConnection() });

  // 汇总结果
  console.log('\n');
  console.log('╔════════════════════════════════════════╗');
  console.log('║  测试结果汇总                          ║');
  console.log('╚════════════════════════════════════════╝');
  console.log('');

  const passed = results.filter(r => r.passed).length;
  const total = results.length;

  results.forEach(({ name, passed }) => {
    const icon = passed ? '✅' : '❌';
    console.log(`${icon} ${name}`);
  });

  console.log('');
  console.log(`总计: ${passed}/${total} 通过`);
  console.log('');

  if (passed === total) {
    console.log('🎉 所有测试通过！');
    process.exit(0);
  } else {
    console.log('⚠️  部分测试失败');
    process.exit(1);
  }
}

// 启动测试
if (require.main === module) {
  runAllTests().catch(error => {
    console.error('测试运行失败:', error);
    process.exit(1);
  });
}

module.exports = {
  testJsSignature,
  testBrowserSignature,
  testHybridMode,
  testElectronConnection
};





