# 玄机算命 - 跨平台应用

基于玄机算命网 (https://xuanjisuanming.top) 的桌面和移动端应用。

## 自动构建

推送代码到 `main` 分支后，GitHub Actions 会自动构建：

- **Windows .exe 安装包** - 在 Actions 页面下载
- **Android .apk 安装包** - 在 Actions 页面下载

## 本地开发

### 桌面版（Electron）

```bash
npm install
npm start         # 测试运行
npm run build:win # 打包 Windows .exe
```

### 系统要求

- Node.js 20+
- npm 11+

## 下载安装包

1. 访问 [Actions 页面](https://github.com/WERLK/suanming/actions)
2. 点击最新的构建任务
3. 在 "Artifacts" 部分下载：
   - `windows-exe.zip` - Windows 安装包
   - `android-apk.zip` - Android 安装包

## 项目结构

```
.
├── .github/workflows/build.yml  # 自动构建配置
├── main.js                       # Electron 主进程
├── index.html                    # 入口页面
├── package.json                  # 项目配置
└── README.md                     # 本文件
```

## 许可证

未经授权，禁止使用。
