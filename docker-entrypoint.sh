#!/bin/bash
# SmartRenamer Docker 容器入口脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印欢迎信息
print_banner() {
    cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║            SmartRenamer Docker 容器                   ║
║           智能媒体文件重命名工具                        ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
}

# 检查 TMDB API Key
check_api_key() {
    if [ -z "$TMDB_API_KEY" ]; then
        warn "未设置 TMDB_API_KEY 环境变量"
        warn "请通过 -e TMDB_API_KEY=your_key 设置"
        warn "或在 docker-compose.yml 中配置"
    else
        info "TMDB API Key 已配置"
    fi
}

# 检查 X11 显示
check_display() {
    if [ -z "$DISPLAY" ]; then
        warn "未设置 DISPLAY 环境变量，GUI 模式可能无法运行"
        return 1
    fi
    
    # 尝试连接 X 服务器
    if ! xdpyinfo >/dev/null 2>&1; then
        warn "无法连接到 X11 服务器"
        warn "请确保："
        warn "  1. 主机允许 X11 连接: xhost +local:docker"
        warn "  2. 正确挂载了 /tmp/.X11-unix"
        warn "  3. 设置了 DISPLAY 环境变量"
        return 1
    fi
    
    info "X11 显示已就绪"
    return 0
}

# 初始化配置
init_config() {
    info "初始化配置目录: /data/config"
    
    # 创建配置目录
    mkdir -p /data/config/.smartrenamer
    
    # 如果设置了 API Key，写入配置文件
    if [ -n "$TMDB_API_KEY" ]; then
        CONFIG_FILE="/data/config/.smartrenamer/config.json"
        if [ ! -f "$CONFIG_FILE" ]; then
            info "创建配置文件: $CONFIG_FILE"
            cat > "$CONFIG_FILE" << EOF
{
    "tmdb_api_key": "$TMDB_API_KEY",
    "language": "zh-CN"
}
EOF
        fi
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF

使用方法:
    docker run [OPTIONS] smartrenamer [COMMAND]

命令:
    gui             启动图形界面（默认）
    cli             进入命令行模式（Python 交互式）
    bash            进入 Bash Shell
    scan <dir>      扫描指定目录的媒体文件
    example         运行示例脚本
    help            显示此帮助信息

示例:
    # GUI 模式（需要 X11 转发）
    docker run -e DISPLAY=\$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix smartrenamer gui
    
    # CLI 模式
    docker run -it smartrenamer cli
    
    # 扫描媒体目录
    docker run -v /path/to/media:/data/media smartrenamer scan /data/media
    
    # 进入容器调试
    docker run -it smartrenamer bash

环境变量:
    TMDB_API_KEY        TMDB API 密钥（必需）
    DISPLAY             X11 显示（GUI 模式需要）
    QT_QPA_PLATFORM     Qt 平台插件（默认: xcb）

卷挂载:
    /data/media         媒体文件目录
    /data/config        配置文件目录
    /data/cache         缓存目录

EOF
}

# 主函数
main() {
    print_banner
    echo
    
    # 检查 API Key
    check_api_key
    
    # 初始化配置
    init_config
    
    # 获取命令
    COMMAND="${1:-gui}"
    
    case "$COMMAND" in
        gui)
            info "启动 GUI 模式"
            if check_display; then
                exec python -m smartrenamer.main
            else
                error "GUI 模式需要 X11 支持"
                error "请使用 CLI 模式或配置 X11 转发"
                exit 1
            fi
            ;;
            
        cli)
            info "启动 CLI 模式（Python 交互式）"
            exec python -i -c "
import sys
from pathlib import Path
sys.path.insert(0, '/app/src')
from smartrenamer.core import *
from smartrenamer.api import *
print('SmartRenamer CLI 模式')
print('已导入: core, api 模块')
print('使用 help(模块名) 查看帮助')
"
            ;;
            
        bash)
            info "启动 Bash Shell"
            exec /bin/bash
            ;;
            
        scan)
            if [ -z "$2" ]; then
                error "请指定要扫描的目录"
                echo "用法: docker run smartrenamer scan <directory>"
                exit 1
            fi
            info "扫描目录: $2"
            exec python /app/examples/scan_library_example.py "$2"
            ;;
            
        example)
            info "运行示例脚本"
            exec python /app/examples/basic_usage.py
            ;;
            
        help|--help|-h)
            show_help
            ;;
            
        *)
            error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
