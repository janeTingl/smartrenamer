# 更新日志

本文档记录 SmartRenamer 项目的所有重要更改。

## [未发布]

## [1.0.0] - 2024-12-03

### 重大变更 ⚠️

#### 停止 Windows 和 Linux 支持 🍎

**SmartRenamer 现在专注于 macOS 平台**

- **平台支持变更**
  - ✅ **macOS**: 继续完全支持（Intel + Apple Silicon）
  - ❌ **Windows**: 停止支持，不再提供可执行文件和安装程序
  - ❌ **Linux**: 停止支持，不再提供 AppImage 和其他打包格式
  - ❌ **Docker**: 不再维护，相关文档已过时

- **变更原因**
  - 专注于提供更好的 macOS 原生体验
  - 充分利用 macOS 的原生功能和设计理念
  - 减少跨平台兼容性问题，降低维护成本
  - 提供更快的功能更新和更好的用户支持

- **用户影响**
  - macOS 用户：无影响，继续享受完整支持和更新
  - Windows/Linux 用户：可以使用 v0.6.0-v0.9.x 旧版本，或通过 Python 源码安装
  - 旧版本仍可从 GitHub Releases 下载，但不再更新

### 文档更新

#### 全面更新为 macOS 专用文档

- **README.md**
  - 移除 Windows 和 Linux 安装说明
  - 突出显示 macOS 专用安装方式
  - 更新系统要求和快速开始指南
  - 添加平台变更说明

- **PACKAGING_GUIDE.md**
  - 完全重写为 macOS 专用打包指南
  - 移除 Windows 和 Linux 打包流程
  - 详细说明 macOS .app 和 DMG 创建流程
  - 更新签名和公证说明

- **SYSTEM_REQUIREMENTS.md**
  - 仅保留 macOS 系统要求
  - 移除 Windows 和 Linux 相关内容
  - 详细说明 Intel 和 Apple Silicon 支持
  - 更新兼容性测试矩阵

- **PACKAGING_CHECKLIST.md**
  - 更新为 macOS 专用检查清单
  - 移除跨平台相关检查项
  - 添加已移除内容说明

- **CROSS_PLATFORM_PACKAGING_SUMMARY.md**
  - 重命名为平台支持变更说明
  - 记录从跨平台到 macOS 专用的变更历史
  - 提供迁移指南
  - 说明已移除的文件和功能

### 修复

#### Windows UTF-8 字符编码问题系统性修复 🔤✨ (v0.9.2)

- **修复范围**
  - ✅ **核心脚本**：`generate_icons.py` (v0.9.1)、`test_icon_compat.py`、`verify_project.py`、`test_encoding_fix.py`
  - ✅ **构建脚本**：`scripts/build.py`
  - ✅ **示例脚本**：`examples/` 下所有 5 个示例文件
  - 📊 **修复总数**：10 个脚本

- **问题描述**
  - 多个脚本包含中文字符（注释、输出、文档字符串）
  - Windows 控制台默认使用 cp1252 编码，无法处理中文
  - 错误信息：`UnicodeEncodeError: 'charmap' codec can't encode characters`
  - 导致构建和测试流程在 Windows 上失败

- **实施方案**
  - 添加 UTF-8 编码声明：`# -*- coding: utf-8 -*-`
  - 在 Windows 平台上配置 stdout/stderr 使用 UTF-8 编码
  - 使用 `sys.stdout.reconfigure(encoding='utf-8')` (Python 3.7+)
  - 兼容 Python 3.6：使用 `codecs.getwriter('utf-8')`
  - 在任何其他导入前执行编码配置

- **特点**
  - 🎯 **系统性修复**：一次性解决所有脚本的编码问题
  - 🖥️ **平台特定**：仅在 Windows 上执行编码配置
  - 🔧 **版本兼容**：支持 Python 3.6+
  - ✅ **向后兼容**：不影响 macOS 和 Linux 平台
  - 🚀 **自动化**：无需手动设置环境变量
  - 📝 **最佳实践**：提供清晰的新脚本开发规范

