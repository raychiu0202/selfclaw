# Selfclaw - 验证指南

## 📋 验证目标

验证 **Selfclaw AI Agent** 的完整功能，特别是：
1. **AI自动识别用户意图并执行命令**
2. **动态命令执行显示（仿OpenClaw）**
3. **用户无感知的极简体验**
4. **命令执行结果的真实性和准确性**

## 🚀 启动步骤

### 1. 启动后端服务

```bash
cd backend
source venv/bin/activate
python main.py
```

**预期输出：**
```
INFO - terminal - 终端服务初始化，工作目录: /Users/ray/Documents/projects/selfclaw/selfclaw
INFO - Started server process [XXXX]
INFO - Waiting for application startup.
INFO - Application startup complete.
INFO - Uvicorn running on http://0.0.0.0:8000
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

**预期输出：**
```
VITE v8.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 3. 打开浏览器

访问 `http://localhost:5173`

## 🔍 验证场景

### 场景1：AI识别并执行命令（创建文件）

**用户输入：** "帮我在当前目录创建一个test.txt文件"

**预期后端日志输出：**
```
INFO - services - 收到用户消息: conversation_id=1, content='帮我在当前目录创建一个test.txt文件'
INFO - services - AI意图分析结果: {'needs_commands': True, 'commands': ['touch test.txt'], 'explanation': '根据用户请求，需要在指定的工作目录下创建一个名为test.txt的文件。'}
INFO - services - 准备执行命令，命令数量: 1
INFO - services - 准备yield命令开始消息: touch test.txt
INFO - services - 已yield命令开始消息
INFO - services - 执行命令: touch test.txt
INFO - terminal - 开始执行命令: 'touch test.txt', conversation_id=1, timeout=10
INFO - terminal - 命令安全验证通过
INFO - terminal - 命令执行前，当前工作目录: /Users/ray/Documents/projects/selfclaw/selfclaw
INFO - terminal - 命令执行后，工作目录: /Users/ray/Documents/projects/selfclaw/selfclaw
INFO - terminal - 命令执行完成: exit_code=0, success=True, execution_time=0.023s
INFO - terminal - 文件创建验证: test.txt - 存在: True, 路径: /Users/ray/Documents/projects/selfclaw/selfclaw/test.txt
INFO - terminal - 文件信息: 大小=0字节
INFO - services - 准备yield命令成功消息: touch test.txt
INFO - services - 已yield命令成功消息
```

**预期前端显示：**
1. 显示：🔧 正在执行命令: `touch test.txt`
2. 显示：✅ 命令执行成功: `touch test.txt`
3. AI回复：已成功创建文件 test.txt

**验证点：**
- [ ] 动态显示命令开始状态
- [ ] 动态显示命令成功状态
- [ ] 命令状态不会消失
- [ ] 文件确实被创建

### 场景2：列出文件

**用户输入：** "帮我列出当前目录的文件"

**预期后端日志输出：**
```
INFO - services - AI意图分析结果: {'needs_commands': True, 'commands': ['ls -la'], 'explanation': '用户请求查看当前目录的内容，因此使用ls命令列出所有文件。'}
INFO - services - 准备执行命令，命令数量: 1
INFO - services - 准备yield命令开始消息: ls -la
INFO - services - 已yield命令开始消息
INFO - services - 执行命令: ls -la
INFO - terminal - 命令执行后，目录文件数: 22
INFO - terminal - 命令执行完成: exit_code=0, success=True, execution_time=0.045s
INFO - services - 准备yield命令成功消息: ls -la
```

**预期前端显示：**
1. 显示：🔧 正在执行命令: `ls -la`
2. 显示：✅ 命令执行成功: `ls -la`
3. 显示命令输出结果（目录列表）

**验证点：**
- [ ] 动态显示命令执行过程
- [ ] 显示目录列表内容
- [ ] 命令执行结果准确

### 场景3：查看文件内容

**用户输入：** "帮我查看 test.txt 的内容"

**预期后端日志输出：**
```
INFO - services - AI意图分析结果: {'needs_commands': True, 'commands': ['cat test.txt'], 'explanation': '用户请求查看文件内容，使用cat命令读取。'}
```

**预期前端显示：**
1. 显示：🔧 正在执行命令: `cat test.txt`
2. 显示：✅ 命令执行成功: `cat test.txt`
3. 显示文件内容

