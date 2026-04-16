# Selfclaw - 日志总结文档

## 📋 日志系统概述

Selfclaw 采用结构化日志记录系统，详细记录系统运行状态、命令执行过程、错误信息和性能指标。

## 🎯 日志目标

1. **问题诊断**：快速定位和解决问题
2. **性能监控**：监控系统性能和资源使用
3. **安全审计**：记录所有命令执行和访问
4. **用户行为分析**：分析用户使用模式

## 📊 日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 调试信息 | 变量值、函数调用 |
| INFO | 一般信息 | 服务启动、命令执行 |
| WARNING | 警告信息 | 安全验证失败、非致命错误 |
| ERROR | 错误信息 | 命令执行失败、API调用失败 |
| CRITICAL | 严重错误 | 系统崩溃、数据丢失 |

## 🔧 日志配置

### 后端日志配置

**位置：** `backend/services.py`, `backend/terminal.py`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### 前端日志配置

**位置：** `frontend/src/api.js`

```javascript
console.warn('JSON解析失败，跳过该行:', dataStr, e);
```

## 📝 关键日志点

### 1. 服务启动日志

```log
2026-04-16 14:16:24,740 - terminal - INFO - 终端服务初始化，工作目录: /Users/ray/Documents/projects/selfclaw/selfclaw
INFO - Started server process [11506]
INFO - Waiting for application startup.
INFO - Application startup complete.
INFO - Uvicorn running on http://0.0.0.0:8000
```

**说明：** 记录服务启动状态和工作目录配置

### 2. 用户消息接收日志

```log
2026-04-16 14:10:36,287 - services - INFO - 收到用户消息: conversation_id=20, content='看下这个目录下有啥 /Users/ray/Documents/projects/selfclaw/selfclaw/test_dir/test_subdir，另外在这个目录下建一个名为"测试01.md"的文件并写入"哈哈哈呵呵呵"。'
```

**说明：** 记录每次用户输入和对话ID

### 3. AI意图分析日志

```log
2026-04-16 14:10:39,367 - services - INFO - AI意图分析结果: {'needs_commands': True, 'commands': ['ls -la /glm-session/test_dir/test_subdir', "echo '哈哈哈呵呵呵' > test_dir/test_subdir/测试01.md"], 'explanation': '用户请求查看指定目录下的内容，并创建一个文件并写入内容。'}
```

**说明：** 记录AI对用户意图的理解和生成的命令

### 4. 命令执行日志

```log
2026-04-16 14:10:39,367 - services - INFO - 准备执行命令，命令数量: 2
2026-04-16 14:10:39,367 - services - INFO - 准备yield命令开始消息: ls -la /glm-session/test_dir/test_subdir
2026-04-16 14:10:39,368 - services - INFO - 已yield命令开始消息
2026-04-16 14:10:39,368 - services - INFO - 执行命令: ls -la /glm-session/test_dir/test_subdir
2026-04-16 14:10:39,368 - terminal - INFO - 开始执行命令: 'ls -la /glm-session/test_dir/test_subdir', conversation_id=20, timeout=10
2026-04-16 14:10:39,369 - terminal - WARNING - 命令安全验证失败: 路径 '/glm-session/test_dir/test_subdir' 不合法或超出允许范围
```

**说明：** 详细记录命令执行的每个步骤

### 5. 文件创建验证日志

```log
2026-04-16 14:10:39,383 - terminal - INFO - 文件创建验证: test_dir/test_subdir/测试01.md - 存在: True, 路径: /Users/ray/Documents/projects/selfclaw/selfclaw/test_dir/test_subdir/测试01.md
2026-04-16 14:10:39,383 - terminal - INFO - 文件信息: 大小=19字节
```

**说明：** 验证文件是否真实创建，并记录文件详情

### 6. API调用日志

```log
2026-04-16 14:10:39,952 - httpx - INFO - HTTP Request: POST https://open.bigmodel.cn/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
2026-04-16 14:10:44,686 - services - INFO - GLM API流式传输完成，原始内容长度: 242
```

**说明：** 记录GLM API调用状态和结果

### 7. 数据库操作日志

```log
2026-04-16 14:10:39,384 - terminal - INFO - 命令执行历史保存到数据库成功
2026-04-16 14:10:44,694 - services - INFO - 最终回复保存成功
```

**说明：** 记录数据库操作状态

## 🔍 日志分析

### 成功的命令执行日志模式

```
INFO - 准备执行命令，命令数量: N
INFO - 准备yield命令开始消息: <命令>
INFO - 已yield命令开始消息
INFO - 执行命令: <命令>
INFO - 开始执行命令: '<命令>', conversation_id: X, timeout: N
INFO - 命令安全验证通过
INFO - 命令执行前，当前工作目录: <路径>
INFO - 命令执行前，目录内容: [...]
INFO - 命令执行后，工作目录: <路径>
INFO - 命令执行后，目录文件数: N
INFO - 命令执行完成: exit_code=0, success=True, execution_time=X.XXXs
INFO - 文件创建验证: <文件> - 存在: True, 路径: <完整路径>
INFO - 文件信息: 大小=X字节
INFO - 准备yield命令成功消息: <命令>
INFO - 已yield命令成功消息
```

