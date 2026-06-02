const { app, BrowserWindow, Menu, Tray, shell, nativeImage } = require('electron')
const path = require('path')

let mainWindow = null
let tray = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    show: false,
    icon: getIconPath(),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true
    }
  })

  // 加载玄机算命网站
  mainWindow.loadURL('https://xuanjisuanming.top')

  // 外部链接用系统浏览器打开
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https://') || url.startsWith('http://')) {
      shell.openExternal(url)
    }
    return { action: 'deny' }
  })

  // 页面加载完成后显示窗口
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function getIconPath() {
  const formats = ['icon.png', 'assets/icon.png', 'assets/icon.ico']
  for (const f of formats) {
    const p = path.join(__dirname, f)
    try {
      return p
    } catch (_) {
      continue
    }
  }
  return undefined
}

function createTray() {
  try {
    // 创建 16x16 的托盘图标作为默认
    const trayIcon = nativeImage.createEmpty()
    if (trayIcon.isEmpty()) {
      // 使用内置默认图标
    }
    tray = new Tray(trayIcon)
    const contextMenu = Menu.buildFromTemplate([
      { label: '打开主窗口', click: () => { if (mainWindow) mainWindow.show() } },
      { label: '关于', click: () => shell.openExternal('https://xuanjisuanming.top') },
      { type: 'separator' },
      { label: '退出', click: () => app.quit() }
    ])
    tray.setToolTip('玄机算命')
    tray.setContextMenu(contextMenu)
    tray.on('click', () => { if (mainWindow) mainWindow.show() })
  } catch (err) {
    console.warn('托盘创建失败（可能无桌面环境）:', err.message)
  }
}

app.whenReady().then(() => {
  createWindow()
  createTray()

  // 隐藏菜单栏
  Menu.setApplicationMenu(null)
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})
