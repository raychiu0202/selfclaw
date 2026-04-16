# Selfclaw

基于GLM-5的智能AI助手系统，仿照OpenClaw设计，支持自然语言文件操作和命令执行。

## 🚀 快速开始

### 前置要求
- Python 3.14+
- Node.js 18+
- MySQL 8.0+

### 安装步骤

1. **后端设置**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 配置环境变量
python main.py
```

2. **前端设置**
```bash
cd frontend
npm install
npm run dev
```

### 访问地址
- 前端界面: http://localhost:5173/
- 后端API: http://localhost:8000/
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
selfclaw/
├── backend/           # 后端服务
│   ├── main.py       # FastAPI主应用
│   ├── services.py   # 业务逻辑
│   ├── terminal.py   # 终端命令执行
│   ├── security.py   # 安全验证
│   └── clean_database.py  # 数据库清理工具
├── frontend/         # 前端应用
│   └── src/          # React组件
├── docs/             # 项目文档
│   ├── README.md     # 详细项目说明
│   ├── SDD.md        # 软件设计文档
│   ├── TASK_PLAN.md  # 任务计划
│   └── 用户需求与问题记录.md
└── README.md         # 本文件
```

## 🔧 主要功能

### 🤖 智能AI对话
- 基于GLM-5的智能对话能力
- 自然语言理解与意图识别
- 上下文感知的对话管理

### 📁 文件操作
- 支持创建、读取、删除文件
- 目录管理和查看
- 文件内容搜索

### 💻 命令执行
- 安全的终端命令执行
- 命令白名单机制
- 沙箱化执行环境

### 🔄 实时流式显示
- 动态显示命令执行过程
- 实时输出命令结果
- 状态反馈和错误处理

### 🛡️ 安全机制
- 命令白名单验证
- 路径安全检查
- 执行超时控制
- 输出大小限制

## 🎯 核心特性

### 仿OpenClaw设计
- 类似的界面交互体验
- 命令执行过程可视化
- 安全的权限管理

### 智能意图识别
- 自动理解用户需求
- 智能生成执行命令
- 减少用户学习成本

### 用户无感知
- 自然语言交互
- 自动命令执行
- 结果自动展示

## 📝 文档

详细文档请查看 `docs/` 目录：
- [详细项目说明](docs/README.md)
- [软件设计文档](docs/SDD.md)
- [任务计划](docs/TASK_PLAN.md)
- [用户需求记录](docs/用户需求与问题记录.md)

## 🧹 数据库清理

清理测试数据：
```bash
cd backend
python clean_database.py
```

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI
- **AI模型**: GLM-5
- **数据库**: MySQL
- **异步**: asyncio + httpx

### 前端
- **框架**: React
- **构建工具**: Vite
- **样式**: TailwindCSS
- **Markdown**: react-markdown

## 🚀 开发路线

- [x] 基础对话功能
- [x] 文件操作支持
- [x] 命令执行机制
- [x] 安全验证系统
- [x] 动态命令显示
- [x] 用户界面优化
- [ ] 高级文件操作
- [ ] 多用户支持
- [ ] 权限管理
- [ ] 插件系统

## 📄 许可证

MIT License

## 🙏 致谢

本项目借鉴了OpenClaw的设计理念，致力于为开发者提供强大的AI辅助工具。
