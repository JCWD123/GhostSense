/**
 * B站 WBI 签名算法
 */

const crypto = require('crypto');

// WBI 密钥（需要定期更新）
const MIXIN_KEY_ENC_TAB = [
  46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
  33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
  61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
  36, 20, 34, 44, 52
];

/**
 * 获取 B站 WBI 签名
 * @param {object} params - 请求参数
 * @returns {object} - 签名后的参数
 */
async function getSign(params) {
  // 获取 mixin key（实际需要从 API 获取）
  // const mixinKey = await getMixinKey();
  const mixinKey = 'ea1db124af3c7062474693fa704f4ff8'; // 示例，实际需要动态获取
  
  // 添加 wts（时间戳）
  params.wts = Math.floor(Date.now() / 1000);
  
  // 排序参数
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((obj, key) => {
      obj[key] = params[key];
      return obj;
    }, {});
  
  // 构建查询字符串
  const query = Object.entries(sortedParams)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');
  
  // 计算 w_rid
  const wRid = crypto
    .createHash('md5')
    .update(query + mixinKey)
    .digest('hex');
  
  sortedParams.w_rid = wRid;
  
  return sortedParams;
}

/**
 * 获取 Mixin Key
 * @returns {string}
 */
function getMixinKey() {
  // 实际需要从 B站 API 获取 img_key 和 sub_key
  // 这里使用示例值
  const imgKey = 'xxx';
  const subKey = 'xxx';
  
  const rawWbiKey = imgKey + subKey;
  const mixinKey = MIXIN_KEY_ENC_TAB.map(n => rawWbiKey[n]).join('').slice(0, 32);
  
  return mixinKey;
}

module.exports = {
  getSign
};




