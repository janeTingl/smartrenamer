#!/bin/bash
# SmartRenamer 快速构建脚本（仅支持 macOS）

set -e

echo "======================================"
echo "SmartRenamer macOS 构建脚本"
echo "======================================"
echo ""

# 检查是否在 macOS 上运行
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "错误: 此构建脚本仅支持 macOS 平台"
    echo "当前平台: $(uname -s)"
    echo "请在 macOS 系统上运行此脚本"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

# 安装依赖
echo "1. 安装依赖..."
pip3 install -r requirements.txt
pip3 install pyinstaller

# 清理旧的构建
echo ""
echo "2. 清理旧的构建..."
rm -rf build dist

# 运行构建脚本
echo ""
echo "3. 运行 PyInstaller 构建..."
python3 scripts/build.py --clean

echo ""
echo "======================================"
echo "macOS 构建完成！"
echo "生成文件位于 dist/ 目录"
echo "  - SmartRenamer.app"
echo "  - SmartRenamer-macOS.dmg"
echo "======================================"
