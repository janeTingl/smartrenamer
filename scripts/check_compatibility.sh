#!/bin/bash
# SmartRenamer 兼容性检查脚本

set -e

echo "======================================"
echo "SmartRenamer 兼容性检查"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

# 1. 操作系统信息
echo "1. 操作系统信息"
echo "   -------------------"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "   发行版: $NAME"
    echo "   版本: $VERSION"
    check_pass "检测到 Linux 系统"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   系统: macOS"
    sw_vers
    check_pass "检测到 macOS 系统"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "   系统: Windows"
    check_pass "检测到 Windows 系统"
else
    echo "   系统: $OSTYPE"
    check_warn "未识别的操作系统"
fi
echo ""

# 2. 内核版本
echo "2. 内核版本"
echo "   -------------------"
if command -v uname &> /dev/null; then
    KERNEL=$(uname -r)
    echo "   内核: $KERNEL"
    check_pass "内核信息可用"
fi
echo ""

# 3. CPU 架构
echo "3. CPU 架构"
echo "   -------------------"
ARCH=$(uname -m)
echo "   架构: $ARCH"
if [[ "$ARCH" == "x86_64" ]] || [[ "$ARCH" == "amd64" ]]; then
    check_pass "支持的 x86_64 架构"
elif [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "aarch64" ]]; then
    check_pass "支持的 ARM64 架构"
else
    check_warn "可能不支持的架构: $ARCH"
fi
echo ""

# 4. 内存
echo "4. 内存"
echo "   -------------------"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    MEM_TOTAL=$(free -h | awk '/^Mem:/{print $2}')
    MEM_AVAIL=$(free -h | awk '/^Mem:/{print $7}')
    echo "   总内存: $MEM_TOTAL"
    echo "   可用内存: $MEM_AVAIL"
    
    # 转换为 MB 进行比较
    MEM_TOTAL_MB=$(free -m | awk '/^Mem:/{print $2}')
    if [ $MEM_TOTAL_MB -ge 8192 ]; then
        check_pass "内存充足 (推荐配置)"
    elif [ $MEM_TOTAL_MB -ge 4096 ]; then
        check_pass "内存满足最低要求"
    else
        check_warn "内存可能不足 (建议至少 4GB)"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    MEM_TOTAL=$(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}')
    echo "   总内存: $MEM_TOTAL"
    check_pass "内存信息可用"
fi
echo ""

# 5. 存储空间
echo "5. 存储空间"
echo "   -------------------"
if command -v df &> /dev/null; then
    DISK_AVAIL=$(df -h . | awk 'NR==2{print $4}')
    echo "   当前目录可用空间: $DISK_AVAIL"
    check_pass "存储空间信息可用"
fi
echo ""

# 6. Python 环境（如果需要）
echo "6. Python 环境"
echo "   -------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "   Python 版本: $PYTHON_VERSION"
    
    # 检查版本号
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ $PYTHON_MAJOR -ge 3 ] && [ $PYTHON_MINOR -ge 8 ]; then
        check_pass "Python 版本满足要求 (>= 3.8)"
    else
        check_warn "Python 版本过低 (需要 >= 3.8)"
    fi
    
    # 检查 pip
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version | awk '{print $2}')
        echo "   pip 版本: $PIP_VERSION"
        check_pass "pip 可用"
    else
        check_warn "pip 未安装"
    fi
else
    check_warn "Python 未安装（使用可执行文件版本不需要）"
fi
echo ""

# 7. Docker 环境（如果需要）
echo "7. Docker 环境"
echo "   -------------------"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,$//')
    echo "   Docker 版本: $DOCKER_VERSION"
    check_pass "Docker 已安装"
    
    # 检查 Docker 是否运行
    if docker info &> /dev/null; then
        check_pass "Docker 守护进程正在运行"
    else
        check_warn "Docker 守护进程未运行"
    fi
    
    # 检查 Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | sed 's/,$//')
        echo "   Docker Compose 版本: $COMPOSE_VERSION"
        check_pass "Docker Compose 已安装"
    else
        check_warn "Docker Compose 未安装"
    fi
else
    check_warn "Docker 未安装（使用可执行文件版本不需要）"
fi
echo ""

