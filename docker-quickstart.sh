#!/bin/bash
# SmartRenamer Docker 快速启动脚本
# 自动检测系统并配置 Docker 环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
title() { echo -e "${BLUE}=== $1 ===${NC}"; }

# 打印欢迎信息
print_banner() {
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        SmartRenamer Docker 快速启动脚本                ║
║           智能媒体文件重命名工具                        ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
    echo
}

# 检测操作系统
detect_os() {
    title "检测操作系统"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        info "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        info "检测到 macOS 系统"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        info "检测到 Windows 系统"
    else
        OS="unknown"
        warn "未知操作系统: $OSTYPE"
    fi
    
    echo
}

# 检查依赖
check_dependencies() {
    title "检查依赖项"
    
    local all_ok=true
    
    # 检查 Docker
    if command -v docker &> /dev/null; then
        info "✓ Docker 已安装: $(docker --version)"
    else
        error "✗ Docker 未安装"
        echo "  请访问: https://docs.docker.com/get-docker/"
        all_ok=false
    fi
    
    # 检查 Docker Compose
    if command -v docker-compose &> /dev/null; then
        info "✓ Docker Compose 已安装: $(docker-compose --version)"
    elif docker compose version &> /dev/null; then
        info "✓ Docker Compose (插件) 已安装"
    else
        error "✗ Docker Compose 未安装"
        echo "  请访问: https://docs.docker.com/compose/install/"
        all_ok=false
    fi
    
    # 检查 Docker 是否运行
    if docker info &> /dev/null; then
        info "✓ Docker 服务运行正常"
    else
        error "✗ Docker 服务未运行"
        echo "  请启动 Docker 服务"
        all_ok=false
    fi
    
    if [ "$all_ok" = false ]; then
        error "依赖检查失败，请安装缺失的依赖"
        exit 1
    fi
    
    echo
}

# 检查环境变量
check_env() {
    title "检查环境配置"
    
    # 检查 .env 文件
    if [ ! -f .env ]; then
        warn ".env 文件不存在"
        if [ -f .env.example ]; then
            read -p "是否从 .env.example 创建 .env 文件？(y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cp .env.example .env
                info "已创建 .env 文件"
                warn "请编辑 .env 文件并填入你的配置"
                echo
                read -p "按 Enter 继续编辑..."
                ${EDITOR:-nano} .env
            fi
        fi
    else
        info "✓ .env 文件存在"
    fi
    
    # 检查 TMDB API Key
    if [ -f .env ]; then
        source .env
        if [ -z "$TMDB_API_KEY" ] || [ "$TMDB_API_KEY" = "your_tmdb_api_key_here" ]; then
            warn "TMDB_API_KEY 未设置或使用默认值"
            read -p "请输入你的 TMDB API Key: " api_key
            if [ -n "$api_key" ]; then
                sed -i.bak "s/TMDB_API_KEY=.*/TMDB_API_KEY=$api_key/" .env
                info "API Key 已保存到 .env 文件"
                export TMDB_API_KEY=$api_key
            fi
        else
            info "✓ TMDB_API_KEY 已配置"
        fi
        
        # 检查媒体路径
        if [ -z "$MEDIA_PATH" ] || [ "$MEDIA_PATH" = "/path/to/your/media/files" ]; then
            warn "MEDIA_PATH 未设置或使用默认值"
            read -p "请输入媒体文件路径: " media_path
            if [ -n "$media_path" ]; then
                sed -i.bak "s|MEDIA_PATH=.*|MEDIA_PATH=$media_path|" .env
                info "媒体路径已保存到 .env 文件"
                export MEDIA_PATH=$media_path
            fi
        else
            info "✓ MEDIA_PATH 已配置: $MEDIA_PATH"
        fi
    fi
    
    echo
}

# 配置 X11（Linux）
setup_x11_linux() {
    title "配置 X11 显示"
    
    if [ -z "$DISPLAY" ]; then
        warn "DISPLAY 环境变量未设置"
        export DISPLAY=:0
    fi
    
    info "允许 Docker 访问 X11..."
    xhost +local:docker 2>/dev/null || warn "xhost 命令执行失败，GUI 可能无法使用"
    
    info "✓ X11 已配置"
    echo
}

# 配置 X11（macOS）
setup_x11_macos() {
    title "配置 XQuartz"
    
    if ! command -v xquartz &> /dev/null; then
        warn "XQuartz 未安装"
        read -p "是否安装 XQuartz？(需要 Homebrew) (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v brew &> /dev/null; then
                brew install --cask xquartz
                info "XQuartz 已安装，请重启并重新运行此脚本"
                exit 0
            else
                error "Homebrew 未安装"
                echo "请访问: https://brew.sh/"
                exit 1
            fi
        else
            warn "将使用 CLI 模式"
            return 1
        fi
    fi
    
    info "配置 XQuartz..."
    xhost + 127.0.0.1 2>/dev/null || warn "xhost 配置失败"
    export DISPLAY=host.docker.internal:0
    
    info "✓ XQuartz 已配置"
    echo
    return 0
}

# 构建镜像
build_image() {
    title "构建 Docker 镜像"
    
    read -p "是否构建 Docker 镜像？(y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "开始构建镜像..."
        docker-compose build
        info "✓ 镜像构建完成"
    else
        info "跳过镜像构建"
    fi
    
    echo
}

# 选择运行模式
choose_mode() {
    title "选择运行模式"
    
    echo "1) GUI 模式（图形界面）"
    echo "2) CLI 模式（命令行）"
    echo "3) Bash Shell"
    echo "4) 退出"
    echo
    
    read -p "请选择 (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            run_gui
            ;;
        2)
            run_cli
            ;;
        3)
            run_bash
            ;;
        4)
            info "退出"
            exit 0
            ;;
        *)
            error "无效选择"
            choose_mode
            ;;
    esac
}

# 运行 GUI 模式
run_gui() {
    title "启动 GUI 模式"
    
    if [ "$OS" = "linux" ]; then
        setup_x11_linux
    elif [ "$OS" = "macos" ]; then
        if ! setup_x11_macos; then
            warn "XQuartz 未配置，切换到 CLI 模式"
            run_cli
            return
        fi
    elif [ "$OS" = "windows" ]; then
        warn "Windows 不支持 GUI 模式，切换到 CLI 模式"
        run_cli
        return
    fi
    
    info "启动容器..."
    docker-compose up
}

# 运行 CLI 模式
run_cli() {
    title "启动 CLI 模式"
    
    info "启动交互式 Python Shell..."
    docker-compose run --rm smartrenamer cli
}

# 运行 Bash
run_bash() {
    title "启动 Bash Shell"
    
    info "进入容器..."
    docker-compose run --rm smartrenamer bash
}

# 主函数
main() {
    print_banner
    detect_os
    check_dependencies
    check_env
    build_image
    choose_mode
}

# 运行主函数
main
