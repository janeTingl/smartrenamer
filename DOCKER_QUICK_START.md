# SmartRenamer Docker 快速启动 🚀

## 5 分钟上手指南

### 前置要求

- ✅ Docker 20.10+
- ✅ TMDB API Key ([获取地址](https://www.themoviedb.org/settings/api))

### 快速启动

#### 方式 1: 自动配置（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd smartrenamer

# 一键启动（自动配置所有内容）
./docker-quickstart.sh
```

#### 方式 2: Docker Compose

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 TMDB_API_KEY 和 MEDIA_PATH

# 2. 启动应用
docker-compose up
```

#### 方式 3: Makefile

```bash
# 构建并启动 GUI
make build && make gui

# 或启动 CLI 模式
make cli

# 查看所有命令
make help
```

---

## 平台特定配置

### 🐧 Linux

```bash
# 允许 Docker 访问 X11
xhost +local:docker

# 启动应用
docker-compose up
```

### 🍎 macOS

```bash
# 1. 安装 XQuartz
brew install --cask xquartz

# 2. 启动 XQuartz 并配置
# 在 XQuartz 偏好设置中：
# ✓ 勾选 "Allow connections from network clients"

# 3. 重启 XQuartz，然后运行
xhost + 127.0.0.1

# 4. 设置 DISPLAY 并启动
export DISPLAY=host.docker.internal:0
docker-compose up
```

### 🪟 Windows (WSL2)

```bash
# CLI 模式（推荐）
docker-compose run --rm smartrenamer cli

# GUI 模式（需要 Windows 11 + WSLg）
docker-compose up
```

---

## 常用命令

### 构建镜像

```bash
# 标准构建
docker-compose build

# 无缓存构建
docker-compose build --no-cache

# 多平台构建
docker buildx build --platform linux/amd64,linux/arm64 -t smartrenamer:latest .
```

### 运行容器

```bash
# GUI 模式（图形界面）
docker-compose up

# CLI 模式（命令行）
docker-compose run --rm smartrenamer cli

# Bash Shell（调试）
docker-compose run --rm smartrenamer bash

# 扫描媒体目录
docker run --rm \
  -e TMDB_API_KEY=your_key \
  -v /path/to/media:/data/media \
  smartrenamer:latest scan /data/media
```

### 日志和调试

```bash
# 查看日志
docker-compose logs -f

# 检查容器状态
docker-compose ps

# 进入运行中的容器
docker exec -it smartrenamer bash

# 停止容器
docker-compose down
```

---

## 环境变量配置

创建 `.env` 文件：

```bash
# TMDB API 配置（必需）
TMDB_API_KEY=your_actual_api_key

# 媒体文件路径（必需）
MEDIA_PATH=/path/to/your/media

# 显示配置（GUI 模式）
DISPLAY=:0

# Qt 平台插件
QT_QPA_PLATFORM=xcb

# 语言设置
LANG=zh_CN.UTF-8
```

---

## 数据持久化

### 查看卷

```bash
docker volume ls | grep smartrenamer
```

### 备份配置

```bash
docker run --rm -v smartrenamer-config:/data -v $(pwd):/backup \
  alpine tar czf /backup/smartrenamer-backup.tar.gz -C /data .
```

### 恢复配置

```bash
docker run --rm -v smartrenamer-config:/data -v $(pwd):/backup \
  alpine tar xzf /backup/smartrenamer-backup.tar.gz -C /data
```

### 清理卷

```bash
docker-compose down -v
```

---

## 故障排除

### GUI 无法启动

**问题**: `无法连接到 X11 服务器`

**解决**:
```bash
# Linux
xhost +local:docker

# macOS
xhost + 127.0.0.1
```

### API Key 未设置

**问题**: `TMDB_API_KEY 未设置`

**解决**:
```bash
# 方式 1: 设置环境变量
export TMDB_API_KEY=your_key

# 方式 2: 在 .env 文件中配置
echo "TMDB_API_KEY=your_key" >> .env
```

### 权限错误

**问题**: `Permission denied`

**解决**:
```bash
# 使用当前用户 ID 运行
docker run --user $(id -u):$(id -g) ...

# 或修改文件权限
chmod -R 755 /path/to/media
```

### 镜像构建失败

**问题**: 网络超时或包安装失败

**解决**:
```bash
# 清理缓存重试
docker builder prune
docker-compose build --no-cache

# 或使用预构建镜像（发布后）
docker pull smartrenamer:latest
```

---

## 测试安装

### 运行验证脚本

```bash
# 验证所有配置
./verify-docker-setup.sh

# 测试 Docker 配置
./test-docker.sh
```

### 手动测试

```bash
# 测试 help 命令
docker run --rm smartrenamer:latest help

# 测试 CLI 模式
docker run -it --rm \
  -e TMDB_API_KEY=test \
  smartrenamer:latest cli

# 测试示例脚本
docker run --rm \
  -e TMDB_API_KEY=test \
  smartrenamer:latest example
```

---

## 使用模式

### GUI 模式（推荐）

适合：日常使用，可视化操作

```bash
docker-compose up
```

### CLI 模式

适合：批量处理，自动化脚本

```bash
docker-compose run --rm smartrenamer cli
```

在 Python Shell 中：

```python
from smartrenamer.core import *
from smartrenamer.api import *

# 扫描媒体库
scanner = FileScanner()
files = scanner.scan_directory('/data/media')

# 使用 TMDB 匹配
client = EnhancedTMDBClient()
results = client.search_movie('盗梦空间')

# 批量重命名
renamer = Renamer()
rule = create_predefined_rule('电影-标准')
# ... 更多操作
```

### Bash 模式

适合：调试和开发

```bash
docker-compose run --rm smartrenamer bash

# 在容器内
python -m smartrenamer.main
python examples/basic_usage.py
```

---

## 性能优化

### 使用缓存

```bash
# 构建时使用缓存
docker-compose build  # 自动使用缓存

# 禁用缓存（完全重建）
docker-compose build --no-cache
```

### 多平台构建

```bash
# 创建 builder（首次）
docker buildx create --name multiplatform --use

# 构建多平台镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t smartrenamer:latest \
  --push .
```

---

## 常见使用场景

### 场景 1: 扫描本地电影目录

```bash
docker run --rm \
  -e TMDB_API_KEY=your_key \
  -v ~/Movies:/data/media \
  smartrenamer:latest scan /data/media
```

### 场景 2: 批量重命名电视剧

```bash
docker-compose run --rm smartrenamer cli

# 在 Python Shell 中
>>> from smartrenamer.core import *
>>> renamer = Renamer()
>>> # 执行重命名操作
```

### 场景 3: 开发和调试

```bash
# 挂载源代码
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  smartrenamer:latest bash
```

---

## 更多帮助

### 文档

- **详细指南**: `DOCKER_USAGE.md` (554 行)
- **快速参考**: `DOCKER_QUICKREF.md`
- **实现报告**: `DOCKER_IMPLEMENTATION_REPORT.md`
- **主文档**: `README.md`

### 命令帮助

```bash
# Docker 帮助
docker run --rm smartrenamer:latest help

# Makefile 帮助
make help

# 快速启动帮助
./docker-quickstart.sh --help
```

### 在线资源

- TMDB API: https://www.themoviedb.org/settings/api
- Docker 文档: https://docs.docker.com/
- 项目仓库: [GitHub URL]

---

## 检查清单

开始使用前，确保：

- [ ] Docker 已安装并运行
- [ ] 已获取 TMDB API Key
- [ ] 已配置 .env 文件（或环境变量）
- [ ] 媒体目录路径正确
- [ ] （Linux）已运行 `xhost +local:docker`
- [ ] （macOS）已安装并配置 XQuartz
- [ ] （Windows）使用 WSL2

---

## 快速命令参考

```bash
# 一键启动
./docker-quickstart.sh

# 构建
make build

# GUI 模式
make gui

# CLI 模式
make cli

# 查看日志
make logs

# 停止
make down

# 清理
make clean

# 帮助
make help
```

---

**提示**: 首次使用建议运行 `./docker-quickstart.sh`，它会自动检测系统、配置环境并启动应用！

**更多详细信息**: 查看 `DOCKER_USAGE.md` 获取完整使用指南。

---

**SmartRenamer 版本**: 0.5.1  
**文档版本**: 1.0  
**更新日期**: 2024-11-23
