# Selfclaw - SDD规格驱动开发文档

## 1. 文档概述

### 1.1 文档目的
本文档遵循规格驱动开发（SDD）方法，为 Selfclaw 系统提供详细的规格说明、功能需求和实现指导。

### 1.2 项目概述
**Selfclaw** 是一个基于 GLM-5 模型的 **AI Agent 系统**，仿照 OpenClaw 设计，为 AI 提供"手和脚"，使其能够从"对话"扩展到"行动"。

**核心定位：**
- AI Agent 聊天工具
- 具备对话和行动双重能力
- 仿照OpenClaw的交互体验

### 1.3 设计原则
为确保系统稳定性和可维护性，本项目严格遵循**极简设计原则**：

1. **功能最小化** - 仅保留核心必需功能，避免过度设计
2. **界面简洁性** - 最少视觉元素，清晰功能分区
3. **代码精简性** - 最小化复杂度，保持可读性
4. **性能优先** - 快速响应，低延迟
5. **安全性优先** - 白名单机制，严格权限控制
6. **Agent 能力优先** - 强调 AI 的行动能力，而非仅仅对话
7. **用户体验优先** - 仿OpenClaw的流畅交互体验

### 1.4 技术栈
- 后端：Python + FastAPI + MySQL + GLM-5 API
- 前端：React + Vite + Tailwind CSS
- 架构：AI Agent（对话+行动）

### 1.5 AI Agent 架构
```
用户输入
    ↓
AI 理解意图（GLM-5）
    ↓
识别需要执行的操作
    ↓
实时显示命令执行状态（仿OpenClaw）
    ↓
执行命令并获取结果
    ↓
融入AI对话上下文
    ↓
返回最终回复（包含行动结果）
```

### 1.6 与传统聊天系统的区别
| 特性 | 传统聊天系统 | Selfclaw (AI Agent) |
|------|-------------|-------------------|
| 能力范围 | 仅对话 | 对话 + 行动 |
| AI 输出 | 文本回复 | 文本回复 + 执行操作 |
| 用户交互 | 阅读回复 | 阅读回复 + 查看操作过程 |
| 命令显示 | 无 | 实时动态显示（仿OpenClaw） |
| 类似产品 | ChatGPT | OpenClaw |

---

## 2. 系统规格说明

### 2.1 功能规格

| 功能ID | 功能名称 | 优先级 | 状态 | 说明 |
|--------|---------|--------|------|------|
| F01 | 流式输出对话 | P0 | ✅ | 实时显示AI回复，支持打字机效果 |
| F02 | 多轮对话 | P0 | ✅ | 保持上下文，支持连续对话 |
| F03 | 会话创建 | P0 | ✅ | 点击创建新对话 |
| F04 | 会话切换 | P0 | ✅ | 左侧边栏切换历史会话 |
| F05 | 会话删除 | P0 | ✅ | 删除不需要的会话 |
| F06 | 会话重命名 | P0 | ✅ | 修改会话标题 |
| F07 | Markdown渲染 | P1 | ✅ | 代码高亮、列表、粗体等格式 |
| F08 | 停止生成 | P1 | ✅ | 生成中可随时停止 |
| F09 | 重新生成 | P1 | ✅ | 重新生成最后一条AI回复 |
| F10 | 消息复制 | P2 | ✅ | 复制AI回复内容或代码块 |
| F11 | 终端命令自动执行 | P0 | ✅ | AI自动识别意图并执行命令 |
| F12 | 动态命令执行显示 | P0 | ✅ | 实时显示命令执行过程（仿OpenClaw） |
| F13 | 命令历史记录 | P1 | ✅ | 记录和查看命令执行历史 |
| F14 | 安全白名单扩展 | P0 | ✅ | 支持读操作和写操作命令 |
| F15 | 修复回复闪现问题 | P0 | ✅ | 解决undefined等异常内容 |
| F16 | 改进错误处理 | P0 | ✅ | 更好的异常内容和错误提示 |

### 2.2 非功能规格

