/**
 * x-s-common 生成（初步实现）
 * 基于逆向分析的小红书代码
 */

const crypto = require('crypto');

/**
 * 生成 x-s-common
 * @param {Object} options
 * @param {string} options.url - 请求URL
 * @param {string} options.a1 - Cookie中的a1字段
 * @param {string} options.webId - Cookie中的webId字段
 * @returns {string} x-s-common值
 */
function generateXsCommon(options = {}) {
    const {
        url = '',
        a1 = '',
        webId = ''
    } = options;

    // 构建参数对象（基于逆向代码）
    const payload = {
        s0: 5,  // 平台类型，PC通常是5
        s1: '',
        x0: '1',  // 默认值，可能需要从实际请求中获取
        x1: '3.7.8-2',  // 版本标识
        x2: 'Windows',  // 或 'PC'
        x3: 'xhs-pc-web',
        x4: '4.86.0',  // webBuild版本，与请求中的一致
        x5: a1 || '',  // cookie中的a1
        x6: '',  // 可能是x-s或其他签名
        x7: '',  // 可能是x-t
        x8: webId || '',  // fingerprint，通常是webId
        x9: '',  // hash值，稍后计算
        x10: 1,  // 签名计数
        x11: 'normal'
    };

    // 计算 x9 (hash of x6+x7+x8)
    payload.x9 = simpleHash(payload.x6 + payload.x7 + payload.x8);

    // 1. JSON序列化
    const jsonStr = JSON.stringify(payload);

    // 2. 加密（这里先用简单的替换，实际需要找到p.lz的实现）
    const encrypted = encryptLz(jsonStr);

    // 3. Base64编码
    const xsCommon = base64Encode(encrypted);

    return xsCommon;
}

/**
 * 简单hash函数（模拟 p.tb）
 * 实际实现需要找到真实的hash算法
 */
function simpleHash(str) {
    if (!str) return '';
    return crypto.createHash('md5').update(str).digest('hex').substring(0, 16);
}

/**
 * 加密函数（模拟 p.lz）
 * 基于推测的简化实现
 */
function encryptLz(data) {
    // 注意：这是推测性实现，可能不准确
    // 真实的 p.lz 可能使用 RC4、AES 或自定义算法
    
    // 方案1：简单XOR（最简单的混淆）
    const key = "xhs2024"; // 可能的密钥
    const result = [];
    for (let i = 0; i < data.length; i++) {
        result.push(data.charCodeAt(i) ^ key.charCodeAt(i % key.length));
    }
    return Buffer.from(result);
    
    // 方案2：如果上面不work，可能需要RC4
    // return rc4Encrypt(data, key);
}

/**
 * Base64编码（模拟 p.xE）
 */
function base64Encode(data) {
    if (Buffer.isBuffer(data)) {
        return data.toString('base64');
    }
    return Buffer.from(data, 'utf-8').toString('base64');
}

module.exports = {
    generateXsCommon
};

// 测试
if (require.main === module) {
    const result = generateXsCommon({
        url: '/api/sns/web/v1/search/notes',
        a1: 'test_a1_value',
        webId: 'test_webid'
    });
    
    console.log('生成的 x-s-common:');
    console.log(result);
    console.log('\n长度:', result.length);
    console.log('前50字符:', result.substring(0, 50));
}

