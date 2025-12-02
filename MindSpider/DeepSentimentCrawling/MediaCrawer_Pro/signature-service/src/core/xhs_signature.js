/**
 * 小红书签名算法（纯JS逆向）
 * 生成 x-s 和 x-t 签名
 * 
 * 基于 xhshow 项目: https://github.com/Cloxl/xhshow
 */

const crypto = require('crypto');

// ==================== 配置常量 ====================
const CONFIG = {
  MAX_32BIT: 0xFFFFFFFF,
  MAX_SIGNED_32BIT: 0x7FFFFFFF,
  BASE58_ALPHABET: "NOPQRStuvwxWXYZabcyz012DEFTKLMdefghijkl4563GHIJBC7mnop89+/AUVqrsOPQefghijkABCDEFGuvwz0123456789xy",
  STANDARD_BASE64_ALPHABET: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
  CUSTOM_BASE64_ALPHABET: "ZmserbBoHQtNP+wOcza/LpngG8yJq42KWYj0DSfdikx3VT16IlUAFM97hECvuRX5",
  HEX_KEY: "af572b95ca65b2d9ec76bb5d2e97cb653299cc663399cc663399cce673399cce6733190c06030100000000008040209048241289c4e271381c0e0703018040a05028148ac56231180c0683c16030984c2693c964b259ac56abd5eaf5fafd7e3f9f4f279349a4d2e9743a9d4e279349a4d2e9f47a3d1e8f47239148a4d269341a8d4623110884422190c86432994ca6d3e974baddee773b1d8e47a35128148ac5623198cce6f3f97c3e1f8f47a3d168b45aad562b158ac5e2f1f87c3e9f4f279349a4d269b45aad56",
  TIMESTAMP_XOR_KEY: 41,
  STARTUP_TIME_OFFSET_MIN: 1000,
  STARTUP_TIME_OFFSET_MAX: 4000,
  VERSION_BYTES: [119, 104, 96, 41],
  FIXED_INT_VALUE_1: 15,
  FIXED_INT_VALUE_2: 1291,
  ENV_STATIC_BYTES: [1, 249, 83, 102, 103, 201, 181, 131, 99, 94, 7, 68, 250, 132, 21],
  SIGNATURE_DATA_TEMPLATE: {
    x0: "4.2.6",
    x1: "xhs-pc-web",
    x2: "Windows",
    x3: "",
    x4: "object"
  },
  X3_PREFIX: "mns0101_",
  XYS_PREFIX: "XYS_"
};

// ==================== Base58 编码器 ====================
class Base58Encoder {
  constructor(alphabet = CONFIG.BASE58_ALPHABET) {
    this.alphabet = alphabet;
    this.base = this.alphabet.length;
  }

  encode(buffer) {
    if (!buffer || buffer.length === 0) return '';
    
    let value = 0n;
    for (const byte of buffer) {
      value = (value << 8n) | BigInt(byte);
    }

    let result = '';
    while (value > 0n) {
      const remainder = Number(value % BigInt(this.base));
      result = this.alphabet[remainder] + result;
      value = value / BigInt(this.base);
    }

    for (const byte of buffer) {
      if (byte === 0) result = this.alphabet[0] + result;
      else break;
    }

    return result;
  }
}

// ==================== Base64 编码器 ====================
class Base64Encoder {
  constructor(alphabet = CONFIG.CUSTOM_BASE64_ALPHABET) {
    this.alphabet = alphabet;
  }

  encode(data) {
    if (typeof data === 'string') {
      data = Buffer.from(data, 'utf-8');
    }
    
    const standardBase64 = data.toString('base64');
    return this._translateBase64(standardBase64, CONFIG.STANDARD_BASE64_ALPHABET, this.alphabet);
  }

  _translateBase64(base64Str, fromAlphabet, toAlphabet) {
    let result = '';
    for (const char of base64Str) {
      const index = fromAlphabet.indexOf(char);
      result += index !== -1 ? toAlphabet[index] : char;
    }
    return result;
  }
}

// ==================== 加密处理器 ====================
class CryptoProcessor {
  constructor() {
    this.b58Encoder = new Base58Encoder();
    this.b64Encoder = new Base64Encoder();
    this.hexKey = Buffer.from(CONFIG.HEX_KEY, 'hex');
    this._initializeTimestamps();
  }

  _initializeTimestamps() {
    this.currentTime = Date.now();
    const offset = Math.floor(
      Math.random() * (CONFIG.STARTUP_TIME_OFFSET_MAX - CONFIG.STARTUP_TIME_OFFSET_MIN + 1)
    ) + CONFIG.STARTUP_TIME_OFFSET_MIN;
    this.startupTime = this.currentTime - offset;
  }

  _toUint32(value) {
    const bigintValue = BigInt(Math.floor(Number(value)));
    return Number(BigInt.asUintN(32, bigintValue));
  }

  _toInt32(value) {
    const uint32 = this._toUint32(value);
    return uint32 > CONFIG.MAX_SIGNED_32BIT ? uint32 - CONFIG.MAX_32BIT - 1 : uint32;
  }

