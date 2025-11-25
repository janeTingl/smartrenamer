# SmartRenamer 打包和发布指南

本文档详细介绍如何为 Windows、macOS 和 Linux 平台打包和发布 SmartRenamer。

## 📋 目录

- [概述](#概述)
- [准备工作](#准备工作)
- [Windows 打包](#windows-打包)
- [macOS 打包](#macos-打包)
- [Linux 打包](#linux-打包)
- [自动化构建](#自动化构建)
- [发布流程](#发布流程)
- [故障排除](#故障排除)

---

## 概述

SmartRenamer 支持以下打包格式：

| 平台 | 格式 | 说明 |
|------|------|------|
| Windows | `.exe` (单文件) | PyInstaller 生成的独立可执行文件 |
| Windows | `.exe` (安装程序) | NSIS 安装程序 |
| macOS | `.app` | macOS 应用包 |
| macOS | `.dmg` | DMG 磁盘镜像 |
| Linux | `.AppImage` | 便携式 AppImage |

---

## 准备工作

### 1. 环境要求

- **Python**: 3.8 或更高版本
- **Git**: 版本控制
- **网络连接**: 下载依赖和工具

### 2. 克隆仓库

```bash
git clone https://github.com/smartrenamer/smartrenamer.git
cd smartrenamer
```

### 3. 安装依赖

```bash
# 安装运行时依赖
pip install -r requirements.txt

# 安装构建工具
pip install pyinstaller
```

### 4. 准备图标

确保 `assets/` 目录下有以下图标文件：
- `icon.ico` - Windows 图标
- `icon.icns` - macOS 图标
- `icon.png` - Linux 图标

参考 `assets/README.md` 了解如何创建图标。

---

## Windows 打包

### 方法 1: 使用自动构建脚本（推荐）

```bash
python scripts/build.py --clean
```

这将自动完成以下步骤：
1. 安装依赖
2. 使用 PyInstaller 构建可执行文件
3. 创建 NSIS 安装程序（如果已安装 NSIS）
4. 生成校验和

### 方法 2: 手动构建

#### 步骤 1: 构建可执行文件

```bash
pyinstaller --clean --noconfirm smartrenamer.spec
```

输出文件位于 `dist/SmartRenamer.exe`

#### 步骤 2: 测试可执行文件

```bash
.\dist\SmartRenamer.exe --help
```

#### 步骤 3: 创建便携版

将 `dist/SmartRenamer.exe` 和 `dist/_internal/` 打包成 ZIP：

```powershell
cd dist
Compress-Archive -Path SmartRenamer.exe, _internal -DestinationPath SmartRenamer-Windows-Portable.zip
```

#### 步骤 4: 创建安装程序（可选）

**前置要求**: 安装 [NSIS](https://nsis.sourceforge.io/)

```bash
# 使用 NSIS 编译安装脚本
makensis scripts\windows\installer.nsi
```

输出文件: `dist/SmartRenamer-0.6.0-Windows-Setup.exe`

### Windows 构建选项

#### 单文件模式 vs 目录模式

**单文件模式**（默认）:
- 优点：分发方便，只有一个文件
- 缺点：启动稍慢（需要解压到临时目录）

**目录模式**:
- 优点：启动快
- 缺点：需要分发整个目录

修改 `smartrenamer.spec`：
```python
# 单文件模式
exe = EXE(..., onefile=True, ...)

# 目录模式
exe = EXE(..., onefile=False, ...)
```

#### 隐藏控制台窗口

在 `smartrenamer.spec` 中设置：
```python
exe = EXE(..., console=False, ...)  # GUI 模式，不显示控制台
```

### NSIS 安装程序自定义

编辑 `scripts/windows/installer.nsi` 可以自定义：
- 安装目录
- 开始菜单项
- 桌面快捷方式
- 卸载程序
- 许可协议

---

## macOS 打包

### 方法 1: 使用自动构建脚本（推荐）

```bash
python scripts/build.py --clean
```

### 方法 2: 手动构建

#### 步骤 1: 构建应用包

```bash
pyinstaller --clean --noconfirm smartrenamer.spec
```

输出文件位于 `dist/SmartRenamer.app`

#### 步骤 2: 测试应用

```bash
./dist/SmartRenamer.app/Contents/MacOS/SmartRenamer --help
```

#### 步骤 3: 创建 DMG 镜像

```bash
cd scripts/macos
./create_dmg.sh
```

输出文件: `dist/SmartRenamer-0.6.0-macOS.dmg`

### macOS 签名和公证（可选）

#### 前置要求
- Apple Developer 账号
- 开发者证书
- Xcode Command Line Tools

#### 签名应用

```bash
# 签名应用包
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  dist/SmartRenamer.app

# 验证签名
codesign --verify --deep --strict --verbose=2 dist/SmartRenamer.app
```

#### 公证应用

```bash
# 1. 创建 DMG
hdiutil create -volname SmartRenamer -srcfolder dist/SmartRenamer.app \
  -ov -format UDZO dist/SmartRenamer.dmg

# 2. 提交公证
xcrun notarytool submit dist/SmartRenamer.dmg \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# 3. 装订公证票据
xcrun stapler staple dist/SmartRenamer.dmg

# 4. 验证公证
xcrun stapler validate dist/SmartRenamer.dmg
```

### 多架构支持

构建通用二进制（Intel + Apple Silicon）：

```bash
# 使用 universal2 选项
pyinstaller --clean --noconfirm --target-arch universal2 smartrenamer.spec
```

---

## Linux 打包

### 方法 1: 使用自动构建脚本（推荐）

```bash
python scripts/build.py --clean
```

### 方法 2: 手动构建

#### 步骤 1: 安装系统依赖

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y \
  libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
  libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-shape0 libxcb-xfixes0 libxkbcommon-x11-0 \
  libgl1-mesa-glx libegl1-mesa libfontconfig1 \
  libdbus-1-3 file wget
```

**Fedora/RHEL**:
```bash
sudo dnf install -y \
  libxcb libXext libXrender libXinerama \
  fontconfig dbus-libs file wget
```

#### 步骤 2: 构建可执行文件

```bash
pyinstaller --clean --noconfirm smartrenamer.spec
```

输出文件位于 `dist/SmartRenamer`

#### 步骤 3: 测试可执行文件

```bash
./dist/SmartRenamer --help
```

#### 步骤 4: 创建 AppImage

```bash
cd scripts/linux
./create_appimage.sh
```

输出文件: `dist/SmartRenamer-0.6.0-x86_64.AppImage`

### AppImage 说明

AppImage 是一种便携式应用格式，优点：
- 无需安装，直接运行
- 包含所有依赖
- 适用于大多数 Linux 发行版
- 支持沙箱运行

使用方法：
```bash
chmod +x SmartRenamer-0.6.0-x86_64.AppImage
./SmartRenamer-0.6.0-x86_64.AppImage
```

### 创建 Debian 包（可选）

使用 `fpm` 工具创建 `.deb` 包：

```bash
# 安装 fpm
gem install fpm

# 创建 deb 包
fpm -s dir -t deb \
  -n smartrenamer \
  -v 0.6.0 \
  --description "智能媒体文件重命名工具" \
  --url "https://github.com/smartrenamer/smartrenamer" \
  --license "MIT" \
  --category "utils" \
  --depends "python3 >= 3.8" \
  dist/SmartRenamer=/usr/bin/smartrenamer
```

---

## 自动化构建

### GitHub Actions

项目已配置 GitHub Actions 自动构建工作流（`.github/workflows/build-release.yml`）。

#### 触发构建

**方法 1: 推送标签**
```bash
git tag v0.6.0
git push origin v0.6.0
```

**方法 2: 手动触发**
1. 访问 GitHub 仓库的 Actions 页面
2. 选择 "构建跨平台发布包" 工作流
3. 点击 "Run workflow"
4. 输入版本号

#### 工作流输出

工作流会自动：
1. 在 Windows、macOS、Linux 上构建可执行文件
2. 创建安装程序（Windows）、DMG（macOS）、AppImage（Linux）
3. 生成 SHA256 校验和
4. 创建 GitHub Release
5. 上传所有构建产物

### 本地自动化

使用提供的构建脚本：

```bash
# 清理并构建
python scripts/build.py --clean

# 调试模式
python scripts/build.py --debug

# 查看帮助
python scripts/build.py --help
```

---

## 发布流程

### 1. 更新版本号

在以下文件中更新版本号：
- `setup.py`
- `pyproject.toml`
- `smartrenamer.spec`
- `scripts/windows/installer.nsi`
- `scripts/macos/create_dmg.sh`
- `scripts/linux/create_appimage.sh`

### 2. 更新文档

- 更新 `CHANGELOG.md`
- 更新 `README.md`
- 更新版本相关文档

### 3. 本地测试

```bash
# 在本地构建和测试所有平台（如果可能）
python scripts/build.py --clean

# 测试可执行文件
./dist/SmartRenamer --help
```

### 4. 提交更改

```bash
git add .
git commit -m "Release v0.6.0"
git push
```

### 5. 创建标签

```bash
git tag -a v0.6.0 -m "Release version 0.6.0"
git push origin v0.6.0
```

### 6. GitHub Actions 自动构建

推送标签后，GitHub Actions 会自动：
- 构建所有平台的可执行文件
- 创建 GitHub Release
- 上传构建产物

### 7. 验证发布

1. 访问 GitHub Releases 页面
2. 下载各平台的文件
3. 验证校验和
4. 测试运行

### 8. 发布公告

- 在 GitHub Discussions 发布公告
- 更新项目网站（如果有）
- 社交媒体宣传

---

## 故障排除

### Windows

#### 问题: 缺少 DLL 文件

**解决方案**:
- 安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- 在 `smartrenamer.spec` 中添加缺失的 DLL

#### 问题: 防病毒软件误报

**解决方案**:
- 使用代码签名证书签名 exe
- 向防病毒软件厂商报告误报
- 提供 VirusTotal 扫描报告

#### 问题: NSIS 编译失败

**解决方案**:
- 确保 NSIS 已正确安装
- 检查路径中是否包含 `makensis`
- 验证 `installer.nsi` 语法

### macOS

#### 问题: "应用已损坏" 错误

**解决方案**:
```bash
# 移除隔离属性
sudo xattr -r -d com.apple.quarantine SmartRenamer.app
```

#### 问题: 签名失败

**解决方案**:
- 确认开发者证书有效
- 使用 `security find-identity -v -p codesigning` 查看证书
- 检查 Keychain Access

#### 问题: DMG 创建失败

**解决方案**:
- 确保有足够的磁盘空间
- 检查文件权限
- 使用 `diskutil list` 查看挂载的卷

#### 问题: PyInstaller Qt 框架符号链接冲突

**错误信息**:
```
FileExistsError: [Errno 17] File exists: 'Versions/Current/Resources'
```

**原因**:
PyInstaller 6.x 在处理 PySide6 的 Qt 框架时，会遇到 macOS 框架符号链接的冲突问题。

**解决方案**:
已在 `smartrenamer.spec` 中修复，无需额外操作。修复方法：

1. macOS 上跳过手动收集 PySide6 数据文件
2. 让 PyInstaller 自动处理 Qt 框架依赖
3. 避免符号链接的重复创建

详细信息参考：`docs/MACOS_PYINSTALLER_FIX.md`

**验证修复**:
```bash
./test_macos_build.sh
```

### Linux

#### 问题: 缺少共享库

**解决方案**:
```bash
# 检查缺失的库
ldd dist/SmartRenamer

# 安装缺失的库（Ubuntu）
sudo apt-get install -y <library-name>
```

#### 问题: AppImage 无法运行

**解决方案**:
```bash
# 启用执行权限
chmod +x SmartRenamer.AppImage

# 提取 AppImage 内容（调试）
./SmartRenamer.AppImage --appimage-extract

# 运行提取的内容
./squashfs-root/AppRun
```

#### 问题: Qt 平台插件错误

**解决方案**:
```bash
# 安装 Qt 依赖
sudo apt-get install -y libxcb-xinerama0

# 设置环境变量
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
```

### 通用问题

#### 问题: PyInstaller 找不到模块

**解决方案**:
在 `smartrenamer.spec` 的 `hiddenimports` 中添加缺失的模块：
```python
hiddenimports = [
    'missing_module',
    'another_module',
]
```

#### 问题: 文件过大

**解决方案**:
- 使用 UPX 压缩（已在 spec 文件中启用）
- 排除不必要的模块
- 使用虚拟环境减少依赖

#### 问题: 图标未显示

**解决方案**:
- 确认图标文件存在且格式正确
- 检查 `smartrenamer.spec` 中的图标路径
- 使用绝对路径

---

## 最佳实践

### 1. 版本管理

- 使用语义化版本（Semantic Versioning）
- 在所有配置文件中保持版本一致
- 记录每个版本的更改

### 2. 测试

- 在真实系统上测试（不只是虚拟机）
- 测试不同的系统版本
- 测试全新安装和升级安装

### 3. 文档

- 提供清晰的安装说明
- 记录系统要求
- 提供故障排除指南

### 4. 安全

- 签名所有可执行文件
- 提供校验和
- 使用 HTTPS 分发

### 5. 用户体验

- 提供多种分发格式
- 简化安装流程
- 提供卸载工具

---

## 相关资源

### 工具文档

- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [NSIS 文档](https://nsis.sourceforge.io/Docs/)
- [AppImage 文档](https://docs.appimage.org/)

### 教程

- [Python 应用打包完整指南](https://realpython.com/pyinstaller-python/)
- [macOS 应用签名和公证](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Linux 应用分发最佳实践](https://packaging.python.org/en/latest/)

### 社区

- [PyInstaller GitHub](https://github.com/pyinstaller/pyinstaller)
- [AppImage GitHub](https://github.com/AppImage/AppImageKit)
- [Stack Overflow - PyInstaller Tag](https://stackoverflow.com/questions/tagged/pyinstaller)

---

## 联系和支持

如有问题或需要帮助：
- 提交 [GitHub Issue](https://github.com/smartrenamer/smartrenamer/issues)
- 查看 [GitHub Discussions](https://github.com/smartrenamer/smartrenamer/discussions)
- 阅读 [FAQ](https://github.com/smartrenamer/smartrenamer/wiki/FAQ)

---

**版本**: 0.6.0  
**更新时间**: 2024-11-24  
**维护者**: SmartRenamer Team
