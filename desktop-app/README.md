# 玄机算命 - 跨平台客户端

基于 [玄机算命网](https://xuanjisuanming.top) 的桌面和移动端应用。

## 自动构建

推送 `desktop-app/` 目录变更到 `main` 分支后，GitHub Actions 自动构建：

- **Windows .exe 安装包** — 在 [Actions](https://github.com/WERLK/suanming/actions) 页面下载
- **Android .apk 源码** — 在 [Actions](https://github.com/WERLK/suanming/actions) 页面下载

## 本地开发

### 桌面版（Electron）

```bash
cd desktop-app
npm install
npm start          # 开发测试
npm run build:win  # 打包 Windows .exe
npm run build:mac  # 打包 macOS .dmg
npm run build:linux # 打包 Linux AppImage
```

### 系统要求

- Node.js 20+
- npm 11+

## 下载安装包

1. 访问 [GitHub Actions](https://github.com/WERLK/suanming/actions)
2. 点击最新的 **"Build Desktop and Mobile Apps"** 任务
3. 在 "Artifacts" 部分下载：
   - `windows-exe.zip` — Windows 安装包（NSIS）
   - `android-apk-src.zip` — Android 项目源码

## 项目结构

```
desktop-app/
├── main.js        # Electron 主进程
├── index.html     # 客户端入口页面
├── preload.js     # 预加载脚本（可选）
├── package.json   # 项目配置与依赖
├── assets/        # 图标资源（icon.png / icon.ico / icon.icns）
└── README.md      # 本文件
```

## 许可证

未经授权，禁止使用。
