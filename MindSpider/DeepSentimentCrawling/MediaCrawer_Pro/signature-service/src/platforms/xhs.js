/**
 * 小红书签名算法 - 基于 xhshow 项目
 * 
 * 生成 x-s 和 x-t 签名
 * 参考: https://github.com/Cloxl/xhshow
 */

const crypto = require('crypto');

// ==================== 配置常量 ====================
const CONFIG = {
  // 基础常量
  MAX_32BIT: 0xFFFFFFFF,
  MAX_SIGNED_32BIT: 0x7FFFFFFF,
  
  // Base58 字母表
  BASE58_ALPHABET: "NOPQRStuvwxWXYZabcyz012DEFTKLMdefghijkl4563GHIJBC7mnop89+/AUVqrsOPQefghijkABCDEFGuvwz0123456789xy",
  
  // Base64 自定义字母表
  STANDARD_BASE64_ALPHABET: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
  CUSTOM_BASE64_ALPHABET: "ZmserbBoHQtNP+wOcza/LpngG8yJq42KWYj0DSfdikx3VT16IlUAFM97hECvuRX5",
  
  // XOR 密钥
  HEX_KEY: "af572b95ca65b2d9ec76bb5d2e97cb653299cc663399cc663399cce673399cce6733190c06030100000000008040209048241289c4e271381c0e0703018040a05028148ac56231180c0683c16030984c2693c964b259ac56abd5eaf5fafd7e3f9f4f279349a4d2e9743a9d4e279349a4d2e9f47a3d1e8f47239148a4d269341a8d4623110884422190c86432994ca6d3e974baddee773b1d8e47a35128148ac5623198cce6f3f97c3e1f8f47a3d168b45aad562b158ac5e2f1f87c3e9f4f279349a4d269b45aad56",
  
  // 时间戳相关
  TIMESTAMP_XOR_KEY: 41,
  STARTUP_TIME_OFFSET_MIN: 1000,
  STARTUP_TIME_OFFSET_MAX: 4000,
  
  // 版本和固定值
  VERSION_BYTES: [119, 104, 96, 41],
  FIXED_INT_VALUE_1: 15,
  FIXED_INT_VALUE_2: 1291,
  
  // 环境静态字节
  ENV_STATIC_BYTES: [1, 249, 83, 102, 103, 201, 181, 131, 99, 94, 7, 68, 250, 132, 21],
  
  // 签名数据模板
  SIGNATURE_DATA_TEMPLATE: {
    x0: "4.2.6",
    x1: "xhs-pc-web",
    x2: "Windows",
    x3: "",
    x4: "object"
  },
  
  // 前缀
  X3_PREFIX: "mns0101_",
  XYS_PREFIX: "XYS_"
};

// ==================== Base58 编码器 ====================
class Base58Encoder {
  encode(inputBytes) {
    const number = this._bytesToNumber(inputBytes);
    const leadingZeros = this._countLeadingZeros(inputBytes);
    const encodedChars = this._numberToBase58Chars(number);
    
    for (let i = 0; i < leadingZeros; i++) {
      encodedChars.push(CONFIG.BASE58_ALPHABET[0]);
    }
    
    return encodedChars.reverse().join('');
  }
  
  decode(encodedString) {
    let leadingZeros = 0;
    for (const char of encodedString) {
      if (char === CONFIG.BASE58_ALPHABET[0]) {
        leadingZeros++;
      } else {
        break;
      }
    }
    
    let number = 0;
    for (const char of encodedString) {
      const charIndex = CONFIG.BASE58_ALPHABET.indexOf(char);
      if (charIndex === -1) {
        throw new Error(`Invalid Base58 character: ${char}`);
      }
      number = number * 58 + charIndex;
    }
    
    const byteArray = this._numberToBytes(number);
    return Array(leadingZeros).fill(0).concat(byteArray);
  }
  
  _bytesToNumber(bytes) {
    let result = 0;
    for (const byte of bytes) {
      result = result * 256 + byte;
    }
    return result;
  }
  
  _numberToBytes(number) {
    if (number === 0) return [];
    const bytes = [];
    while (number > 0) {
      bytes.unshift(number % 256);
      number = Math.floor(number / 256);
    }
    return bytes;
  }
  
  _countLeadingZeros(bytes) {
    let count = 0;
    for (const byte of bytes) {
      if (byte === 0) count++;
      else break;
    }
    return count;
  }
  
  _numberToBase58Chars(number) {
    const chars = [];
    while (number > 0) {
      const remainder = number % 58;
      chars.push(CONFIG.BASE58_ALPHABET[remainder]);
      number = Math.floor(number / 58);
    }
    return chars;
  }
}

