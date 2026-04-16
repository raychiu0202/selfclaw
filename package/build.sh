#!/bin/bash
# Selfclaw 包构建脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Selfclaw 包构建脚本"
echo "=================================================="

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数定义
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 1. 清理旧的构建文件
echo -e "\n步骤1: 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info __pycache__ */__pycache__ */*/__pycache__
print_success "清理完成"

# 2. 运行测试
echo -e "\n步骤2: 运行测试..."
python3 test_package.py
if [ $? -eq 0 ]; then
    print_success "测试通过"
else
    print_error "测试失败"
    exit 1
fi

# 3. 检查包结构
echo -e "\n步骤3: 检查包结构..."
required_files=("setup.py" "requirements.txt" "MANIFEST.in" "package.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file 存在"
    else
        print_error "$file 不存在"
        exit 1
    fi
done

# 4. 构建Python包
echo -e "\n步骤4: 构建Python包..."
if command -v python3 &> /dev/null; then
    python3 -m build
    if [ $? -eq 0 ]; then
        print_success "Python包构建成功"
    else
        print_error "Python包构建失败"
        exit 1
    fi
else
    print_error "python3 未安装"
    exit 1
fi

# 5. 检查Python包
echo -e "\n步骤5: 检查Python包..."
if command -v twine &> /dev/null; then
    twine check dist/*
    if [ $? -eq 0 ]; then
        print_success "Python包检查通过"
    else
        print_error "Python包检查失败"
        exit 1
    fi
else
    print_warning "twine 未安装，跳过检查"
fi

# 6. 构建NPM包（可选）
echo -e "\n步骤6: 构建NPM包..."
if command -v npm &> /dev/null; then
    npm run build 2>/dev/null || print_warning "NPM构建脚本不存在，跳过"
    print_success "NPM包准备完成"
else
    print_warning "npm 未安装，跳过NPM构建"
fi

# 7. 显示构建结果
echo -e "\n=================================================="
echo "构建结果"
echo "=================================================="

# 显示Python包
if [ -d "dist" ]; then
    echo -e "\nPython包:"
    ls -lh dist/
fi

# 显示包大小
if [ -d "dist" ]; then
    total_size=$(du -sh dist/ | cut -f1)
    echo -e "\n总包大小: ${total_size}"
fi

echo -e "\n=================================================="
echo "构建完成!"
echo "=================================================="

# 下一步提示
echo -e "\n下一步:"
echo -e "1. 测试安装: pip install dist/selfclaw-*.whl"
echo -e "2. 发布到测试环境: twine upload --repository testpypi dist/*"
echo -e "3. 发布到正式环境: twine upload dist/*"
echo -e "4. 发布NPM包: npm publish"

echo -e "\n发布前请确保:"
echo -e "  • 所有测试通过"
echo -e "  • 文档完整更新"
echo -e "  • 版本号已更新"
echo -e "  • 发布说明已准备"

exit 0