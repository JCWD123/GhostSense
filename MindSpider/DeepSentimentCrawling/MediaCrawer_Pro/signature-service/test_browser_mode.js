#!/usr/bin/env node
/**
 * 浏览器模式诊断测试脚本
 * 
 * 用途：
 * 1. 检查Electron连接
 * 2. 测试Playwright浏览器模式
 * 3. 提供详细的错误诊断
 */

const { chromium } = require('playwright');
const http = require('http');

// 配置
const ELECTRON_PORT = 9222;
const TEST_URL = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes';

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

function log(type, message) {
  const prefix = {
    info: `${colors.blue}ℹ${colors.reset}`,
    success: `${colors.green}✓${colors.reset}`,
    error: `${colors.red}✗${colors.reset}`,
    warn: `${colors.yellow}⚠${colors.reset}`
  };
  console.log(`${prefix[type] || '•'} ${message}`);
}

// 测试1：检查Electron调试端口
async function testElectronPort() {
  log('info', '测试1: 检查Electron调试端口');
  console.log('----------------------------------------');
  
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${ELECTRON_PORT}/json/version`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const version = JSON.parse(data);
          log('success', `Electron调试端口正常 (端口 ${ELECTRON_PORT})`);
          log('info', `   浏览器: ${version.Browser}`);
          log('info', `   协议版本: ${version['Protocol-Version']}`);
          resolve(true);
        } catch (e) {
          log('error', '端口响应但数据格式错误');
          resolve(false);
        }
      });
    });

    req.on('error', (err) => {
      log('error', `Electron调试端口不可用 (端口 ${ELECTRON_PORT})`);
      log('warn', '可能原因:');
      console.log('   1. Electron应用未运行');
      console.log('   2. 调试端口未开启或端口号错误');
      console.log('');
      log('info', '解决方法:');
      console.log('   cd frontend');
      console.log('   npm run electron:dev');
      resolve(false);
    });

    req.setTimeout(3000, () => {
      req.destroy();
      log('error', '连接超时');
      resolve(false);
    });
  });
}

// 测试2：CDP连接
async function testCDPConnection() {
  log('info', '测试2: CDP协议连接');
  console.log('----------------------------------------');
  
  try {
    log('info', `尝试连接到 http://localhost:${ELECTRON_PORT}`);
    const browser = await chromium.connectOverCDP(`http://localhost:${ELECTRON_PORT}`);
    log('success', 'CDP连接成功');
    
    const contexts = browser.contexts();
    log('info', `找到 ${contexts.length} 个浏览器上下文`);
    
    if (contexts.length > 0) {
      const pages = contexts[0].pages();
      log('info', `找到 ${pages.length} 个页面`);
    }
    
    await browser.close();
    return true;
  } catch (error) {
    log('error', `CDP连接失败: ${error.message}`);
    log('warn', '可能原因:');
    console.log('   1. Electron未开启远程调试');
    console.log('   2. CDP协议版本不兼容');
    console.log('');
    log('info', '检查Electron配置 (electron/main.js):');
    console.log("   app.commandLine.appendSwitch('--remote-debugging-port', '9222');");
    return false;
  }
}

// 测试3：启动独立浏览器
async function testStandaloneBrowser() {
  log('info', '测试3: 启动独立Playwright浏览器');
  console.log('----------------------------------------');
  
  try {
    log('info', '启动Chromium...');
    const browser = await chromium.launch({
      headless: true,
      args: ['--disable-blink-features=AutomationControlled']
    });
    log('success', '浏览器启动成功');
    
    const context = await browser.newContext();
    const page = await context.newPage();
    log('success', '页面创建成功');
    
    log('info', '测试导航到小红书...');
    await page.goto('https://www.xiaohongshu.com', {
      waitUntil: 'domcontentloaded',
      timeout: 10000
    });
    log('success', '页面加载成功');
    
    await browser.close();
    return true;
  } catch (error) {
    log('error', `浏览器启动失败: ${error.message}`);
    
    if (error.message.includes('Executable')) {
      log('warn', 'Chromium未安装');
      log('info', '解决方法:');
      console.log('   npx playwright install chromium');
    }
    return false;
  }
}