// ==================== Base64 编码器 ====================
class Base64Encoder {
  encode(data) {
    const buffer = Buffer.from(data, 'utf-8');
    const standardBase64 = buffer.toString('base64');
    return this._translate(standardBase64, CONFIG.STANDARD_BASE64_ALPHABET, CONFIG.CUSTOM_BASE64_ALPHABET);
  }
  
  decode(encodedString) {
    const standardBase64 = this._translate(encodedString, CONFIG.CUSTOM_BASE64_ALPHABET, CONFIG.STANDARD_BASE64_ALPHABET);
    return Buffer.from(standardBase64, 'base64').toString('utf-8');
  }
  
  _translate(str, fromAlphabet, toAlphabet) {
    let result = '';
    for (const char of str) {
      const index = fromAlphabet.indexOf(char);
      result += index !== -1 ? toAlphabet[index] : char;
    }
    return result;
  }
}

// ==================== 位运算工具 ====================
class BitOperations {
  xorTransformArray(sourceIntegers) {
    const hexKeyBytes = Buffer.from(CONFIG.HEX_KEY, 'hex');
    const result = [];
    
    for (let i = 0; i < sourceIntegers.length; i++) {
      result.push((sourceIntegers[i] ^ hexKeyBytes[i]) & 0xFF);
    }
    
    return result;
  }
}

// ==================== 随机数生成器 ====================
class RandomGenerator {
  generateRandomInt() {
    return Math.floor(Math.random() * (CONFIG.MAX_32BIT + 1));
  }
  
  generateRandomByteInRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
}

// ==================== 加密处理器 ====================
class CryptoProcessor {
  constructor() {
    this.b58Encoder = new Base58Encoder();
    this.b64Encoder = new Base64Encoder();
    this.bitOps = new BitOperations();
    this.randomGen = new RandomGenerator();
  }
  
  buildPayloadArray(hexParameter, a1Value, appIdentifier = "xhs-pc-web", stringParam = "") {
    const randNum = this.randomGen.generateRandomInt();
    const ts = Date.now();
    const startupTs = ts - (
      CONFIG.STARTUP_TIME_OFFSET_MIN +
      this.randomGen.generateRandomByteInRange(
        0,
        CONFIG.STARTUP_TIME_OFFSET_MAX - CONFIG.STARTUP_TIME_OFFSET_MIN
      )
    );
    
    const arr = [];
    
    // 添加版本字节
    arr.push(...CONFIG.VERSION_BYTES);
    
    // 添加随机字节
    const randBytes = this._intToLEBytes(randNum, 4);
    arr.push(...randBytes);
    
    const xorKey = randBytes[0];
    
    // 添加时间戳
    arr.push(...this._encodeTimestamp(ts, true));
    arr.push(...this._intToLEBytes(startupTs, 8));
    arr.push(...this._intToLEBytes(CONFIG.FIXED_INT_VALUE_1));
    arr.push(...this._intToLEBytes(CONFIG.FIXED_INT_VALUE_2));
    
    // 添加字符串参数长度
    const stringParamLength = Buffer.byteLength(stringParam, 'utf-8');
    arr.push(...this._intToLEBytes(stringParamLength));
    
    // 处理 MD5 字节
    const md5Bytes = Buffer.from(hexParameter, 'hex');
    const xorMd5Bytes = [];
    for (let i = 0; i < 8; i++) {
      xorMd5Bytes.push(md5Bytes[i] ^ xorKey);
    }
    arr.push(...xorMd5Bytes);
    
    // 添加 a1 和 appIdentifier
    arr.push(...this._strToLenPrefixedBytes(a1Value));
    arr.push(...this._strToLenPrefixedBytes(appIdentifier));
    
    // 添加环境字节
    arr.push(
      CONFIG.ENV_STATIC_BYTES[0],
      this.randomGen.generateRandomByteInRange(0, 255),
      ...CONFIG.ENV_STATIC_BYTES.slice(1)
    );
    
    return arr;
  }
  
  _encodeTimestamp(ts, randomizeFirst = true) {
    const keyByte = CONFIG.TIMESTAMP_XOR_KEY & 0xFF;
    const arr = this._intToLEBytes(ts, 8);
    const encoded = arr.map((a, i) => a ^ keyByte);
    
    if (randomizeFirst) {
      encoded[0] = this.randomGen.generateRandomByteInRange(0, 255);
    }
    
    return encoded;
  }
  
  _intToLEBytes(val, length = 4) {
    let value = BigInt(Math.floor(Number(val)));
    const mask = (1n << BigInt(length * 8)) - 1n;
    value = BigInt.asUintN(length * 8, value & mask);
    
    const arr = [];
    for (let i = 0; i < length; i++) {
      arr.push(Number(value & 0xFFn));
      value >>= 8n;
    }
    return arr;
  }
  
  _strToLenPrefixedBytes(s) {
    const buf = Buffer.from(s, 'utf-8');
    return [buf.length, ...buf];
  }
}

