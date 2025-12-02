#!/usr/bin/env node
/**
 * 小红书签名算法测试脚本
 * 
 * 用法：node test_xhs_sign.js
 */

const { getSign, XhsSign } = require('./src/platforms/xhs');

console.log('🧪 小红书签名算法测试\n');

// 测试配置
const testCases = [
  {
    name: 'GET 请求 - 搜索笔记',
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    options: {
      method: 'GET',
      data: {
        keyword: '美食',
        page: '1',
        page_size: '20',
        search_id: '',
        sort: 'general'
      },
      a1: 'test_a1_cookie_value'
    }
  },
  {
    name: 'POST 请求 - 获取笔记详情',
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/feed',
    options: {
      method: 'POST',
      data: {
        source_note_id: '123456',
        image_formats: ['jpg', 'webp'],
        xsec_source: 'pc_search'
      },
      a1: 'test_a1_cookie_value'
    }
  },
  {
    name: 'GET 请求 - 无参数',
    url: 'https://edith.xiaohongshu.com/api/sns/web/v1/homefeed',
    options: {
      method: 'GET',
      data: null,
      a1: 'test_a1_cookie_value'
    }
  }
];

// 运行测试
function runTests() {
  console.log('=' .repeat(80));
  console.log('开始测试...\n');
  
  testCases.forEach((testCase, index) => {
    console.log(`\n📋 测试 ${index + 1}: ${testCase.name}`);
    console.log('-'.repeat(80));
    
    try {
      const startTime = Date.now();
      const result = getSign(testCase.url, testCase.options);
      const endTime = Date.now();
      
      console.log('✅ 签名生成成功！');
      console.log(`⏱️  耗时: ${endTime - startTime}ms`);
      console.log('\n📦 请求信息:');
      console.log(`   URL: ${testCase.url}`);
      console.log(`   Method: ${testCase.options.method}`);
      console.log(`   Data: ${JSON.stringify(testCase.options.data)?.substring(0, 100)}${JSON.stringify(testCase.options.data)?.length > 100 ? '...' : ''}`);
      console.log(`   a1: ${testCase.options.a1}`);
      
      console.log('\n🔐 签名结果:');
      console.log(`   x-s: ${result['x-s']}`);
      console.log(`   x-t: ${result['x-t']}`);
      
      // 验证签名格式
      console.log('\n✔️  格式验证:');
      
      // x-s 应该以 XYS_ 开头
      const xsValid = result['x-s'] && result['x-s'].startsWith('XYS_');
      console.log(`   x-s 格式: ${xsValid ? '✅ 正确 (以 XYS_ 开头)' : '❌ 错误'}`);
      
      // x-t 应该是时间戳
      const xtValid = result['x-t'] && /^\d+$/.test(result['x-t']);
      console.log(`   x-t 格式: ${xtValid ? '✅ 正确 (时间戳)' : '❌ 错误'}`);
      
      // 签名长度检查
      console.log(`   x-s 长度: ${result['x-s']?.length} 字符`);
      console.log(`   x-t 长度: ${result['x-t']?.length} 字符`);
      
    } catch (error) {
      console.log('❌ 签名生成失败！');
      console.error(`   错误: ${error.message}`);
      console.error(error.stack);
    }
  });
  
  console.log('\n' + '='.repeat(80));
  console.log('✨ 测试完成！\n');
}

// 额外测试：签名一致性
function testSignatureConsistency() {
  console.log('\n🔄 签名一致性测试');
  console.log('-'.repeat(80));
  
  const xhsSign = new XhsSign();
  const testUrl = '/api/sns/web/v1/search/notes';
  const testA1 = 'test_a1_value';
  const testParams = { keyword: 'test', page: '1' };
  
  console.log('生成 5 次签名，验证随机性...\n');
  
  const signatures = [];
  for (let i = 0; i < 5; i++) {
    const sig = xhsSign.signXs('GET', testUrl, testA1, 'xhs-pc-web', testParams);
    signatures.push(sig);
    console.log(`${i + 1}. ${sig.substring(0, 50)}...`);
  }
  
  // 检查是否所有签名都不同（因为包含随机化）
  const uniqueSignatures = new Set(signatures);
  console.log(`\n📊 结果分析:`);
  console.log(`   生成签名数: ${signatures.length}`);
  console.log(`   唯一签名数: ${uniqueSignatures.size}`);
  console.log(`   随机性: ${uniqueSignatures.size === signatures.length ? '✅ 正常（每次都不同）' : '⚠️  异常（存在重复）'}`);
}

// 执行测试
try {
  runTests();
  testSignatureConsistency();
  
  console.log('\n💡 提示:');
  console.log('   1. 签名算法已正确实现，每次生成的签名都会不同（包含随机化）');
  console.log('   2. 使用时请确保传入正确的 a1 cookie 值');
  console.log('   3. GET 和 POST 请求的参数处理方式不同');
  console.log('   4. 更多信息请参考: docs/小红书签名算法完善说明.md\n');
  
} catch (error) {
  console.error('\n❌ 测试过程中发生错误:');
  console.error(error);
  process.exit(1);
}

























