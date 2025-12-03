# SmartRenamer 系统要求

> **重要提示**: SmartRenamer 现在专注于 macOS 平台。本文档仅说明 macOS 系统要求。

本文档详细说明 SmartRenamer 在 macOS 上的系统要求和兼容性信息。

## 📋 目录

- [通用要求](#通用要求)
- [macOS 要求](#macos-要求)
- [网络要求](#网络要求)
- [硬件要求](#硬件要求)
- [兼容性测试](#兼容性测试)

---

## 通用要求

### 必需
- **网络连接**: 访问 TMDB API
- **TMDB API Key**: 免费注册获取
- **显示器**: 最低 1280x800 分辨率（推荐 1920x1080 或 Retina）

### 可选
- **互联网连接**: 用于软件更新和下载元数据
- **存储空间**: 至少 500MB 可用空间（用于缓存和临时文件）

---

## macOS 要求

### 最低要求

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 10.13 (High Sierra) |
| 处理器 | Intel Core i3 或 Apple M1 |
| 内存 | 4 GB RAM |
| 存储空间 | 500 MB 可用空间 |
| 显示器 | 1280x800 分辨率 |

### 推荐配置

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 11 (Big Sur) 或更高 |
| 处理器 | Intel Core i5 或 Apple M1/M2 |
| 内存 | 8 GB RAM 或更多 |
| 存储空间 | 2 GB 可用空间 |
| 显示器 | Retina 显示器（推荐）|

### 依赖项

**应用包版本**（推荐）:
- 无需额外依赖
- 支持 Intel 和 Apple Silicon（Universal Binary）
- 所有依赖已打包在 .app 中

**Python 版本**（开发者）:
- Python 3.8 或更高版本
- pip 包管理器
- Xcode Command Line Tools（可选，用于源码编译）

### 测试的 macOS 版本

✅ macOS 14 (Sonoma)  
✅ macOS 13 (Ventura)  
✅ macOS 12 (Monterey)  
✅ macOS 11 (Big Sur)  
✅ macOS 10.15 (Catalina)  
⚠️ macOS 10.13-10.14 (High Sierra - Mojave) - 部分功能可能受限  
❌ macOS 10.12 及更早版本（不支持）

### 处理器架构

✅ **Apple Silicon** (M1, M1 Pro, M1 Max, M2, M2 Pro, M2 Max, M3)  
✅ **Intel** (x86_64)  
✅ **Universal Binary** (同时支持两种架构)

### 系统功能要求

- **图形界面**: 需要完整的 macOS 桌面环境
- **网络权限**: 应用需要访问 TMDB API
- **文件系统访问**: 需要读写媒体文件的权限
- **Gatekeeper**: 首次运行可能需要在"系统偏好设置"中允许

### 已知问题

#### 1. 首次运行安全提示

**问题**: macOS 可能阻止未签名应用

**解决方案**: 
```bash
# 方法 1: 右键点击应用 > "打开"

# 方法 2: 在系统偏好设置中允许
# "系统偏好设置 > 安全性与隐私" > 点击"仍要打开"

# 方法 3: 移除隔离属性（仅当您信任该应用）
sudo xattr -r -d com.apple.quarantine /Applications/SmartRenamer.app
```

#### 2. 网络权限

**问题**: 首次运行时需要授予网络访问权限

**解决方案**: 在弹出提示时点击"允许"

#### 3. Rosetta 2（仅 Intel 版本在 Apple Silicon 上）

**问题**: Intel 版本在 Apple Silicon Mac 上运行需要 Rosetta 2

**解决方案**: 
```bash
# 系统会自动提示安装，或手动安装：
softwareupdate --install-rosetta

# 使用 Universal Binary 版本可避免此问题
```

#### 4. 文件访问权限

**问题**: 某些系统文件夹可能需要额外权限

**解决方案**: 
- 在"系统偏好设置 > 安全性与隐私 > 文件和文件夹"中授予权限
- 或使用"完全磁盘访问权限"（不推荐）

---

## 网络要求

### 必需的网络连接

- **TMDB API**: 
  - 域名: `api.themoviedb.org`
  - 端口: 443 (HTTPS)
  - 协议: HTTPS
  - 用途: 获取电影和电视剧元数据

### 可选的网络连接

- **GitHub**: 软件更新检查
  - 域名: `api.github.com`
  - 端口: 443 (HTTPS)

### 防火墙配置

如果使用防火墙，需要允许以下出站连接：
- HTTPS (端口 443) 到 `api.themoviedb.org`
- HTTPS (端口 443) 到 `api.github.com` (可选)

### 代理支持

SmartRenamer 支持 HTTP/HTTPS 代理：

**环境变量**:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

**配置文件** (`~/.smartrenamer/config.json`):
```json
{
  "proxy": {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
  }
}
```

### TMDB API 要求

- **API Key**: 必需，从 [TMDB 官网](https://www.themoviedb.org/) 免费获取
- **API 限制**: TMDB 有速率限制，建议不要过于频繁调用
- **语言支持**: 支持多种语言，默认为简体中文 (zh-CN)

---

## 硬件要求

### CPU

**最低**:
- Intel Core i3 (第 6 代) 或同等
- Apple M1 或更高

**推荐**:
- Intel Core i5 (第 8 代) 或更高
- Apple M1 Pro/Max 或 M2 系列

**性能说明**:
- Apple Silicon 性能优于同代 Intel 处理器
- 多核处理器可提升批量处理速度

### 内存 (RAM)

| 使用场景 | 最低 | 推荐 |
|---------|------|------|
| 基本使用 | 4 GB | 8 GB |
| 大型媒体库 (1000+ 文件) | 8 GB | 16 GB |
| 批量处理 | 8 GB | 16 GB+ |

**内存使用说明**:
- 应用基础内存占用: 约 100-200 MB
- 媒体库缓存: 根据文件数量动态增长
- 图片预览: 每张海报约 1-2 MB

### 存储空间

| 组件 | 空间要求 |
|------|---------|
| 应用程序 | 100-300 MB |
| 缓存数据 | 50-500 MB |
| 临时文件 | 100-1000 MB |
| **总计** | **500 MB - 2 GB** |

**存储建议**:
- 建议使用 SSD 以获得最佳性能
- 缓存会随时间增长，定期清理可节省空间
- 如果处理大型媒体库，建议预留更多空间

### 显示器

**最低分辨率**: 1280x800  
**推荐分辨率**: 1920x1080 或更高  
**Retina 显示器**: 完全支持  
**色深**: 24位真彩色

**界面优化**:
- 支持 Retina 显示器的高分辨率图标
- 自适应不同屏幕尺寸
- 支持 Dark Mode（暗色模式）

---

## 兼容性测试

### 测试矩阵

SmartRenamer 已在以下环境中测试：

| macOS 版本 | 架构 | 状态 |
|-----------|------|------|
| macOS 14 Sonoma | ARM64 (M1/M2/M3) | ✅ 完全支持 |
| macOS 13 Ventura | ARM64 (M1/M2) | ✅ 完全支持 |
| macOS 13 Ventura | x64 (Intel) | ✅ 完全支持 |
| macOS 12 Monterey | ARM64 (M1) | ✅ 完全支持 |
| macOS 12 Monterey | x64 (Intel) | ✅ 完全支持 |
| macOS 11 Big Sur | ARM64 (M1) | ✅ 完全支持 |
| macOS 11 Big Sur | x64 (Intel) | ✅ 完全支持 |
| macOS 10.15 Catalina | x64 (Intel) | ✅ 完全支持 |
| macOS 10.14 Mojave | x64 (Intel) | ⚠️ 部分功能受限 |
| macOS 10.13 High Sierra | x64 (Intel) | ⚠️ 部分功能受限 |

### 功能兼容性

| 功能 | macOS 10.13+ | macOS 11+ |
|------|--------------|-----------|
| 基本重命名 | ✅ | ✅ |
| TMDB 匹配 | ✅ | ✅ |
| GUI 界面 | ✅ | ✅ |
| 媒体库扫描 | ✅ | ✅ |
| Dark Mode | ⚠️ 部分支持 | ✅ |
| Universal Binary | ❌ | ✅ |
| 完整 Retina 支持 | ⚠️ | ✅ |

---

## 故障排除

### 常见问题

#### 1. 应用无法启动

**Windows 用户**: SmartRenamer 不再支持 Windows 平台。

**macOS 解决方案**:
- 检查"系统偏好设置 > 安全性与隐私"
- 移除隔离属性：`xattr -cr /Applications/SmartRenamer.app`
- 确保系统版本满足最低要求（macOS 10.13+）

#### 2. 网络连接失败

**检查**:
```bash
# 测试 TMDB API 连接
curl -I https://api.themoviedb.org

# 检查防火墙设置
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getappblocked /Applications/SmartRenamer.app
```

**解决方案**:
- 确保网络连接正常
- 检查防火墙是否阻止应用
- 验证 TMDB API Key 有效

#### 3. 性能问题

**症状**: 应用运行缓慢或卡顿

**解决方案**:
```bash
# 清理缓存
rm -rf ~/.smartrenamer/cache/*

# 检查系统资源
top -o cpu
top -o mem

# 确保有足够的可用内存和磁盘空间
```

#### 4. 在 Apple Silicon Mac 上运行 Intel 版本

**问题**: 性能不佳或兼容性问题

**解决方案**:
- 下载 Universal Binary 版本
- 或确保已安装 Rosetta 2

---

## 最佳实践

### 1. 系统准备

- 使用最新稳定版的 macOS
- 保持系统更新
- 确保有足够的可用磁盘空间
- 定期清理缓存

### 2. 性能优化

- 使用 SSD 存储媒体文件
- 在处理大型媒体库时关闭不必要的应用
- 定期清理 SmartRenamer 缓存
- 使用 Universal Binary 版本以获得最佳性能

### 3. 安全建议

- 从官方 GitHub Releases 下载应用
- 验证下载文件的 SHA256 校验和
- 首次运行时仔细检查权限请求
- 定期备份重命名历史和配置

### 4. 数据管理

- 定期备份媒体文件
- 使用重命名预览功能
- 保留重命名历史记录
- 定期导出配置文件

---

## 相关文档

- [README.md](README.md) - 项目说明
- [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md) - macOS 打包指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
- [docs/MACOS_PYINSTALLER_FIX.md](docs/MACOS_PYINSTALLER_FIX.md) - PyInstaller 修复报告

---

## 获取帮助

如果遇到问题：

1. **查看文档**: 检查本文档和 README.md
2. **搜索 Issues**: 在 GitHub Issues 中搜索类似问题
3. **创建 Issue**: 如果找不到解决方案，创建新的 Issue
4. **提供信息**: 包括 macOS 版本、架构、错误信息等

---

**最后更新**: 2024-12-03  
**适用版本**: v0.9.0+  
**平台**: macOS only
