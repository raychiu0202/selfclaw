"""
数据库清理脚本
清理测试对话、消息和命令执行历史
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, engine
from models import Conversation, Message, CommandHistory
from sqlalchemy import text

def clean_database():
    """清理数据库中的测试数据"""
    db = SessionLocal()

    try:
        print("🧹 开始清理数据库...")

        # 删除所有命令执行历史
        deleted_commands = db.query(CommandHistory).count()
        db.query(CommandHistory).delete()
        print(f"✅ 删除了 {deleted_commands} 条命令执行历史")

        # 删除所有消息
        deleted_messages = db.query(Message).count()
        db.query(Message).delete()
        print(f"✅ 删除了 {deleted_messages} 条消息记录")

        # 删除所有对话
        deleted_conversations = db.query(Conversation).count()
        db.query(Conversation).delete()
        print(f"✅ 删除了 {deleted_conversations} 个对话记录")

        # 重置自增ID
        db.execute(text("ALTER TABLE conversations AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE messages AUTO_INCREMENT = 1"))
        db.execute(text("ALTER TABLE command_history AUTO_INCREMENT = 1"))

        db.commit()
        print("🎉 数据库清理完成！")

    except Exception as e:
        db.rollback()
        print(f"❌ 清理失败: {e}")
        return False
    finally:
        db.close()

    return True

if __name__ == "__main__":
    if clean_database():
        print("\n✨ 数据库已清空，可以开始新的测试！")
    else:
        print("\n❌ 数据库清理失败，请检查错误信息")
        sys.exit(1)
