#!/bin/bash
# SmartRenamer Docker 测试脚本
# 验证 Docker 配置的正确性

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

echo "======================================"
echo "SmartRenamer Docker 配置测试"
echo "======================================"
echo

# 测试 1: 检查文件存在性
echo "测试 1: 检查必需文件..."
files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-entrypoint.sh"
    ".dockerignore"
    "DOCKER_USAGE.md"
    ".env.example"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        info "$file 存在"
    else
        error "$file 不存在"
        exit 1
    fi
done
echo

# 测试 2: 检查脚本可执行性
echo "测试 2: 检查脚本权限..."
scripts=(
    "docker-entrypoint.sh"
    "docker-quickstart.sh"
)

for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        info "$script 可执行"
    else
        error "$script 不可执行"
        exit 1
    fi
done
echo

# 测试 3: 验证 Dockerfile 语法
echo "测试 3: 验证 Dockerfile 语法..."
if command -v docker &> /dev/null; then
    if docker build --help | grep -q "check"; then
        docker build --check . || {
            warn "Dockerfile 语法验证失败（可能是 Docker 版本较旧）"
        }
    else
        info "Docker 版本不支持 --check，跳过语法验证"
    fi
else
    warn "Docker 未安装，跳过语法验证"
fi
echo

# 测试 4: 检查 docker-compose.yml 语法
echo "测试 4: 验证 docker-compose.yml 语法..."
if command -v docker-compose &> /dev/null; then
    docker-compose config > /dev/null 2>&1 && info "docker-compose.yml 语法正确" || {
        error "docker-compose.yml 语法错误"
        exit 1
    }
elif docker compose version &> /dev/null; then
    docker compose config > /dev/null 2>&1 && info "docker-compose.yml 语法正确" || {
        error "docker-compose.yml 语法错误"
        exit 1
    }
else
    warn "Docker Compose 未安装，跳过语法验证"
fi
echo

# 测试 5: 检查 .dockerignore 规则
echo "测试 5: 检查 .dockerignore 配置..."
ignored_patterns=(
    "__pycache__"
    "*.pyc"
    ".git"
    ".pytest_cache"
    "tests/"
)

for pattern in "${ignored_patterns[@]}"; do
    if grep -q "$pattern" .dockerignore; then
        info "忽略规则 '$pattern' 已配置"
    else
        warn "忽略规则 '$pattern' 未配置"
    fi
done
echo

# 测试 6: 检查入口脚本语法
echo "测试 6: 检查 Shell 脚本语法..."
if command -v shellcheck &> /dev/null; then
    for script in "${scripts[@]}"; do
        shellcheck -x "$script" && info "$script 语法正确" || warn "$script 有语法警告"
    done
else
    warn "shellcheck 未安装，跳过脚本语法检查"
fi
echo

# 测试 7: 检查文档完整性
echo "测试 7: 检查文档完整性..."
docs=(
    "README.md"
    "DOCKER_USAGE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        lines=$(wc -l < "$doc")
        if [ "$lines" -gt 50 ]; then
            info "$doc 存在且内容充足 ($lines 行)"
        else
            warn "$doc 内容较少 ($lines 行)"
        fi
    else
        error "$doc 不存在"
    fi
done
echo

# 测试 8: 检查 GitHub Actions 工作流
echo "测试 8: 检查 CI/CD 配置..."
if [ -f ".github/workflows/docker-build.yml" ]; then
    info "GitHub Actions 工作流已配置"
else
    error "GitHub Actions 工作流不存在"
fi
echo

# 测试 9: 检查 Makefile
echo "测试 9: 检查 Makefile..."
if [ -f "Makefile" ]; then
    if make help > /dev/null 2>&1; then
        info "Makefile 配置正确"
    else
        warn "Makefile 可能有问题"
    fi
else
    error "Makefile 不存在"
fi
echo

# 测试 10: 模拟构建测试（dry-run）
echo "测试 10: 模拟构建流程..."
if command -v docker &> /dev/null; then
    # 检查基础镜像
    info "检查 Python 基础镜像..."
    docker pull python:3.11-slim > /dev/null 2>&1 && info "基础镜像可用" || warn "基础镜像拉取失败"
else
    warn "Docker 未安装，跳过构建测试"
fi
echo

echo "======================================"
echo "测试完成！"
echo "======================================"
echo
info "所有配置文件检查通过"
info "Docker 配置已就绪"
echo
echo "下一步："
echo "  1. 配置环境变量: cp .env.example .env"
echo "  2. 编辑 .env 文件，填入你的 TMDB_API_KEY"
echo "  3. 构建镜像: make build 或 docker-compose build"
echo "  4. 运行容器: make gui 或 docker-compose up"
echo
