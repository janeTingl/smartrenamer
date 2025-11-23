# SmartRenamer Docker Makefile
# 简化 Docker 操作的便捷命令

.PHONY: help build build-nc up down restart logs shell cli gui clean test

# 默认目标：显示帮助
help:
	@echo "SmartRenamer Docker 管理命令"
	@echo ""
	@echo "使用方法: make [命令]"
	@echo ""
	@echo "构建命令:"
	@echo "  build       构建 Docker 镜像"
	@echo "  build-nc    构建 Docker 镜像（不使用缓存）"
	@echo "  build-multi 构建多平台镜像"
	@echo ""
	@echo "运行命令:"
	@echo "  up          启动容器（后台）"
	@echo "  down        停止并删除容器"
	@echo "  restart     重启容器"
	@echo "  gui         启动 GUI 模式"
	@echo "  cli         启动 CLI 模式（交互式）"
	@echo "  shell       进入容器 Shell"
	@echo ""
	@echo "日志和调试:"
	@echo "  logs        查看容器日志"
	@echo "  logs-f      实时查看容器日志"
	@echo "  ps          查看容器状态"
	@echo ""
	@echo "测试命令:"
	@echo "  test        运行容器测试"
	@echo "  test-build  测试镜像构建"
	@echo ""
	@echo "清理命令:"
	@echo "  clean       清理容器和卷"
	@echo "  clean-all   清理所有（包括镜像）"
	@echo ""
	@echo "示例:"
	@echo "  make build && make gui    # 构建并启动 GUI"
	@echo "  make cli                  # 启动命令行模式"

# 构建镜像
build:
	@echo "正在构建 Docker 镜像..."
	docker-compose build

# 无缓存构建
build-nc:
	@echo "正在构建 Docker 镜像（无缓存）..."
	docker-compose build --no-cache

# 多平台构建
build-multi:
	@echo "正在构建多平台镜像..."
	docker buildx build --platform linux/amd64,linux/arm64 -t smartrenamer:latest .

# 启动容器（后台）
up:
	@echo "正在启动容器..."
	docker-compose up -d

# 停止容器
down:
	@echo "正在停止容器..."
	docker-compose down

# 重启容器
restart:
	@echo "正在重启容器..."
	docker-compose restart

# GUI 模式
gui:
	@echo "正在启动 GUI 模式..."
	@echo "注意：Linux 系统请先运行: xhost +local:docker"
	docker-compose up

# CLI 模式
cli:
	@echo "正在启动 CLI 模式..."
	docker-compose run --rm smartrenamer cli

# Shell 模式
shell:
	@echo "正在进入容器 Shell..."
	docker-compose run --rm smartrenamer bash

# 查看日志
logs:
	docker-compose logs

# 实时查看日志
logs-f:
	docker-compose logs -f

# 查看容器状态
ps:
	docker-compose ps

# 测试镜像构建
test-build:
	@echo "测试镜像构建..."
	docker build --target builder -t smartrenamer:builder .
	docker build -t smartrenamer:test .
	@echo "构建测试通过 ✓"

# 测试容器运行
test:
	@echo "测试容器运行..."
	@echo "1. 测试 help 命令"
	docker run --rm smartrenamer:latest help
	@echo "2. 测试镜像大小"
	@SIZE=$$(docker image inspect smartrenamer:latest --format='{{.Size}}' | awk '{print int($$1/1024/1024)}'); \
	echo "镜像大小: $${SIZE}MB"; \
	if [ $$SIZE -gt 2048 ]; then \
		echo "警告: 镜像大小超过 2GB"; \
		exit 1; \
	fi
	@echo "所有测试通过 ✓"

# 清理容器和卷
clean:
	@echo "清理容器和卷..."
	docker-compose down -v
	@echo "清理完成 ✓"

# 清理所有（包括镜像）
clean-all: clean
	@echo "清理镜像..."
	docker rmi smartrenamer:latest || true
	docker image prune -f
	@echo "清理完成 ✓"

# 显示版本信息
version:
	@echo "Docker 版本:"
	@docker --version
	@echo "Docker Compose 版本:"
	@docker-compose --version
	@echo "SmartRenamer 镜像:"
	@docker images smartrenamer

# 准备 X11（Linux）
x11-setup:
	@echo "配置 X11 访问..."
	xhost +local:docker
	@echo "X11 已配置 ✓"

# 检查环境
check:
	@echo "检查 Docker 环境..."
	@docker info > /dev/null 2>&1 && echo "✓ Docker 运行正常" || echo "✗ Docker 未运行"
	@docker-compose version > /dev/null 2>&1 && echo "✓ Docker Compose 已安装" || echo "✗ Docker Compose 未安装"
	@[ -n "$$TMDB_API_KEY" ] && echo "✓ TMDB_API_KEY 已设置" || echo "✗ TMDB_API_KEY 未设置"
	@[ -f .env ] && echo "✓ .env 文件存在" || echo "⚠ .env 文件不存在"