// 测试4：完整浏览器模式测试
async function testFullBrowserMode() {
  log('info', '测试4: 完整浏览器模式（连接Electron）');
  console.log('----------------------------------------');
  
  try {
    // 连接到Electron
    const browser = await chromium.connectOverCDP(`http://localhost:${ELECTRON_PORT}`);
    const contexts = browser.contexts();
    
    let page;
    if (contexts.length > 0 && contexts[0].pages().length > 0) {
      page = contexts[0].pages()[0];
      log('success', '复用现有页面');
    } else {
      const context = contexts.length > 0 ? contexts[0] : await browser.newContext();
      page = await context.newPage();
      log('success', '创建新页面');
    }
    
    // 导航到小红书
    log('info', '导航到小红书...');
    await page.goto('https://www.xiaohongshu.com/explore', {
      waitUntil: 'domcontentloaded',
      timeout: 15000
    });
    log('success', '页面加载成功');
    
    // 测试拦截
    let intercepted = false;
    await page.route('**/*', async (route) => {
      const url = route.request().url();
      if (url.includes('/api/sns/')) {
        intercepted = true;
        log('success', `成功拦截API请求: ${url.substring(0, 60)}...`);
      }
      await route.continue();
    });
    
    log('info', '注入测试请求...');
    await page.evaluate(() => {
      fetch('https://edith.xiaohongshu.com/api/sns/web/v1/search/notes?keyword=test', {
        credentials: 'include'
      }).catch(() => {});
    });
    
    // 等待拦截
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    if (intercepted) {
      log('success', '请求拦截正常工作');
    } else {
      log('warn', '未能拦截到API请求（可能网络问题）');
    }
    
    await browser.close();
    return true;
  } catch (error) {
    log('error', `完整测试失败: ${error.message}`);
    return false;
  }
}

// 主函数
async function main() {
  console.log('');
  console.log('╔════════════════════════════════════════╗');
  console.log('║  Playwright浏览器模式诊断工具        ║');
  console.log('╚════════════════════════════════════════╝');
  console.log('');

  const results = [];
  
  // 执行测试
  results.push(await testElectronPort());
  console.log('');
  
  if (results[0]) {
    results.push(await testCDPConnection());
    console.log('');
  } else {
    log('warn', '跳过CDP连接测试（Electron端口不可用）');
    results.push(false);
    console.log('');
  }
  
  results.push(await testStandaloneBrowser());
  console.log('');
  
  if (results[0] && results[1]) {
    results.push(await testFullBrowserMode());
    console.log('');
  } else {
    log('warn', '跳过完整浏览器模式测试');
    results.push(false);
    console.log('');
  }
  
  // 汇总
  console.log('╔════════════════════════════════════════╗');
  console.log('║  测试结果汇总                          ║');
  console.log('╚════════════════════════════════════════╝');
  console.log('');
  
  const tests = [
    'Electron调试端口',
    'CDP协议连接',
    '独立浏览器启动',
    '完整浏览器模式'
  ];
  
  tests.forEach((test, i) => {
    log(results[i] ? 'success' : 'error', test);
  });
  
  console.log('');
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  if (passed === total) {
    log('success', `所有测试通过 (${passed}/${total})`);
    console.log('');
    log('info', '浏览器模式配置正常，可以使用！');
  } else {
    log('warn', `部分测试失败 (${passed}/${total})`);
    console.log('');
    log('info', '建议操作:');
    if (!results[0]) {
      console.log('   1. 启动Electron应用: cd frontend && npm run electron:dev');
    }
    if (!results[2]) {
      console.log('   2. 安装Playwright浏览器: npx playwright install chromium');
    }
  }
  
  console.log('');
}

// 运行
main().catch(error => {
  console.error('测试运行失败:', error);
  process.exit(1);
});