// ==================== 主要签名类 ====================
class XhsSign {
  constructor() {
    this.cryptoProcessor = new CryptoProcessor();
  }
  
  /**
   * 提取 URI（去除域名和协议）
   */
  _extractUri(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.pathname;
    } catch {
      // 如果已经是 URI，直接返回
      return url.split('?')[0];
    }
  }
  
  /**
   * 构建内容字符串
   */
  _buildContentString(method, uri, payload = null) {
    payload = payload || {};
    
    if (method.toUpperCase() === 'POST') {
      return uri + JSON.stringify(payload, null, 0).replace(/\s/g, '');
    } else {
      if (!payload || Object.keys(payload).length === 0) {
        return uri;
      }
      
      const params = [];
      for (const [key, value] of Object.entries(payload)) {
        let valueStr;
        if (Array.isArray(value)) {
          valueStr = value.join(',');
        } else if (value === null || value === undefined) {
          valueStr = '';
        } else {
          valueStr = String(value);
        }
        
        // 只将 = 编码为 %3D
        valueStr = valueStr.replace(/=/g, '%3D');
        params.push(`${key}=${valueStr}`);
      }
      
      return `${uri}?${params.join('&')}`;
    }
  }
  
  /**
   * 生成 D 值（MD5）
   */
  _generateDValue(content) {
    return crypto.createHash('md5').update(content, 'utf-8').digest('hex');
  }
  
  /**
   * 构建签名
   */
  _buildSignature(dValue, a1Value, xsecAppid = "xhs-pc-web", stringParam = "") {
    const payloadArray = this.cryptoProcessor.buildPayloadArray(
      dValue,
      a1Value,
      xsecAppid,
      stringParam
    );
    
    const xorResult = this.cryptoProcessor.bitOps.xorTransformArray(payloadArray);
    return this.cryptoProcessor.b58Encoder.encode(xorResult);
  }
  
  /**
   * 生成 x-s 签名
   */
  signXs(method, uri, a1Value, xsecAppid = "xhs-pc-web", payload = null) {
    uri = this._extractUri(uri);
    
    const signatureData = { ...CONFIG.SIGNATURE_DATA_TEMPLATE };
    const contentString = this._buildContentString(method, uri, payload);
    const dValue = this._generateDValue(contentString);
    
    signatureData.x3 = CONFIG.X3_PREFIX + this._buildSignature(dValue, a1Value, xsecAppid, contentString);
    
    const jsonStr = JSON.stringify(signatureData).replace(/\s/g, '');
    return CONFIG.XYS_PREFIX + this.cryptoProcessor.b64Encoder.encode(jsonStr);
  }
}

// ==================== 导出函数 ====================
const xhsSign = new XhsSign();

/**
 * 获取小红书签名（基础版，仅 x-s 和 x-t）
 * @param {string} url - 请求 URL
 * @param {object} options - 选项
 * @param {string} options.method - 请求方法 GET/POST
 * @param {object} options.data - 请求数据
 * @param {string} options.a1 - Cookie 中的 a1 值
 * @returns {object} - {x-s: string, x-t: string}
 */
function getSign(url, options = {}) {
  const {
    method = 'GET',
    data = null,
    a1 = ''
  } = options;
  
  const timestamp = Date.now().toString();
  
  // 生成 x-s 签名
  const xs = xhsSign.signXs(method, url, a1, "xhs-pc-web", data);
  
  return {
    'x-s': xs,
    'x-t': timestamp
  };
}

/**
 * 获取小红书完整签名（包括 x-s-common 和 X-B3-Traceid）
 * @param {string} url - 请求 URL
 * @param {object} options - 选项
 * @param {string} options.method - 请求方法 GET/POST
 * @param {object} options.data - 请求数据
 * @param {string} options.a1 - Cookie 中的 a1 值
 * @param {string} options.b1 - localStorage 中的 b1 值
 * @returns {object} - {x-s: string, x-t: string, x-s-common: string, x-b3-traceid: string}
 */
function getFullSign(url, options = {}) {
  const {
    method = 'GET',
    data = null,
    a1 = '',
    b1 = ''
  } = options;
  
  const timestamp = Date.now().toString();
  
  // 生成 x-s 签名
  const xs = xhsSign.signXs(method, url, a1, "xhs-pc-web", data);
  
  // 如果提供了 b1，使用增强版签名生成完整的请求头
  if (b1) {
    const { sign } = require('../utils/xhs_sign_enhanced');
    return sign(a1, b1, xs, timestamp);
  }
  
  // 如果没有 b1，只返回基础签名
  return {
    'x-s': xs,
    'x-t': timestamp,
    'x-s-common': '',
    'x-b3-traceid': ''
  };
}

module.exports = {
  getSign,
  getFullSign,
  XhsSign
};



