const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const fs = require('fs')

// 启用远程调试端口 9222
// 这样可以通过 chrome://inspect 或 Playwright 连接到 Electron 进行调试
app.commandLine.appendSwitch('--remote-debugging-port', '9222')
app.commandLine.appendSwitch('--remote-allow-origins', '*')

// 两个窗口实例
let mainWindow = null // 主窗口：桌面应用 UI
let xhsWindow = null // 小红书窗口：登录和签名

/**
 * 创建主窗口（桌面应用 UI）
 * - 显示你的 Vue 应用
 * - 不会被 Playwright 控制
 * - 不会跳转到小红书
 */
function createMainWindow() {
  console.log('🪟 创建主窗口...')

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false,
    },
    icon: path.join(__dirname, '../public/icon.png'),
    title: 'MediaCrawer Pro',
  })

  // 加载你的应用界面
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  console.log('✅ 主窗口创建成功')
}

/**
 * 创建小红书窗口（登录和签名专用）
 * - 初始隐藏，只在需要时显示
 * - 被 Playwright 控制
 * - 加载小红书网站
 * - 保持会话状态
 */
function createXhsWindow() {
  console.log('🪟 创建小红书登录窗口...')

  xhsWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    show: false, // 初始隐藏
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true, // 保持安全性
      partition: 'persist:xhs', // 独立的会话分区，保留 Cookie
    },
    title: '小红书登录 - MediaCrawer Pro',
    backgroundColor: '#ffffff',
    // 可选：设置为子窗口（如果需要）
    // parent: mainWindow,
    // modal: false
  })

  // 加载小红书首页
  xhsWindow.loadURL('https://www.xiaohongshu.com/explore')

  // 窗口加载完成
  xhsWindow.webContents.on('did-finish-load', () => {
    console.log('✅ 小红书窗口加载完成')

    // 注入指纹脚本
    try {
      const fingerprintScript = fs.readFileSync(path.join(__dirname, 'fingerprint.js'), 'utf8')

      xhsWindow.webContents
        .executeJavaScript(fingerprintScript)
        .then(() => {
          console.log('✅ 指纹脚本注入成功（WebGL/Canvas）')
        })
        .catch(err => {
          console.error('❌ 指纹脚本注入失败:', err.message)
        })
    } catch (err) {
      console.error('❌ 读取指纹脚本失败:', err.message)
    }
  })

  // 导航事件监听（可选：记录登录状态）
  xhsWindow.webContents.on('did-navigate', (event, url) => {
    console.log('📍 小红书窗口导航:', url)

    // 检测登录成功（可根据URL判断）
    if (url.includes('/explore') || url.includes('/user/profile')) {
      console.log('✅ 检测到可能已登录')
      // 可以自动隐藏窗口
      // xhsWindow.hide();
    }
  })

  xhsWindow.on('closed', () => {
    console.log('⚠️  小红书窗口被关闭')
    xhsWindow = null
  })

  console.log('✅ 小红书窗口创建成功（隐藏状态）')
  console.log('💡 窗口将在需要登录时显示，登录后自动隐藏')
}

/**
 * 显示小红书窗口（用于登录）
 */
function showXhsWindow() {
  if (!xhsWindow) {
    createXhsWindow()
  }

  console.log('👁️  显示小红书登录窗口')
  xhsWindow.show()
  xhsWindow.focus()
}

/**
 * 隐藏小红书窗口（登录完成后）
 */
function hideXhsWindow() {
  if (xhsWindow && !xhsWindow.isDestroyed()) {
    console.log('🙈 隐藏小红书窗口（保持后台运行）')
    xhsWindow.hide()
  }
}

/**
 * 获取小红书窗口的 Cookie
 */
async function getXhsCookies() {
  if (!xhsWindow || xhsWindow.isDestroyed()) {
    console.error('❌ 小红书窗口不存在')
    return null
  }

  try {
    const cookies = await xhsWindow.webContents.session.cookies.get({
      domain: '.xiaohongshu.com',
    })

    console.log(`🍪 获取到 ${cookies.length} 个 Cookie`)

    // 转换为字符串格式
    const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ')

    return {
      cookies: cookies,
      cookieString: cookieString,
    }
  } catch (error) {
    console.error('❌ 获取 Cookie 失败:', error)
    return null
  }
}

// ==================== IPC 通信（与渲染进程交互） ====================

// 主窗口请求显示登录窗口
ipcMain.on('show-xhs-login', () => {
  console.log('📨 收到显示登录窗口请求')
  showXhsWindow()
})

// 主窗口请求隐藏登录窗口
ipcMain.on('hide-xhs-login', () => {
  console.log('📨 收到隐藏登录窗口请求')
  hideXhsWindow()
})

// 主窗口请求获取 Cookie
ipcMain.handle('get-xhs-cookies', async () => {
  console.log('📨 收到获取 Cookie 请求')
  return await getXhsCookies()
})

