# SmartRenamer Docker 快速参考

## 快速启动

```bash
# 自动配置和启动
./docker-quickstart.sh

# 或使用 Docker Compose
docker-compose up
```

## 常用命令

### 使用 Makefile（推荐）

```bash
make help       # 显示帮助
make build      # 构建镜像
make gui        # 启动 GUI 模式
make cli        # 启动 CLI 模式
make shell      # 进入 Bash Shell
make logs       # 查看日志
make clean      # 清理容器和卷
```

### 使用 Docker Compose

```bash
# 构建镜像
docker-compose build

# 启动容器（GUI 模式）
docker-compose up

# 启动容器（后台）
docker-compose up -d

# CLI 模式
docker-compose run --rm smartrenamer cli

# Bash Shell
docker-compose run --rm smartrenamer bash

# 停止容器
docker-compose down

# 查看日志
docker-compose logs -f
```

### 使用 Docker

```bash
# 构建镜像
docker build -t smartrenamer:latest .

# GUI 模式（Linux）
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e TMDB_API_KEY=your_key \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/media:/data/media \
  --network host \
  smartrenamer:latest gui

# CLI 模式
docker run -it --rm \
  -e TMDB_API_KEY=your_key \
  -v $(pwd)/media:/data/media \
  smartrenamer:latest cli

# Bash Shell
docker run -it --rm \
  -e TMDB_API_KEY=your_key \
  -v $(pwd)/media:/data/media \
  smartrenamer:latest bash
```

## 环境配置

### 创建配置文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
nano .env
```

### 必需环境变量

```bash
# .env 文件
TMDB_API_KEY=your_api_key_here
MEDIA_PATH=/path/to/your/media
```

## 平台特定配置

### Linux

```bash
# 允许 Docker 访问 X11
xhost +local:docker

# 启动
docker-compose up
```

### macOS

```bash
# 安装 XQuartz
brew install --cask xquartz

# 配置 XQuartz（启动后在偏好设置中启用网络连接）

# 允许连接
xhost + 127.0.0.1

# 设置显示
export DISPLAY=host.docker.internal:0

# 启动
docker-compose up
```

### Windows (WSL2)

```bash
# 使用 CLI 模式（推荐）
docker-compose run --rm smartrenamer cli

# GUI 模式（Windows 11 + WSLg）
docker-compose up
```

## 运行模式

| 模式 | 命令 | 说明 |
|------|------|------|
| GUI | `gui` | 图形界面（需要 X11） |
| CLI | `cli` | Python 交互式 Shell |
| Bash | `bash` | 容器 Shell |
| 扫描 | `scan <dir>` | 扫描媒体目录 |
| 示例 | `example` | 运行示例脚本 |
| 帮助 | `help` | 显示帮助信息 |

## 卷挂载

```bash
# 媒体文件（必需）
-v /path/to/media:/data/media

# 配置持久化
-v smartrenamer-config:/data/config

# 缓存持久化
-v smartrenamer-cache:/data/cache

# X11 套接字（GUI 需要）
-v /tmp/.X11-unix:/tmp/.X11-unix
```

## 测试和调试

```bash
# 验证配置
./test-docker.sh

# 检查镜像
docker images smartrenamer

# 查看容器日志
docker logs smartrenamer

# 进入运行中的容器
docker exec -it smartrenamer bash

# 查看卷
docker volume ls

# 检查配置
docker-compose config
```

## 数据管理

```bash
# 备份配置
docker run --rm \
  -v smartrenamer-config:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/config.tar.gz -C /data .

# 恢复配置
docker run --rm \
  -v smartrenamer-config:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/config.tar.gz -C /data

# 清理卷
docker volume rm smartrenamer-config smartrenamer-cache
```

## 故障排除

### GUI 无法启动

```bash
# 1. 检查 X11
xhost +local:docker
echo $DISPLAY

# 2. 测试 X11 连接
xdpyinfo

# 3. 检查容器日志
docker-compose logs
```

### API Key 问题

```bash
# 1. 检查环境变量
docker-compose config | grep TMDB_API_KEY

# 2. 手动设置
export TMDB_API_KEY=your_key
docker-compose up
```

### 权限问题

```bash
# 使用当前用户
docker run --user $(id -u):$(id -g) ...

# 修改权限
chmod -R 755 /path/to/media
```

## 多平台构建

```bash
# 创建 builder
docker buildx create --name multiplatform --use

# 构建多平台镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t smartrenamer:latest \
  --load .
```

## 资源链接

- 📚 [完整文档](DOCKER_USAGE.md)
- 📋 [实现报告](DOCKER_IMPLEMENTATION_REPORT.md)
- 🐛 [问题追踪](https://github.com/yourusername/smartrenamer/issues)
- 🎬 [TMDB API](https://www.themoviedb.org/settings/api)

## 获取帮助

```bash
# 容器内帮助
docker run --rm smartrenamer:latest help

# Makefile 帮助
make help

# 查看文档
cat DOCKER_USAGE.md
```

---

**提示**: 首次使用建议运行 `./docker-quickstart.sh` 进行自动配置！
