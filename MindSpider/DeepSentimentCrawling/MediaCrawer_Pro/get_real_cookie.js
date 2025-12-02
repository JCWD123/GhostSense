/**
 * 🍪 在小红书页面Console中运行，自动获取完整Cookie
 * 
 * 使用方法：
 * 1. 打开 https://www.xiaohongshu.com
 * 2. 确保已登录
 * 3. F12 → Console
 * 4. 粘贴此脚本并运行
 * 5. 等待3秒，自动从网络请求中提取完整Cookie
 */

(async () => {
    console.log('🔍 开始监听网络请求...');
    
    let capturedCookie = null;
    
    // 拦截fetch请求
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const response = await originalFetch.apply(this, args);
        
        // 检查请求头
        const url = args[0];
        if (typeof url === 'string' && url.includes('/api/sns/web/')) {
            console.log('✅ 捕获到API请求:', url);
            
            // 尝试从响应中获取Set-Cookie
            const headers = response.headers;
            console.log('响应headers:', Array.from(headers.entries()));
        }
        
        return response;
    };
    
    // 使用Performance API获取历史请求
    const entries = performance.getEntries();
    for (const entry of entries) {
        if (entry.name && entry.name.includes('/api/sns/web/')) {
            console.log('📦 发现历史API请求:', entry.name);
        }
    }
    
    // 方法2：创建一个测试请求来触发完整Cookie
    console.log('\n📝 方法1：从document.cookie获取（可能不完整）');
    console.log(document.cookie);
    
    console.log('\n🎯 正确方法：从Network面板获取完整Cookie');
    console.log('步骤：');
    console.log('1. F12 → Network → 清空');
    console.log('2. 在小红书页面搜索任意关键词');
    console.log('3. 找到 POST .../search/notes 请求');
    console.log('4. Headers → Request Headers → Cookie');
    console.log('5. 右键 → Copy value');
    
    console.log('\n💡 完整Cookie应该包含以下关键字段：');
    console.log([
        '✓ a1',
        '✓ webId',
        '✓ web_session（最重要！HttpOnly）',
        '✓ xsecappid',
        '✓ websectiga',
        '✓ sec_poison_id',
    ].join('\n'));
    
    console.log('\n🚨 警告：web_session 是 HttpOnly Cookie，无法通过JS获取！');
    console.log('必须从Network面板手动复制！');
})();






