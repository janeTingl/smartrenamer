#!/bin/bash
# SmartRenamer macOS DMG 创建脚本

set -e

# 配置
APP_NAME="SmartRenamer"
VERSION="0.6.0"
APP_BUNDLE="../../dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}-${VERSION}-macOS"
DMG_PATH="../../dist/${DMG_NAME}.dmg"
VOLUME_NAME="${APP_NAME}"

# 临时目录
TMP_DIR="../../build/dmg_tmp"

echo "======================================"
echo "创建 ${APP_NAME} DMG 镜像"
echo "======================================"

# 检查应用包是否存在
if [ ! -d "$APP_BUNDLE" ]; then
    echo "错误: 应用包不存在: $APP_BUNDLE"
    echo "请先运行 PyInstaller 构建应用"
    exit 1
fi

# 创建临时目录
echo "创建临时目录..."
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

# 复制应用到临时目录
echo "复制应用包..."
cp -R "$APP_BUNDLE" "$TMP_DIR/"

# 创建 Applications 符号链接
echo "创建 Applications 链接..."
ln -s /Applications "$TMP_DIR/Applications"

# 删除旧的 DMG（如果存在）
if [ -f "$DMG_PATH" ]; then
    echo "删除旧的 DMG 文件..."
    rm "$DMG_PATH"
fi

# 创建 DMG
echo "创建 DMG 镜像..."
hdiutil create \
    -volname "$VOLUME_NAME" \
    -srcfolder "$TMP_DIR" \
    -ov \
    -format UDZO \
    "$DMG_PATH"

# 清理临时目录
echo "清理临时文件..."
rm -rf "$TMP_DIR"

echo "======================================"
echo "DMG 创建完成！"
echo "输出文件: $DMG_PATH"
echo "======================================"

# 可选：验证 DMG
echo "验证 DMG..."
hdiutil verify "$DMG_PATH"

echo "✓ DMG 验证通过"