  _xorTimestamp(timestamp) {
    const tsBig = BigInt(Math.floor(Number(timestamp)));
    const keyBig = BigInt(CONFIG.TIMESTAMP_XOR_KEY);
    const xoredTime = Number(BigInt.asUintN(32, tsBig ^ keyBig));
    const buffer = Buffer.alloc(4);
    buffer.writeUInt32BE(this._toUint32(xoredTime), 0);
    return buffer;
  }

  _intToBuffer(value, size) {
    const buffer = Buffer.alloc(size);
    if (size === 4) {
      buffer.writeUInt32BE(this._toUint32(value), 0);
    } else if (size === 2) {
      buffer.writeUInt16BE(Number(BigInt.asUintN(16, BigInt(Math.floor(Number(value))))), 0);
    }
    return buffer;
  }

  _xorWithKey(data) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
      result.push(data[i] ^ this.hexKey[i % this.hexKey.length]);
    }
    return Buffer.from(result);
  }

  _calculateMD5(buffer) {
    return crypto.createHash('md5').update(buffer).digest();
  }
}

// ==================== 主要签名类 ====================
class XhsSignature {
  constructor() {
    this.cryptoProcessor = new CryptoProcessor();
  }

  /**
   * 生成签名
   * @param {Object} options
   * @param {string} options.method - HTTP方法 (GET/POST)
   * @param {string} options.url - 请求URL（完整URL或路径）
   * @param {Object} options.data - 请求数据（GET为params，POST为body）
   * @param {string} options.a1 - Cookie中的a1值
   * @param {string} options.appId - 应用ID，默认 xhs-pc-web
   * @returns {Object} { xs, xt }
   */
  sign(options = {}) {
    const {
      method = "GET",
      url = "",
      data = null,
      a1 = "",
      appId = "xhs-pc-web"
    } = options;

    const uri = this._extractUri(url);
    const contentString = this._buildContentString(method, uri, data);
    const dValue = this._generateDValue(contentString);
    
    const signatureData = { ...CONFIG.SIGNATURE_DATA_TEMPLATE };
    signatureData.x3 = CONFIG.X3_PREFIX + this._buildSignature(dValue, a1, appId, contentString);
    
    const jsonStr = JSON.stringify(signatureData).replace(/\s/g, '');
    const xs = CONFIG.XYS_PREFIX + this.cryptoProcessor.b64Encoder.encode(jsonStr);
    const xt = this._generateTimestamp();

    return { xs, xt };
  }

  _extractUri(url) {
    if (!url) return "";
    
    if (url.startsWith("http://") || url.startsWith("https://")) {
      try {
        const urlObj = new URL(url);
        return urlObj.pathname + (urlObj.search || "");
      } catch (e) {
        return url;
      }
    }
    return url;
  }

  _buildContentString(method, uri, data) {
    method = method.toUpperCase();
    let parts = [method, uri];
    
    if (data) {
      if (method === "POST") {
        parts.push(typeof data === "string" ? data : JSON.stringify(data));
      } else if (method === "GET") {
        const params = typeof data === "object" ? data : JSON.parse(data);
        const sortedKeys = Object.keys(params).sort();
        const queryString = sortedKeys
          .map(key => `${key}=${params[key]}`)
          .join("&");
        parts.push(queryString);
      }
    }
    
    return parts.join(" ");
  }

  _generateDValue(contentString) {
    const md5Hash = this.cryptoProcessor._calculateMD5(Buffer.from(contentString, 'utf-8'));
    return md5Hash.toString('hex');
  }

  _generateTimestamp() {
    return Date.now().toString();
  }

  _buildSignature(dValue, a1Value, xsecAppid, stringParam) {
    const payloadComponents = [
      this.cryptoProcessor._xorTimestamp(this.cryptoProcessor.currentTime),
      this.cryptoProcessor._xorTimestamp(this.cryptoProcessor.startupTime),
      Buffer.from(CONFIG.VERSION_BYTES),
      this.cryptoProcessor._intToBuffer(CONFIG.FIXED_INT_VALUE_1, 2),
      this.cryptoProcessor._calculateMD5(Buffer.from(dValue, 'utf-8')),
      this.cryptoProcessor._calculateMD5(Buffer.from(a1Value, 'utf-8')),
      this.cryptoProcessor._calculateMD5(Buffer.from(xsecAppid, 'utf-8')),
      this.cryptoProcessor._intToBuffer(CONFIG.FIXED_INT_VALUE_2, 2),
      Buffer.from(CONFIG.ENV_STATIC_BYTES),
      this.cryptoProcessor._calculateMD5(Buffer.from(stringParam, 'utf-8'))
    ];

    const payloadArray = Buffer.concat(payloadComponents);
    const xorResult = this.cryptoProcessor._xorWithKey(payloadArray);
    return this.cryptoProcessor.b58Encoder.encode(xorResult);
  }
}

// ==================== 导出 ====================
module.exports = {
  XhsSignature,
  CONFIG
};