// 检查登录状态
ipcMain.handle('check-xhs-login', async () => {
  if (!xhsWindow || xhsWindow.isDestroyed()) {
    return { loggedIn: false, message: '小红书窗口未创建' }
  }

  const cookies = await getXhsCookies()
  const hasA1 = cookies && cookies.cookies.some(c => c.name === 'a1')

  return {
    loggedIn: hasA1,
    message: hasA1 ? '已登录' : '未登录',
    cookies: cookies,
  }
})

// 获取 UserAgent（从小红书窗口）
ipcMain.handle('get-xhs-user-agent', async () => {
  console.log('📨 收到获取 UserAgent 请求')

  if (!xhsWindow || xhsWindow.isDestroyed()) {
    console.error('❌ 小红书窗口不存在')
    return null
  }

  try {
    const userAgent = await xhsWindow.webContents.executeJavaScript('navigator.userAgent')
    console.log('🔍 获取到 UserAgent:', userAgent.substring(0, 50) + '...')
    return userAgent
  } catch (error) {
    console.error('❌ 获取 UserAgent 失败:', error.message)
    return null
  }
})

// 保存登录信息到数据库（Cookie + UA）
ipcMain.handle('save-xhs-login', async () => {
  console.log('📨 收到保存登录信息请求')

  if (!xhsWindow || xhsWindow.isDestroyed()) {
    return { success: false, message: '小红书窗口不存在' }
  }

  try {
    const cookies = await getXhsCookies()
    const userAgent = await xhsWindow.webContents.executeJavaScript('navigator.userAgent')

    if (!cookies || !userAgent) {
      return { success: false, message: '获取登录信息失败' }
    }

    const hasA1 = cookies.cookies.some(c => c.name === 'a1')
    if (!hasA1) {
      return { success: false, message: '未检测到登录状态（缺少 a1 cookie）' }
    }

    console.log('✅ 成功获取登录信息:')
    console.log(`   Cookies: ${cookies.cookies.length} 个`)
    console.log(`   UserAgent: ${userAgent.substring(0, 50)}...`)

    return {
      success: true,
      message: '登录信息获取成功',
      data: {
        cookies: cookies,
        userAgent: userAgent,
        timestamp: Date.now(),
      },
    }
  } catch (error) {
    console.error('❌ 保存登录信息失败:', error.message)
    return { success: false, message: error.message }
  }
})

// 获取浏览器指纹
ipcMain.handle('get-xhs-fingerprint', async () => {
  console.log('📨 收到获取指纹请求')

  if (!xhsWindow || xhsWindow.isDestroyed()) {
    return { success: false, message: '小红书窗口不存在' }
  }

  try {
    const fingerprint = await xhsWindow.webContents.executeJavaScript(`
      (function() {
        try {
          const stored = localStorage.getItem('browser_fingerprint');
          if (stored) {
            return JSON.parse(stored);
          }
          return null;
        } catch (e) {
          return { error: e.message };
        }
      })();
    `)

    if (fingerprint) {
      console.log('✅ 成功获取浏览器指纹')
      return { success: true, data: fingerprint }
    } else {
      return { success: false, message: '指纹未生成或已过期' }
    }
  } catch (error) {
    console.error('❌ 获取指纹失败:', error.message)
    return { success: false, message: error.message }
  }
})

// ==================== 应用生命周期 ====================

app.whenReady().then(() => {
  console.log('')
  console.log('╔════════════════════════════════════════════════╗')
  console.log('║  MediaCrawer Pro - 双窗口模式启动            ║')
  console.log('╚════════════════════════════════════════════════╝')
  console.log('')
  console.log('🔍 远程调试已启用，端口: 9222')
  console.log('📖 Chrome DevTools: chrome://inspect/#devices')
  console.log('🎯 Playwright 连接: http://localhost:9222')
  console.log('')

  // 1. 创建主窗口（桌面应用）
  createMainWindow()

  // 2. 创建小红书窗口（隐藏状态，Playwright 控制用）
  createXhsWindow()

  console.log('')
  console.log('✅ 双窗口架构初始化完成')
  console.log('')
  console.log('📝 窗口说明:')
  console.log('   🪟 主窗口: 桌面应用 UI（不受 Playwright 影响）')
  console.log('   🪟 小红书窗口: 登录和签名专用（Playwright 控制）')
  console.log('')
  console.log('💡 使用提示:')
  console.log('   - 点击主窗口的"登录小红书"按钮显示登录窗口')
  console.log('   - 扫码登录后窗口会自动隐藏')
  console.log('   - Playwright 会自动连接到小红书窗口获取签名')
  console.log('')

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow()
      createXhsWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 优雅关闭
app.on('before-quit', () => {
  console.log('')
  console.log('👋 正在关闭应用...')

  if (xhsWindow && !xhsWindow.isDestroyed()) {
    xhsWindow.close()
  }

  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.close()
  }

  console.log('✅ 应用已关闭')
})
