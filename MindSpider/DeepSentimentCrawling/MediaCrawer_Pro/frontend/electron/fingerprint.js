/**
 * 浏览器指纹生成脚本
 *
 * 在 Electron 小红书窗口中注入，生成 WebGL/Canvas 等指纹，
 * 模拟真实用户环境，降低被识别为爬虫的风险。
 */

/**
 * 生成 Canvas 指纹
 */
function generateCanvasFingerprint() {
  try {
    const canvas = document.createElement('canvas')
    canvas.width = 200
    canvas.height = 50

    const ctx = canvas.getContext('2d')
    if (!ctx) return null

    // 绘制文本
    ctx.textBaseline = 'top'
    ctx.font = '14px "Arial"'
    ctx.textBaseline = 'alphabetic'
    ctx.fillStyle = '#f60'
    ctx.fillRect(125, 1, 62, 20)

    ctx.fillStyle = '#069'
    ctx.fillText('MediaCrawler <Canvas> 🎨', 2, 15)

    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)'
    ctx.fillText('MediaCrawler <Canvas> 🎨', 4, 17)

    // 获取指纹
    const dataURL = canvas.toDataURL()

    // 计算简单哈希
    let hash = 0
    for (let i = 0; i < dataURL.length; i++) {
      const char = dataURL.charCodeAt(i)
      hash = (hash << 5) - hash + char
      hash = hash & hash
    }

    console.log('[指纹] Canvas 指纹生成:', hash)
    return {
      hash: hash.toString(16),
      dataURL: dataURL.substring(0, 100) + '...',
    }
  } catch (e) {
    console.error('[指纹] Canvas 指纹生成失败:', e.message)
    return null
  }
}

/**
 * 生成 WebGL 指纹
 */
function generateWebGLFingerprint() {
  try {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')

    if (!gl) {
      console.warn('[指纹] WebGL 不可用')
      return null
    }

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
    const fingerprint = {
      vendor: gl.getParameter(gl.VENDOR),
      renderer: gl.getParameter(gl.RENDERER),
      version: gl.getParameter(gl.VERSION),
      shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
      unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null,
      unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : null,
      maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
      maxViewportDims: gl.getParameter(gl.MAX_VIEWPORT_DIMS),
      aliasedLineWidthRange: gl.getParameter(gl.ALIASED_LINE_WIDTH_RANGE),
      aliasedPointSizeRange: gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE),
    }

    console.log('[指纹] WebGL 指纹生成:', fingerprint)
    return fingerprint
  } catch (e) {
    console.error('[指纹] WebGL 指纹生成失败:', e.message)
    return null
  }
}

/**
 * 生成并存储指纹
 */
function initFingerprint() {
  console.log('[指纹] 开始初始化浏览器指纹...')

  const fingerprint = {
    canvas: generateCanvasFingerprint(),
    webgl: generateWebGLFingerprint(),
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: navigator.deviceMemory || 'unknown',
    screenResolution: `${screen.width}x${screen.height}`,
    colorDepth: screen.colorDepth,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    timestamp: Date.now(),
  }

  // 存储到 localStorage
  try {
    localStorage.setItem('browser_fingerprint', JSON.stringify(fingerprint))
    console.log('[指纹] 指纹已存储到 localStorage')
  } catch (e) {
    console.error('[指纹] 存储指纹失败:', e.message)
  }

  // 触发一次 Canvas 和 WebGL 渲染，让浏览器"记住"这些操作
  try {
    const testCanvas = document.createElement('canvas')
    testCanvas.width = 256
    testCanvas.height = 128
    const ctx2d = testCanvas.getContext('2d')
    if (ctx2d) {
      // 绘制一些复杂图形
      ctx2d.fillStyle = 'rgb(255,0,0)'
      ctx2d.fillRect(0, 0, 256, 128)
      ctx2d.fillStyle = 'rgb(0,255,0)'
      ctx2d.beginPath()
      ctx2d.arc(128, 64, 50, 0, Math.PI * 2)
      ctx2d.fill()
    }

    const ctxWebGL = testCanvas.getContext('webgl')
    if (ctxWebGL) {
      // 简单的 WebGL 渲染
      ctxWebGL.clearColor(0.0, 0.0, 0.0, 1.0)
      ctxWebGL.clear(ctxWebGL.COLOR_BUFFER_BIT)
    }

    console.log('[指纹] Canvas/WebGL 预渲染完成')
  } catch (e) {
    console.error('[指纹] 预渲染失败:', e.message)
  }

  console.log('[指纹] 浏览器指纹初始化完成')
  return fingerprint
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initFingerprint, generateCanvasFingerprint, generateWebGLFingerprint }
}

// 如果在浏览器环境中直接运行，自动初始化
if (typeof window !== 'undefined') {
  // 等待 DOM 加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFingerprint)
  } else {
    initFingerprint()
  }
}
