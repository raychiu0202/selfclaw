from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base, get_db
from models import Conversation, Message
from schemas import (
    ConversationCreate, ConversationResponse, ConversationListResponse,
    MessageSend, MessageResponse, StreamResponse,
    CommandExecuteRequest, CommandExecuteResponse, CommandHistoryResponse
)
from services import ConversationService, ChatService
from terminal import TerminalService

# 创建数据库表
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    yield
    # 关闭时执行


app = FastAPI(
    title="GLM Chat API",
    description="基于GLM-5的聊天系统API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
conversation_service = ConversationService()
chat_service = ChatService()
terminal_service = TerminalService()


@app.get("/")
async def root():
    return {"message": "GLM Chat API is running"}


# ========== 会话管理 ==========

@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate):
    """创建新会话"""
    return conversation_service.create_conversation(conversation.title)


@app.get("/api/conversations", response_model=ConversationListResponse)
async def get_conversations():
    """获取所有会话"""
    return conversation_service.get_all_conversations()


@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int):
    """获取单个会话"""
    conv = conversation_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    return conv


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """删除会话"""
    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "删除成功"}


@app.put("/api/conversations/{conversation_id}")
async def update_conversation(conversation_id: int, conversation: ConversationCreate):
    """更新会话标题"""
    conv = conversation_service.update_conversation(conversation_id, conversation.title)
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    return conv


# ========== 消息管理 ==========

@app.get("/api/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(conversation_id: int):
    """获取会话的所有消息"""
    return conversation_service.get_messages(conversation_id)


@app.post("/api/chat/stream")
async def chat_stream(message: MessageSend):
    """流式对话接口"""
    return StreamingResponse(
        chat_service.stream_chat(message),
        media_type="text/event-stream"
    )


# ========== 终端命令管理 ==========

@app.post("/api/terminal/execute", response_model=CommandExecuteResponse)
async def execute_command(request: CommandExecuteRequest):
    """执行终端命令"""
    result = await terminal_service.execute_command(
        command=request.command,
        conversation_id=request.conversation_id,
        timeout=request.timeout
    )
    return result


@app.get("/api/terminal/history/{conversation_id}")
async def get_command_history(conversation_id: int, limit: int = 10):
    """获取命令执行历史"""
    history = terminal_service.get_history(conversation_id, limit)
    return {
        "history": history,
        "total": len(history)
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