- **验证测试**
  - 创建专门的测试脚本 `test_encoding_fix.py`
  - 测试基本中文输出、各种字符、标准输出/错误
  - 在 Linux 环境验证通过
  - 等待在 Windows/macOS 环境进一步验证

- **文档更新**
  - 新增 `docs/WINDOWS_UTF8_ENCODING_FIX.md` - 系统性修复完整报告
  - 更新 `docs/WINDOWS_ENCODING_FIX.md` - generate_icons.py 修复报告 (v0.9.1)

#### Windows 图标处理问题 🖼️ (v0.9.1)

- **问题修复**
  - 修复 PyInstaller 在 Windows 平台无法处理图标文件的问题
  - 原因：图标文件是文本占位符，而非有效的图像文件
  - 错误信息：`Something went wrong converting icon image ... image format is unsupported`

- **图标文件生成**
  - 创建 `generate_icons.py` 脚本自动生成有效的图标文件
  - 生成 Windows ICO（多尺寸：16-256px）
  - 生成 macOS ICNS（iconset，16-1024px）
  - 生成 PNG（512x512）
  - 图标设计：蓝色背景 + "SR" 字母

- **图标验证工具**
  - 创建 `test_icon_compat.py` 脚本验证图标兼容性
  - 测试 Pillow 兼容性
  - 测试 PyInstaller 兼容性
  - 验证 ICO 文件格式和头部

- **构建流程优化**
  - 更新 `scripts/build.py` 自动生成图标
  - 更新 GitHub Actions 工作流添加图标生成步骤
  - 更新文档说明图标生成流程

- **文档更新**
  - 新增 `WINDOWS_ICON_FIX.md` - 问题修复报告
  - 新增 `.github/ICON_BUILD_PROCESS.md` - 图标构建流程说明
  - 更新 `README.md` - 添加图标生成说明
  - 更新 `assets/README.md` - 更新当前图标说明

### 新增功能

#### 网盘存储集成 ☁️ (v0.9.0)

- **存储适配器框架**
  - 统一的 `StorageAdapter` 抽象基类
  - `StorageFile` 数据类：统一表示本地和网盘文件
  - `StorageManager`：管理多个存储适配器实例
  - 支持本地文件系统、115 网盘、123 网盘

- **本地存储适配器**
  - 提供本地文件系统的统一访问接口
  - 支持文件列表、读写、删除、重命名等操作
  - 流式扫描大目录支持

- **115 网盘适配器**
  - 基于 Cookie 认证
  - 支持文件列表、下载、上传、重命名、删除
  - 文件信息缓存机制（5 分钟）
  - 支持文件哈希和缩略图
  - 大文件和秒传支持

- **123 网盘适配器**
  - OAuth 2.0 Token 认证
  - 自动刷新过期 token
  - 支持分片上传大文件
  - 完整的文件管理功能

- **配置管理集成**
  - 新增 `storage_type` 配置项
  - 新增 `storage_configs` 配置项
  - 支持多网盘账号配置
  - 安全存储认证信息

- **API 增强**
  - 中文主接口 + 英文兼容接口
  - 流式文件列表支持（`列出文件迭代`）
  - 文件过滤器支持
  - 递归扫描支持
  - 存储空间信息查询

- **测试和文档**
  - 34 个单元测试（100% 通过）
  - `CLOUD_STORAGE_GUIDE.md` - 完整使用指南
  - `examples/storage_example.py` - 使用示例
  - 覆盖所有核心功能

**功能特点：**
- ✅ 统一的存储抽象层
- ✅ 多网盘无缝切换
- ✅ 智能缓存机制
- ✅ 流式处理大目录
- ✅ 完全中文化

**文件变更：**
- `src/smartrenamer/storage/` - 新增存储模块
  - `base.py` - 基类和数据类
  - `local.py` - 本地适配器
  - `storage_115.py` - 115 网盘适配器
  - `storage_123.py` - 123 网盘适配器
  - `manager.py` - 存储管理器
