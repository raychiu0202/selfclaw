from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import Conversation, Message
from schemas import ConversationCreate, ConversationResponse, ConversationListResponse, MessageResponse
from typing import Generator, Optional
import httpx
import os
from dotenv import load_dotenv
import json
import logging
from terminal import TerminalService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


class ConversationService:
    """会话服务"""

    def __init__(self):
        pass

    def create_conversation(self, title: str) -> ConversationResponse:
        """创建新会话"""
        db = SessionLocal()
        try:
            conversation = Conversation(title=title)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return ConversationResponse.model_validate(conversation)
        finally:
            db.close()

    def get_all_conversations(self) -> ConversationListResponse:
        """获取所有会话"""
        db = SessionLocal()
        try:
            conversations = db.query(Conversation).order_by(
                Conversation.updated_at.desc()
            ).all()
            return ConversationListResponse(
                conversations=[ConversationResponse.model_validate(c) for c in conversations],
                total=len(conversations)
            )
        finally:
            db.close()

    def get_conversation(self, conversation_id: int) -> Optional[ConversationResponse]:
        """获取单个会话"""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if not conversation:
                return None
            return ConversationResponse.model_validate(conversation)
        finally:
            db.close()

    def delete_conversation(self, conversation_id: int) -> bool:
        """删除会话"""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if not conversation:
                return False
            db.delete(conversation)
            db.commit()
            return True
        finally:
            db.close()

    def update_conversation(self, conversation_id: int, title: str) -> Optional[ConversationResponse]:
        """更新会话标题"""
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if not conversation:
                return None
            conversation.title = title
            db.commit()
            db.refresh(conversation)
            return ConversationResponse.model_validate(conversation)
        finally:
            db.close()

    def get_messages(self, conversation_id: int) -> list[MessageResponse]:
        """获取会话的所有消息"""
        db = SessionLocal()
        try:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()
            return [MessageResponse.model_validate(m) for m in messages]
        finally:
            db.close()

    def save_message(self, conversation_id: int, role: str, content: str) -> MessageResponse:
        """保存消息"""
        db = SessionLocal()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # 更新会话的updated_at
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                from datetime import datetime
                conversation.updated_at = datetime.utcnow()
                db.commit()

            return MessageResponse.model_validate(message)
        finally:
            db.close()


