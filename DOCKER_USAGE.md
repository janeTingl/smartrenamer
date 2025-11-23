# SmartRenamer Docker 使用指南

本文档介绍如何使用 Docker 运行 SmartRenamer 应用程序。

## 目录

- [快速开始](#快速开始)
- [构建镜像](#构建镜像)
- [运行容器](#运行容器)
- [环境变量](#环境变量)
- [卷挂载](#卷挂载)
- [平台支持](#平台支持)
- [常见问题](#常见问题)

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+ （可选）
- TMDB API Key（[注册获取](https://www.themoviedb.org/settings/api)）

### 使用 Docker Compose（推荐）

1. **配置环境变量**

创建 `.env` 文件：

```bash
# .env 文件
TMDB_API_KEY=your_api_key_here
MEDIA_PATH=/path/to/your/media/files
```

或者直接在命令行设置：

```bash
export TMDB_API_KEY=your_api_key_here
export MEDIA_PATH=/path/to/your/media/files
```

2. **启动应用（GUI 模式）**

```bash
# Linux: 允许 Docker 访问 X11
xhost +local:docker

# 启动容器
docker-compose up
```

3. **启动应用（CLI 模式）**

```bash
docker-compose run --rm smartrenamer cli
```

## 构建镜像

### 单平台构建

```bash
# 构建当前平台镜像
docker build -t smartrenamer:latest .

# 指定平台构建（例如 ARM64）
docker build --platform linux/arm64 -t smartrenamer:arm64 .
```

### 多平台构建

使用 Docker Buildx 构建多平台镜像：

```bash
# 创建 builder（首次需要）
docker buildx create --name multiplatform --driver docker-container --use

# 构建并推送多平台镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t smartrenamer:latest \
  --push .

# 或者构建到本地
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t smartrenamer:latest \
  --load .
```

### 构建参数

```bash
# 使用 Docker Compose 构建
docker-compose build

# 强制重新构建（不使用缓存）
docker-compose build --no-cache
```

## 运行容器

### GUI 模式（图形界面）

**Linux:**

```bash
# 方式 1: 使用 Docker Compose
xhost +local:docker
docker-compose up

# 方式 2: 使用 docker run
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e TMDB_API_KEY=your_api_key \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/media:/data/media \
  -v smartrenamer-config:/data/config \
  --network host \
  smartrenamer:latest gui
```

**macOS (使用 XQuartz):**

```bash
# 1. 安装 XQuartz
brew install --cask xquartz

# 2. 启动 XQuartz 并允许网络连接
# 在 XQuartz 偏好设置中启用 "Allow connections from network clients"

# 3. 允许本地连接
xhost + 127.0.0.1

# 4. 运行容器
docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -e TMDB_API_KEY=your_api_key \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/Movies:/data/media \
  -v smartrenamer-config:/data/config \
  smartrenamer:latest gui
```

**Windows (WSL2):**

Windows 上 GUI 模式需要额外配置，推荐使用 CLI 模式。

如需 GUI 支持，可以使用 WSLg（Windows 11 内置）：

```bash
# WSL2 环境中运行
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY \
  -e TMDB_API_KEY=your_api_key \
  -v /mnt/wslg:/mnt/wslg \
  -v /mnt/c/Users/username/Videos:/data/media \
  smartrenamer:latest gui
```

### CLI 模式（命令行）

```bash
# 交互式 Python Shell
docker run -it --rm \
  -e TMDB_API_KEY=your_api_key \
  -v $(pwd)/media:/data/media \
  smartrenamer:latest cli

# 在 Python Shell 中使用
>>> from smartrenamer.core import FileScanner, MediaLibrary
>>> scanner = FileScanner()
>>> files = scanner.scan_directory('/data/media')
>>> print(f"找到 {len(files)} 个媒体文件")
```

### Bash Shell 模式

```bash
# 进入容器调试
docker run -it --rm \
  -e TMDB_API_KEY=your_api_key \
  -v $(pwd)/media:/data/media \
  smartrenamer:latest bash

# 在容器内
root@container:/app# python -m smartrenamer.main
root@container:/app# python examples/basic_usage.py
```

### 扫描媒体目录

```bash
# 快速扫描指定目录
docker run --rm \
  -e TMDB_API_KEY=your_api_key \
  -v /path/to/media:/data/media \
  smartrenamer:latest scan /data/media
```

### 运行示例脚本

```bash
# 运行基础示例
docker run --rm \
  -e TMDB_API_KEY=your_api_key \
  smartrenamer:latest example
```

## 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `TMDB_API_KEY` | ✅ | - | TMDB API 密钥 |
| `DISPLAY` | GUI 需要 | `:0` | X11 显示服务器地址 |
| `QT_QPA_PLATFORM` | - | `xcb` | Qt 平台插件 |
| `LANG` | - | `zh_CN.UTF-8` | 系统语言 |
| `HOME` | - | `/data/config` | 主目录（配置文件位置） |

### 配置方式

**方式 1: 命令行参数**

```bash
docker run -e TMDB_API_KEY=your_key smartrenamer:latest
```

**方式 2: .env 文件（推荐）**

```bash
# .env
TMDB_API_KEY=your_api_key_here
MEDIA_PATH=/path/to/media
```

```bash
docker-compose --env-file .env up
```

**方式 3: docker-compose.override.yml**

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  smartrenamer:
    environment:
      TMDB_API_KEY: "your_api_key_here"
```

## 卷挂载

### 必需挂载

| 主机路径 | 容器路径 | 说明 |
|----------|----------|------|
| 你的媒体目录 | `/data/media` | 要处理的媒体文件 |

### 可选挂载

| 主机路径 | 容器路径 | 说明 |
|----------|----------|------|
| 命名卷 | `/data/config` | 配置文件持久化 |
| 命名卷 | `/data/cache` | 缓存数据持久化 |
| `/tmp/.X11-unix` | `/tmp/.X11-unix` | X11 套接字（GUI） |

### 示例

```bash
# 基础挂载
-v /home/user/Movies:/data/media

# 持久化配置和缓存
-v smartrenamer-config:/data/config
-v smartrenamer-cache:/data/cache

# GUI 支持（X11）
-v /tmp/.X11-unix:/tmp/.X11-unix:rw
```

### 数据持久化

查看和管理 Docker 卷：

```bash
# 查看所有卷
docker volume ls

# 查看配置卷详情
docker volume inspect smartrenamer-config

# 备份配置
docker run --rm -v smartrenamer-config:/data -v $(pwd):/backup \
  alpine tar czf /backup/smartrenamer-config-backup.tar.gz -C /data .

# 恢复配置
docker run --rm -v smartrenamer-config:/data -v $(pwd):/backup \
  alpine tar xzf /backup/smartrenamer-config-backup.tar.gz -C /data

# 清理卷
docker volume rm smartrenamer-config smartrenamer-cache
```

## 平台支持

### Linux (amd64/arm64)

✅ 完全支持，包括 GUI 和 CLI 模式

```bash
docker-compose up
```

### macOS (Apple Silicon / Intel)

✅ 支持，GUI 需要 XQuartz

```bash
# 安装 XQuartz
brew install --cask xquartz

# 配置 XQuartz（在偏好设置中启用网络连接）
# 重启 XQuartz

# 允许连接
xhost + 127.0.0.1

# 运行（注意 DISPLAY 设置）
docker run -e DISPLAY=host.docker.internal:0 ... smartrenamer:latest
```

### Windows (WSL2)

⚠️ 部分支持

- **CLI 模式**: ✅ 完全支持
- **GUI 模式**: ⚠️ 需要 WSLg（Windows 11）或 VcXsrv

```bash
# WSL2 中运行 CLI 模式
docker run -it --rm \
  -e TMDB_API_KEY=your_key \
  -v /mnt/c/Users/username/Videos:/data/media \
  smartrenamer:latest cli
```

### 架构支持

- `linux/amd64` - x86_64 架构（标准 PC）
- `linux/arm64` - ARM64 架构（Mac M1/M2, Raspberry Pi 4）

查看当前镜像支持的架构：

```bash
docker manifest inspect smartrenamer:latest
```

## 常见问题

### Q1: GUI 无法启动，提示 "无法连接到 X11 服务器"

**解决方案：**

```bash
# Linux: 允许 Docker 访问 X11
xhost +local:docker

# 确保挂载了 X11 套接字
-v /tmp/.X11-unix:/tmp/.X11-unix:rw

# 确保设置了 DISPLAY
-e DISPLAY=$DISPLAY
```

### Q2: macOS 上 GUI 无法显示

**解决方案：**

1. 安装 XQuartz：`brew install --cask xquartz`
2. 启动 XQuartz
3. 在 XQuartz 偏好设置中启用 "Allow connections from network clients"
4. 重启 XQuartz
5. 运行：`xhost + 127.0.0.1`
6. 设置 `DISPLAY=host.docker.internal:0`

### Q3: 权限错误，无法读写文件

**解决方案：**

```bash
# 方案 1: 使用用户 ID 运行
docker run --user $(id -u):$(id -g) ... smartrenamer:latest

# 方案 2: 修改宿主机目录权限
chmod -R 755 /path/to/media
```

### Q4: TMDB API Key 未设置

**解决方案：**

```bash
# 方式 1: 环境变量
export TMDB_API_KEY=your_api_key
docker-compose up

# 方式 2: .env 文件
echo "TMDB_API_KEY=your_api_key" > .env
docker-compose up

# 方式 3: 命令行参数
docker run -e TMDB_API_KEY=your_api_key ... smartrenamer:latest
```

### Q5: 镜像构建失败

**解决方案：**

```bash
# 清理构建缓存
docker builder prune

# 重新构建（不使用缓存）
docker-compose build --no-cache

# 检查网络连接
# 确保可以访问 PyPI (pip 依赖源)
```

### Q6: 容器内修改文件，宿主机看不到

**解决方案：**

确保正确挂载了卷：

```bash
# 检查挂载
docker inspect smartrenamer | grep -A 10 Mounts

# 正确的挂载方式
-v /absolute/path/to/media:/data/media
```

### Q7: 如何更新镜像？

```bash
# 重新构建镜像
docker-compose build --no-cache

# 或拉取最新镜像（如果发布到 Docker Hub）
docker pull smartrenamer:latest

# 重启容器
docker-compose down
docker-compose up -d
```

### Q8: 如何查看容器日志？

```bash
# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f smartrenamer

# 使用 docker logs
docker logs -f smartrenamer
```

## 高级用法

### 自定义配置文件

```bash
# 挂载自定义配置
docker run -v /path/to/custom/config.json:/data/config/.smartrenamer/config.json \
  smartrenamer:latest
```

### 开发模式（源代码挂载）

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  smartrenamer:
    volumes:
      - ./src:/app/src:ro
    command: bash
```

### 使用 Docker Secrets（生产环境）

```yaml
# docker-compose.yml
version: '3.8'
services:
  smartrenamer:
    secrets:
      - tmdb_api_key
    environment:
      TMDB_API_KEY_FILE: /run/secrets/tmdb_api_key

secrets:
  tmdb_api_key:
    file: ./secrets/tmdb_api_key.txt
```

### 资源限制

```yaml
# docker-compose.yml
services:
  smartrenamer:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```

## 获取帮助

```bash
# 查看容器内帮助
docker run --rm smartrenamer:latest help

# 查看版本信息
docker run --rm smartrenamer:latest --version

# 进入容器调试
docker run -it --rm smartrenamer:latest bash
```

## 相关链接

- [项目主页](https://github.com/yourusername/smartrenamer)
- [TMDB API 文档](https://developers.themoviedb.org/3)
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