- `src/smartrenamer/core/config.py` - 新增存储配置
- `tests/test_storage_adapters.py` - 存储测试
- `examples/storage_example.py` - 使用示例
- `CLOUD_STORAGE_GUIDE.md` - 使用指南

### 修复

#### PyInstaller macOS 框架符号链接问题 🔧 (v0.9.1)

- **问题描述**
  - PyInstaller 6.x 在 macOS 上打包 PySide6 应用时遇到符号链接冲突
  - 错误：`FileExistsError: [Errno 17] File exists: 'Versions/Current/Resources'`
  - 发生在处理 Qt3DAnimation.framework 等 Qt 框架时

- **修复方案**
  - 在 `smartrenamer.spec` 中条件化 PySide6 数据文件收集
  - macOS 平台跳过 `collect_data_files('PySide6')`
  - 依赖 PyInstaller 自动处理 Qt 框架
  - 避免框架符号链接的重复创建

- **技术细节**
  - 修改 Analysis 阶段的数据收集逻辑
  - 仅在 Windows 和 Linux 上收集 PySide6 数据文件
  - macOS 上让 PyInstaller 自动检测和打包框架
  - 优化 BUNDLE 配置，添加 Qt 环境变量

- **测试验证**
  - 创建 `test_macos_build.sh` 自动化测试脚本
  - 验证 spec 文件配置正确性
  - 检查构建产物和框架结构
  - 测试应用启动和基本功能

- **文档更新**
  - 新增 `docs/MACOS_PYINSTALLER_FIX.md` - 详细修复报告
  - 更新 `PACKAGING_GUIDE.md` - 添加故障排除条目
  - 更新内存 (Memory) - PyInstaller 最佳实践

**影响范围：**
- `smartrenamer.spec` - PyInstaller 配置文件
- `test_macos_build.sh` - macOS 构建测试脚本
- `docs/MACOS_PYINSTALLER_FIX.md` - 新增文档
- `PACKAGING_GUIDE.md` - 故障排除更新

**兼容性：**
- ✅ Windows: 不受影响（继续使用原有逻辑）
- ✅ macOS: 修复符号链接问题
- ✅ Linux: 不受影响（继续使用原有逻辑）

### 维护更新

#### GitHub Actions 升级 🔧

- **Artifact Actions 升级**
  - 升级 `actions/upload-artifact` 从 v3 到 v4（3 处）
  - 升级 `actions/download-artifact` 从 v3 到 v4（1 处）
  - 改进的 artifact 存储和传输性能
  - 消除 v3 弃用警告

- **Python Setup 升级**
  - 升级 `actions/setup-python` 从 v4 到 v5（3 处）
  - 改进的 Python 缓存机制
  - 更快的环境设置速度
  - 支持更多 Python 版本

- **安全扫描升级**
  - 升级 `github/codeql-action/upload-sarif` 从 v2 到 v3（1 处）
  - 改进的 SARIF 文件处理
  - 更好的安全分析集成

- **文档**
  - GITHUB_ACTIONS_UPGRADE.md（完整升级报告）
  - UPGRADE_SUMMARY.md（升级总结）

**影响范围：**
- `.github/workflows/build-release.yml` - 跨平台构建工作流
- `.github/workflows/docker-build.yml` - Docker 构建工作流

**兼容性：**
- ✅ 所有更改向后兼容
- ✅ 工作流语法检查通过
- ✅ Artifact 命名策略已适配 v4
- ✅ 无破坏性变更

## [0.6.0] - 2024-11-24

### 新增功能

#### 跨平台打包支持 📦

- **Windows 打包**
  - PyInstaller 配置文件（smartrenamer.spec）
  - 单文件可执行文件支持
  - NSIS 安装程序脚本（installer.nsi）
  - 便携版 ZIP 打包
  - 桌面和开始菜单快捷方式
  - 完整的卸载程序

- **macOS 打包**
  - .app 应用包生成
  - DMG 镜像创建脚本
  - Universal Binary 支持（Intel + Apple Silicon）
  - 签名和公证支持（可选）
  - Applications 文件夹集成