**验证点：**
- [ ] 命令执行状态正确显示
- [ ] 文件内容正确显示
- [ ] 格式化显示效果良好

### 场景4：写入内容

**用户输入：** "在test.txt中写入'Hello World'"

**预期后端日志输出：**
```
INFO - services - AI意图分析结果: {'needs_commands': True, 'commands': ["echo 'Hello World' > test.txt"], 'explanation': '用户请求在文件中写入内容，使用echo命令重定向。'}
INFO - services - 准备yield命令开始消息: echo 'Hello World' > test.txt
INFO - services - 已yield命令开始消息
INFO - terminal - 文件创建验证: test.txt - 存在: True
INFO - terminal - 文件信息: 大小=11字节
```

**预期前端显示：**
1. 显示：🔧 正在执行命令: `echo 'Hello World' > test.txt`
2. 显示：✅ 命令执行成功
3. AI回复确认操作完成

**验证点：**
- [ ] 命令包含重定向操作符
- [ ] 内容正确写入文件
- [ ] 文件大小正确

### 场景5：删除文件

**用户输入：** "帮我删除 test.txt 文件"

**预期后端日志输出：**
```
INFO - services - AI意图分析结果: {'needs_commands': True, 'commands': ['rm test.txt'], 'explanation': '用户请求删除文件，使用rm命令。'}
```

**预期前端显示：**
1. 显示：🔧 正在执行命令: `rm test.txt`
2. 显示：✅ 命令执行成功
3. AI回复确认删除完成

**验证点：**
- [ ] 文件确实被删除
- [ ] 命令执行状态正确
- [ ] 不会产生幻觉回复

### 场景6：错误处理（安全验证失败）

**用户输入：** "删除 /etc/passwd 文件"

**预期后端日志输出：**
```
INFO - terminal - WARNING - 命令安全验证失败: 路径 '/etc/passwd' 不合法或超出允许范围
INFO - services - 准备yield命令失败消息: rm /etc/passwd
```

**预期前端显示：**
1. 显示：🔧 正在执行命令: `rm /etc/passwd`
2. 显示：❌ 命令执行失败: `rm /etc/passwd`
3. 显示错误信息：路径不合法或超出允许范围

**验证点：**
- [ ] 命令被安全验证拒绝
- [ ] 错误信息清晰明确
- [ ] 不会执行危险操作

## ✅ 验证检查清单

### AI 意图识别
- [ ] AI 能识别"创建文件" → `touch` 命令
- [ ] AI 能识别"列出文件" → `ls` 命令
- [ ] AI 能识别"查看文件" → `cat` 命令
- [ ] AI 能识别"搜索" → `grep` 命令
- [ ] AI 能识别"删除文件" → `rm` 命令
- [ ] AI 能识别"写入内容" → `echo` 命令

### 动态命令执行显示
- [ ] 命令开始状态正确显示（🔧）
- [ ] 命令成功状态正确显示（✅）
- [ ] 命令失败状态正确显示（❌）
- [ ] 命令内容清晰可见
- [ ] 执行结果/错误信息正确显示
- [ ] 命令状态不会在对话完成后消失

### 命令执行
- [ ] 命令格式正确
- [ ] 命令被正确提取
- [ ] 命令安全验证通过
- [ ] 命令执行成功
- [ ] 执行结果正确捕获
- [ ] 文件创建验证通过

### 结果融合
- [ ] 命令输出正确显示
- [ ] 命令结果融入 AI 回复
- [ ] 页面正确显示最终回复
- [ ] 代码块格式正确
- [ ] 没有 undefined 等异常内容

### 日志记录
- [ ] 后端日志正常输出
- [ ] 命令执行历史保存
- [ ] 错误信息正确记录
- [ ] 文件创建验证记录

### 安全机制
- [ ] 危险命令被拒绝执行
- [ ] 路径遍历攻击被阻止
- [ ] 绝对路径处理正确
- [ ] 命令超时机制有效

## 📊 关键日志信息

