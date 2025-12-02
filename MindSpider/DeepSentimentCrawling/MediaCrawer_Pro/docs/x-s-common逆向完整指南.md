#!/usr/bin/env node
/**
 * 小红书 x-s-common 签名算法
 * 
 * 说明：
 * x-s-common 是小红书的设备指纹签名
 * 用于标识客户端环境，相对固定
 * 
 * ⚠️ 注意：
 * 1. 这是基于逆向分析的实现，可能随小红书更新而失效
 * 2. 需要根据实际抓包结果调整算法
 * 3. 如果小红书加密算法复杂，可能需要更详细的逆向工作
 */

const crypto = require('crypto');

/**
 * 生成 x-s-common
 * 
 * @param {Object} options 配置选项
 * @param {string} options.deviceId 设备ID（从webId提取）
 * @param {string} options.a1 用户a1 Cookie
 * @param {string} options.platform 平台标识
 * @param {string} options.version 版本号
 * @returns {string} x-s-common 签名
 */
function generateXsCommon(options = {}) {
  const {
    deviceId = '',
    a1 = '',
    platform = 'PC',
    version = '1.0.0',
    timestamp = Date.now()
  } = options;
  
  // ========================================
  // 方案1：基础实现（如果小红书算法较简单）
  // ========================================
  
  // 1. 拼接基础数据
  const baseData = [
    platform,
    version,
    deviceId || 'unknown',
    a1 ? a1.substring(0, 16) : 'guest',  // 使用a1的前16位
    Math.floor(timestamp / 1000)  // 秒级时间戳
  ].join('|');
  
  // 2. MD5哈希
  const hash = crypto.createHash('md5').update(baseData).digest('hex');
  
  // 3. 取前32位，转Base64
  const xs_common = Buffer.from(hash.substring(0, 32)).toString('base64');
  
  // 4. 格式化（小红书可能有特定格式）
  const formatted = `2UQAPsHC+${xs_common.substring(0, 32)}`;
  
  return formatted;
  
  // ========================================
  // 方案2：完整实现（如果需要更复杂的逆向）
  // ========================================
  
  /*
  // 如果x-s-common算法更复杂，可能需要：
  
  // 1. 获取浏览器指纹
  const fingerprint = getDeviceFingerprint();
  
  // 2. 使用自定义加密算法
  const encrypted = customEncrypt(baseData, fingerprint);
  
  // 3. 特定的编码方式
  const encoded = customBase64Encode(encrypted);
  
  return encoded;
  */
}

/**
 * 获取设备指纹（如果x-s-common需要）
 * 
 * @returns {string} 设备指纹
 */
function getDeviceFingerprint() {
  // 浏览器指纹通常包含：
  // - User-Agent
  // - 屏幕分辨率
  // - 时区
  // - 语言
  // - Canvas指纹
  // - WebGL指纹
  // 等等
  
  // Node.js环境下，我们需要模拟这些信息
  const fingerprint = {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    screenResolution: '1920x1080',
    timezone: -480,  // GMT+8
    language: 'zh-CN',
    platform: 'Win32'
  };
  
  return JSON.stringify(fingerprint);
}

/**
 * 自定义加密函数（根据实际逆向结果实现）
 * 
 * @param {string} data 待加密数据
 * @param {string} key 密钥
 * @returns {string} 加密结果
 */
function customEncrypt(data, key) {
  // TODO: 根据实际逆向的小红书加密算法实现
  
  // 示例：简单的XOR加密
  let result = '';
  for (let i = 0; i < data.length; i++) {
    result += String.fromCharCode(
      data.charCodeAt(i) ^ key.charCodeAt(i % key.length)
    );
  }
  
  return result;
}

/**
 * 验证 x-s-common 是否有效
 * 
 * @param {string} xsCommon x-s-common值
 * @returns {boolean} 是否有效
 */
function validateXsCommon(xsCommon) {
  // 基本验证
  if (!xsCommon || typeof xsCommon !== 'string') {
    return false;
  }
  
  // 长度验证（根据实际情况调整）
  if (xsCommon.length < 20 || xsCommon.length > 100) {
    return false;
  }
  
  // 格式验证（如果有固定前缀）
  if (!xsCommon.startsWith('2UQAPsHC')) {
    return false;
  }
  
  return true;
}

module.exports = {
  generateXsCommon,
  getDeviceFingerprint,
  validateXsCommon
};







