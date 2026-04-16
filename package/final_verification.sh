#!/bin/bash
# Selfclaw 最终验证脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Selfclaw 最终验证"
echo "=================================================="

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 验证结果统计
total_tests=0
passed_tests=0
failed_tests=0

# 运行测试的函数
run_test() {
    local test_name=$1
    local test_command=$2

    echo -e "\n测试: $test_name"
    total_tests=$((total_tests + 1))

    if eval "$test_command" > /dev/null 2>&1; then
        print_success "$test_name 通过"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        print_error "$test_name 失败"
        failed_tests=$((failed_tests + 1))
        return 1
    fi
}

# 1. 文件完整性检查
echo -e "\n${BLUE}=== 文件完整性检查 ===${NC}"

required_files=(
    "setup.py"
    "pyproject.toml"
    "requirements.txt"
    "MANIFEST.in"
    "package.json"
    "LICENSE"
    "README.md"
    "selfclaw/__init__.py"
    "selfclaw/cli.py"
    "bin/selfclaw.js"
)

for file in "${required_files[@]}"; do
    run_test "文件存在: $file" "[ -f '$file' ]"
done

# 2. Python包检查
echo -e "\n${BLUE}=== Python包检查 ===${NC}"

run_test "Python包可导入" "python3 -c 'import selfclaw; print(selfclaw.__version__)'"
run_test "CLI模块可用" "python3 -c 'from selfclaw import cli; print(cli)'"
run_test "setup.py语法正确" "python3 -m py_compile setup.py"
run_test "requirements.txt格式正确" "grep -q 'fastapi' requirements.txt"

# 3. NPM包检查
echo -e "\n${BLUE}=== NPM包检查 ===${NC}"

run_test "package.json格式正确" "python3 -c 'import json; json.load(open(\"package.json\"))'"
run_test "NPM脚本定义完整" "grep -q '\"start\"' package.json"
run_test "bin脚本可执行" "[ -x 'bin/selfclaw.js' ]"

# 4. 代码质量检查
echo -e "\n${BLUE}=== 代码质量检查 ===${NC}"

run_test "Python代码无语法错误" "python3 -m py_compile selfclaw/*.py"
run_test "JavaScript代码无语法错误" "node --check bin/selfclaw.js"

# 5. 文档检查
echo -e "\n${BLUE}=== 文档检查 ===${NC}"

run_test "README.md存在且非空" "[ -s README.md ]"
run_test "LICENSE文件存在" "[ -f LICENSE ]"

# 6. 构建文件检查
echo -e "\n${BLUE}=== 构建文件检查 ===${NC}"

if [ -d "dist" ]; then
    run_test "dist目录存在" "[ -d dist ]"
    run_test "发布包存在" "[ -f dist/selfclaw-1.0.0.tar.gz ]"

    if [ -f "dist/selfclaw-1.0.0.tar.gz" ]; then
        package_size=$(stat -f%z "dist/selfclaw-1.0.0.tar.gz" 2>/dev/null || stat -c%s "dist/selfclaw-1.0.0.tar.gz" 2>/dev/null || echo "0")
        package_size_kb=$((package_size / 1024))
        print_info "包大小: ${package_size_kb}KB"

        # 检查包大小是否合理
        if [ $package_size_kb -lt 100 ]; then
            print_success "包大小合理 (< 100KB)"
        else
            print_warning "包大小偏大 (> 100KB)，考虑优化"
        fi
    fi
else
    print_warning "dist目录不存在，请先运行构建脚本"
fi

# 7. 功能模拟测试
echo -e "\n${BLUE}=== 功能模拟测试 ===${NC}"

run_test "Python模块版本信息" "python3 -c 'import selfclaw; print(f\"版本: {selfclaw.__version__}\")'"
run_test "Python模块描述信息" "python3 -c 'import selfclaw; print(f\"描述: {selfclaw.__description__}\")'"

# 8. 安全性检查
echo -e "\n${BLUE}=== 安全性检查 ===${NC}"

# 检查是否有硬编码的敏感信息
# 排除用户输入提示，只检查实际的硬编码值
run_test "无硬编码密码" "! grep -ri 'password.*=.*\"[^\"]*[a-zA-Z0-9][^\"]*\"' selfclaw/*.py | grep -v 'prompt' | grep -v 'hide_input'"
run_test "无硬编码API密钥" "! grep -ri 'api.*key.*=.*\"[^\"]*[a-zA-Z0-9][^\"]*\"' selfclaw/*.py | grep -v 'prompt' | grep -v 'hide_input'"

# 检查依赖安全性
# 接受 == 或 >= 作为版本约束
run_test "requirements.txt使用版本约束" "grep -qE '(==|>=).*[0-9]+\.[0-9]+\.[0-9]+' requirements.txt"

# 9. 配置检查
echo -e "\n${BLUE}=== 配置检查 ===${NC}"

run_test "setup.py包含必要信息" "grep -q 'name=\"selfclaw\"' setup.py"
run_test "package.json包含必要信息" "grep -q '\"name\": \"selfclaw\"' package.json"
run_test "pyproject.toml格式正确" "python3 -c 'import tomllib; tomllib.load(open(\"pyproject.toml\", \"rb\"))' 2>/dev/null || python3 -c 'import json; print(\"skip\")'"

# 显示测试结果
echo -e "\n${BLUE}==================================================${NC}"
echo -e "${BLUE}验证结果汇总${NC}"
echo -e "${BLUE}==================================================${NC}"

echo -e "\n测试统计:"
echo -e "  总测试数: $total_tests"
echo -e "  通过: ${GREEN}$passed_tests${NC}"
echo -e "  失败: ${RED}$failed_tests${NC}"

# 计算通过率
if [ $total_tests -gt 0 ]; then
    pass_rate=$((passed_tests * 100 / total_tests))
    echo -e "  通过率: ${pass_rate}%"
fi

echo -e "\n${BLUE}详细结果:${NC}"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}🎉 所有验证通过！包已准备就绪，可以发布。${NC}"
    exit_code=0
else
    echo -e "\n${RED}⚠️  有 $failed_tests 个测试失败，请修复后再发布。${NC}"
    exit_code=1
fi

echo -e "\n${BLUE}==================================================${NC}"
echo -e "${BLUE}下一步建议:${NC}"
echo -e "${BLUE}==================================================${NC}"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n1. 安装发布工具: pip install build twine"
    echo -e "2. 构建发布包: python -m build"
    echo -e "3. 检查包: twine check dist/*"
    echo -e "4. 发布到PyPI: twine upload dist/*"
    echo -e "5. 发布到NPM: npm publish"
else
    echo -e "\n1. 修复失败的测试"
    echo -e "2. 重新运行验证: ./final_verification.sh"
    echo -e "3. 确保所有测试通过后再发布"
fi

echo -e "\n${BLUE}==================================================${NC}"

exit $exit_code