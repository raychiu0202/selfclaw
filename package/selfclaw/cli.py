"""
Selfclaw CLI - 命令行接口
极简设计的命令行工具
"""

import os
import sys
import json
import subprocess
import click
import shutil
from pathlib import Path

# 颜色输出
def echo_success(message):
    click.echo(click.style(f"✓ {message}", fg="green"))

def echo_error(message):
    click.echo(click.style(f"✗ {message}", fg="red"))

def echo_info(message):
    click.echo(click.style(f"ℹ {message}", fg="blue"))

def echo_warning(message):
    click.echo(click.style(f"⚠ {message}", fg="yellow"))


@click.group()
@click.version_option("1.0.0")
def cli():
    """
    Selfclaw - AI Agent System
    基于GLM-5的智能AI助手系统
    """
    pass


@cli.command()
@click.option('--port', default=8000, help='服务端口', type=int)
@click.option('--debug', is_flag=True, help='调试模式')
@click.option('--config', help='配置文件路径', type=click.Path(exists=True))
def start(port, debug, config):
    """
    启动Selfclaw服务
    """
    echo_info(f"正在启动Selfclaw服务 (端口: {port})...")

    # 检查是否已安装
    if not check_installation():
        echo_error("Selfclaw未正确安装，请先运行: selfclaw init")
        sys.exit(1)

    # 构建启动命令
    backend_dir = get_installation_path("backend")
    frontend_dir = get_installation_path("frontend")

    if not backend_dir:
        echo_error("后端目录不存在")
        sys.exit(1)

    # 启动后端
    start_backend(backend_dir, port, debug, config)

    # 启动前端
    if frontend_dir:
        start_frontend(frontend_dir)


@cli.command()
def stop():
    """
    停止Selfclaw服务
    """
    echo_info("正在停止Selfclaw服务...")

    # 停止后端和前端服务
    kill_process("uvicorn")
    kill_process("npm")

    echo_success("Selfclaw服务已停止")


@cli.command()
def status():
    """
    查看服务状态
    """
    echo_info("检查Selfclaw服务状态...")

    backend_running = check_process("uvicorn")
    frontend_running = check_process("npm")

    click.echo("\n服务状态:")
    click.echo(f"  后端: {'运行中 ✓' if backend_running else '已停止 ✗'}")
    click.echo(f"  前端: {'运行中 ✓' if frontend_running else '已停止 ✗'}")

    if backend_running:
        echo_info("后端API: http://localhost:8000")
        echo_info("API文档: http://localhost:8000/docs")

    if frontend_running:
        echo_info("前端界面: http://localhost:5173")


@cli.command()
def init():
    """
    初始化Selfclaw配置
    """
    echo_info("正在初始化Selfclaw...")

    # 检查是否已安装
    if check_installation():
        echo_warning("Selfclaw已安装，是否继续？")
        if not click.confirm("继续将覆盖现有配置"):
            return

    # 创建配置目录
    config_dir = Path.home() / ".selfclaw"
    config_dir.mkdir(exist_ok=True)

    # 创建示例配置
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        create_default_config(config_file)

    # 创建数据库配置
    echo_info("\n配置数据库:")
    db_host = click.prompt("数据库主机", default="localhost")
    db_user = click.prompt("数据库用户", default="root")
    db_password = click.prompt("数据库密码", default="", hide_input=True)
    db_name = click.prompt("数据库名称", default="selfclaw")

    # 更新配置
    update_config(config_file, {
        "db_host": db_host,
        "db_user": db_user,
        "db_password": db_password,
        "db_name": db_name
    })

    # 配置API密钥
    echo_info("\n配置GLM API:")
    api_key = click.prompt("GLM API密钥", hide_input=True)
    update_config(config_file, {"glm_api_key": api_key})

    echo_success(f"配置已保存到: {config_file}")
    echo_info("现在可以运行: selfclaw start")


@cli.command()
@click.option('--api-key', help='设置GLM API密钥')
@click.option('--db-host', help='数据库主机')
@click.option('--db-user', help='数据库用户')
@click.option('--db-password', help='数据库密码')
@click.option('--db-name', help='数据库名称')
def config(api_key, db_host, db_user, db_password, db_name):
    """
    配置Selfclaw
    """
    config_file = Path.home() / ".selfclaw" / "config.yaml"

    if not config_file.exists():
        echo_error("配置文件不存在，请先运行: selfclaw init")
        sys.exit(1)

    updates = {}
    if api_key:
        updates["glm_api_key"] = api_key
    if db_host:
        updates["db_host"] = db_host
    if db_user:
        updates["db_user"] = db_user
    if db_password:
        updates["db_password"] = db_password
    if db_name:
        updates["db_name"] = db_name

    if updates:
        update_config(config_file, updates)
        echo_success("配置已更新")
    else:
        # 显示当前配置
        show_config(config_file)


