from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.chat import MessageRole


class ChatSessionCreate(BaseModel):
    session_name: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: int
    business_id: int
    user_id: int
    session_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    role: MessageRole
    content: str
    message_metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: MessageRole
    content: str
    message_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
