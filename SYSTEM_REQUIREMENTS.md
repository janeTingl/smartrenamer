# SmartRenamer 系统要求

本文档详细说明 SmartRenamer 在不同平台上的系统要求和兼容性信息。

## 📋 目录

- [通用要求](#通用要求)
- [Windows](#windows)
- [macOS](#macos)
- [Linux](#linux)
- [Docker](#docker)
- [网络要求](#网络要求)
- [硬件要求](#硬件要求)
- [兼容性测试](#兼容性测试)

---

## 通用要求

无论使用哪种安装方式，SmartRenamer 都需要：

### 必需
- **网络连接**: 访问 TMDB API
- **TMDB API Key**: 免费注册获取
- **显示器**: 最低 1024x768 分辨率（推荐 1920x1080）

### 可选
- **互联网连接**: 用于软件更新和下载元数据
- **存储空间**: 至少 500MB 可用空间（用于缓存和临时文件）

---

## Windows

### 最低要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 (64位) |
| 处理器 | Intel Core i3 或同等 AMD 处理器 |
| 内存 | 4 GB RAM |
| 存储空间 | 500 MB 可用空间 |
| 显示器 | 1024x768 分辨率 |

### 推荐配置

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 (64位) |
| 处理器 | Intel Core i5 或更高 |
| 内存 | 8 GB RAM 或更多 |
| 存储空间 | 2 GB 可用空间 |
| 显示器 | 1920x1080 分辨率或更高 |

### 依赖项

**可执行文件版本**（推荐）:
- 无需额外依赖
- Visual C++ Redistributable（自动包含）

**Python 版本**:
- Python 3.8 或更高版本
- pip 包管理器

### 测试的 Windows 版本

✅ Windows 11 (21H2, 22H2)  
✅ Windows 10 (20H2, 21H1, 21H2, 22H2)  
⚠️ Windows 8.1 (部分功能可能受限)  
❌ Windows 7 及更早版本（不支持）

### 已知问题

1. **Windows Defender 误报**: 首次运行时可能被标记为可疑文件
   - 解决方案: 添加到白名单或使用签名版本

2. **高 DPI 显示**: 部分 Windows 10 版本可能出现界面缩放问题
   - 解决方案: 在兼容性设置中禁用高 DPI 缩放

---

## macOS

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

**Python 版本**:
- Python 3.8 或更高版本
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

✅ Apple Silicon (M1, M1 Pro, M1 Max, M2, M2 Pro, M2 Max)  
✅ Intel (x86_64)

### 已知问题

1. **首次运行安全提示**: macOS 可能阻止未签名应用
   - 解决方案: 右键点击应用 > "打开"，或在"系统偏好设置 > 安全性与隐私"中允许

2. **网络权限**: 首次运行时需要授予网络访问权限
   - 解决方案: 在弹出提示时点击"允许"

3. **Rosetta 2**: Intel 版本在 Apple Silicon 上运行需要 Rosetta 2
   - 解决方案: 系统会自动提示安装，或手动安装：
     ```bash
     softwareupdate --install-rosetta
     ```

---

## Linux

### 最低要求

| 项目 | 要求 |
|------|------|
| 操作系统 | 主流发行版（见下文）|
| 内核版本 | Linux Kernel 4.15 或更高 |
| 处理器 | x86_64 (AMD64) |
| 内存 | 4 GB RAM |
| 存储空间 | 500 MB 可用空间 |
| 显示服务器 | X11 或 Wayland |

### 推荐配置

| 项目 | 要求 |
|------|------|
| 操作系统 | Ubuntu 22.04 LTS 或同等发行版 |
| 内核版本 | Linux Kernel 5.15 或更高 |
| 处理器 | x86_64 多核处理器 |
| 内存 | 8 GB RAM 或更多 |
| 存储空间 | 2 GB 可用空间 |
| 显示服务器 | X11（推荐）或 Wayland |

### 依赖项

**AppImage 版本**（推荐）:
- FUSE 2.x（大多数发行版已预装）
- X11 或 Wayland 显示服务器
- 标准 Linux 图形库

**Python 版本**:
- Python 3.8 或更高版本
- 系统包管理器或 pip

### 测试的 Linux 发行版

#### Ubuntu/Debian 系列
✅ Ubuntu 22.04 LTS (Jammy)  
✅ Ubuntu 20.04 LTS (Focal)  
✅ Debian 11 (Bullseye)  
✅ Debian 12 (Bookworm)  
✅ Linux Mint 21

#### Red Hat/Fedora 系列
✅ Fedora 38, 39  
✅ RHEL 8, 9  
✅ CentOS Stream 8, 9  
✅ Rocky Linux 8, 9

#### Arch 系列
✅ Arch Linux (滚动更新)  
✅ Manjaro 23

#### openSUSE
✅ openSUSE Leap 15.5  
✅ openSUSE Tumbleweed

#### 其他
✅ Pop!_OS 22.04  
✅ Zorin OS 16, 17  
⚠️ 其他发行版可能需要额外配置

### 系统包依赖

#### Ubuntu/Debian
```bash
sudo apt-get install -y \
  libxcb-xinerama0 \
  libxcb-icccm4 \
  libxcb-image0 \
  libxcb-keysyms1 \
  libxcb-randr0 \
  libxcb-render-util0 \
  libxcb-shape0 \
  libxcb-xfixes0 \
  libxkbcommon-x11-0 \
  libgl1-mesa-glx \
  libegl1-mesa \
  libfontconfig1 \
  libdbus-1-3
```

#### Fedora/RHEL
```bash
sudo dnf install -y \
  libxcb \
  libXext \
  libXrender \
  libXinerama \
  fontconfig \
  dbus-libs
```

#### Arch Linux
```bash
sudo pacman -S \
  libxcb \
  libxext \
  libxrender \
  fontconfig \
  dbus
```

### 显示服务器

**X11**（推荐）:
- 完全支持
- 最佳兼容性

**Wayland**:
- 支持，但可能需要 XWayland
- 某些功能可能受限

**检查当前显示服务器**:
```bash
echo $XDG_SESSION_TYPE
```

### AppImage 使用

#### 运行 AppImage

```bash
# 1. 下载
wget https://github.com/smartrenamer/smartrenamer/releases/latest/download/SmartRenamer-Linux-x86_64.AppImage

# 2. 添加执行权限
chmod +x SmartRenamer-Linux-x86_64.AppImage

# 3. 运行
./SmartRenamer-Linux-x86_64.AppImage
```

#### 集成到系统

可选：使用 `appimaged` 守护进程自动集成 AppImage 到系统：

```bash
# 安装 appimaged
wget https://github.com/AppImage/appimaged/releases/download/continuous/appimaged-x86_64.AppImage
chmod +x appimaged-x86_64.AppImage
./appimaged-x86_64.AppImage --install
```

### 已知问题

1. **FUSE 权限**: 某些系统需要 FUSE 权限
   - 解决方案: 
     ```bash
     sudo apt-get install fuse libfuse2
     sudo modprobe fuse
     ```

2. **Wayland 问题**: 在某些 Wayland 环境下可能出现渲染问题
   - 解决方案: 使用 XWayland 或切换到 X11

3. **缺少库**: 可能需要安装额外的图形库
   - 解决方案: 使用上述系统包依赖命令

---

## Docker

### 最低要求

| 项目 | 要求 |
|------|------|
| Docker | 20.10 或更高 |
| Docker Compose | 1.29 或更高（可选）|
| 内存 | 2 GB 可用内存 |
| 存储空间 | 2 GB 可用空间 |

### 推荐配置

| 项目 | 要求 |
|------|------|
| Docker | 最新稳定版 |
| Docker Compose | 最新稳定版 |
| 内存 | 4 GB 或更多 |
| 存储空间 | 5 GB 可用空间 |

### 平台支持

#### Linux
✅ 原生 Docker 支持  
✅ X11 转发支持（GUI）  
✅ 最佳性能

#### macOS
✅ Docker Desktop for Mac  
✅ XQuartz + X11 转发（GUI）  
⚠️ 性能略低于原生

#### Windows
✅ Docker Desktop for Windows  
✅ WSL2 后端（推荐）  
⚠️ GUI 支持有限（建议使用 CLI 模式）

### 架构支持

✅ linux/amd64 (x86_64)  
✅ linux/arm64 (Apple Silicon, ARM servers)

### 检查 Docker 版本

```bash
docker --version
docker-compose --version
```

### Docker 资源配置

建议的 Docker Desktop 资源分配：
- CPU: 2 核或更多
- 内存: 4 GB 或更多
- 磁盘: 10 GB 或更多

---

## 网络要求

### 必需的网络连接

- **TMDB API**: 
  - 域名: `api.themoviedb.org`
  - 端口: 443 (HTTPS)
  - 协议: HTTPS

### 可选的网络连接

- **GitHub**: 软件更新检查
  - 域名: `api.github.com`
  - 端口: 443 (HTTPS)

- **Docker Hub** (Docker 用户):
  - 域名: `hub.docker.com`
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

**配置文件**:
```json
{
  "proxy": {
    "http": "http://proxy.example.com:8080",
    "https": "http://proxy.example.com:8080"
  }
}
```

---

## 硬件要求

### CPU

**最低**:
- Intel Core i3 (第 6 代) 或同等
- AMD Ryzen 3 或同等
- Apple M1 或更高

**推荐**:
- Intel Core i5 (第 8 代) 或更高
- AMD Ryzen 5 或更高
- Apple M1 Pro/Max 或 M2 系列

### 内存 (RAM)

| 使用场景 | 最低 | 推荐 |
|---------|------|------|
| 基本使用 | 4 GB | 8 GB |
| 大型媒体库 (1000+ 文件) | 8 GB | 16 GB |
| 批量处理 | 8 GB | 16 GB+ |

### 存储空间

| 组件 | 空间要求 |
|------|---------|
| 应用程序 | 100-300 MB |
| 缓存数据 | 50-500 MB |
| 临时文件 | 100-1000 MB |
| **总计** | **500 MB - 2 GB** |

建议使用 SSD 以获得最佳性能。

### 显示器

**最低分辨率**: 1024x768  
**推荐分辨率**: 1920x1080 或更高  
**色深**: 24位真彩色

---

## 兼容性测试

### 测试矩阵

SmartRenamer 已在以下环境中测试：

| 平台 | 版本 | 架构 | 状态 |
|------|------|------|------|
| Windows 11 | 22H2 | x64 | ✅ 完全支持 |
| Windows 10 | 21H2 | x64 | ✅ 完全支持 |
| macOS Sonoma | 14.x | ARM64 | ✅ 完全支持 |
| macOS Ventura | 13.x | ARM64 | ✅ 完全支持 |
| macOS Monterey | 12.x | x64 | ✅ 完全支持 |
| Ubuntu | 22.04 | x64 | ✅ 完全支持 |
| Ubuntu | 20.04 | x64 | ✅ 完全支持 |
| Fedora | 38 | x64 | ✅ 完全支持 |
| Debian | 11 | x64 | ✅ 完全支持 |
| Docker | Latest | multi | ✅ 完全支持 |

### 测试工具

我们提供了诊断脚本来检查系统兼容性：

```bash
# 下载诊断脚本
wget https://raw.githubusercontent.com/smartrenamer/smartrenamer/main/scripts/check_compatibility.sh

# 运行诊断
chmod +x check_compatibility.sh
./check_compatibility.sh
```

---

## 故障排除

### 常见问题

#### 1. 应用无法启动

**Windows**:
- 检查是否安装了 Visual C++ Redistributable
- 检查防病毒软件是否阻止
- 以管理员身份运行

**macOS**:
- 检查"系统偏好设置 > 安全性与隐私"
- 移除隔离属性：`xattr -cr SmartRenamer.app`

**Linux**:
- 检查库依赖：`ldd SmartRenamer`
- 检查 FUSE：`sudo modprobe fuse`

#### 2. 网络连接失败

- 检查防火墙设置
- 验证 TMDB API Key
- 测试网络连接：`curl https://api.themoviedb.org`

#### 3. 性能问题

- 增加可用内存
- 清除缓存数据
- 减少同时处理的文件数量

---

## 获取帮助

如果遇到系统兼容性问题：

1. 查看 [故障排除文档](PACKAGING_GUIDE.md#故障排除)
2. 运行诊断脚本
3. 提交 [GitHub Issue](https://github.com/smartrenamer/smartrenamer/issues)，并附上：
   - 操作系统和版本
   - 应用版本
   - 错误信息
   - 诊断脚本输出

---

**文档版本**: 0.6.0  
**更新时间**: 2024-11-24  
**维护者**: SmartRenamer Team
