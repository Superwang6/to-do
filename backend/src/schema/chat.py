from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.schema.common import PageRequest


class TodoBrief(BaseModel):
    id: int
    title: str
    priority: str = "medium"
    status: str = "pending"

    class Config:
        from_attributes = True


class ChatTextRequest(BaseModel):
    text: str
    type: str = "once"
    recurrence_rule: Optional[dict] = None


class ChatMessageListRequest(BaseModel):
    """POST /api/chat/messages/list request body."""
    page: PageRequest = PageRequest()


class ChatResponse(BaseModel):
    response: str
    todo_created: bool
    bot_message: Optional["ChatMessageResponse"] = None


class AudioTranscribeResponse(BaseModel):
    transcribed_text: str
    user_message: "ChatMessageResponse"


class ChatMessageCreate(BaseModel):
    role: str
    content: Optional[str] = None
    duration: Optional[int] = None
    todo_created: bool = False
    todo_ids: Optional[list[int]] = None


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: Optional[str] = None
    duration: Optional[int] = None
    todo_created: bool
    todos: list[TodoBrief] = []
    created_at: datetime

    class Config:
        from_attributes = True
