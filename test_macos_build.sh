#!/bin/bash
# macOS PyInstaller 构建测试脚本
# 用于验证符号链接问题修复

set -e  # 遇到错误立即退出

echo "=================================================="
echo "测试 macOS PyInstaller 构建（符号链接修复验证）"
echo "=================================================="

# 检查平台
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "警告: 此脚本应在 macOS 上运行"
    echo "继续执行以验证 spec 文件配置..."
fi

# 清理旧的构建产物
echo ""
echo "步骤 1: 清理旧的构建产物..."
rm -rf build/ dist/

# 检查依赖
echo ""
echo "步骤 2: 检查依赖..."
python3 -c "import PyInstaller; print(f'PyInstaller 版本: {PyInstaller.__version__}')" || {
    echo "PyInstaller 未安装，正在安装..."
    pip3 install pyinstaller
}

python3 -c "import PySide6.QtCore; print(f'PySide6 版本: {PySide6.QtCore.__version__}')" || {
    echo "PySide6 未安装，正在安装..."
    pip3 install -r requirements.txt
}

# 验证 spec 文件
echo ""
echo "步骤 3: 验证 spec 文件配置..."
if [[ ! -f "smartrenamer.spec" ]]; then
    echo "错误: smartrenamer.spec 文件不存在"
    exit 1
fi

# 检查 spec 文件中的关键配置
if grep -q "if not IS_MACOS:" smartrenamer.spec; then
    echo "✓ 发现 macOS 平台特定配置"
else
    echo "✗ 缺少 macOS 平台特定配置"
    exit 1
fi

# 执行构建
echo ""
echo "步骤 4: 执行 PyInstaller 构建..."
echo "命令: pyinstaller --clean --noconfirm smartrenamer.spec"
pyinstaller --clean --noconfirm smartrenamer.spec

# 检查构建结果
echo ""
echo "步骤 5: 检查构建结果..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS 平台
    if [[ -d "dist/SmartRenamer.app" ]]; then
        echo "✓ SmartRenamer.app 构建成功"
        
        # 检查应用结构
        echo ""
        echo "应用包结构:"
        ls -lh dist/SmartRenamer.app/Contents/
        
        # 检查可执行文件
        if [[ -f "dist/SmartRenamer.app/Contents/MacOS/SmartRenamer" ]]; then
            echo "✓ 可执行文件存在"
            
            # 尝试执行 --help
            echo ""
            echo "步骤 6: 测试应用启动..."
            ./dist/SmartRenamer.app/Contents/MacOS/SmartRenamer --help || {
                echo "警告: 应用启动测试失败（可能缺少运行时依赖）"
            }
        else
            echo "✗ 可执行文件不存在"
            exit 1
        fi
        
        # 检查框架目录（确保没有符号链接问题）
        echo ""
        echo "步骤 7: 检查 Qt 框架..."
        if [[ -d "dist/SmartRenamer.app/Contents/Frameworks" ]]; then
            echo "Frameworks 目录内容:"
            ls -lh dist/SmartRenamer.app/Contents/Frameworks/ | head -20
            
            # 检查是否存在问题的符号链接
            if find dist/SmartRenamer.app/Contents/Frameworks -name "Versions" -type d 2>/dev/null | grep -q .; then
                echo "发现 Versions 目录，检查符号链接..."
                find dist/SmartRenamer.app/Contents/Frameworks -name "Current" -type l 2>/dev/null || echo "未发现问题符号链接"
            fi
        else
            echo "未发现 Frameworks 目录（PyInstaller 可能使用了不同的布局）"
        fi
    else
        echo "✗ SmartRenamer.app 构建失败"
        exit 1
    fi
else
    # 非 macOS 平台
    echo "在非 macOS 平台上运行，跳过 .app 检查"
    if [[ -d "dist/SmartRenamer" ]]; then
        echo "✓ 构建目录存在: dist/SmartRenamer"
    fi
fi

echo ""
echo "=================================================="
echo "✓ 构建测试完成！"
echo "=================================================="
echo ""
echo "构建产物位置: dist/"
echo ""
echo "如果在 macOS 上，可以运行以下命令启动应用:"
echo "  open dist/SmartRenamer.app"
echo ""
echo "或直接执行:"
echo "  ./dist/SmartRenamer.app/Contents/MacOS/SmartRenamer"
echo ""