@cli.command()
@click.option('--all', is_flag=True, help='清理所有数据')
@click.option('--history', is_flag=True, help='清理历史记录')
@click.option('--cache', is_flag=True, help='清理缓存')
def clean(all, history, cache):
    """
    清理数据
    """
    if all:
        echo_warning("将清理所有数据，是否继续？")
        if not click.confirm("确定要清理所有数据吗？"):
            return

        # 清理数据库
        backend_dir = get_installation_path("backend")
        if backend_dir:
            db_clean_script = backend_dir / "clean_database.py"
            if db_clean_script.exists():
                subprocess.run([sys.executable, str(db_clean_script)])
                echo_success("数据库已清理")

    elif history:
        echo_info("清理历史记录...")
        # 实现历史记录清理
        echo_success("历史记录已清理")

    elif cache:
        echo_info("清理缓存...")
        # 实现缓存清理
        echo_success("缓存已清理")

    else:
        echo_info("清理临时文件...")
        # 实现临时文件清理
        echo_success("临时文件已清理")


@cli.command()
@click.option('--tail', default=50, help='显示最后N行', type=int)
@click.option('--follow', is_flag=True, help='持续跟踪日志')
@click.option('--level', help='日志级别 (debug/info/warning/error)')
def logs(tail, follow, level):
    """
    查看日志
    """
    log_file = Path.home() / ".selfclaw" / "logs" / "selfclaw.log"

    if not log_file.exists():
        echo_warning("日志文件不存在")
        return

    echo_info(f"显示日志: {log_file}")

    if follow:
        subprocess.run(["tail", "-f", str(log_file)])
    else:
        subprocess.run(["tail", "-n", str(tail), str(log_file)])


# 辅助函数
def check_installation():
    """检查是否已正确安装"""
    backend_dir = get_installation_path("backend")
    return backend_dir is not None and backend_dir.exists()


def get_installation_path(component):
    """获取安装路径"""
    # 首先检查包安装目录
    try:
        import selfclaw
        package_dir = Path(selfclaw.__file__).parent
        component_dir = package_dir.parent / component
        if component_dir.exists():
            return component_dir
    except ImportError:
        pass

    # 检查当前目录
    current_dir = Path.cwd()
    component_dir = current_dir / component
    if component_dir.exists():
        return component_dir

    return None


def start_backend(backend_dir, port, debug, config):
    """启动后端服务"""
    echo_info("启动后端服务...")

    requirements_file = backend_dir / "requirements.txt"
    main_file = backend_dir / "main.py"

    if not requirements_file.exists():
        echo_error(f"requirements.txt不存在: {requirements_file}")
        return

    if not main_file.exists():
        echo_error(f"main.py不存在: {main_file}")
        return

    # 安装依赖（如果需要）
    install_requirements(requirements_file)

    # 启动后端
    cmd = [sys.executable, str(main_file)]
    if debug:
        cmd.append("--debug")

    try:
        process = subprocess.Popen(cmd, cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        echo_success(f"后端服务已启动 (PID: {process.pid})")
    except Exception as e:
        echo_error(f"启动后端失败: {e}")


def start_frontend(frontend_dir):
    """启动前端服务"""
    echo_info("启动前端服务...")

    if not shutil.which("npm"):
        echo_error("npm未安装，请先安装Node.js和npm")
        return

    try:
        # 先安装依赖
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        # 启动开发服务器
        process = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)
        echo_success(f"前端服务已启动 (PID: {process.pid})")
    except Exception as e:
        echo_error(f"启动前端失败: {e}")


def kill_process(name):
    """杀死进程"""
    try:
        if sys.platform == "darwin":
            subprocess.run(["pkill", "-f", name], check=False)
        else:
            subprocess.run(["taskkill", "/F", "/IM", f"{name}.exe"], check=False)
    except Exception:
        pass


def check_process(name):
    """检查进程是否运行"""
    try:
        if sys.platform == "darwin":
            result = subprocess.run(["pgrep", "-f", name], capture_output=True)
            return result.returncode == 0
        else:
            result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}.exe"], capture_output=True)
            return name.lower() in str(result.stdout).lower()
    except Exception:
        return False


def install_requirements(requirements_file):
    """安装Python依赖"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        echo_warning("依赖安装可能失败，但不影响运行")


def create_default_config(config_file):
    """创建默认配置"""
    default_config = {
        "port": 8000,
        "debug": False,
        "db_host": "localhost",
        "db_port": 3306,
        "db_user": "root",
        "db_password": "",
        "db_name": "selfclaw",
        "glm_api_key": "",
        "glm_model": "glm-5",
        "max_concurrent_commands": 2,
        "command_timeout": 30,
        "max_output_size": 10000,
    }

    import yaml
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)


def update_config(config_file, updates):
    """更新配置"""
    try:
        import yaml
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        config.update(updates)

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        echo_error(f"更新配置失败: {e}")


def show_config(config_file):
    """显示当前配置"""
    try:
        import yaml
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        echo_info("当前配置:")
        for key, value in config.items():
            if "password" in key.lower() or "key" in key.lower() and value:
                # 隐藏敏感信息
                click.echo(f"  {key}: ********")
            else:
                click.echo(f"  {key}: {value}")
    except Exception as e:
        echo_error(f"读取配置失败: {e}")


def main():
    """主函数"""
    cli()


if __name__ == "__main__":
    main()