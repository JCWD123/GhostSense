/**
 * 🧪 在小红书页面Console中直接运行，测试API是否返回数据
 * 这样可以排除时效性和环境问题
 */

(async () => {
    console.log('🧪 开始测试小红书搜索API...\n');
    
    const url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes';
    
    const payload = {
        keyword: '美食',
        page: 1,
        page_size: 20,
        sort: 'general',
        note_type: 0
    };
    
    try {
        console.log('📝 请求参数:', payload);
        console.log('🚀 发送请求...\n');
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            credentials: 'include'  // 自动带上Cookie
        });
        
        console.log('📡 响应状态:', response.status);
        
        const data = await response.json();
        
        console.log('\n📦 响应数据:');
        console.log('  - code:', data.code);
        console.log('  - success:', data.success);
        console.log('  - msg:', data.msg);
        
        if (data.success) {
            const items = data.data?.items || [];
            const has_more = data.data?.has_more || false;
            
            console.log('\n🎉 返回结果:');
            console.log('  - 笔记数:', items.length);
            console.log('  - has_more:', has_more);
            
            if (items.length > 0) {
                console.log('\n📝 前3条笔记:');
                items.slice(0, 3).forEach((item, i) => {
                    const note = item.note_card || {};
                    console.log(`  ${i + 1}. ${note.display_title}`);
                    console.log(`     ID: ${note.note_id}`);
                    console.log(`     作者: ${note.user?.nickname}`);
                });
                
                console.log('\n' + '='.repeat(80));
                console.log('✅ 成功！浏览器环境可以获取数据！');
                console.log('='.repeat(80));
                console.log('\n💡 结论：不是IP或Cookie问题，是Python环境的问题');
                console.log('可能是：');
                console.log('  1. 签名时效性（需要实时生成x-s-common）');
                console.log('  2. TLS指纹差异（Python httpx vs 浏览器）');
                console.log('  3. 请求头顺序或格式差异');
            } else {
                console.log('\n' + '='.repeat(80));
                console.log('⚠️ 返回0条结果（即使在浏览器中）');
                console.log('='.repeat(80));
                console.log('\n💡 可能原因：');
                console.log('  1. 账号被风控（降低请求频率，等待1小时）');
                console.log('  2. IP被封（需要更换IP或使用代理）');
                console.log('  3. 关键词"美食"被特殊限制（尝试其他关键词）');
                console.log('\n🧪 建议测试：');
                console.log('  - 尝试搜索其他关键词（如"旅游"、"穿搭"）');
                console.log('  - 等待1小时后再试');
                console.log('  - 更换网络（手机热点）');
            }
        } else {
            console.log('\n❌ API返回失败:', data.msg);
        }
        
    } catch (error) {
        console.error('\n❌ 请求失败:', error);
    }
})();






