"""
Selfclaw - AI Agent System
极简设计的AI智能助手系统
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="selfclaw",
    version="1.0.0",
    description="Selfclaw - AI Agent System based on GLM-5",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="raychiu0202",
    author_email="your-email@example.com",
    url="https://github.com/raychiu0202/selfclaw",
    license="MIT",

    # 包含的包
    packages=find_packages(include=["selfclaw*"]),
    python_requires=">=3.8",

    # 依赖包 - 精简到最小
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.0",
        "pymysql>=1.1.0",
        "cryptography>=41.0.0",
        "python-dotenv>=1.0.0",
        "zhipuai>=2.0.0",
        "click>=8.1.0",  # CLI框架
    ],

    # CLI入口点
    entry_points={
        "console_scripts": [
            "selfclaw=selfclaw.cli:main",
        ],
    },

    # 包数据
    package_data={
        "selfclaw": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },

    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],

    # 关键词
    keywords="ai agent chatbot llm glm-5 terminal automation",

    # 项目URL
    project_urls={
        "Bug Reports": "https://github.com/raychiu0202/selfclaw/issues",
        "Source": "https://github.com/raychiu0202/selfclaw",
        "Documentation": "https://github.com/raychiu0202/selfclaw/docs",
    },
)