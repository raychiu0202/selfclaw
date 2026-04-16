# Selfclaw - 快速开始指南

## 🚀 快速启动

### 前置要求
- Python 3.14+
- Node.js 18+
- MySQL 8.0+

### 1. 环境准备

#### 1.1 数据库配置

```bash
# 启动MySQL服务
mysql.server start

# 创建数据库
mysql -u root -p
```

```sql
CREATE DATABASE selfclaw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

#### 1.2 后端环境配置

```bash
cd backend

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
vim .env
```

**.env 配置内容：**
```env
# MySQL数据库配置
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=selfclaw

# GLM API配置
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-5
```

**获取GLM API密钥：**
1. 访问：https://open.bigmodel.cn/
2. 注册/登录账号
3. 在控制台创建API密钥
4. 复制API密钥到 `.env` 文件

#### 1.3 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 启动服务

#### 2.1 启动后端服务

```bash
cd backend
source venv/bin/activate
python main.py
```

**后端服务运行在：** http://localhost:8000

**验证后端服务：**
```bash
# 访问API文档
open http://localhost:8000/docs

# 或使用curl测试
curl http://localhost:8000/
```

#### 2.2 启动前端服务

```bash
# 新开一个终端窗口
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

**前端服务运行在：** http://localhost:5173

### 3. 访问应用

#### 3.1 访问前端界面

```
浏览器访问：http://localhost:5173
```

#### 3.2 访问API文档

```
浏览器访问：http://localhost:8000/docs
```

## 📊 数据模型

### 3.1 Conversation（会话表）

```sql
CREATE TABLE conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### 3.2 Message（消息表）

```sql
CREATE TABLE messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### 3.3 CommandHistory（命令执行历史表）

```sql
CREATE TABLE command_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    command VARCHAR(1000) NOT NULL,
    output TEXT,
    error TEXT,
    exit_code INT NOT NULL,
    execution_time FLOAT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

## 🔌 API接口

### 4.1 会话管理接口

#### 创建会话
```http
POST /api/conversations
Content-Type: application/json

{
  "title": "新对话"
}
```

#### 获取所有会话
```http
GET /api/conversations
```

#### 删除会话
```http
DELETE /api/conversations/{id}
```

#### 更新会话标题
```http
PUT /api/conversations/{id}
Content-Type: application/json

{
  "title": "新的标题"
}
```

### 4.2 消息管理接口

#### 获取会话消息
```http
GET /api/conversations/{id}/messages
```

#### 流式对话（SSE）
```http
POST /api/chat/stream
Content-Type: application/json

{
  "conversation_id": 1,
  "content": "创建一个test.txt文件"
}
```

**响应格式（Server-Sent Events）：**
```
data: {"type": "command_start", "command": "touch test.txt", "message": "🔧 正在执行命令: `touch test.txt`"}

data: {"type": "command_success", "command": "touch test.txt", "output": "", "message": "✅ 命令执行成功: `touch test.txt`"}

data: {"content": "已成功创建文件", "done": false}

data: {"content": " test.txt", "done": false}

data: {"done": true}
```

### 4.3 终端命令接口

#### 执行命令
```http
POST /api/terminal/execute
Content-Type: application/json

