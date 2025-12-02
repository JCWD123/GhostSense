/**
 * 测试详情接口签名获取
 * 诊断浏览器模式超时问题
 */

const { getXhsHeaders } = require('./src/playwright/xhs_browser');

async function test() {
  console.log('╔════════════════════════════════════════╗');
  console.log('║  测试详情接口签名获取                  ║');
  console.log('╚════════════════════════════════════════╝\n');

  const testNoteId = '68303bbb000000002100f85c';  // 替换为实际的 note_id
  
  console.log('📋 测试参数:');
  console.log(`   note_id: ${testNoteId}`);
  console.log('   URL: https://edith.xiaohongshu.com/api/sns/web/v1/note/detail');
  console.log('   Method: POST');
  console.log(`   Body: { note_id: "${testNoteId}", image_formats: ["jpg", "webp", "avif"] }\n`);

  console.log('⏰ 开始测试 (最长等待 60 秒)...\n');
  const startTime = Date.now();

  try {
    const headers = await getXhsHeaders({
      url: 'https://edith.xiaohongshu.com/api/sns/web/v1/note/detail',
      method: 'POST',
      data: {
        note_id: testNoteId,
        image_formats: ['jpg', 'webp', 'avif']
      },
      cookie: '',
      debugPort: 9222,  // 连接到 Electron
      headless: false   // 显示窗口便于调试
    });

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    
    console.log(`\n✅ 成功获取请求头 (用时 ${elapsed} 秒):`);
    console.log('   x-s:', headers['x-s'] ? headers['x-s'].substring(0, 30) + '...' : '❌ 空值');
    console.log('   x-t:', headers['x-t'] || '❌ 空值');
    console.log('   x-s-common:', headers['x-s-common'] ? headers['x-s-common'].substring(0, 30) + '...' : '❌ 空值');
    console.log('   x-b3-traceid:', headers['x-b3-traceid'] || '❌ 空值');

    // 验证必需的头
    const required = ['x-s', 'x-t', 'x-s-common', 'x-b3-traceid'];
    const missing = required.filter(key => !headers[key]);

    if (missing.length > 0) {
      console.log('\n❌ 缺少必需的请求头:', missing.join(', '));
      process.exit(1);
    } else {
      console.log('\n✅ 所有必需的请求头都已获取!');
      process.exit(0);
    }

  } catch (error) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
    console.error(`\n❌ 测试失败 (用时 ${elapsed} 秒):`, error.message);
    console.error('   堆栈:', error.stack);
    
    // 提供诊断建议
    console.log('\n💡 可能的原因:');
    if (error.message.includes('timeout') || elapsed > 25) {
      console.log('   1. 页面加载太慢或请求未触发');
      console.log('   2. Electron 窗口没有加载小红书页面');
      console.log('   3. 网络连接问题');
      console.log('\n🔧 建议:');
      console.log('   - 确保 Electron 已打开并加载小红书页面');
      console.log('   - 检查 Electron 调试端口: curl http://localhost:9222/json/version');
      console.log('   - 尝试手动在 Electron 中访问一个笔记详情页');
    } else if (error.message.includes('CDP') || error.message.includes('connect')) {
      console.log('   1. Electron 未运行或调试端口不正确');
      console.log('   2. 防火墙阻止了连接');
      console.log('\n🔧 建议:');
      console.log('   - 启动 Electron: cd frontend && npm run dev');
      console.log('   - 检查端口: netstat -an | grep 9222');
    }
    
    process.exit(1);
  }
}

// 添加总超时控制
const timeout = setTimeout(() => {
  console.error('\n❌ 测试超时 (60 秒)');
  console.log('💡 这表明请求拦截逻辑可能有问题');
  process.exit(1);
}, 60000);

test().finally(() => {
  clearTimeout(timeout);
});


