#!/bin/bash
# SmartRenamer Linux AppImage 创建脚本

set -e

# 配置
APP_NAME="SmartRenamer"
VERSION="0.6.0"
ARCH=$(uname -m)
APPIMAGE_NAME="${APP_NAME}-${VERSION}-${ARCH}.AppImage"
DIST_DIR="../../dist"
BUILD_DIR="../../build/appimage"
APPDIR="${BUILD_DIR}/${APP_NAME}.AppDir"

echo "======================================"
echo "创建 ${APP_NAME} AppImage"
echo "======================================"

# 检查 appimagetool
if ! command -v appimagetool &> /dev/null; then
    echo "下载 appimagetool..."
    wget -O /tmp/appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    chmod +x /tmp/appimagetool
    APPIMAGETOOL="/tmp/appimagetool"
else
    APPIMAGETOOL="appimagetool"
fi

# 检查可执行文件
if [ ! -f "${DIST_DIR}/SmartRenamer" ]; then
    echo "错误: 可执行文件不存在: ${DIST_DIR}/SmartRenamer"
    echo "请先运行 PyInstaller 构建应用"
    exit 1
fi

# 创建 AppDir 结构
echo "创建 AppDir 结构..."
rm -rf "$BUILD_DIR"
mkdir -p "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# 复制可执行文件
echo "复制可执行文件..."
cp "${DIST_DIR}/SmartRenamer" "$APPDIR/usr/bin/"
chmod +x "$APPDIR/usr/bin/SmartRenamer"

# 复制依赖库（如果有）
if [ -d "${DIST_DIR}/_internal" ]; then
    echo "复制依赖库..."
    cp -R "${DIST_DIR}/_internal" "$APPDIR/usr/lib/"
fi

# 创建 desktop 文件
echo "创建 desktop 文件..."
cat > "$APPDIR/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=SmartRenamer
Comment=智能媒体文件重命名工具
Exec=SmartRenamer
Icon=smartrenamer
Categories=Utility;AudioVideo;
Terminal=false
EOF

# 复制图标（如果存在）
if [ -f "../../assets/icon.png" ]; then
    cp "../../assets/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/smartrenamer.png"
    cp "../../assets/icon.png" "$APPDIR/smartrenamer.png"
else
    echo "警告: 图标文件不存在，跳过图标复制"
fi

# 创建 AppRun 脚本
echo "创建 AppRun 脚本..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
# AppImage 启动脚本

APPDIR="$(dirname "$(readlink -f "$0")")"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"

# 设置 Qt 平台插件路径
export QT_PLUGIN_PATH="${APPDIR}/usr/lib/_internal/PySide6/Qt/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${APPDIR}/usr/lib/_internal/PySide6/Qt/plugins/platforms"

# 运行应用
exec "${APPDIR}/usr/bin/SmartRenamer" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# 创建符号链接
ln -sf usr/share/applications/${APP_NAME}.desktop "$APPDIR/${APP_NAME}.desktop"
ln -sf usr/bin/SmartRenamer "$APPDIR/AppRun"

# 构建 AppImage
echo "构建 AppImage..."
cd "$BUILD_DIR"
"$APPIMAGETOOL" "$APPDIR" "${APPIMAGE_NAME}"

# 移动到 dist 目录
echo "移动 AppImage 到 dist 目录..."
mv "${APPIMAGE_NAME}" "../../dist/"

# 清理
echo "清理临时文件..."
cd ../..
rm -rf "$BUILD_DIR"

echo "======================================"
echo "AppImage 创建完成！"
echo "输出文件: ${DIST_DIR}/${APPIMAGE_NAME}"
echo "======================================"

# 显示文件信息
ls -lh "${DIST_DIR}/${APPIMAGE_NAME}"