- **Linux 打包**
  - AppImage 便携格式支持
  - 自动依赖打包
  - FUSE 集成
  - Desktop 文件和图标
  - 主流发行版兼容性

- **自动化构建**
  - 统一构建脚本（scripts/build.py）
  - 平台特定脚本（Windows/macOS/Linux）
  - 快速构建脚本（build.sh/build.bat）
  - SHA256 校验和生成
  - 构建日志和错误处理

- **CI/CD 工作流**
  - GitHub Actions 跨平台构建（.github/workflows/build-release.yml）
  - Windows、macOS、Linux 并行构建
  - 自动发布到 GitHub Releases
  - 发布说明自动生成
  - 多架构支持（x86_64, ARM64）

- **完整文档**
  - PACKAGING_GUIDE.md（打包和发布完整指南）
  - SYSTEM_REQUIREMENTS.md（系统要求和兼容性）
  - assets/README.md（图标创建指南）
  - 诊断脚本（scripts/check_compatibility.sh）

- **资源文件**
  - 应用图标占位符（.ico/.icns/.png）
  - 图标创建工具和指南
  - 品牌资源管理

### 改进

- 更新 README.md 添加跨平台安装说明
- 更新 requirements.txt 添加打包依赖说明
- 优化 PyInstaller 配置
- 添加构建脚本自动化
- 改进错误处理和日志记录

### 文档

- 新增 PACKAGING_GUIDE.md（打包指南，300+ 行）
- 新增 SYSTEM_REQUIREMENTS.md（系统要求，600+ 行）
- 新增 assets/README.md（资源文件说明）
- 更新 README.md 安装部分
- 新增诊断脚本文档

### 工具和脚本

- scripts/build.py - 统一构建脚本
- scripts/windows/installer.nsi - Windows NSIS 安装程序
- scripts/macos/create_dmg.sh - macOS DMG 创建脚本
- scripts/linux/create_appimage.sh - Linux AppImage 创建脚本
- scripts/check_compatibility.sh - 兼容性检查脚本
- build.sh / build.bat - 快速构建脚本

---

## [0.5.1] - 2024-11-23

### 新增功能

#### Docker 容器化支持 🐳

- **完整的 Docker 支持**
  - 多阶段构建优化镜像大小
  - 支持 Linux amd64/arm64 多架构
  - GUI 模式（X11 转发）和 CLI 模式
  - 智能入口脚本（docker-entrypoint.sh）
  - 自动配置和环境检测

- **Docker Compose 配置**
  - 简化的启动流程
  - 卷挂载配置（媒体、配置、缓存）
  - 环境变量管理
  - 持久化数据支持
  - docker-compose.override.yml 示例

- **便捷工具**
  - Makefile（简化 Docker 命令）
  - docker-quickstart.sh（自动配置脚本）
  - test-docker.sh（配置验证脚本）
  - .env.example（环境变量模板）

- **完整文档**
  - DOCKER_USAGE.md（553 行详细使用指南）
  - 平台特定说明（Linux/macOS/Windows）
  - 多平台构建教程
  - 常见问题解答

- **CI/CD 集成**
  - GitHub Actions 自动构建工作流
  - 多平台镜像构建
  - 安全扫描（Trivy）
  - 镜像大小检查
  - Docker Hub 发布支持

### 改进

- 更新 README.md 添加 Docker 安装方式
- 更新 .gitignore 添加 Docker 相关规则
- Dockerfile 优化（多阶段构建）
- 支持 X11 GUI 在容器中运行

### 文档

- 新增 DOCKER_USAGE.md（Docker 完整使用指南）
- 添加平台特定配置说明
- 添加故障排除指南

## [0.5.0] - 2024-11-22

### 新增功能

#### PySide6 GUI 界面