#### 2.2.1 性能规格
- 响应时间：首屏加载 < 2秒
- 流式输出延迟：< 100ms
- 数据库查询：< 100ms
- 并发支持：至少50个并发用户

#### 2.2.2 可用性规格
- 系统可用性：99%+
- 错误恢复：自动重连机制
- 错误提示：友好的用户反馈
- 界面响应：实时更新，无延迟感

#### 2.2.3 安全规格
- 数据存储：MySQL持久化
- API密钥：环境变量配置
- CORS配置：仅允许本地开发（可扩展）
- 命令白名单：严格的安全验证

---

## 3. 数据模型规格

### 3.1 Conversation（会话）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| id | Integer | 是 | 主键，自增 | 1 |
| title | String(200) | 是 | 会话标题 | "新对话" |
| created_at | DateTime | 是 | 创建时间 | "2024-01-01 12:00:00" |
| updated_at | DateTime | 是 | 更新时间 | "2024-01-01 12:30:00" |

**业务规则：**
- 删除会话时级联删除所有相关消息
- 会话列表按更新时间倒序排列
- 自动生成默认标题

### 3.2 Message（消息）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| id | Integer | 是 | 主键，自增 | 1 |
| conversation_id | Integer | 是 | 外键，关联会话 | 1 |
| role | String(20) | 是 | 角色：user/assistant | "user" |
| content | Text | 是 | 消息内容 | "你好，请帮我写代码" |
| created_at | DateTime | 是 | 创建时间 | "2024-01-01 12:00:00" |

**业务规则：**
- 消息按创建时间正序排列
- 用户消息和AI消息交替保存
- 流式输出完成后保存完整AI回复

### 3.3 CommandHistory（命令执行历史）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| id | Integer | 是 | 主键，自增 | 1 |
| conversation_id | Integer | 是 | 外键，关联会话 | 1 |
| command | String(1000) | 是 | 执行的命令 | "ls -la" |
| output | Text | 否 | 命令输出 | "文件列表..." |
| error | Text | 否 | 错误信息 | "权限不足" |
| exit_code | Integer | 是 | 退出码 | 0 |
| execution_time | Float | 是 | 执行时间（秒） | 0.5 |
| created_at | DateTime | 是 | 创建时间 | "2024-01-01 12:00:00" |

**业务规则：**
- 记录每次命令执行的详细信息
- 支持执行历史查询和审计
- 按时间倒序排列

---

## 4. API接口规格

### 4.1 会话管理接口

#### 4.1.1 创建会话
```
POST /api/conversations
Content-Type: application/json

Request:
{
  "title": "新对话"
}

Response:
{
  "id": 1,
  "title": "新对话",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

#### 4.1.2 获取所有会话
```
GET /api/conversations

Response:
{
  "conversations": [...],
  "total": 10
}
```

#### 4.1.3 删除会话
```
DELETE /api/conversations/{id}

Response:
{
  "message": "删除成功"
}
```

#### 4.1.4 更新会话标题
```
PUT /api/conversations/{id}
Content-Type: application/json

Request:
{
  "title": "新的标题"
}

Response:
{
  "id": 1,
  "title": "新的标题",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:30:00"
}
```

### 4.2 消息管理接口

#### 4.2.1 获取会话消息
```
GET /api/conversations/{id}/messages

Response:
[
  {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "你好",
    "created_at": "2024-01-01T12:00:00"
  },
  ...
]
```

#### 4.2.2 流式对话（SSE）
```
POST /api/chat/stream
Content-Type: application/json

Request:
{
  "conversation_id": 1,
  "content": "创建一个test.txt文件"
}

Response (Server-Sent Events):
data: {"type": "command_start", "command": "touch test.txt", "message": "🔧 正在执行命令: `touch test.txt`"}

data: {"type": "command_success", "command": "touch test.txt", "output": "", "message": "✅ 命令执行成功: `touch test.txt`"}

data: {"content": "已成功创建文件", "done": false}

data: {"content": " test.txt", "done": false}