# 8. 显示环境（Linux）
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "8. 显示环境"
    echo "   -------------------"
    
    # 检查显示服务器
    if [ -n "$DISPLAY" ]; then
        echo "   DISPLAY: $DISPLAY"
        check_pass "X11 DISPLAY 已设置"
    else
        check_warn "DISPLAY 未设置（CLI 模式可用）"
    fi
    
    # 检查显示服务器类型
    if [ -n "$XDG_SESSION_TYPE" ]; then
        echo "   会话类型: $XDG_SESSION_TYPE"
        if [ "$XDG_SESSION_TYPE" == "x11" ]; then
            check_pass "使用 X11 显示服务器（推荐）"
        elif [ "$XDG_SESSION_TYPE" == "wayland" ]; then
            check_warn "使用 Wayland（可能需要 XWayland）"
        fi
    fi
    
    # 检查 Qt 库
    echo ""
    echo "9. Qt 依赖库"
    echo "   -------------------"
    
    MISSING_LIBS=()
    
    # 检查关键库
    REQUIRED_LIBS=(
        "libxcb-xinerama.so.0"
        "libxcb-icccm.so.4"
        "libxcb-image.so.0"
        "libxkbcommon-x11.so.0"
        "libGL.so.1"
        "libfontconfig.so.1"
        "libdbus-1.so.3"
    )
    
    for lib in "${REQUIRED_LIBS[@]}"; do
        if ldconfig -p | grep -q "$lib"; then
            check_pass "$lib"
        else
            check_warn "$lib (缺失)"
            MISSING_LIBS+=("$lib")
        fi
    done
    
    if [ ${#MISSING_LIBS[@]} -gt 0 ]; then
        echo ""
        echo "   缺失的库可以通过以下命令安装："
        echo ""
        if command -v apt-get &> /dev/null; then
            echo "   sudo apt-get install -y libxcb-xinerama0 libxcb-icccm4 \\"
            echo "     libxcb-image0 libxkbcommon-x11-0 libgl1-mesa-glx \\"
            echo "     libfontconfig1 libdbus-1-3"
        elif command -v dnf &> /dev/null; then
            echo "   sudo dnf install -y libxcb libXext libXrender fontconfig dbus-libs"
        elif command -v pacman &> /dev/null; then
            echo "   sudo pacman -S libxcb libxext libxrender fontconfig dbus"
        fi
    fi
    echo ""
fi

# 9/10. 网络连接
echo "10. 网络连接"
echo "   -------------------"
if command -v curl &> /dev/null || command -v wget &> /dev/null; then
    # 检查 TMDB API
    if command -v curl &> /dev/null; then
        if curl -s --head https://api.themoviedb.org | grep "200 OK" > /dev/null; then
            check_pass "TMDB API 可访问"
        else
            check_warn "TMDB API 无法访问（可能被防火墙阻止）"
        fi
        
        # 检查 GitHub
        if curl -s --head https://api.github.com | grep "200 OK" > /dev/null; then
            check_pass "GitHub API 可访问"
        else
            check_warn "GitHub API 无法访问"
        fi
    else
        check_warn "curl 未安装，无法测试网络连接"
    fi
else
    check_warn "curl/wget 未安装，无法测试网络连接"
fi
echo ""

# 11. FUSE（Linux AppImage）
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "11. FUSE 支持 (AppImage)"
    echo "   -------------------"
    if [ -e /dev/fuse ]; then
        check_pass "FUSE 设备可用"
        
        # 检查 libfuse
        if ldconfig -p | grep -q "libfuse.so.2"; then
            check_pass "libfuse2 已安装"
        else
            check_warn "libfuse2 未安装"
            echo "   安装命令: sudo apt-get install fuse libfuse2"
        fi
    else
        check_warn "FUSE 设备不可用"
        echo "   启用命令: sudo modprobe fuse"
    fi
    echo ""
fi

# 总结
echo "======================================"
echo "检查完成！"
echo "======================================"
echo ""
echo "总结："
echo "- 如果所有检查都通过（✓），系统完全兼容"
echo "- 如果有警告（⚠），功能可能受限但仍可使用"
echo "- 如果有错误（✗），需要先解决问题"
echo ""
echo "详细文档："
echo "- 系统要求: https://github.com/smartrenamer/smartrenamer/blob/main/SYSTEM_REQUIREMENTS.md"
echo "- 安装指南: https://github.com/smartrenamer/smartrenamer/blob/main/README.md"
echo "- 故障排除: https://github.com/smartrenamer/smartrenamer/blob/main/PACKAGING_GUIDE.md#故障排除"
echo ""
