const { app, BrowserWindow, Menu, Tray, shell } = require('electron')
const path = require('path')

let mainWindow
let tray

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  // 加载玄机算命网站
  mainWindow.loadURL('https://xuanjisuanming.top')

  // 外部链接用系统浏览器打开
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function createTray() {
  // 创建系统托盘
  tray = new Tray(path.join(__dirname, 'icon.png'))
  const contextMenu = Menu.buildFromTemplate([
    { label: '打开主窗口', click: () => mainWindow.show() },
    { label: '关于', click: () => shell.openExternal('https://xuanjisuanming.top') },
    { type: 'separator' },
    { label: '退出', click: () => app.quit() }
  ])
  tray.setToolTip('玄机算命')
  tray.setContextMenu(contextMenu)
  tray.on('click', () => mainWindow.show())
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
