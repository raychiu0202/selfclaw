"""
终端命令执行模块
安全地执行白名单命令并捕获输出
"""
import subprocess
import asyncio
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from database import get_db
from models import CommandHistory
from security import CommandSecurity

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TerminalService:
    """终端命令执行服务"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.absolute()
        logger.info(f"终端服务初始化，工作目录: {self.base_dir}")

    async def execute_command(
        self,
        command: str,
        conversation_id: int,
        timeout: int = 30
    ) -> dict:
        """
        执行命令并返回结果

        Args:
            command: 要执行的命令
            conversation_id: 会话ID
            timeout: 超时时间（秒）

        Returns:
            执行结果字典
        """
        logger.info(f"开始执行命令: '{command}', conversation_id: {conversation_id}, timeout: {timeout}")

        # 验证命令安全性
        is_safe, error_msg = CommandSecurity.validate_command(command)
        if not is_safe:
            logger.warning(f"命令安全验证失败: {error_msg}")
            return {
                "success": False,
                "command": command,
                "output": None,
                "error": f"安全检查失败: {error_msg}",
                "exit_code": -1,
                "execution_time": 0,
                "timestamp": datetime.utcnow()
            }

        logger.info("命令安全验证通过")

        # 记录开始时间
        start_time = time.time()

        try:
            # 记录执行前的目录
            logger.info(f"命令执行前，当前工作目录: {self.base_dir}")
            logger.info(f"命令执行前，目录内容: {list(self.base_dir.iterdir())[:10]}")

            # 执行命令
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.base_dir)
            )

            # 等待命令完成，设置超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "command": command,
                    "output": None,
                    "error": f"命令执行超时（{timeout}秒）",
                    "exit_code": -1,
                    "execution_time": timeout,
                    "timestamp": datetime.utcnow()
                }

            # 计算执行时间
            execution_time = time.time() - start_time

            # 获取输出
            output = stdout.decode('utf-8', errors='ignore').strip()
            error = stderr.decode('utf-8', errors='ignore').strip()
            exit_code = process.returncode

            # 限制输出长度
            max_output_length = 10000
            if len(output) > max_output_length:
                output = output[:max_output_length] + f"\n... (输出已截断，共 {len(output)} 字符)"

            if len(error) > max_output_length:
                error = error[:max_output_length] + f"\n... (错误已截断，共 {len(error)} 字符)"

            # 判断是否成功
            success = exit_code == 0

            # 记录执行后的目录信息（用于验证文件是否真的被创建）
            after_dir_contents = list(self.base_dir.iterdir())
            logger.info(f"命令执行后，工作目录: {self.base_dir}")
            logger.info(f"命令执行后，目录文件数: {len(after_dir_contents)}")
            logger.info(f"命令执行完成: exit_code={exit_code}, success={success}, execution_time={execution_time:.3f}s")

            if output:
                logger.info(f"命令输出: {output[:100]}...")  # 只记录前100个字符
            if error:
                logger.warning(f"命令错误输出: {error[:100]}...")  # 只记录前100个字符

            # 对于文件创建命令，添加额外的验证日志
            if 'touch' in command or 'echo' in command and '>' in command:
                # 提取可能的文件名
                import re
                touch_match = re.search(r'touch\s+(\S+)', command)
                echo_match = re.search(r'echo[^>]*>\s*(\S+)', command)

                filename = None
                if touch_match:
                    filename = touch_match.group(1)
                elif echo_match:
                    filename = echo_match.group(1)

                if filename:
                    file_path = self.base_dir / filename
                    file_exists = file_path.exists()
                    logger.info(f"文件创建验证: {filename} - 存在: {file_exists}, 路径: {file_path}")
                    if file_exists:
                        file_size = file_path.stat().st_size
                        logger.info(f"文件信息: 大小={file_size}字节")
                    else:
                        logger.warning(f"警告: 命令显示成功但文件不存在！")

            # 保存执行历史
            await self._save_history(
                conversation_id=conversation_id,
                command=command,
                output=output,
                error=error,
                exit_code=exit_code,
                execution_time=execution_time
            )

            logger.info("命令执行历史保存成功")

            return {
                "success": success,
                "command": command,
                "output": output if output else None,
                "error": error if error else None,
                "exit_code": exit_code,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "command": command,
                "output": None,
                "error": f"执行错误: {str(e)}",
                "exit_code": -1,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow()
            }

    async def _save_history(
        self,
        conversation_id: int,
        command: str,
        output: Optional[str],
        error: Optional[str],
        exit_code: int,
        execution_time: float
    ):
        """保存命令执行历史"""
        try:
            db = next(get_db())
            history = CommandHistory(
                conversation_id=conversation_id,
                command=command,
                output=output,
                error=error,
                exit_code=exit_code,
                execution_time=execution_time
            )
            db.add(history)
            db.commit()
            logger.info("命令执行历史保存到数据库成功")
        except Exception as e:
            logger.error(f"保存命令历史失败: {e}")
        finally:
            try:
                db.close()
            except:
                pass

    def get_history(self, conversation_id: int, limit: int = 10) -> list[dict]:
        """获取命令执行历史"""
        try:
            db = next(get_db())
            history = db.query(CommandHistory)\
                .filter(CommandHistory.conversation_id == conversation_id)\
                .order_by(CommandHistory.created_at.desc())\
                .limit(limit)\
                .all()

            return [
                {
                    "id": h.id,
                    "command": h.command,
                    "output": h.output,
                    "error": h.error,
                    "exit_code": h.exit_code,
                    "execution_time": h.execution_time,
                    "created_at": h.created_at
                }
                for h in history
            ]
        except Exception as e:
            print(f"获取命令历史失败: {e}")
            return []
        finally:
            try:
                db.close()
            except:
                pass