- **MainWindow (主窗口)**
  - 完整的应用程序主窗口
  - 菜单栏（文件、编辑、工具、帮助）
  - 工具栏（快速操作按钮）
  - 状态栏（显示状态和文件计数）
  - 选项卡式界面组织
  - 可调整大小的分栏布局
  - 快捷键支持（Ctrl+O, Ctrl+M, Ctrl+R, Ctrl+Z 等）

- **MediaLibraryPanel (媒体库浏览面板)**
  - 目录扫描（多线程）
  - 文件夹树形浏览
  - 媒体文件列表显示（7列：文件名、类型、标题、年份、大小、状态、路径）
  - 实时搜索和过滤（标题、路径、类型）
  - 多选支持
  - 文件大小自动格式化（B/KB/MB/GB/TB）

- **MatchPanel (匹配识别面板)**
  - 批量 TMDB 匹配（多线程）
  - 匹配结果列表显示
  - 详细信息展示（海报、标题、年份、简介、匹配度）
  - 手动选择匹配项
  - 自动确认高置信度匹配
  - 进度对话框

- **RuleEditorPanel (规则配置和预览面板)**
  - 规则列表（预定义 + 自定义）
  - Jinja2 模板编辑器
  - 实时预览（编辑时自动更新）
  - 新建、保存、删除规则
  - 示例输出显示
  - 预览前10个文件的重命名结果

- **HistoryPanel (历史记录面板)**
  - 显示所有重命名历史（最近100条）
  - 撤销重命名操作
  - 清空历史记录
  - 按时间倒序排序
  - 状态标识（已应用/已撤销）

- **LogPanel (日志面板)**
  - 实时显示应用日志
  - 彩色日志级别（DEBUG、INFO、WARNING、ERROR）
  - 清空日志功能
  - 自定义日志处理器集成 Python logging

- **SettingsDialog (设置对话框)**
  - API 配置（TMDB API Key、语言）
  - 路径配置（默认扫描路径、缓存目录）
  - 重命名选项（备份、预览、自动确认、相似度阈值）
  - 清空缓存功能
  - 选项卡式组织

- **RenameDialog (批量重命名对话框)**
  - 显示重命名进度
  - 实时日志输出
  - 取消支持
  - 操作摘要（成功/失败/跳过统计）
  - 模态对话框

#### 自定义 UI 控件

- **LogWidget**: 日志显示控件
- **MediaFileTableWidget**: 媒体文件表格控件
- **ImageLabel**: 图片显示标签（用于海报）
- **PathSelector**: 路径选择控件
- **ProgressWidget**: 进度显示控件

#### 批量处理工作流

- **完整工作流**: 扫描 → 匹配 → 规则配置 → 预览 → 重命名 → 历史记录
- **多线程处理**: 
  - ScanWorker: 异步文件扫描
  - MatchWorker: 异步 TMDB 匹配
  - RenameWorker: 异步批量重命名
- **信号槽机制**: 组件间松耦合通信
- **实时反馈**: 进度条、日志、状态栏更新

#### 用户体验优化

- **完全中文化**: 所有界面元素、菜单、按钮、对话框
- **快捷键支持**: 
  - Ctrl+O: 打开目录
  - Ctrl+M: 匹配选中文件
  - Ctrl+R: 批量重命名
  - Ctrl+Z: 撤销
  - Ctrl+,: 设置
  - Ctrl+Q: 退出
- **友好错误提示**: 详细的错误对话框和日志
- **确认对话框**: 关键操作需要用户确认
- **撤销机制**: 支持操作回滚

### 测试

- 新增 26 个 UI 测试用例
- 测试类别：
  - 控件测试（5个类）
  - 面板测试（5个类）
  - 主窗口测试（1个类）
  - 集成测试（1个类）
- 总测试用例数: 151 个（全部通过 ✅）
- 测试文件: `tests/test_ui.py` (441 行)

### 文档

- 新增 `UI_GUIDE.md` 完整用户使用指南
  - 启动应用
  - 主界面布局
  - 各个面板详细说明
  - 设置对话框
  - 批量重命名工作流
  - 快捷键列表
  - 常见问题
