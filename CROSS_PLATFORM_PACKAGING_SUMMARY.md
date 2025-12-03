# SmartRenamer 平台支持变更说明

> **重要通知**: 本文档记录了 SmartRenamer 从跨平台支持转向 macOS 专用的变更历史。

## 📋 状态变更

### 当前状态（v0.10.0+）

**SmartRenamer 现在专注于 macOS 平台**

- ✅ **macOS**: 完全支持（Intel + Apple Silicon）
- ❌ **Windows**: 已停止支持
- ❌ **Linux**: 已停止支持
- ❌ **Docker**: 已过时（不再维护）

### 变更原因

为了提供更好的用户体验，SmartRenamer 团队决定专注于 macOS 平台：

1. **原生体验**: 充分利用 macOS 的原生功能和设计理念
2. **开发效率**: 集中资源在单一平台上提供更好的功能
3. **维护成本**: 减少跨平台兼容性问题
4. **用户群体**: 主要用户在 macOS 平台

---

## 历史版本支持

### v0.6.0 - v0.9.x：跨平台时代

在这些版本中，SmartRenamer 支持三大平台：

#### Windows 支持（已停止）
- ✅ PyInstaller 单文件可执行文件
- ✅ NSIS 安装程序
- ✅ 便携版 ZIP 打包
- ✅ 桌面和开始菜单快捷方式

#### macOS 支持（继续）
- ✅ .app 应用包
- ✅ DMG 镜像
- ✅ Universal Binary（Intel + Apple Silicon）
- ✅ 签名和公证支持

#### Linux 支持（已停止）
- ✅ AppImage 便携格式
- ✅ Desktop 文件集成
- ✅ 主流发行版兼容

#### 自动化构建（已过时）
- ✅ GitHub Actions 跨平台构建
- ✅ Windows、macOS、Linux 并行构建
- ✅ 自动发布到 GitHub Releases

---

## 迁移指南

### Windows 用户

如果您之前在 Windows 上使用 SmartRenamer：

**选项 1: 使用 Python 源码（不推荐）**
```bash
# 克隆仓库
git clone https://github.com/smartrenamer/smartrenamer.git
cd smartrenamer

# 安装依赖
pip install -r requirements.txt

# 运行
python src/smartrenamer/main.py
```

**选项 2: 寻找替代方案**
- 考虑使用其他支持 Windows 的媒体文件重命名工具
- 或在虚拟机中运行 macOS（需要 Apple 硬件）

**注意**: 不再提供 Windows 可执行文件和安装程序。

### Linux 用户

如果您之前在 Linux 上使用 SmartRenamer：

**选项 1: 使用 Python 源码**
```bash
# 克隆仓库
git clone https://github.com/smartrenamer/smartrenamer.git
cd smartrenamer

# 安装依赖（Ubuntu/Debian）
sudo apt-get install python3-pip python3-venv
sudo apt-get install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
  libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-shape0 libxcb-xfixes0 libxkbcommon-x11-0

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行
python src/smartrenamer/main.py
```

**选项 2: 寻找替代方案**
- 考虑使用其他支持 Linux 的媒体文件重命名工具
- 或使用命令行工具（如 FileBot）

**注意**: 不再提供 AppImage 或其他 Linux 打包格式。

### Docker 用户

Docker 支持已过时：

- Docker 镜像不再更新
- Docker 相关文档仍可参考，但可能过时
- 推荐使用 Python 源码安装替代

---

## 已移除的文件和功能

### 构建脚本
- ❌ `scripts/windows/installer.nsi` - Windows NSIS 安装脚本
- ❌ `scripts/linux/create_appimage.sh` - Linux AppImage 创建脚本
- ❌ `scripts/build.py` - 跨平台统一构建脚本（部分功能）
- ❌ `build.bat` - Windows 快速构建脚本
- ❌ `.github/workflows/build-release.yml` - 跨平台构建工作流

### 文档
- 📝 `PACKAGING_GUIDE.md` - 更新为 macOS 专用
- 📝 `SYSTEM_REQUIREMENTS.md` - 更新为 macOS 专用
- 📝 `PACKAGING_CHECKLIST.md` - 更新为 macOS 专用
- 📝 `README.md` - 更新安装说明

### 资源文件
- ⚠️ `assets/icon.ico` - Windows 图标（保留用于备份）
- ⚠️ `assets/smartrenamer.desktop` - Linux Desktop 文件（不再维护）

---

## 保留的功能

