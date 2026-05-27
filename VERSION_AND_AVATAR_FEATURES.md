# 版本管理和头像上传功能 - 实现说明

## 📋 功能清单

### ✅ 1. 脚本时长修改到 5 分钟（300秒）

**修改文件：**
- `remote_update.sh`
  - 停止进程等待：`sleep 2` → `sleep 5`
  - 启动进程等待：`sleep 3` → `sleep 5`
  - Gunicorn 超时：添加 `-t 300` 参数

- `api/app.py`（自动更新接口）
  - Git fetch 超时：30s → 300s
  - Git reset 超时：30s → 300s
  - Pip install 超时：60s → 300s
  - Pkill 超时：10s → 300s
  - 修正路径：`/home/suanming-fix` → `/root/suanming`

### ✅ 2. 健康检查端点格式修改

**新增文件：** 无

**修改文件：** `api/app.py`

**添加的端点：**
```python
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'xuanji-fortune',
        'version': version_info.get('version', '1.0.0'),
        'build_time': version_info.get('build_time', ''),
        'database': 'connected' if users_file_exists else 'disconnected'
    }), 200
```

### ✅ 3. 版本号功能（方案B：动态版本管理）

**新增文件：**
- `version.json` - 版本信息配置文件
- `update_version.sh` - 版本更新脚本
- `test_features.sh` - 功能测试脚本

**修改文件：**
- `api/app.py` - 添加 `/api/version` 接口
- `index.html` - 页脚显示版本号

**功能说明：**
1. **版本信息存储**：`version.json` 包含 version、build_time、git_commit、author
2. **版本API**：`GET /api/version` 返回版本信息
3. **自动显示**：页面右下角显示版本号，点击可查看详情
4. **版本更新**：运行 `./update_version.sh` 自动更新版本号

### ✅ 4. 个人中心头像自定义（带自动审核）

**新增文件：**
- `api/avatar_audit.py` - 头像自动审核模块

**修改文件：**
- `api/app.py` - 添加 `/api/avatar/upload` 接口
- `profile.html` - 添加头像上传功能

**自动审核规则（基于全网标准）：**

| 审核项 | 规则 | 处理方式 |
|--------|------|----------|
| 文件大小 | > 2MB | 拒绝（Block） |
| 图片格式 | 非 JPG/PNG/GIF | 拒绝（Block） |
| 图片尺寸 | < 50px 或 > 1000px | 拒绝（Block） |
| 皮肤色调 | 占比 > 60% | 人工复审（Review） |
| 血腥色调 | 红色占比 > 50% | 人工复审（Review） |
| 纯色图片 | 黑色或白色占比 > 80% | 人工复审（Review） |
| 广告特征 | 单一颜色占比 > 30% | 人工复审（Review） |
| 正常图片 | 通过所有检测 | 通过（Pass） |

**API 接口：**
- `POST /api/avatar/upload` - 上传头像（自动审核）
  - 请求体：`{ "image": "base64编码的图片" }`
  - 返回：`{ success, message, avatar_url, audit_result }`

---

## 🚀 部署步骤

### 步骤 1：提交代码到 GitHub

```bash
cd /workspace/suanming-fix
git add .
git commit -m "feat: 添加版本管理和头像上传功能

- 修改脚本超时到 5 分钟（300秒）
- 添加 /api/health 健康检查端点
- 添加 /api/version 版本信息接口
- 实现头像自动审核（基于全网规则）
- 添加头像上传功能（个人中心）
- 页面页脚显示版本号"
git push origin main
```

### 步骤 2：在服务器上拉取更新

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 进入项目目录
cd /root/suanming

# 拉取最新代码
git pull origin main

# 停止旧进程
pkill -f gunicorn
sleep 5

# 启动新进程（带 300 秒超时）
cd /root/suanming/api
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &

# 检查服务状态
cd /root/suanming
python3 backend_check.py
```

### 步骤 3：验证功能

```bash
# 1. 检查健康检查
curl http://localhost:5000/api/health

# 2. 检查版本信息
curl http://localhost:5000/api/version

# 3. 测试头像上传（需要登录 token）
curl -X POST http://localhost:5000/api/avatar/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64编码的图片数据"}'
```

---

## 📝 使用说明

### 版本管理

**查看当前版本：**
```bash
cat /workspace/suanming-fix/version.json
```

**更新版本号：**
```bash
cd /workspace/suanming-fix
chmod +x update_version.sh
./update_version.sh
# 选择更新类型：1) 修订号 +1  2) 次版本号 +1  3) 主版本号 +1  4) 自定义
```

**页面显示：**
- 右下角显示版本号（如 `v1.0.0`）
- 点击版本号查看详细信息（版本号、构建时间、Git提交哈希）

### 头像上传

**用户操作：**
1. 进入"个人中心"页面
2. 点击头像区域
3. 选择图片文件（支持 JPG/PNG/GIF，< 2MB）
4. 系统自动审核并上传
5. 审核通过后头像立即生效

**审核结果：**
- ✅ **通过（Pass）**：头像立即生效
- ⚠️ **复审（Review）**：头像已上传，待人工审核
- ❌ **拒绝（Block）**：头像审核未通过，请更换图片

---

## 🔧 技术细节

### 头像审核算法

**基于 PIL 的图片分析：**
1. **颜色分布统计**：计算 RGB 平均值，判断主色调
2. **皮肤色调检测**：识别人体肤色范围（R > 95, G > 40, B > 20, |R-G| > 15）
3. **血腥色调检测**：红色占比过高（R > 200, G < 100, B < 100）
4. **纯色图片检测**：黑色或白色占比 > 80%
5. **广告特征检测**：单一颜色占比 > 30%

### 版本号命名规范

**语义化版本号：** `主版本.次版本.修订号` (MAJOR.MINOR.PATCH)
- **主版本**：不兼容的 API 修改
- **次版本**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

**示例：**
- `1.0.0` → `1.0.1`：修复 Bug
- `1.0.0` → `1.1.0`：新增功能
- `1.0.0` → `2.0.0`：架构重构

---

## ⚠️ 注意事项

1. **强制更新命令**：根据你的要求，只有在你明确要求时才会提供强制更新命令
2. **头像存储路径**：上传的头像保存在 `/static/avatars/` 目录
3. **审核准确性**：当前为基于规则的自动审核，可能无法识别所有违规内容，建议定期人工抽查
4. **版本号同步**：每次提交代码前，建议运行 `update_version.sh` 更新版本号

---

## 📞 技术支持

如遇问题，请检查：
1. 服务器日志：`/root/suanming/logs/gunicorn.log`
2. 健康检查：`http://你的域名或IP/api/health`
3. 版本信息：`http://你的域名或IP/api/version`

---

**最后更新时间：** 2026-05-27
**作者：** 玄机算命网技术团队
**版本：** v1.0.0