- 新增 `UI_IMPLEMENTATION_REPORT.md` UI 实现报告
  - 架构设计
  - 功能实现详情
  - 代码统计
  - 技术特性
  - 性能考虑
- 更新 `main.py` 启动 GUI 界面

### 代码统计

- UI 模块: 9 个文件，2,251 行代码
- 测试代码: 441 行
- 文档: 2 个新文档

### 改进

- 应用程序启动流程优化
- 日志系统集成
- 配置管理界面化
- 所有功能可视化操作
- 无需命令行即可使用

### 技术亮点

- PySide6/Qt 6 现代 GUI 框架
- 多线程异步处理保持 UI 响应
- 信号槽机制实现松耦合
- 自定义控件封装
- 实时预览和反馈
- 完整的错误处理
- 国际化准备（预留接口）

### 性能优化

- 异步文件扫描
- 异步 TMDB 匹配
- 异步批量重命名
- 缓存机制（TMDB API）
- 惰性加载和限制显示
- 进度条实时更新

---

## [0.4.0] - 2024-11-22

### 新增功能

#### Jinja2 高级重命名规则引擎

- **Renamer (重命名器)**
  - 基于 Jinja2 模板引擎的灵活重命名系统
  - 支持预览模式（不实际执行重命名）
  - 支持批量重命名
  - 撤销机制（记录重命名历史）
  - 自动处理文件名冲突（添加数字后缀）
  - 支持带目录的重命名（自动创建目录）
  - 重命名历史持久化
  - 完整的错误处理和详细错误信息

- **RenameRuleManager (重命名规则管理器)**
  - 管理和验证重命名规则
  - 模板语法验证
  - 规则的添加、删除、查询
  - 规则持久化到 JSON 文件
  - 从文件加载规则

- **RenameHistory (重命名历史记录)**
  - 记录每次重命名操作
  - 包含原始路径、新路径、时间戳
  - 记录成功/失败状态和错误信息
  - 支持序列化和反序列化

#### 自定义 Jinja2 过滤器

- **填充 (pad)**：填充数字到指定宽度
- **清理文件名 (clean)**：清理非法文件名字符
- **截断 (truncate)**：截断字符串到指定长度
- **大写首字母 (capitalize)**：每个单词首字母大写
- **全大写 (upper)**：转换为全大写
- **全小写 (lower)**：转换为全小写
- **默认值 (default)**：提供默认值
- 所有过滤器均提供中英双语接口

#### 预定义重命名模板

**电影模板（3个）**
- **电影-简洁**：`标题 (年份)`
- **电影-标准**：`标题.年份.分辨率`
- **电影-完整**：`标题.年份.分辨率.来源.编码`

**电视剧模板（4个）**
- **电视剧-标准**：`标题 S01E01`
- **电视剧-带剧集名**：`标题 S01E01 剧集名`
- **电视剧-完整**：`标题 S01E01 剧集名 分辨率`
- **电视剧-分季目录**：`标题/Season 01/标题 S01E01`

#### 工具函数

- **创建预定义规则**：根据模板名称快速创建规则
- **预定义模板字典**：访问所有预定义模板信息

### 测试

- 新增 31 个 Renamer 测试用例
- 测试覆盖所有核心功能：
  - 自定义过滤器（4个测试）
  - 预定义模板（5个测试）
  - 规则管理器（8个测试）
  - 重命名器（13个测试）
  - 高级功能（1个测试）
- 总测试用例数: 125 个（全部通过 ✅）
- 整体覆盖率: 80%
- renamer.py 覆盖率: 80%

### 文档

- 新增 `RENAMER_GUIDE.md` 完整使用指南（60+ KB）
  - 快速开始
  - 预定义模板详解
  - 自定义过滤器使用
  - 高级用法（批量处理、规则管理、撤销等）
  - API 参考
  - 最佳实践和常见问题
- 新增 `RENAMER_IMPLEMENTATION.md` 实现报告
- 新增 `examples/renamer_example.py` 示例代码（7个示例）
- 更新 `README.md` 添加重命名引擎功能