### 继续支持

1. **macOS 打包**
   - .app 应用包生成
   - DMG 磁盘镜像创建
   - Universal Binary 支持
   - 签名和公证

2. **核心功能**
   - 媒体文件扫描
   - TMDB API 匹配
   - 智能重命名
   - GUI 界面
   - 所有核心业务逻辑

3. **开发功能**
   - Python 源码安装
   - 开发者工具
   - 测试框架
   - API 文档

### 通用功能（跨平台）

虽然专注于 macOS，但核心 Python 代码仍然是跨平台的：
- 核心业务逻辑
- TMDB API 客户端
- 文件解析和匹配
- 重命名引擎

**注意**: 虽然代码可以在其他平台运行，但不再提供预编译的可执行文件和官方支持。

---

## 技术细节

### PyInstaller 配置变更

`smartrenamer.spec` 已优化为 macOS 专用：

```python
# macOS 特定优化
IS_MACOS = sys.platform == 'darwin'

# 仅在 macOS 上构建
if not IS_MACOS:
    raise RuntimeError("此配置仅支持 macOS 平台")

# macOS 框架处理
if IS_MACOS:
    # 跳过 PySide6 数据文件收集，避免符号链接冲突
    # 让 PyInstaller 自动处理 Qt 框架
    pass
```

### 文档更新

所有主要文档已更新：
1. **README.md**: 移除 Windows/Linux 安装说明
2. **PACKAGING_GUIDE.md**: 仅描述 macOS 打包流程
3. **SYSTEM_REQUIREMENTS.md**: 仅列出 macOS 要求
4. **PACKAGING_CHECKLIST.md**: 仅包含 macOS 检查项

---

## 时间线

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.5.1 | 2024-11-23 | Docker 支持添加 |
| v0.6.0 | 2024-11-24 | 跨平台打包支持完成 |
| v0.7.0-v0.9.2 | 2024-11-25+ | 性能优化和功能增强 |
| v0.10.0 | 2024-12-03 | 停止 Windows/Linux 支持，专注 macOS |

---

## 未来计划

### 短期（v0.10.x）
- ✅ 完善 macOS 专用功能
- ✅ 优化 macOS 用户体验
- ✅ 改进 DMG 安装体验
- 🔄 获取代码签名和公证

### 中期（v0.11.x+）
- 🔄 macOS 原生功能集成
- 🔄 Spotlight 集成
- 🔄 Finder 扩展
- 🔄 macOS 特有 UI 改进

### 长期
- 🔄 考虑 Mac App Store 发布
- 🔄 沙箱化应用
- 🔄 自动更新机制
- 🔄 iCloud 同步支持

---

## 常见问题

### Q: 为什么停止 Windows 和 Linux 支持？

A: 为了提供更好的 macOS 用户体验，我们决定专注于单一平台。这使我们能够：
- 利用 macOS 原生功能
- 减少跨平台兼容性问题
- 提供更快的功能更新
- 降低维护成本

### Q: 旧版本还能用吗？

A: 是的，v0.6.0 - v0.9.x 版本的 Windows 和 Linux 可执行文件仍可从 GitHub Releases 下载。但这些版本不再更新，也不提供技术支持。

### Q: 可以在其他平台上运行源码吗？

A: 技术上可以，核心 Python 代码仍然是跨平台的。但我们不再提供官方支持，也不保证在其他平台上的兼容性。

### Q: Docker 支持会恢复吗？

A: 目前没有计划。Docker 主要用于跨平台场景，现在专注于 macOS 后不再需要。

### Q: 会考虑支持 iPad 或 iOS 吗？

A: 目前没有计划，但未来可能考虑。

---

## 获取帮助

如果您对平台变更有疑问：

1. **阅读文档**: 查看更新后的 README 和 PACKAGING_GUIDE
2. **搜索 Issues**: 在 GitHub 搜索相关问题
3. **创建 Issue**: 提出您的问题或建议
4. **联系开发者**: 通过 GitHub Discussions

---

## 相关文档

- [README.md](README.md) - 项目说明（已更新）
- [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md) - macOS 打包指南
- [SYSTEM_REQUIREMENTS.md](SYSTEM_REQUIREMENTS.md) - macOS 系统要求
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [PACKAGING_CHECKLIST.md](PACKAGING_CHECKLIST.md) - macOS 检查清单

---

**最后更新**: 2024-12-03  
**当前版本**: v0.10.0  
**状态**: macOS only
