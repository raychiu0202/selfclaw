#!/usr/bin/env python3
"""
测试Selfclaw包的基本功能
"""
import sys
import os

# 添加包路径
sys.path.insert(0, os.path.dirname(__file__))

def test_import():
    """测试包导入"""
    try:
        import selfclaw
        print(f"✓ 导入成功: {selfclaw.__version__}")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_cli_import():
    """测试CLI模块导入"""
    try:
        from selfclaw import cli
        print("✓ CLI模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ CLI模块导入失败: {e}")
        return False

def test_package_structure():
    """测试包结构"""
    required_files = [
        "setup.py",
        "requirements.txt",
        "MANIFEST.in",
        "selfclaw/__init__.py",
        "selfclaw/cli.py",
        "package.json",
        "bin/selfclaw.js",
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 不存在")
            all_exist = False

    return all_exist

def test_npm_package():
    """测试NPM包配置"""
    try:
        import json
        with open("package.json", "r") as f:
            package = json.load(f)

        print(f"✓ NPM包名: {package['name']}")
        print(f"✓ NPM版本: {package['version']}")
        print(f"✓ NPM脚本: {list(package['scripts'].keys())}")
        return True
    except Exception as e:
        print(f"✗ NPM包配置检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Selfclaw 包测试")
    print("=" * 50)

    tests = [
        ("包结构", test_package_structure),
        ("包导入", test_import),
        ("CLI模块", test_cli_import),
        ("NPM配置", test_npm_package),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n测试 {name}:")
        result = test_func()
        results.append((name, result))

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)

    all_passed = True
    for name, result in results:
        status = "通过 ✓" if result else "失败 ✗"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("所有测试通过!")
        return 0
    else:
        print("部分测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())