### 成功标志
- `AI意图分析结果` - AI 识别成功
- `准备执行命令，命令数量: N` - 命令识别成功
- `准备yield命令开始消息` - 开始推送状态
- `已yield命令开始消息` - 状态推送成功
- `命令安全验证通过` - 安全检查通过
- `命令执行完成` - 命令执行成功
- `文件创建验证: xxx - 存在: True` - 文件创建成功
- `命令执行成功` - 结果处理成功
- `最终回复保存成功` - 整个流程完成

### 失败标志
- `命令安全验证失败` - 命令不在白名单
- `路径不合法或超出允许范围` - 路径验证失败
- `命令执行超时` - 命令执行超时
- `命令执行失败` - 命令执行错误

### 调试信息
- `命令执行前，当前工作目录` - 执行前状态
- `命令执行前，目录内容` - 目录内容快照
- `命令执行后，目录文件数` - 执行后状态
- `文件创建验证: xxx - 存在: True/False` - 文件验证结果
- `文件信息: 大小=XX字节` - 文件详情

## 🔧 调试技巧

### 查看后端日志
启动后端后，日志会直接输出到控制台，包括：
- 用户消息接收
- AI 意图分析结果
- 命令识别和提取
- 命令执行过程和结果
- 文件创建验证
- 错误信息

### 常见问题排查

1. **没有看到命令执行日志**
   - 检查 AI 是否返回了 `needs_commands: true`
   - 查看原始 AI 意图分析结果
   - 检查 GLM API 调用是否成功

2. **命令安全验证失败**
   - 检查命令是否在白名单中
   - 检查命令参数是否合法
   - 检查路径是否在允许范围内

3. **命令执行超时**
   - 增加超时时间或优化命令执行速度
   - 检查命令是否卡在某个操作

4. **文件创建显示成功但实际不存在**
   - 检查工作目录设置是否正确
   - 检查文件创建验证日志
   - 验证文件是否在其他位置创建

5. **出现 undefined 等异常内容**
   - 检查前端 JSON 解析是否正确
   - 检查后端内容过滤机制
   - 查看浏览器控制台错误信息

## 📝 测试建议

1. **从简单的命令开始**（`ls`, `pwd`）
2. **逐步测试更复杂的命令**（`grep`, `find`）
3. **测试动态命令显示**（观察状态变化）
4. **测试错误场景**（不存在的文件、无效命令、危险操作）
5. **验证文件创建**（确认文件真实存在）
6. **测试连续操作**（创建、写入、查看、删除）
7. **记录每次测试的日志输出**
8. **对比预期结果和实际结果**

## 🎯 验证标准

### 功能完整性
- [ ] 所有计划的功能都已实现
- [ ] 所有命令类型都能正常工作
- [ ] 动态命令执行显示正常

### 准确性
- [ ] 命令执行结果准确无误
- [ ] 文件操作真实有效
- [ ] 没有幻觉回复

### 用户体验
- [ ] 命令执行过程清晰可见
- [ ] 状态反馈及时准确
- [ ] 错误提示友好明确
- [ ] 界面响应流畅自然

### 安全性
- [ ] 危险命令被正确拒绝
- [ ] 路径遍历被有效阻止
- [ ] 超时机制正常工作
- [ ] 没有安全漏洞

### 稳定性
- [ ] 系统运行稳定可靠
- [ ] 没有内存泄漏
- [ ] 没有死锁或卡死
- [ ] 错误处理完善

## 📈 验证结果记录

### 测试日期：2026-04-16

| 测试场景 | 测试结果 | 状态 | 备注 |
|---------|---------|------|------|
| 创建文件 | ✅ 成功 | 已修复 | 动态显示正常 |
| 列出文件 | ✅ 成功 | 正常 | 结果准确 |
| 查看文件 | ✅ 成功 | 正常 | 内容正确 |
| 写入内容 | ✅ 成功 | 已修复 | 重定向正常 |
| 删除文件 | ✅ 成功 | 正常 | 操作有效 |
| 搜索内容 | ✅ 成功 | 正常 | 结果正确 |
| 动态显示 | ✅ 成功 | 已实现 | 仿OpenClaw |
| 错误处理 | ✅ 成功 | 已修复 | 提示明确 |
| 安全验证 | ✅ 成功 | 正常 | 拒绝危险操作 |

### 总体评估：**✅ 验证通过，系统可以投入使用**

---

**最后更新：** 2026-04-16
**版本：** 2.0
**状态：** 已完成
