"""
终端命令安全模块
实现命令白名单验证、参数检查、路径防护等安全机制
"""
import os
import re
from typing import Optional, List
from pathlib import Path


class CommandSecurity:
    """命令安全检查器"""

    # 允许执行的命令白名单
    ALLOWED_COMMANDS = {
        # 只读命令
        'ls': ['-la', '-l', '-h', '-a', '-al'],
        'pwd': [],
        'cat': [],
        'grep': ['-n', '-i', '-v', '-r', '-e'],
        'head': ['-n'],
        'tail': ['-n'],
        'wc': ['-l', '-w', '-c'],
        'date': [],
        # 写操作命令（严格限制）
        'touch': [],
        'mkdir': ['-p'],
        'echo': [],
        'rm': ['-r'],
        'mv': [],
        'find': ['-name', '-type', '-maxdepth']
    }

    # 禁止的命令模式
    FORBIDDEN_PATTERNS = [
        r'^\s*rm\s+',           # 删除命令
        r'^\s*rmdir\s+',        # 删除目录
        r'^\s*del\s+',          # 删除（Windows）
        r'^\s*mv\s+',           # 移动
        r'^\s*cp\s+',           # 复制
        r'^\s*chmod\s+',        # 修改权限
        r'^\s*chown\s+',        # 修改所有者
        r'^\s*sudo\s+',         # 权限提升
        r'^\s*su\s+',           # 切换用户
        r'^\s*curl\s+',         # 网络请求
        r'^\s*wget\s+',         # 网络请求
        r'^\s*nc\s+',           # Netcat
        r'^\s*telnet\s+',       # 远程登录
        r'^\s*ssh\s+',          # SSH连接
        r'^\s*\.\/',            # 执行本地脚本
        r'>>',                  # 追加重定向
        r'\|',                  # 管道
        r'&\s*$',               # 后台运行
        r';\s*$',               # 命令分隔
        r'&&',                  # 条件执行
        r'\|\|',                # 条件执行
        r'\$\(',                # 命令替换
        r'`',                   # 命令替换
    ]

    # 允许的工作目录
    ALLOWED_BASE_DIR = Path(__file__).parent.parent.absolute()

    @classmethod
    def validate_command(cls, command: str) -> tuple[bool, Optional[str]]:
        """
        验证命令是否安全

        Args:
            command: 用户输入的命令

        Returns:
            (是否安全, 错误信息)
        """
        if not command or not command.strip():
            return False, "命令不能为空"

        command = command.strip()

        # 检查禁止的模式
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, command):
                return False, f"命令包含禁止的操作符或关键字: {pattern}"

        # 解析命令
        parts = command.split()
        if not parts:
            return False, "无效的命令格式"

        cmd = parts[0]

        # 检查命令是否在白名单中
        if cmd not in cls.ALLOWED_COMMANDS:
            return False, f"命令 '{cmd}' 不在允许的命令列表中"

        # 特殊处理 echo 命令的重定向
        if cmd == 'echo':
            # 检查是否包含重定向操作
            if '>' in command:
                # 只允许简单的 echo "内容" > 文件名 格式
                # 检查重定向后的文件名是否合法
                try:
                    # 找到 > 符号后的文件名
                    redirect_parts = command.split('>')
                    if len(redirect_parts) == 2:
                        filename = redirect_parts[1].strip()
                        if not cls._validate_path(filename):
                            return False, f"echo重定向的文件路径不合法: {filename}"
                        else:
                            return True, None  # 路径验证成功
                    else:
                        return False, "echo命令只允许单个重定向操作"
                except Exception:
                    return False, "echo重定向格式错误"
            return True, None

        # 检查参数
        allowed_params = cls.ALLOWED_COMMANDS[cmd]
        if allowed_params:
            # 检查参数是否合法
            for part in parts[1:]:
                if part.startswith('-'):
                    # 这是一个参数
                    param_name = part
                    # 允许无值参数或有值参数
                    if param_name not in allowed_params:
                        return False, f"参数 '{param_name}' 不被允许"
                else:
                    # 这是一个值（如文件名）
                    if not cls._validate_path(part):
                        return False, f"路径 '{part}' 不合法或超出允许范围"

        return True, None

    @classmethod
    def _validate_path(cls, path: str) -> bool:
        """
        验证路径是否在允许范围内

        Args:
            path: 要验证的路径

        Returns:
            是否合法
        """
        # 检查路径遍历
        if '..' in path or '~' in path:
            return False

        # 如果是绝对路径
        if path.startswith('/'):
            try:
                # 验证绝对路径是否在允许的目录内
                abs_path = Path(path).resolve()
                # 检查是否在允许的目录内
                try:
                    abs_path.relative_to(cls.ALLOWED_BASE_DIR)
                    return True  # 绝对路径在允许范围内
                except ValueError:
                    return False  # 绝对路径超出允许范围
            except Exception:
                return False

        # 相对路径，转换为绝对路径检查
        try:
            abs_path = (cls.ALLOWED_BASE_DIR / path).resolve()
            # 检查是否在允许的目录内
            try:
                abs_path.relative_to(cls.ALLOWED_BASE_DIR)
                return True
            except ValueError:
                return False
        except Exception:
            return False

    @classmethod
    def get_allowed_commands(cls) -> List[str]:
        """获取所有允许的命令"""
        return list(cls.ALLOWED_COMMANDS.keys())

    @classmethod
    def get_command_help(cls, command: str) -> Optional[str]:
        """获取命令帮助信息"""
        if command not in cls.ALLOWED_COMMANDS:
            return None

        params = cls.ALLOWED_COMMANDS[command]
        if params:
            return f"{command} - 允许的参数: {', '.join(params)}"
        else:
            return f"{command} - 无需参数"
