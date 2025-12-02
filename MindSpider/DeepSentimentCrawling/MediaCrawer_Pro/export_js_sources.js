/**
 * 导出小红书所有JS源码，方便离线分析
 * 在 Console 中运行
 */

(async () => {
    console.log('🔍 开始导出所有JS源码...\n');
    
    // 获取所有脚本URL
    const scripts = Array.from(document.querySelectorAll('script[src]'))
        .map(s => s.src)
        .filter(src => src.includes('xiaohongshu') || src.includes('xhscdn'));
    
    console.log(`📦 发现 ${scripts.length} 个JS文件\n`);
    
    // 打印所有URL
    scripts.forEach((url, i) => {
        console.log(`${i + 1}. ${url}`);
    });
    
    console.log('\n💡 关键文件（重点关注）：');
    
    const keyFiles = scripts.filter(url => 
        url.includes('sign') || 
        url.includes('encrypt') || 
        url.includes('common') ||
        url.includes('security') ||
        url.includes('shield') ||
        url.includes('sec')
    );
    
    if (keyFiles.length > 0) {
        keyFiles.forEach(url => {
            console.log(`🔑 ${url}`);
        });
    } else {
        console.log('⚠️ 未找到明显的加密相关文件');
        console.log('可能代码在主bundle中或被高度混淆');
    }
    
    console.log('\n📝 导出方法：');
    console.log('1. Sources → 找到目标JS文件');
    console.log('2. 右键 → Save as...');
    console.log('3. 或使用curl下载：');
    console.log('   curl "URL" -o filename.js');
})();






