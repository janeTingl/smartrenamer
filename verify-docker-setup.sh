#!/bin/bash
# SmartRenamer Docker 设置验证脚本

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
title() { echo -e "${BLUE}=== $1 ===${NC}"; }

echo "======================================"
echo "SmartRenamer Docker 设置验证"
echo "======================================"
echo

# 统计
total_tests=0
passed_tests=0
failed_tests=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    total_tests=$((total_tests + 1))
    
    if eval "$test_command"; then
        info "$test_name"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        error "$test_name"
        failed_tests=$((failed_tests + 1))
        return 1
    fi
}

# 测试 1: 必需文件存在性
title "1. 检查必需文件"
run_test "Dockerfile 存在" "[ -f Dockerfile ]"
run_test "docker-compose.yml 存在" "[ -f docker-compose.yml ]"
run_test "docker-entrypoint.sh 存在" "[ -f docker-entrypoint.sh ]"
run_test ".dockerignore 存在" "[ -f .dockerignore ]"
run_test ".env.example 存在" "[ -f .env.example ]"
run_test "Makefile 存在" "[ -f Makefile ]"
run_test "docker-quickstart.sh 存在" "[ -f docker-quickstart.sh ]"
run_test "test-docker.sh 存在" "[ -f test-docker.sh ]"
run_test "docker-compose.override.example.yml 存在" "[ -f docker-compose.override.example.yml ]"
echo

# 测试 2: 脚本可执行权限
title "2. 检查脚本权限"
run_test "docker-entrypoint.sh 可执行" "[ -x docker-entrypoint.sh ]"
run_test "docker-quickstart.sh 可执行" "[ -x docker-quickstart.sh ]"
run_test "test-docker.sh 可执行" "[ -x test-docker.sh ]"
echo

# 测试 3: 文档存在性
title "3. 检查文档"
run_test "DOCKER_USAGE.md 存在" "[ -f DOCKER_USAGE.md ]"
run_test "README.md 包含 Docker 说明" "grep -q 'Docker' README.md"
run_test "CHANGELOG.md 包含 0.5.1 版本" "grep -q '0.5.1' CHANGELOG.md"
echo

# 测试 4: GitHub Actions 工作流
title "4. 检查 CI/CD"
run_test "docker-build.yml 存在" "[ -f .github/workflows/docker-build.yml ]"
run_test "工作流包含多平台构建" "grep -q 'linux/amd64,linux/arm64' .github/workflows/docker-build.yml"
echo

# 测试 5: Dockerfile 内容检查
title "5. 检查 Dockerfile"
run_test "使用多阶段构建" "grep -q 'FROM.*AS builder' Dockerfile"
run_test "包含 Python 3.11" "grep -q 'python:3.11' Dockerfile"
run_test "设置工作目录" "grep -q 'WORKDIR' Dockerfile"
run_test "配置入口脚本" "grep -q 'ENTRYPOINT.*docker-entrypoint.sh' Dockerfile"
echo

# 测试 6: docker-compose.yml 检查
title "6. 检查 docker-compose.yml"
run_test "定义 smartrenamer 服务" "grep -q 'smartrenamer:' docker-compose.yml"
run_test "配置环境变量" "grep -q 'TMDB_API_KEY' docker-compose.yml"
run_test "配置卷挂载" "grep -q 'volumes:' docker-compose.yml"
run_test "支持多平台" "grep -q 'linux/amd64' docker-compose.yml"
echo

# 测试 7: 入口脚本检查
title "7. 检查 docker-entrypoint.sh"
run_test "包含 shebang" "head -1 docker-entrypoint.sh | grep -q '#!/bin/bash'"
run_test "支持 GUI 模式" "grep -q 'gui)' docker-entrypoint.sh"
run_test "支持 CLI 模式" "grep -q 'cli)' docker-entrypoint.sh"
run_test "检查 API Key" "grep -q 'TMDB_API_KEY' docker-entrypoint.sh"
run_test "检查 X11 显示" "grep -q 'check_display' docker-entrypoint.sh"
echo

# 测试 8: Makefile 检查
title "8. 检查 Makefile"
run_test "包含 build 目标" "grep -q '^build:' Makefile"
run_test "包含 gui 目标" "grep -q '^gui:' Makefile"
run_test "包含 cli 目标" "grep -q '^cli:' Makefile"
run_test "包含 test 目标" "grep -q '^test:' Makefile"
echo

# 测试 9: .dockerignore 检查
title "9. 检查 .dockerignore"
run_test "忽略 Git 文件" "grep -q '.git' .dockerignore"
run_test "忽略 Python 缓存" "grep -q '__pycache__' .dockerignore"
run_test "忽略测试文件" "grep -q 'tests/' .dockerignore"
run_test "忽略文档" "grep -q 'docs/' .dockerignore"
echo

# 测试 10: .gitignore 更新
title "10. 检查 .gitignore"
run_test ".gitignore 包含 Docker 规则" "grep -q 'docker-compose.override.yml' .gitignore"
run_test "忽略媒体目录" "grep -q 'media/' .gitignore"
echo

# 测试 11: setup.py 版本检查
title "11. 检查版本号"
run_test "setup.py 版本为 0.5.1" "grep -q 'version=\"0.5.1\"' setup.py"
echo

# 测试 12: 文档内容检查
title "12. 检查文档内容"
run_test "DOCKER_USAGE.md 包含快速开始" "grep -q '快速开始' DOCKER_USAGE.md"
run_test "DOCKER_USAGE.md 包含平台支持" "grep -q '平台支持' DOCKER_USAGE.md"
run_test "DOCKER_USAGE.md 包含常见问题" "grep -q '常见问题' DOCKER_USAGE.md"
run_test "README.md 包含 Docker 安装方式" "grep -q 'docker-quickstart' README.md"
echo

# 最终统计
echo "======================================"
echo "测试结果统计"
echo "======================================"
echo "总测试数: $total_tests"
echo -e "${GREEN}通过: $passed_tests${NC}"
echo -e "${RED}失败: $failed_tests${NC}"
echo

if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！Docker 设置完整。${NC}"
    exit 0
else
    echo -e "${RED}✗ 有 $failed_tests 个测试失败。${NC}"
    exit 1
fi