class ChatService:
    """聊天服务"""

    def __init__(self):
        self.conversation_service = ConversationService()
        self.terminal_service = TerminalService()

    def get_conversation_history(self, conversation_id: int) -> list[dict]:
        """获取对话历史"""
        messages = self.conversation_service.get_messages(conversation_id)
        return [{"role": m.role, "content": m.content} for m in messages]

    def _get_system_prompt(self) -> str:
        """获取系统提示词，包含命令执行指令"""
        return """你是一个AI助手，可以帮助用户回答问题和执行终端命令。

你能够直接理解用户的意图并执行相应的文件操作，包括：
- 创建文件/目录
- 查看文件/目录
- 删除文件/目录
- 列出文件列表
- 搜索文件内容

重要规则：
1. 工作目录是：/Users/ray/Documents/projects/selfclaw/selfclaw
2. 你只能操作工作目录及其子目录下的文件
3. 如果用户询问其他目录（如 /Users/ray/Documents/projects），请明确告知你只能访问当前工作目录
4. 当用户说"看下当前目录"或"列出文件"时，执行 ls -la 命令
5. 当执行了文件操作命令后，你的回复必须包含以下信息：
   - 执行了什么操作（创建文件/删除文件/列出文件等）
   - 操作的目标（文件名/目录名等）
   - 操作的结果（成功/失败及详细信息）

示例：
- 创建文件："已成功创建文件 test.md"
- 列出文件："当前工作目录 /Users/ray/Documents/projects/selfclaw/selfclaw 的文件列表如下：\n```\n文件1.md\n文件2.txt\n```"
- 查看文件："文件 test.md 的内容如下：\n```\n文件内容\n```"
- 用户询问其他目录："抱歉，我只能访问当前工作目录 /Users/ray/Documents/projects/selfclaw/selfclaw 及其子目录。您可以指定工作目录内的文件或子目录。"

如果用户只是问问题或聊天，不需要执行命令，直接回答即可。"""

    async def _analyze_and_execute_commands(self, user_content: str, conversation_id: int) -> list[dict]:
        """使用AI语义理解来分析用户意图，并自动执行相应的命令"""
        intent_prompt = f"""你是一个智能系统，负责分析用户的自然语言请求，理解他们的真实意图，并生成要执行的终端命令。

用户请求：{user_content}

重要规则（必须严格遵守）：
1. 工作目录是：/Users/ray/Documents/projects/selfclaw/selfclaw
2. **只能使用相对路径，绝对禁止使用绝对路径**
3. **绝对禁止在命令中使用 / 开头的路径**
4. 不要使用 cd 命令，因为命令已经在正确的工作目录中执行
5. 所有文件名都应该是简单的相对路径，如：test.md, filename.txt, data/

请分析用户的请求，如果需要执行文件操作，生成相应的命令。可用命令包括：
- 创建文件：echo "内容" > filename 或 touch filename
- 创建目录：mkdir dirname
- 列出文件：ls -la
- 查看文件内容：cat filename
- 删除文件：rm filename
- 搜索内容：grep keyword filename

示例：
❌ 错误：echo "Hello" > /Users/ray/Documents/projects/selfclaw/selfclaw/test.txt
✅ 正确：echo "Hello" > test.txt

❌ 错误：touch /absolute/path/to/file.txt
✅ 正确：touch file.txt

以JSON格式返回结果：
{{
    "needs_commands": true/false,
    "commands": ["命令1", "命令2"],
    "explanation": "你的理解"
}}

如果用户只是问问题或聊天，不需要执行命令，返回 needs_commands: false。
只返回JSON，不要有其他内容。"""

        try:
            headers = {
                "Authorization": f"Bearer {GLM_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": os.getenv("GLM_MODEL", "glm-4-flash"),
                "messages": [{"role": "user", "content": intent_prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GLM_API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    ai_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                    try:
                        # 提取JSON
                        import re
                        json_match = re.search(r'\{.*?\}', ai_content, re.DOTALL)
                        if json_match:
                            intent_result = json.loads(json_match.group())
                            logger.info(f"AI意图分析结果: {intent_result}")

                            if intent_result.get('needs_commands'):
                                commands = intent_result.get('commands', [])
                                results = []
                                for cmd in commands:
                                    try:
                                        logger.info(f"执行命令: {cmd}")
                                        result = await self.terminal_service.execute_command(
                                            command=cmd.strip(),
                                            conversation_id=conversation_id,
                                            timeout=10
                                        )
                                        results.append(result)
                                    except Exception as e:
                                        logger.error(f"命令执行异常: {str(e)}")
                                        results.append({
                                            "success": False,
                                            "command": cmd,
                                            "error": str(e)
                                        })
                                return results
                    except json.JSONDecodeError as e:
                        logger.warning(f"无法解析AI意图分析结果: {e}, 内容: {ai_content}")

        except Exception as e:
            logger.error(f"AI意图分析失败: {str(e)}")

        return []

    async def stream_chat(self, message_data):
        """流式调用GLM API"""
        conversation_id = message_data.conversation_id
        user_content = message_data.content

        logger.info(f"收到用户消息: conversation_id={conversation_id}, content='{user_content}'")

        # 保存用户消息
        self.conversation_service.save_message(conversation_id, "user", user_content)

        # 首先分析意图，获取要执行的命令
        intent_prompt = f"""你是一个智能系统，负责分析用户的自然语言请求，理解他们的真实意图，并生成要执行的终端命令。

用户请求：{user_content}

重要规则（必须严格遵守）：
1. 工作目录是：/Users/ray/Documents/projects/selfclaw/selfclaw
2. 用户想要"看下目录"、"查看文件"、"列出文件"时，应该执行 ls -la 命令
3. 即使提到其他路径（如 /Users/ray/Documents/projects），也只执行查看当前目录的命令
4. **只能使用相对路径，绝对禁止使用绝对路径**
5. **绝对禁止在命令中使用 / 开头的路径**
6. 不要使用 cd 命令，因为命令已经在正确的工作目录中执行
7. 所有文件名都应该是简单的相对路径，如：test.md, filename.txt, data/

请分析用户的请求，如果需要执行文件操作，生成相应的命令。可用命令包括：
- 创建文件：echo "内容" > filename 或 touch filename
- 创建目录：mkdir dirname
- 列出文件：ls -la
- 查看文件内容：cat filename
- 删除文件：rm filename
- 搜索内容：grep keyword filename

示例：
用户请求："看下/Users/ray/Documents/projects目录下有哪些文件？"
正确理解：用户想查看目录内容，应该列出当前工作目录
正确命令：["ls -la"]

用户请求："创建一个test.txt文件"
正确命令：["touch test.txt"]

❌ 错误：echo "Hello" > /Users/ray/Documents/projects/selfclaw/selfclaw/test.txt
✅ 正确：echo "Hello" > test.txt

❌ 错误：touch /absolute/path/to/file.txt
✅ 正确：touch file.txt

以JSON格式返回结果：
{{
    "needs_commands": true/false,
    "commands": ["命令1", "命令2"],
    "explanation": "你的理解"
}}

如果用户只是问问题或聊天，不需要执行命令，返回 needs_commands: false。
只返回JSON，不要有其他内容。"""

        # 获取要执行的命令
        commands_to_execute = []
        try:
            headers = {
                "Authorization": f"Bearer {GLM_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": os.getenv("GLM_MODEL", "glm-4-flash"),
                "messages": [{"role": "user", "content": intent_prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(GLM_API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    ai_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                    try:
                        import re
                        json_match = re.search(r'\{.*?\}', ai_content, re.DOTALL)
                        if json_match:
                            intent_result = json.loads(json_match.group())
                            logger.info(f"AI意图分析结果: {intent_result}")
                            if intent_result.get('needs_commands'):
                                commands_to_execute = intent_result.get('commands', [])
                    except json.JSONDecodeError as e:
                        logger.warning(f"无法解析AI意图分析结果: {e}, 内容: {ai_content}")
        except Exception as e:
            logger.error(f"AI意图分析失败: {str(e)}")

        # 执行命令并实时发送状态
        command_results = []
        logger.info(f"准备执行命令，命令数量: {len(commands_to_execute)}")
        for i, cmd in enumerate(commands_to_execute):
            try:
                logger.info(f"准备yield命令开始消息: {cmd.strip()}")
                # 发送正在执行的命令
                yield f"data: {json.dumps({'type': 'command_start', 'command': cmd.strip(), 'message': f'🔧 正在执行命令: `{cmd.strip()}`'}, ensure_ascii=False)}\n\n"
                logger.info(f"已yield命令开始消息")

                logger.info(f"执行命令: {cmd}")
                result = await self.terminal_service.execute_command(
                    command=cmd.strip(),
                    conversation_id=conversation_id,
                    timeout=10
                )
                command_results.append(result)

                # 发送命令执行结果
                if result.get('success'):
                    output = result.get('output', '无输出')
                    logger.info(f"准备yield命令成功消息: {cmd.strip()}")
                    yield f"data: {json.dumps({'type': 'command_success', 'command': cmd.strip(), 'output': output, 'message': f'✅ 命令执行成功: `{cmd.strip()}`'}, ensure_ascii=False)}\n\n"
                    logger.info(f"已yield命令成功消息")
                else:
                    error = result.get('error', '未知错误')
                    logger.info(f"准备yield命令失败消息: {cmd.strip()}")
                    yield f"data: {json.dumps({'type': 'command_error', 'command': cmd.strip(), 'error': error, 'message': f'❌ 命令执行失败: `{cmd.strip()}` - {error}'}, ensure_ascii=False)}\n\n"
                    logger.info(f"已yield命令失败消息")

            except Exception as e:
                logger.error(f"命令执行异常: {str(e)}")
                command_results.append({
                    "success": False,
                    "command": cmd,
                    "error": str(e)
                })
                # 发送命令执行异常
                yield f"data: {json.dumps({'type': 'command_error', 'command': cmd.strip(), 'error': str(e), 'message': f'❌ 命令执行异常: `{cmd.strip()}` - {str(e)}'}, ensure_ascii=False)}\n\n"

        # 获取对话历史
        history = self.get_conversation_history(conversation_id)
        logger.info(f"对话历史长度: {len(history)}")

        # 构建系统提示词，包含命令执行结果
        system_prompt = self._get_system_prompt()
        if command_results:
            # 如果有命令执行结果，添加到系统提示词中
            system_prompt += "\n\n已自动执行以下操作，结果如下：\n"
            for i, result in enumerate(command_results, 1):
                if result.get('success'):
                    output = result.get('output', '无输出')
                    system_prompt += f"{i}. 执行命令: {result.get('command')}\n结果: {output}\n"
                else:
                    error = result.get('error', '未知错误')
                    system_prompt += f"{i}. 执行命令: {result.get('command')}\n失败: {error}\n"
            system_prompt += "\n请根据执行结果给用户友好的回复，告诉他们操作已完成或失败了。"

        # 添加系统提示词
        messages_with_system = [
            {"role": "system", "content": system_prompt},
            *history
        ]

        logger.info(f"准备调用GLM API，消息数量: {len(messages_with_system)}")

        # 调用GLM API
        headers = {
            "Authorization": f"Bearer {GLM_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": os.getenv("GLM_MODEL", "glm-5"),
            "messages": messages_with_system,
            "stream": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096
        }

        assistant_content = ""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", GLM_API_URL, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield f"data: {json.dumps({'error': f'API调用失败: {error_text.decode()}'}, ensure_ascii=False)}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 移除 "data: " 前缀
                            if data_str == "[DONE]":
                                logger.info(f"GLM API流式传输完成，原始内容长度: {len(assistant_content)}")
                                logger.info(f"保存最终回复到数据库，内容长度: {len(assistant_content)}")
                                # 保存最终回复
                                self.conversation_service.save_message(conversation_id, "assistant", assistant_content)
                                logger.info("最终回复保存成功")

                                yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
                                logger.info("对话流程完成")
                                break

                            try:
                                data = json.loads(data_str)
                                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    # 过滤掉可能的控制字符或异常字符
                                    if content.strip() and len(content.strip()) > 0:
                                        assistant_content += content
                                        # 流式输出原始内容
                                        yield f"data: {json.dumps({'content': content, 'done': False}, ensure_ascii=False)}\n\n"
                            except json.JSONDecodeError:
                                logger.warning(f"JSON解析失败，跳过该行: {data_str[:100]}")
                                continue

        except Exception as e:
            yield f"data: {json.dumps({'error': f'发生错误: {str(e)}'}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"


# 导出服务实例
conversation_service = ConversationService()
chat_service = ChatService()