data: {"done": true}
```

**业务规则：**
- 支持命令状态消息：command_start, command_success, command_error
- 支持普通内容消息：content
- 使用SSE实现流式传输
- 命令状态消息会保留在界面上，不会消失

#### 4.2.3 终端命令执行
```
POST /api/terminal/execute
Content-Type: application/json

Request:
{
  "conversation_id": 1,
  "command": "ls -la",
  "timeout": 30
}

Response:
{
  "success": true,
  "output": "命令执行结果",
  "error": null,
  "exit_code": 0,
  "execution_time": 0.5
}
```

**业务规则：**
- 命令执行超时时间默认30秒
- 仅执行安全命令列表（白名单）
- 捕获命令的标准输出和错误输出
- 返回退出码判断执行成功与否
- 添加详细的执行日志和验证

---

## 5. 用户界面规格

### 5.1 布局结构

```
+-------------------+----------------------+
|                   |                      |
|   Sidebar         |      Chat Area       |
|   (256px)         |      (Flex)          |
|                   |                      |
|   - 会话列表      |   - 消息列表         |
|   - 新建按钮      |   - 命令执行状态      |
|   - 底部信息      |   - 输入框           |
|                   |   - 发送/停止按钮    |
|                   |                      |
+-------------------+----------------------+
```

### 5.2 动态命令显示规格（仿OpenClaw）

#### 5.2.1 命令状态显示
```
+---------------------------------------------+
| 系统                              🔧 ⏳    |
| ┌─────────────────────────────────────┐  |
| │ touch test.txt                       │  |
| └─────────────────────────────────────┘  |
| 🔧 正在执行命令: `touch test.txt`         |
+---------------------------------------------+
```

#### 5.2.2 命令成功显示
```
+---------------------------------------------+
| 系统                              ✅       |
| ┌─────────────────────────────────────┐  |
| │ touch test.txt                       │  |
| └─────────────────────────────────────┘  |
| ✅ 命令执行成功: `touch test.txt`          |
+---------------------------------------------+
```

#### 5.2.3 命令失败显示
```
+---------------------------------------------+
| 系统                              ❌       |
| ┌─────────────────────────────────────┐  |
| │ rm /protected/file                  │  |
| └─────────────────────────────────────┘  |
| ❌ 命令执行失败: `rm /protected/file`      |
| 权限不足                                |
+---------------------------------------------+
```

### 5.3 交互规格

#### 5.3.1 发送消息
- 输入框按Enter发送（Shift+Enter换行）
- 发送按钮点击发送
- 发送后清空输入框
- 显示加载状态
- 实时显示命令执行状态

#### 5.3.2 会话操作
- 点击会话切换
- 悬停显示操作按钮（删除/重命名）
- 点击删除需确认
- 双击标题进入编辑模式

#### 5.3.3 消息操作
- AI消息显示复制按钮
- 代码块显示复制按钮
- 生成中显示"停止"按钮
- 完成后显示"重新生成"
- 命令状态保留显示，不自动消失

---

## 6. 实现检查清单

### 6.1 后端实现检查

- [x] 数据库模型定义（models.py）
- [x] API路由定义（main.py）
- [x] Pydantic模型定义（schemas.py）
- [x] 业务逻辑实现（services.py）
- [x] 数据库连接配置（database.py）
- [x] 环境变量配置（.env）
- [x] GLM API集成（services.py）
- [x] 流式输出实现（services.py）
- [x] CORS配置（main.py）
- [x] 错误处理（services.py）
- [x] 动态命令状态推送（services.py）
- [x] 改进的错误处理和内容过滤

### 6.2 前端实现检查

- [x] 主应用组件（App.jsx）
- [x] 聊天区域组件（Chat.jsx）
- [x] 侧边栏组件（Sidebar.jsx）
- [x] API调用模块（api.js）
- [x] Tailwind CSS配置
- [x] React Markdown集成
- [x] 代码高亮集成
- [x] 流式数据处理（Chat.jsx）
- [x] 状态管理（App.jsx, Chat.jsx）
- [x] 响应式布局
- [x] 命令状态显示组件
- [x] 修复undefined闪现问题

### 6.3 测试检查

- [x] 后端服务启动
- [x] 前端服务启动
- [x] API接口测试
- [x] 数据库连接测试
- [x] 流式输出测试
- [x] 动态命令显示测试
- [x] 错误处理测试
- [ ] 功能集成测试
- [ ] 性能测试
- [ ] 浏览器兼容性测试

---

## 7. 部署规格

### 7.1 包管理器安装（推荐）

#### 7.1.1 NPM安装

```bash
npm install -g selfclaw
selfclaw --help
```

**包名：** selfclaw
**发布平台：** npmjs.com
**CLI命令：** selfclaw

#### 7.1.2 pip安装

```bash
pip install selfclaw
selfclaw --help
```

**包名：** selfclaw
**发布平台：** pypi.org
**CLI命令：** selfclaw

#### 7.1.3 安装后配置

```bash
# 初始化配置
selfclaw init

