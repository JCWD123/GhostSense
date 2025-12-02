/**
 * 🔍 在小红书页面中查找 x-s-common 生成代码
 * 
 * 使用方法：
 * 1. 打开 https://www.xiaohongshu.com （已登录）
 * 2. F12 → Sources 标签
 * 3. Ctrl+Shift+F（全局搜索）
 * 4. 搜索以下关键词（依次尝试）
 */

// ============================================
// 搜索关键词列表（按优先级排序）
// ============================================

const SEARCH_KEYWORDS = [
    // 直接搜索字段名
    '"x-s-common"',
    "'x-s-common'",
    'x-s-common',
    'xscommon',
    'xs-common',
    'XSCommon',
    
    // 搜索生成签名的函数名
    'getXsCommon',
    'generateXsCommon',
    'buildXsCommon',
    'createXsCommon',
    'makeXsCommon',
    'signCommon',
    'commonSign',
    
    // 搜索特征前缀（我们看到的固定开头）
    '2UQAPsHC',
    
    // 搜索Base64编码相关
    'btoa(',
    'atob(',
    'base64',
    
    // 搜索请求拦截器
    'request.interceptors',
    'axios.interceptors',
    'fetch(',
    
    // 搜索header设置
    'setRequestHeader',
    'headers[',
    '"headers"',
];

// ============================================
// 自动化搜索脚本（在 Console 运行）
// ============================================

console.log('🔍 开始搜索 x-s-common 生成代码...\n');
console.log('📝 推荐搜索路径：');
console.log('1. F12 → Sources → Ctrl+Shift+F');
console.log('2. 依次搜索以下关键词：\n');

SEARCH_KEYWORDS.forEach((keyword, index) => {
    console.log(`${index + 1}. ${keyword}`);
});

console.log('\n💡 搜索技巧：');
console.log('- 优先搜索 "x-s-common"（带引号）');
console.log('- 找到后，查看周围的代码上下文');
console.log('- 查找函数定义和调用链');
console.log('- 关注加密/编码相关的函数调用');

console.log('\n🎯 预期发现：');
console.log('- 生成 x-s-common 的主函数');
console.log('- 输入参数（URL、method、data等）');
console.log('- 加密/编码算法');
console.log('- 密钥或salt值');

// ============================================
// 拦截网络请求，监控 x-s-common 的添加
// ============================================

console.log('\n🕵️ 方法2：拦截 XMLHttpRequest');
console.log('运行以下代码监控请求：\n');

const interceptorCode = `
// 拦截 XMLHttpRequest
(function() {
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;
    
    let currentHeaders = {};
    
    XMLHttpRequest.prototype.open = function(...args) {
        currentHeaders = {};
        console.log('🌐 XHR Open:', args[0], args[1]);
        return originalOpen.apply(this, args);
    };
    
    XMLHttpRequest.prototype.setRequestHeader = function(header, value) {
        if (header.toLowerCase().includes('x-s') || header.toLowerCase().includes('common')) {
            console.log('🔑 发现关键Header:', header, '=', value.substring(0, 50) + '...');
            console.trace('调用栈：');
        }
        currentHeaders[header] = value;
        return originalSetRequestHeader.apply(this, arguments);
    };
    
    console.log('✅ XMLHttpRequest 拦截器已安装');
})();

// 拦截 fetch
(function() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        const [url, options] = args;
        
        if (options && options.headers) {
            const headers = options.headers;
            for (const key in headers) {
                if (key.toLowerCase().includes('x-s') || key.toLowerCase().includes('common')) {
                    console.log('🔑 Fetch发现关键Header:', key, '=', headers[key].substring(0, 50) + '...');
                    console.trace('调用栈：');
                }
            }
        }
        
        return originalFetch.apply(this, args);
    };
    
    console.log('✅ Fetch 拦截器已安装');
})();
`;

console.log(interceptorCode);

console.log('\n🎯 运行上述代码后，再次搜索，会在Console中看到：');
console.log('- x-s-common 是在哪个函数中设置的');
console.log('- 完整的调用栈');
console.log('- 可以直接点击调用栈跳转到源码！');






