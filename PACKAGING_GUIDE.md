# SmartRenamer 打包和发布指南

> **重要提示**: SmartRenamer 现在专注于 macOS 平台。本指南仅涵盖 macOS 打包流程。

本文档详细介绍如何为 macOS 平台打包和发布 SmartRenamer。

## 📋 目录

- [概述](#概述)
- [准备工作](#准备工作)
- [macOS 打包](#macos-打包)
- [发布流程](#发布流程)
- [故障排除](#故障排除)

---

## 概述

SmartRenamer 支持以下 macOS 打包格式：

| 格式 | 说明 |
|------|------|
| `.app` | macOS 应用包 |
| `.dmg` | DMG 磁盘镜像（推荐分发格式）|

**架构支持**:
- Intel (x86_64)
- Apple Silicon (ARM64/M1/M2)
- Universal Binary (同时支持两种架构)

---

## 准备工作

### 1. 环境要求

- **macOS**: 10.13 或更高版本
- **Python**: 3.8 或更高版本
- **Xcode Command Line Tools**: 用于签名和公证
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
pip3 install -r requirements.txt

# 安装构建工具
pip3 install pyinstaller
```

### 4. 准备图标

生成应用图标：

```bash
python3 generate_icons.py
```

这将在 `assets/` 目录下创建：
- `icon.icns` - macOS 图标
- `icon.ico` - 备用图标
- `icon.png` - PNG 图标

---

## macOS 打包

### 方法 1: 使用自动构建脚本（推荐）

```bash
cd scripts/macos
./create_dmg.sh
```

这将自动完成以下步骤：
1. 使用 PyInstaller 构建 .app 应用包
2. 创建 DMG 磁盘镜像
3. 生成校验和

### 方法 2: 手动构建

#### 步骤 1: 构建应用包

```bash
pyinstaller --clean --noconfirm smartrenamer.spec
```

输出文件位于 `dist/SmartRenamer.app`

#### 步骤 2: 测试应用

```bash
# 测试应用启动
./dist/SmartRenamer.app/Contents/MacOS/SmartRenamer --help

# 或者直接打开应用
open dist/SmartRenamer.app
```

#### 步骤 3: 创建 DMG 镜像

```bash
cd scripts/macos
./create_dmg.sh
```

输出文件: `dist/SmartRenamer-{version}-macOS.dmg`

### Universal Binary 构建

构建同时支持 Intel 和 Apple Silicon 的通用二进制：

```bash
# 使用 universal2 选项
pyinstaller --clean --noconfirm --target-arch universal2 smartrenamer.spec
```

**注意**: 
- 需要在 macOS 11 或更高版本上构建
- 某些依赖可能不支持 universal2

### 应用签名（可选）

#### 前置要求
- Apple Developer 账号
- 开发者证书（Developer ID Application）
- Xcode Command Line Tools

#### 签名应用包

```bash
# 查看可用的签名证书
security find-identity -v -p codesigning

# 签名应用包
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  dist/SmartRenamer.app

# 验证签名
codesign --verify --deep --strict --verbose=2 dist/SmartRenamer.app
spctl -a -vv dist/SmartRenamer.app
```

### 应用公证（推荐）

公证（Notarization）可以让您的应用在 macOS Gatekeeper 中更容易通过。

#### 步骤 1: 创建 DMG

```bash
hdiutil create -volname SmartRenamer -srcfolder dist/SmartRenamer.app \
  -ov -format UDZO dist/SmartRenamer.dmg
```

#### 步骤 2: 提交公证

```bash
# 使用 notarytool（macOS 12+ 推荐）
xcrun notarytool submit dist/SmartRenamer.dmg \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# 或使用 altool（旧版本 macOS）
xcrun altool --notarize-app \
  --primary-bundle-id "com.smartrenamer.SmartRenamer" \
  --username "your@email.com" \
  --password "app-specific-password" \
  --file dist/SmartRenamer.dmg
```

#### 步骤 3: 装订公证票据

```bash
# 装订票据到 DMG
xcrun stapler staple dist/SmartRenamer.dmg

# 验证公证
xcrun stapler validate dist/SmartRenamer.dmg
spctl -a -vv dist/SmartRenamer.dmg
```

### DMG 自定义

您可以自定义 DMG 的外观和行为。编辑 `scripts/macos/create_dmg.sh` 脚本：

```bash
# 自定义卷名
VOLUME_NAME="SmartRenamer"

# 自定义背景图片
BACKGROUND_IMAGE="path/to/background.png"

# 自定义窗口大小和图标位置
# 编辑脚本中的 AppleScript 部分
```

---

## 发布流程

### 1. 更新版本号

在以下文件中更新版本号：
- `setup.py`
- `pyproject.toml`
- `smartrenamer.spec`
- `scripts/macos/create_dmg.sh`

### 2. 更新文档

- 更新 `CHANGELOG.md`
- 更新 `README.md`
- 更新版本相关文档

### 3. 本地测试

```bash
# 构建和测试
cd scripts/macos
./create_dmg.sh

# 测试 DMG
open dist/SmartRenamer-{version}-macOS.dmg

# 测试应用安装和运行
```

### 4. 提交更改

```bash
git add .
git commit -m "Release v{version}"
git push
```

### 5. 创建标签

```bash
git tag -a v{version} -m "Release version {version}"
git push origin v{version}
```

### 6. 创建 GitHub Release

1. 访问 GitHub 仓库的 Releases 页面
2. 点击 "Draft a new release"
3. 选择刚创建的标签
4. 上传构建产物：
   - `SmartRenamer-{version}-macOS.dmg`
   - `checksums-macos.txt`（校验和文件）
5. 填写发布说明
6. 发布 Release

### 7. 验证发布

1. 下载发布的 DMG 文件
2. 验证校验和：
   ```bash
   shasum -a 256 SmartRenamer-{version}-macOS.dmg
   ```
3. 测试安装和运行

### 8. 发布公告

- 在 GitHub Discussions 发布公告
- 更新项目网站（如果有）
- 社交媒体宣传

---

## 故障排除

### 常见问题

#### 问题: "应用已损坏" 错误

**原因**: macOS Gatekeeper 阻止未签名或未公证的应用。

**解决方案**:
```bash
# 方法 1: 移除隔离属性
sudo xattr -r -d com.apple.quarantine /Applications/SmartRenamer.app

# 方法 2: 在"系统偏好设置 > 安全性与隐私"中允许
# 打开应用后，如果被阻止，会在系统偏好设置中出现"仍要打开"按钮
```

#### 问题: 签名失败

**原因**: 证书无效或配置错误。

**解决方案**:
```bash
# 检查可用证书
security find-identity -v -p codesigning

# 查看证书详情
security find-certificate -c "Developer ID Application" -p | openssl x509 -text

# 如果证书过期，需要在 Apple Developer 网站更新
```

#### 问题: DMG 创建失败

**原因**: 磁盘空间不足或文件权限问题。

**解决方案**:
```bash
# 检查磁盘空间
df -h

# 检查文件权限
ls -la dist/

# 清理旧的 DMG
rm -f dist/*.dmg

# 重新创建
cd scripts/macos
./create_dmg.sh
```

#### 问题: PyInstaller 符号链接冲突

**错误信息**:
```
FileExistsError: [Errno 17] File exists: 'Versions/Current/Resources'
```

**原因**: PyInstaller 在处理 PySide6 的 Qt 框架时遇到符号链接冲突。

**解决方案**: 
此问题已在 `smartrenamer.spec` 中修复。如果仍然遇到问题：

```bash
# 确保使用最新的 spec 文件
git pull origin main

# 清理构建缓存
rm -rf build/ dist/

# 重新构建
pyinstaller --clean --noconfirm smartrenamer.spec
```

详见：`docs/MACOS_PYINSTALLER_FIX.md`

#### 问题: 应用无法访问网络

**原因**: 缺少网络权限配置。

**解决方案**:
检查 `smartrenamer.spec` 中的 `info_plist` 配置：

```python
info_plist={
    'CFBundleName': 'SmartRenamer',
    'NSHighResolutionCapable': 'True',
    'NSRequiresAquaSystemAppearance': 'False',
    # 添加网络权限
    'com.apple.security.network.client': True,
}
```

#### 问题: 在某些 macOS 版本上崩溃

**原因**: 依赖库不兼容或系统版本太旧。

**解决方案**:
```bash
# 检查最低系统版本要求
otool -l dist/SmartRenamer.app/Contents/MacOS/SmartRenamer | grep -A 3 LC_VERSION_MIN_MACOSX

# 如果需要支持更旧的系统，在构建时设置环境变量
export MACOSX_DEPLOYMENT_TARGET=10.13
pyinstaller --clean --noconfirm smartrenamer.spec
```

### 调试技巧

#### 查看应用日志

```bash
# 启动 Console.app 查看系统日志
open -a Console

# 或使用命令行查看日志
log stream --predicate 'process == "SmartRenamer"' --level debug
```

#### 测试应用包内容

```bash
# 查看应用包结构
ls -R dist/SmartRenamer.app/Contents/

# 检查依赖库
otool -L dist/SmartRenamer.app/Contents/MacOS/SmartRenamer

# 验证签名
codesign -dvvv dist/SmartRenamer.app
```

#### 手动运行可执行文件

```bash
# 从终端启动应用，查看错误输出
./dist/SmartRenamer.app/Contents/MacOS/SmartRenamer --debug
```

---

## 最佳实践

### 1. 版本管理

- 使用语义化版本号（Semantic Versioning）
- 在所有相关文件中保持版本号一致
- 为每个发布版本创建 Git 标签

### 2. 签名和公证

- 始终签名您的应用（即使不公证）
- 对于公开发布，强烈建议进行公证
- 保护好您的签名证书和密钥

### 3. 测试

- 在不同的 macOS 版本上测试（至少测试最新的两个主要版本）
- 在 Intel 和 Apple Silicon Mac 上测试
- 测试全新安装和升级场景
- 测试在没有开发工具的"干净"系统上运行

### 4. 文档

- 保持 CHANGELOG.md 更新
- 记录每个版本的重要变更
- 提供清晰的安装和使用说明
- 记录已知问题和限制

### 5. 发布流程

- 自动化构建流程（使用脚本）
- 验证构建产物（校验和）
- 提供详细的发布说明
- 及时响应用户反馈

---

## 相关文档

- [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) - 系统要求
- [README.md](README.md) - 项目说明
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [docs/MACOS_PYINSTALLER_FIX.md](docs/MACOS_PYINSTALLER_FIX.md) - PyInstaller 修复报告

---

**最后更新**: 2024-12-03  
**适用版本**: v0.9.0+  
**平台**: macOS only
