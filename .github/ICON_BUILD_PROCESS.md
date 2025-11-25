# 图标构建流程说明

本文档说明 SmartRenamer 在 GitHub Actions 中如何处理应用图标的生成和打包。

## 问题背景

PyInstaller 在 Windows 平台打包时需要有效的图标文件（.ico 格式），如果图标文件无效或缺失，会导致构建失败：

```
Something went wrong converting icon image ... image format is unsupported
```

## 解决方案

### 1. 本地图标文件

在项目的 `assets/` 目录中已经提供了预生成的有效图标文件：
- `icon.ico` - Windows 图标（多尺寸，27KB+）
- `icon.icns` - macOS 图标（12KB+）
- `icon.png` - PNG 图标（512x512，11KB+）

这些文件会被提交到 Git 仓库，因此 GitHub Actions 可以直接使用。

### 2. 动态生成（可选）

如果需要在 CI 中动态生成图标（例如测试图标生成脚本），GitHub Actions 工作流中包含了图标生成步骤：

```yaml
- name: 生成应用图标
  run: |
    python generate_icons.py

- name: 验证图标文件
  run: |
    python test_icon_compat.py
```

**注意**：
- Windows runner 已经安装了 Python 和 Pillow（通过 requirements.txt）
- 图标生成步骤在构建可执行文件之前执行
- 如果图标文件已存在且有效，生成脚本会跳过生成（性能优化）

## 工作流步骤

### Windows 构建

```yaml
build-windows:
  steps:
    - checkout 代码
    - 设置 Python 3.10
    - 安装依赖（包括 Pillow）
    - 生成应用图标（可选）
    - 验证图标文件（可选）
    - 构建可执行文件（PyInstaller）
    - 测试可执行文件
    - 创建便携版压缩包
    - 创建 NSIS 安装程序
    - 生成校验和
    - 上传构建产物
```

### macOS 构建

```yaml
build-macos:
  steps:
    - checkout 代码
    - 设置 Python 3.10
    - 安装依赖（包括 Pillow）
    - 生成应用图标（可选）
    - 构建应用包（PyInstaller）
    - 测试应用
    - 创建 DMG
    - 生成校验和
    - 上传构建产物
```

### Linux 构建

```yaml
build-linux:
  steps:
    - checkout 代码
    - 设置 Python 3.10
    - 安装系统依赖
    - 安装 Python 依赖（包括 Pillow）
    - 生成应用图标（可选）
    - 构建可执行文件（PyInstaller）
    - 测试可执行文件
    - 下载 appimagetool
    - 创建 AppImage
    - 测试 AppImage
    - 生成校验和
    - 上传构建产物
```

## 图标生成脚本

### generate_icons.py

自动生成所有平台的图标文件：

- **输入**：无（硬编码的图标设计）
- **输出**：
  - `assets/icon.png` (512x512)
  - `assets/icon.ico` (多尺寸: 16, 32, 48, 64, 128, 256)
  - `assets/icon.icns` (PNG 占位符或完整 iconset)
  - `assets/icon.iconset/` (macOS iconset 目录，10 个文件)
- **依赖**：Pillow（PIL）
- **运行时间**：< 1 秒

### test_icon_compat.py

验证图标文件与 PyInstaller 的兼容性：

- **测试项目**：
  1. Pillow 能否打开 ICO 文件
  2. ICO 文件是否包含多个尺寸
  3. ICO 文件头部格式是否正确
  4. PNG 和 ICNS 文件是否有效
- **退出码**：0（成功）或 1（失败）
- **运行时间**：< 1 秒

## 图标文件规范

### Windows ICO

- **格式**：Windows Icon (.ico)
- **尺寸**：多尺寸（16x16, 32x32, 48x48, 64x64, 128x128, 256x256）
- **颜色模式**：RGBA（支持透明背景）
- **文件大小**：约 27KB
- **PyInstaller 要求**：
  - 必须是有效的 ICO 格式
  - 文件头部必须符合 ICO 规范
  - Pillow 必须能够成功打开和加载

### macOS ICNS

- **格式**：Apple Icon Image (.icns) 或 PNG
- **尺寸**：多尺寸（16x16 到 1024x1024，含 @2x 版本）
- **颜色模式**：RGBA
- **文件大小**：约 12KB（PNG 占位符）
- **PyInstaller 要求**：
  - 在 macOS 上，PyInstaller 优先使用 iconutil 生成的 .icns
  - 如果 .icns 不可用，可以使用 PNG 格式作为占位符

### Linux PNG

- **格式**：Portable Network Graphics (.png)
- **尺寸**：512x512 或 256x256
- **颜色模式**：RGBA
- **文件大小**：约 11KB
- **PyInstaller 要求**：
  - 标准 PNG 格式
  - AppImage 使用此图标作为桌面图标

## 故障排除

### 问题：图标生成失败

**原因**：Pillow 未安装或版本不兼容

**解决方案**：
```bash
pip install Pillow>=10.1.0
```

### 问题：ICO 文件无效

**症状**：
```
Something went wrong converting icon image
OSError: image format is unsupported
```

**原因**：ICO 文件是文本占位符或损坏

**解决方案**：
1. 运行 `python generate_icons.py` 重新生成
2. 验证文件大小（应该 > 10KB）
3. 运行 `python test_icon_compat.py` 验证

### 问题：macOS 框架符号链接冲突

**症状**：
```
FileExistsError: [Errno 17] File exists: 'Versions/Current/Resources'
```

**原因**：PyInstaller 在处理 Qt 框架时遇到符号链接问题

**解决方案**：
已在 `smartrenamer.spec` 中修复，macOS 平台不收集 PySide6 数据文件。
详见 `docs/MACOS_PYINSTALLER_FIX.md`

### 问题：GitHub Actions 构建失败

**检查清单**：
1. ✅ 图标文件已提交到 Git 仓库
2. ✅ requirements.txt 包含 Pillow
3. ✅ 工作流中安装了所有依赖
4. ✅ 图标生成步骤在构建步骤之前
5. ✅ smartrenamer.spec 中的图标路径正确

**调试步骤**：
1. 查看 "生成应用图标" 步骤的输出
2. 查看 "验证图标文件" 步骤的输出（如果有）
3. 查看 PyInstaller 的详细输出
4. 检查构建产物的图标是否正确

## 最佳实践

1. **提交图标文件到仓库**：避免 CI 每次都生成图标，节省构建时间
2. **验证图标有效性**：在本地生成后运行测试脚本
3. **保持图标文件较小**：优化文件大小，减少仓库体积
4. **多尺寸支持**：确保在不同 DPI 设置下显示清晰
5. **跨平台测试**：在所有目标平台上测试图标显示效果

## 相关文档

- [WINDOWS_ICON_FIX.md](../WINDOWS_ICON_FIX.md) - Windows 图标问题修复报告
- [MACOS_PYINSTALLER_FIX.md](../docs/MACOS_PYINSTALLER_FIX.md) - macOS 符号链接修复
- [PACKAGING_GUIDE.md](../PACKAGING_GUIDE.md) - 完整打包指南
- [assets/README.md](../assets/README.md) - 图标设计建议

## 版本历史

- **v0.9.1**：修复 Windows 图标处理问题
  - 创建有效的 ICO、PNG、ICNS 文件
  - 添加图标生成和验证脚本
  - 更新 GitHub Actions 工作流
  - 更新构建脚本自动生成图标
