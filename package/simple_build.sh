#!/bin/bash
# Selfclaw 简化构建脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Selfclaw 包简化构建"
echo "=================================================="

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# 4. 创建dist目录
echo -e "\n步骤4: 创建发布目录..."
mkdir -p dist
print_success "dist目录已创建"

# 5. 复制包文件
echo -e "\n步骤5: 复制包文件..."
cp setup.py dist/
cp requirements.txt dist/
cp MANIFEST.in dist/
cp pyproject.toml dist/
cp README.md dist/
cp LICENSE dist/
cp -r selfclaw dist/
cp -r bin dist/
print_success "包文件已复制"

# 6. 创建压缩包
echo -e "\n步骤6: 创建发布压缩包..."
cd dist
tar -czf selfclaw-1.0.0.tar.gz selfclaw/ setup.py requirements.txt MANIFEST.in pyproject.toml README.md LICENSE bin/
cd ..
print_success "压缩包已创建: dist/selfclaw-1.0.0.tar.gz"

# 7. 显示构建结果
echo -e "\n=================================================="
echo "构建结果"
echo "=================================================="

if [ -d "dist" ]; then
    echo -e "\n发布文件:"
    ls -lh dist/
fi

# 显示包大小
if [ -f "dist/selfclaw-1.0.0.tar.gz" ]; then
    package_size=$(ls -lh "dist/selfclaw-1.0.0.tar.gz" | awk '{print $5}')
    echo -e "\n包大小: ${package_size}"
fi

echo -e "\n=================================================="
echo "构建完成!"
echo "=================================================="

# 统计包信息
echo -e "\n包统计:"
echo -e "  Python文件: $(find dist/selfclaw -name '*.py' | wc -l | tr -d ' ')"
echo -e "  总行数: $(find dist/selfclaw -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}')"

# 下一步提示
echo -e "\n下一步:"
echo -e "1. 安装发布工具: pip install build twine"
echo -e "2. 构建标准包: python -m build"
echo -e "3. 检查包: twine check dist/*"
echo -e "4. 发布到PyPI: twine upload dist/*"
echo -e "5. 发布到NPM: npm publish"

echo -e "\n注意事项:"
echo -e "  • 当前是简化构建，未生成wheel包"
echo -e "  • 发布前需要使用标准构建流程"
echo -e "  • 确保所有测试通过"

exit 0