### 改进

- 完整中文化（代码、注释、变量名、函数名）
- 提供双语接口（中文和英文）
- 完善的错误处理和验证
- 高质量的测试覆盖
- 详细的使用文档和示例

### 技术亮点

- Jinja2 模板系统集成
- 自定义过滤器扩展
- 命令模式实现撤销功能
- 文件冲突智能处理
- 历史记录持久化
- 批量处理优化

---

## [0.3.0] - 2024-11-22

### 新增功能

#### 文件名智能解析模块

- **FileNameParser (文件名解析器)**
  - 智能识别常见命名格式
  - 支持电影格式: `Movie.Title.Year.Resolution.Source.Codec`
  - 支持电视剧格式: `Show.Title.S01E01`, `Show.Title.1x01`, `第1季第1集`
  - 支持多种分隔符: `.`, `_`, `-`, 空格
  - 自动提取标题、年份、分辨率、来源、编码
  - 自动提取季数和集数（电视剧）
  - 智能清理标签和发布组信息
  - 支持中文和英文接口
  - 可扩展的自定义解析规则

#### 增强 TMDB 客户端

- **EnhancedTMDBClient (增强TMDB客户端)**
  - 基于原 TMDBClient 的增强版本
  - 智能缓存系统（7天过期）
  - API 请求重试机制（默认3次，指数退避）
  - 年份过滤支持
  - 电影搜索和详情获取
  - 电视剧搜索和详情获取
  - 剧集详情获取（支持指定季和集）
  - 缓存管理（手动清空、自动过期）
  - 完整的错误处理和日志记录

#### 智能匹配引擎

- **Matcher (智能匹配器)**
  - 将本地文件与 TMDB 数据智能匹配
  - 多条件匹配算法（标题 + 年份）
  - 字符串相似度计算（SequenceMatcher）
  - 电影匹配：标题 70% + 年份 30%
  - 电视剧匹配：标题 75% + 年份 25%
  - 可配置的相似度阈值（最小 60%，高 85%）
  - 自动确认高相似度匹配
  - 支持多个匹配结果返回
  - 匹配结果应用到 MediaFile
  - 详细的匹配原因说明

#### 缓存管理系统

- **缓存管理器**
  - JSON 文件缓存
  - 自动过期检测
  - MD5 哈希避免文件名冲突
  - 缓存目录: `~/.smartrenamer/cache/tmdb/`
  - 支持手动清空缓存

### 测试

- 新增 16 个 FileNameParser 测试用例
- 新增 14 个 EnhancedTMDBClient 测试用例
- 新增 20 个 Matcher 测试用例
- 总测试用例数: 95 个（全部通过 ✅）
- 整体覆盖率: 80%
- parser.py 覆盖率: 94%
- matcher.py 覆盖率: 87%
- tmdb_client_enhanced.py 覆盖率: 77%

### 文档

- 新增 `PARSER_MATCHER_GUIDE.md` 完整使用指南
- 新增 `examples/parser_and_matcher_example.py` 示例代码
- 更新 `README.md` 添加新功能说明

### 改进

- 完整中文化（代码、注释、变量名、函数名）
- 提供双语接口（中文和英文）
- 完善的错误处理和日志记录
- 高质量的测试覆盖

### 技术亮点

- 使用正则表达式进行复杂模式匹配
- difflib.SequenceMatcher 实现智能相似度计算
- 指数退避重试策略
- JSON 文件缓存机制
- 综合评分算法

---

## [0.2.0] - 2024-11-22

### 新增功能

#### 媒体库扫描模块

- **FileScanner (文件扫描器)**
  - 递归扫描指定目录
  - 支持 12 种常见视频格式 (.mkv, .mp4, .avi, .mov, .wmv, .flv, .m4v, .ts, .mpg, .mpeg, .m2ts, .webm)
  - 智能过滤和排除不相关文件
  - 自动排除 Sample、Subs、Extras 等目录
  - 可配置文件大小过滤（默认 10 MB）
  - 可限制最大扫描深度
  - 支持进度回调
  - 提供扫描统计信息

