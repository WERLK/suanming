#!/bin/bash
# 版本更新脚本

VERSION_FILE="/workspace/suanming-fix/version.json"

# 读取当前版本
CURRENT_VERSION=$(jq -r '.version' "$VERSION_FILE")

echo "当前版本：$CURRENT_VERSION"
echo ""
echo "请选择版本更新类型："
echo "1) 修订号 +1 (1.0.0 -> 1.0.1)"
echo "2) 次版本号 +1 (1.0.0 -> 1.1.0)"
echo "3) 主版本号 +1 (1.0.0 -> 2.0.0)"
echo "4) 自定义版本号"
read -p "请选择 (1-4): " choice

# 解析版本号
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

case $choice in
    1)
        PATCH=$((PATCH + 1))
        ;;
    2)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    3)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    4)
        read -p "请输入新版本号 (如 1.2.3): " NEW_VERSION
        if [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            IFS='.' read -ra VERSION_PARTS <<< "$NEW_VERSION"
            MAJOR=${VERSION_PARTS[0]}
            MINOR=${VERSION_PARTS[1]}
            PATCH=${VERSION_PARTS[2]}
        else
            echo "版本号格式错误！"
            exit 1
        fi
        ;;
    *)
        echo "无效选择！"
        exit 1
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

# 更新版本文件
jq --arg v "$NEW_VERSION" \
   --arg bt "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
   --arg gc "$(git rev-parse --short HEAD 2>/dev/null || echo '')" \
   '.version = $v | .build_time = $bt | .git_commit = $gc' \
   "$VERSION_FILE" > "$VERSION_FILE.tmp" && mv "$VERSION_FILE.tmp" "$VERSION_FILE"

echo ""
echo "✅ 版本已更新：$CURRENT_VERSION -> $NEW_VERSION"
echo "📝 构建时间：$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "🔖 Git提交：$(git rev-parse --short HEAD 2>/dev/null || echo '无')"
echo ""
echo "版本文件内容："
cat "$VERSION_FILE"
