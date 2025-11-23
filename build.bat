@echo off
REM SmartRenamer 快速构建脚本（Windows）

echo ======================================
echo SmartRenamer 快速构建脚本
echo ======================================
echo.

REM 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到 Python
    exit /b 1
)

REM 安装依赖
echo 1. 安装依赖...
pip install -r requirements.txt
pip install pyinstaller pywin32

REM 清理旧的构建
echo.
echo 2. 清理旧的构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM 运行构建脚本
echo.
echo 3. 运行 PyInstaller 构建...
python scripts\build.py --clean

echo.
echo ======================================
echo 构建完成！
echo 可执行文件位于 dist\ 目录
echo ======================================

pause