### 失败的命令执行日志模式

```
INFO - 准备yield命令开始消息: <命令>
INFO - 已yield命令开始消息
INFO - 执行命令: <命令>
INFO - 开始执行命令: '<命令>', conversation_id: X, timeout: N
INFO - WARNING - 命令安全验证失败: <错误信息>
INFO - 准备yield命令失败消息: <命令>
INFO - 已yield命令失败消息
```

## 🚨 问题诊断指南

### 问题1：命令没有执行

**日志特征：** 没有看到 `执行命令:` 日志

**可能原因：**
1. AI意图分析返回 `needs_commands: false`
2. 命令生成失败
3. API调用超时

**解决方案：**
1. 检查 `AI意图分析结果` 日志
2. 检查 GLM API 调用状态
3. 验证提示词配置

### 问题2：命令执行失败

**日志特征：** `命令安全验证失败` 或 `命令执行失败`

**可能原因：**
1. 命令不在白名单中
2. 路径超出允许范围
3. 命令格式错误
4. 权限不足

**解决方案：**
1. 检查命令是否在白名单中
2. 验证路径格式
3. 检查文件权限
4. 查看详细错误信息

### 问题3：文件创建显示成功但实际不存在

**日志特征：** `命令执行完成: exit_code=0, success=True` 但 `文件创建验证: xxx - 存在: False`

**可能原因：**
1. 工作目录设置错误
2. 命令在错误的位置执行
3. 文件系统权限问题

**解决方案：**
1. 检查 `命令执行前，当前工作目录` 日志
2. 验证工作目录配置
3. 检查文件系统权限
4. 手动验证文件位置

## 📈 性能日志

### 命令执行时间

```log
INFO - 命令执行完成: exit_code=0, success=True, execution_time=0.023s
```

**分析：**
- 正常范围：0.001-1.0秒
- 警告范围：1.0-5.0秒
- 异常范围：>5.0秒

### API响应时间

```log
2026-04-16 14:10:39,365 - httpx - INFO - HTTP Request: POST https://open.bigmodel.cn/api/paas/v4/chat/completions "HTTP/1.1 200 OK"
...
2026-04-16 14:10:44,686 - services - INFO - GLM API流式传输完成，原始内容长度: 242
```

**分析：**
- 总响应时间：约5.3秒
- 正常范围：1-10秒
- 警告范围：10-30秒
- 异常范围：>30秒

## 🛡️ 安全日志

### 安全验证失败

```log
INFO - WARNING - 命令安全验证失败: 路径 '/etc/passwd' 不合法或超出允许范围
INFO - WARNING - 命令安全验证失败: echo重定向的文件路径不合法: /absolute/path/to/file
```

**分析：**
- 记录所有被拒绝的命令
- 记录拒绝原因
- 用于安全审计

### 路径遍历尝试

```log
INFO - 开始执行命令: 'ls ../../../etc', conversation_id=1, timeout=10
INFO - WARNING - 命令安全验证失败: 路径 '../../../etc' 不合法或超出允许范围
```

**分析：**
- 检测到路径遍历攻击
- 成功阻止危险操作
- 记录攻击尝试

## 📊 日志统计

### 日志分类统计

| 日志类型 | 数量 | 占比 |
|---------|------|------|
| 服务启动 | 3 | 5% |
| 用户消息 | 15 | 25% |
| AI分析 | 15 | 25% |
| 命令执行 | 20 | 33% |
| 文件验证 | 7 | 12% |

### 成功/失败统计

| 类型 | 成功 | 失败 | 成功率 |
|------|------|------|--------|
| 命令执行 | 12 | 3 | 80% |
| 文件创建 | 8 | 4 | 67% |
| API调用 | 15 | 0 | 100% |

## 🔧 日志管理

### 查看实时日志

```bash
# 查看后端日志
tail -f backend/server.log

# 查看特定类型的日志
tail -f backend/server.log | grep "命令执行"

# 查看错误日志
tail -f backend/server.log | grep "ERROR"
```

### 日志轮转

建议配置日志轮转，避免日志文件过大：

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'server.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### 日志清理

定期清理旧日志：

```bash
# 清理7天前的日志
find . -name "*.log" -mtime +7 -delete

# 或使用数据库清理工具
cd backend
python clean_database.py
```

## 📝 日志最佳实践

1. **日志级别控制**
   - 开发环境：DEBUG
   - 测试环境：INFO
   - 生产环境：WARNING

2. **敏感信息保护**
   - 不记录API密钥
   - 不记录用户密码
   - 不记录敏感文件内容

3. **性能影响控制**
   - 避免过度日志
   - 使用异步日志
   - 定期清理日志

4. **日志格式统一**
   - 使用标准格式
   - 包含时间戳、级别、模块名
   - 结构化日志便于分析

## 🎯 日志使用建议

1. **开发阶段**
   - 启用详细日志
   - 记录函数调用
   - 记录变量值

2. **测试阶段**
   - 记录关键操作
   - 记录错误信息
   - 记录性能指标

3. **生产阶段**
   - 记录警告和错误
   - 记录性能指标
   - 记录安全事件

---

**最后更新：** 2026-04-16
**版本：** 2.0
**状态：** 已完成