# 配置API密钥
selfclaw config --api-key your_glm_api_key_here

# 启动服务
selfclaw start
```

### 7.2 开发环境

**后端：**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

### 7.2 生产环境

**后端配置：**
- 使用Gunicorn或Uvicorn生产服务器
- 配置环境变量
- 启用HTTPS
- 配置日志和监控

**前端配置：**
- 构建静态文件：`npm run build`
- 配置Nginx或其他Web服务器
- 启用HTTPS
- 配置CDN

**包发布规格：**

**NPM包规格：**
```json
{
  "name": "selfclaw",
  "version": "1.0.0",
  "description": "AI Agent system based on GLM-5",
  "main": "index.js",
  "bin": {
    "selfclaw": "./bin/selfclaw"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "scripts": {
    "start": "node bin/selfclaw.js"
  }
}
```

**Python包规格：**
```python
from setuptools import setup, find_packages

setup(
    name="selfclaw",
    version="1.0.0",
    description="AI Agent system based on GLM-5",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "mysql-connector-python>=8.0.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.0.0",
        "httpx>=0.25.0"
    ],
    entry_points={
        "console_scripts": [
            "selfclaw=selfclaw.cli:main"
        ]
    }
)
```

**后端配置：**
- 使用Gunicorn或Uvicorn生产服务器
- 配置环境变量
- 启用HTTPS
- 配置日志和监控

**前端配置：**
- 构建静态文件：`npm run build`
- 配置Nginx或其他Web服务器
- 启用HTTPS
- 配置CDN

---

## 8. 扩展规格

### 8.1 功能扩展

- [ ] 暗色模式主题切换
- [ ] 消息搜索功能
- [ ] 导出对话功能
- [ ] 代码块自动检测
- [ ] 多语言支持
- [ ] 插件系统
- [ ] 多用户支持
- [ ] 权限管理
- [ ] NPM包发布
- [ ] PyPI包发布
- [ ] Docker容器化
- [ ] 一键安装脚本

### 8.2 性能扩展

- [ ] Redis缓存
- [ ] 数据库索引优化
- [ ] 前端代码分割
- [ ] 图片压缩
- [ ] CDN加速

### 8.3 安全扩展

- [ ] 用户认证
- [ ] API限流
- [ ] 数据加密
- [ ] 访问日志
- [ ] 安全审计

---

## 9. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2024-01-01 | 初始版本，核心功能完成 |
| 1.1.0 | 2026-04-16 | 新增动态命令执行显示，修复回复闪现问题 |
| 2.0.0 | 2026-04-16 | 添加包发布规格，支持npm和pip一键安装 |

---

## 10. 附录

### 10.1 参考资料
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [React文档](https://react.dev/)
- [GLM API文档](https://open.bigmodel.cn/)
- [Tailwind CSS文档](https://tailwindcss.com/)
- [OpenClaw设计理念](https://openclaw.ai/)

### 10.2 联系方式
- 项目地址：/Users/ray/Documents/projects/glm-session
- 后端地址：http://localhost:8000
- 前端地址：http://localhost:5173
- API文档：http://localhost:8000/docs

### 10.3 维护工具
- 数据库清理：`cd backend && python clean_database.py`
- 项目整理：查看 `docs/CLEANUP_SUMMARY.md`