{
  "command": "ls -la",
  "conversation_id": 1,
  "timeout": 30
}
```

**响应格式：**
```json
{
  "success": true,
  "command": "ls -la",
  "output": "命令执行结果...",
  "error": null,
  "exit_code": 0,
  "execution_time": 0.523,
  "timestamp": "2024-04-16T10:30:00Z"
}
```

#### 获取命令历史
```http
GET /api/terminal/history/{conversation_id}?limit=10
```

## 🎯 使用示例

### 示例1：创建文件

**用户输入：**
```
创建一个test.txt文件
```

**系统行为：**
1. AI识别意图：创建文件
2. 生成命令：`touch test.txt`
3. 显示：🔧 正在执行命令: `touch test.txt`
4. 执行成功：✅ 命令执行成功: `touch test.txt`
5. AI回复：已成功创建文件 test.txt

### 示例2：写入内容

**用户输入：**
```
在test.txt中写入"Hello World"
```

**系统行为：**
1. AI识别意图：写入文件内容
2. 生成命令：`echo 'Hello World' > test.txt`
3. 显示：🔧 正在执行命令: `echo 'Hello World' > test.txt`
4. 执行成功：✅ 命令执行成功
5. AI回复：已成功在 test.txt 中写入内容

### 示例3：查看目录

**用户输入：**
```
看看当前目录有什么文件
```

**系统行为：**
1. AI识别意图：列出目录内容
2. 生成命令：`ls -la`
3. 显示：🔧 正在执行命令: `ls -la`
4. 执行成功：✅ 命令执行成功
5. AI回复：当前目录的文件列表如下：[文件列表]

### 示例4：查看文件内容

**用户输入：**
```
查看test.txt的内容
```

**系统行为：**
1. AI识别意图：查看文件内容
2. 生成命令：`cat test.txt`
3. 显示：🔧 正在执行命令: `cat test.txt`
4. 执行成功：✅ 命令执行成功
5. AI回复：文件 test.txt 的内容如下：[文件内容]

## 🔧 维护工具

### 数据库清理

清理所有测试数据：
```bash
cd backend
source venv/bin/activate
python clean_database.py
```

**清理内容：**
- 删除所有对话记录
- 删除所有消息记录
- 删除所有命令执行历史
- 重置所有自增ID

### 查看日志

```bash
# 查看后端日志
tail -f backend/server.log

# 查看最新的执行日志
tail -50 backend/server.log | grep "命令"
```

## 🛡️ 安全配置

### 命令白名单

**只读命令：**
- `ls`, `pwd`, `cat`, `grep`, `head`, `tail`, `wc`, `date`

**写操作命令：**
- `touch`, `mkdir`, `echo`, `rm`, `mv`

### 安全限制

- 路径限制：仅限项目目录
- 命令超时：默认30秒
- 输出限制：最多10,000字符
- 并发限制：最多2个命令同时执行

## ⚠️ 故障排查

### 问题1：后端启动失败

**症状：**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案：**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 问题2：数据库连接失败

**症状：**
```
Can't connect to MySQL server
```

**解决方案：**
```bash
# 检查MySQL是否启动
mysql.server status

# 启动MySQL服务
mysql.server start

# 检查.env配置是否正确
cat backend/.env
```

### 问题3：前端无法连接后端

**症状：**
```
Network Error
```

**解决方案：**
```bash
# 检查后端是否运行
curl http://localhost:8000/

# 检查端口是否被占用
lsof -i :8000

# 检查CORS配置
# 确保backend/main.py中已配置CORS
```

### 问题4：GLM API调用失败

**症状：**
```
API调用失败: 401 Unauthorized
```

**解决方案：**
```bash
# 检查API密钥是否正确
cat backend/.env | grep GLM_API_KEY

# 重新获取API密钥
# 访问 https://open.bigmodel.cn/
```

## 📖 更多文档

- [README.md](../README.md) - 项目说明
- [SDD.md](./SDD.md) - 软件设计文档
- [TASK_PLAN.md](./TASK_PLAN.md) - 任务规划文档
- [TERMINAL_DESIGN.md](./TERMINAL_DESIGN.md) - 终端设计文档
- [用户需求与问题记录.md](./用户需求与问题记录.md) - 用户需求记录

## 🆘 获取帮助

- **API文档：** http://localhost:8000/docs
- **项目地址：** /Users/ray/Documents/projects/glm-session
- **前端地址：** http://localhost:5173
- **后端地址：** http://localhost:8000

---

**最后更新：** 2026-04-16
**版本：** 1.0
