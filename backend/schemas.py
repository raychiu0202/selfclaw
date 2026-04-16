from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ========== 会话相关 ==========

class ConversationCreate(BaseModel):
    title: str = Field(..., description="会话标题", max_length=200)


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


# ========== 消息相关 ==========

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageSend(BaseModel):
    conversation_id: int
    content: str
    stream: bool = True


class StreamResponse(BaseModel):
    content: str
    done: bool


# ========== 终端命令相关 ==========
class CommandExecuteRequest(BaseModel):
    command: str = Field(..., description="要执行的命令", max_length=500)
    conversation_id: int = Field(..., description="会话ID")
    timeout: int = Field(default=30, description="超时时间（秒）", ge=1, le=60)


class CommandExecuteResponse(BaseModel):
    success: bool
    command: str
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: int
    execution_time: float
    timestamp: datetime


class CommandHistoryResponse(BaseModel):
    id: int
    conversation_id: int
    command: str
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: int
    execution_time: int
    created_at: datetime

    class Config:
        from_attributes = True
