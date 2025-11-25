# macOS PyInstaller 框架符号链接问题修复

## 问题描述

在使用 PyInstaller 6.x 打包 PySide6 应用到 macOS 时，会遇到 Qt 框架符号链接冲突的错误：

```
FileExistsError: [Errno 17] File exists: 'Versions/Current/Resources'
```

这个错误通常发生在打包过程中处理 Qt 框架（如 `Qt3DAnimation.framework`）时。

## 问题原因

1. **PyInstaller 6.x 与 PySide6 的兼容性问题**：
   - PyInstaller 在复制 Qt 框架时会处理 macOS 框架的标准目录结构
   - 框架目录包含 `Versions/Current` 符号链接指向当前版本
   - 当尝试重新创建这些符号链接时，如果已存在会导致 `FileExistsError`

2. **过度收集数据文件**：
   - 使用 `collect_data_files('PySide6')` 会收集所有 PySide6 数据文件
   - 包括框架的元数据和符号链接结构
   - 导致 PyInstaller 处理框架时出现冲突

## 解决方案

### 修改 1: 条件化 PySide6 数据文件收集

在 `smartrenamer.spec` 中，仅在非 macOS 平台收集 PySide6 数据文件：

```python
# 收集 PySide6 数据文件
# 注意: 在 macOS 上，不应收集 PySide6 的框架数据文件，
# 因为这会导致符号链接冲突（FileExistsError: Versions/Current/Resources）
# PyInstaller 会自动处理必要的 Qt 框架依赖
if not IS_MACOS:
    try:
        pyside6_datas = collect_data_files('PySide6', include_py_files=False)
        datas.extend(pyside6_datas)
    except Exception as e:
        print(f"警告: 收集 PySide6 数据文件失败: {e}")
else:
    print("macOS 平台: 跳过 PySide6 数据文件收集，避免框架符号链接冲突")
```

**原理**：
- macOS 上，PyInstaller 会自动检测和打包必要的 Qt 框架
- 无需手动收集 PySide6 的数据文件
- 避免了框架符号链接的重复处理

### 修改 2: 优化 BUNDLE 配置

在 macOS 的 `BUNDLE` 配置中添加 Qt 环境变量：

```python
info_plist={
    'CFBundleName': APP_NAME,
    'CFBundleDisplayName': APP_NAME,
    'CFBundleVersion': APP_VERSION,
    'CFBundleShortVersionString': APP_VERSION,
    'NSHighResolutionCapable': 'True',
    'NSPrincipalClass': 'NSApplication',
    'NSAppleScriptEnabled': False,
    # 避免 Qt 框架符号链接问题
    'LSEnvironment': {
        'QT_MAC_WANTS_LAYER': '1',
    },
},
```

**原理**：
- `QT_MAC_WANTS_LAYER=1` 确保 Qt 在 macOS 上使用 Core Animation 层
- 这是 Qt 在 macOS 上的推荐配置
- 有助于避免某些框架加载问题

## 测试验证

使用提供的测试脚本验证修复：

```bash
./test_macos_build.sh
```

测试脚本会：
1. 清理旧的构建产物
2. 验证依赖安装
3. 检查 spec 文件配置
4. 执行 PyInstaller 构建
5. 验证构建产物结构
6. 测试应用启动
7. 检查 Qt 框架符号链接

## GitHub Actions 集成

在 `.github/workflows/build-release.yml` 中，macOS 构建已配置为使用修复后的 spec 文件：

```yaml
- name: 构建应用包
  run: |
    pyinstaller --clean --noconfirm smartrenamer.spec

- name: 测试应用
  run: |
    ./dist/SmartRenamer.app/Contents/MacOS/SmartRenamer --help
```

无需额外配置，修复已集成到 spec 文件中。

## 技术细节

### macOS 框架结构

标准的 macOS 框架目录结构：

```
Framework.framework/
├── Versions/
│   ├── A/
│   │   ├── Framework (可执行文件)
│   │   ├── Resources/
│   │   └── Headers/
│   └── Current -> A (符号链接)
├── Framework -> Versions/Current/Framework (符号链接)
├── Resources -> Versions/Current/Resources (符号链接)
└── Headers -> Versions/Current/Headers (符号链接)
```

### PyInstaller 处理流程

1. **分析阶段**：
   - 检测 PySide6 依赖
   - 发现 Qt 框架

2. **收集阶段**（修复前的问题点）：
   - `collect_data_files('PySide6')` 收集所有数据文件
   - 包括框架的符号链接结构
   - 尝试复制时发现符号链接已存在 → 错误

3. **打包阶段**：
   - 将框架复制到 `.app/Contents/Frameworks/`
   - 创建必要的符号链接
   - 修复前：与收集阶段的符号链接冲突

### 修复后的流程

1. **分析阶段**：
   - 同上

2. **收集阶段**（修复后）：
   - macOS 上跳过 `collect_data_files('PySide6')`
   - 仅依赖 PyInstaller 的自动框架检测

3. **打包阶段**：
   - PyInstaller 自动处理框架
   - 正确创建符号链接结构
   - 无冲突

## 兼容性

- ✅ **Windows**: 不受影响（继续使用 `collect_data_files`）
- ✅ **macOS**: 修复符号链接问题
- ✅ **Linux**: 不受影响（继续使用 `collect_data_files`）

## 已知限制

1. **框架大小**：
   - macOS .app 包可能较大（包含完整的 Qt 框架）
   - 可以使用 DMG 压缩减小分发大小

2. **代码签名**：
   - 如需发布到 Mac App Store，需要额外的代码签名配置
   - 参考 Apple 开发者文档

3. **公证 (Notarization)**：
   - macOS 10.15+ 需要公证才能在 Gatekeeper 下运行
   - 需要 Apple 开发者账号

## 参考资源

- [PyInstaller 官方文档 - macOS](https://pyinstaller.org/en/stable/usage.html#macos)
- [PySide6 打包指南](https://doc.qt.io/qtforpython/deployment.html)
- [PyInstaller GitHub Issues - PySide6 符号链接](https://github.com/pyinstaller/pyinstaller/issues?q=pyside6+symlink)

## 更新日志

- **2024-01-XX**: 初始版本，修复 Qt3DAnimation.framework 符号链接问题
- **版本**: SmartRenamer v0.9.0+

## 贡献者

如遇到相关问题或有改进建议，请在 GitHub Issues 中反馈。