- **MediaLibrary (媒体库管理器)**
  - 多扫描源管理
  - 内存缓存和 JSON 文件缓存
  - 增量更新机制（检测新增和删除的文件）
  - 快速搜索功能（按标题、类型）
  - 自动索引构建
  - 统计信息收集
  - 缓存刷新和清除功能

- **智能信息提取**
  - 从文件名自动提取标题
  - 识别年份 (1900-2099)
  - 识别分辨率 (4K, 2160p, 1080p, 720p, 480p)
  - 识别来源 (BluRay, WEB-DL, HDTV, DVDRip)
  - 识别编码 (H.265, H.264, x264, x265)
  - 识别季集信息 (S01E01)
  - 自动区分电影和电视剧

- **配置系统集成**
  - Config 类新增 `scan_sources` 配置项
  - Config 类新增 `exclude_dirs` 配置项
  - Config 类新增 `max_scan_depth` 配置项

### 测试

- 新增 11 个 FileScanner 测试用例
- 新增 14 个 MediaLibrary 测试用例
- 总测试用例数: 45 个（全部通过）
- 代码覆盖率: 75%
- scanner.py 覆盖率: 89%
- library.py 覆盖率: 83%

### 文档

- 新增 `MEDIA_LIBRARY_GUIDE.md` 完整使用指南
- 新增 `examples/scan_library_example.py` 示例代码
- 更新 `README.md` 添加媒体库扫描功能说明
- 更新 `PROJECT_STATUS.md` 记录新版本信息

### 改进

- 完善了 file_utils.py 的信息提取功能
- 优化了文件名标题提取算法
- 改进了错误处理和日志记录

---

## [0.1.0] - 2024-11-22

### 项目初始化

#### 核心功能

- **数据模型**
  - MediaFile: 媒体文件数据类
  - MediaType: 媒体类型枚举 (MOVIE, TV_SHOW, UNKNOWN)
  - RenameRule: 重命名规则类（基于 Jinja2 模板）
  - 预定义的默认规则: DEFAULT_MOVIE_RULE, DEFAULT_TV_RULE

- **配置管理**
  - Config: 应用配置类
  - 支持 TMDB API 配置
  - 支持重命名选项配置
  - 支持文件过滤配置
  - 配置持久化到 ~/.smartrenamer/config.json
  - 配置验证功能

- **API 集成**
  - TMDBClient: TMDB API 客户端封装
  - 支持电影搜索
  - 支持电视剧搜索
  - 支持详细信息获取
  - 中文语言支持

- **工具函数**
  - 文件格式检查
  - 文件名清理
  - 文件大小格式化
  - 信息提取（年份、分辨率、来源、编码、季集）

#### 项目结构

- 完整的 src 布局项目结构
- 模块化设计（core, api, ui, utils）
- 符合 PEP 8 代码规范
- 完整的中文注释和文档

#### 测试

- 20 个单元测试用例（全部通过）
- 测试覆盖率: 63%
- pytest 测试框架
- pytest-cov 覆盖率报告

#### 文档

- README.md: 完整的项目说明（中文）
- ARCHITECTURE.md: 架构设计文档（中文）
- LICENSE: MIT 许可证
- .gitignore: 完善的忽略规则

#### 开发工具

- requirements.txt: 依赖管理
- pyproject.toml: 现代 Python 项目配置
- setup.py: 安装脚本
- 命令行入口: smartrenamer

---

## 语义化版本说明

- **主版本号**: 不兼容的 API 更改
- **次版本号**: 向后兼容的功能新增
- **修订号**: 向后兼容的问题修正

---

## 贡献指南

查看更新日志时请注意：
- [新增] 表示新功能
- [改进] 表示功能改进
- [修复] 表示问题修复
- [弃用] 表示即将移除的功能
- [移除] 表示已移除的功能
- [安全] 表示安全相关的修复

---

**注**: 所有日期均使用 ISO 8601 格式 (YYYY-MM-DD)
