# Windows 字符编码问题修复报告

## 问题描述

`generate_icons.py` 脚本在 Windows 平台上运行时出现 Unicode 字符编码错误：

```
UnicodeEncodeError: 'charmap' codec can't encode characters
```

### 问题原因

1. Windows 控制台默认使用 cp1252 或其他区域编码，无法处理 UTF-8 中文字符
2. `generate_icons.py` 包含大量中文注释和打印语句
3. Python 默认使用系统控制台编码，导致中文输出失败

## 修复方案

### 实施的修复

在 `generate_icons.py` 文件头部添加了以下内容：

1. **添加文件编码声明**
```python
# -*- coding: utf-8 -*-
```

2. **配置标准输出使用 UTF-8 编码**
```python
import sys
import os

# 配置标准输出使用 UTF-8 编码，解决 Windows 控制台中文显示问题
if sys.platform == 'win32':
    try:
        # Python 3.7+
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6 及更早版本
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
```

### 修复特点

1. **平台特定**：仅在 Windows 平台 (`sys.platform == 'win32'`) 上执行编码配置
2. **版本兼容**：支持 Python 3.6+ 的不同 API
3. **向后兼容**：不影响 macOS 和 Linux 平台的正常运行
4. **自动化**：无需手动设置环境变量

## 测试验证

### Linux 测试（开发环境）

```bash
$ python3 generate_icons.py
正在生成 SmartRenamer 应用图标...
============================================================
✓ 已创建 PNG 图标: /home/engine/project/assets/icon.png
✓ 已创建 ICO 图标: /home/engine/project/assets/icon.ico
✓ 已创建 iconset 目录: /home/engine/project/assets/icon.iconset
提示: 在 macOS 上可以使用以下命令生成 .icns 文件:
  iconutil -c icns /home/engine/project/assets/icon.iconset
✓ 已创建 ICNS 占位符（PNG 格式）: /home/engine/project/assets/icon.icns
============================================================
✓ 图标生成完成！

验证生成的文件:
  icon.png: 11,669 字节
    → 格式: PNG, 尺寸: (512, 512), 模式: RGBA
  icon.ico: 27,877 字节
    → 格式: ICO, 尺寸: (256, 256), 模式: RGBA
  icon.icns: 12,777 字节
    → 格式: PNG, 尺寸: (512, 512), 模式: RGBA

$ echo $?
0
```

### 生成的文件

```bash
$ ls -lh assets/icon.*
-rw-r--r-- 1 engine engine  13K Nov 25 08:02 assets/icon.icns
-rw-r--r-- 1 engine engine  28K Nov 25 08:02 assets/icon.ico
-rw-r--r-- 1 engine engine  12K Nov 25 08:02 assets/icon.png
```

### Windows 平台测试（GitHub Actions）

修复后的代码将在 GitHub Actions 的 Windows runner 上进行测试：

- 工作流文件：`.github/workflows/build-release.yml`
- 测试步骤：第 39-41 行（Windows 构建）
- 预期结果：exit code 0，图标文件正确生成

## 验收标准

✅ **已完成**：
- [x] 添加 UTF-8 编码声明
- [x] 配置 sys.stdout/stderr 使用 UTF-8
- [x] 平台特定代码（仅在 Windows 上生效）
- [x] Python 版本兼容（3.6+）
- [x] Linux 平台测试通过
- [x] 退出码为 0
- [x] 图标文件正确生成
- [x] 中文字符正确输出

⏳ **待 GitHub Actions 验证**：
- [ ] Windows runner 测试通过
- [ ] macOS runner 测试通过（确认不受影响）

## 替代方案

如果当前修复方案在某些 Windows 环境中仍有问题，可以考虑以下备选方案：

### 方案 A：环境变量（不推荐）
在 GitHub Actions 工作流中添加：
```yaml
- name: 生成应用图标
  run: |
    python generate_icons.py
  env:
    PYTHONIOENCODING: utf-8
```

**缺点**：需要修改 CI/CD 配置，本地开发者也需要手动设置

### 方案 B：移除中文字符（不推荐）
将所有中文注释和打印语句改为英文。

**缺点**：违反项目代码规范，降低可读性

## 技术细节

### Python 3.7+ 方法
`sys.stdout.reconfigure(encoding='utf-8')` 是最简洁的方式，直接重新配置已有的流对象。

### Python 3.6 及更早版本
需要使用 `codecs.getwriter()` 包装标准输出流：
```python
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
```

### 为什么只在 Windows 上执行
- Linux/macOS 默认使用 UTF-8 编码
- 仅 Windows 的控制台编码需要特殊处理
- 避免在其他平台上不必要的流重配置

## 参考资料

- [PEP 540 - Add a new UTF-8 Mode](https://www.python.org/dev/peps/pep-0540/)
- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [sys.stdout.reconfigure() documentation](https://docs.python.org/3/library/sys.html#sys.stdout)

## 修复日期

- **修复时间**：2024-11-25
- **修复版本**：v0.9.1+
- **修复分支**：`fix-windows-encoding-generate-icons`
