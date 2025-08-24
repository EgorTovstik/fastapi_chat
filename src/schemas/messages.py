# app/schemas/message.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from src.schemas.users import User

# Базовая схема сообщения
class MessageBase(BaseModel):
    content: Optional[str] = None
    msg_type: str = "text"

# Схема для создания сообщения
class MessageCreate(MessageBase):
    chat_id: int
    reply_to: Optional[int] = None

# Схема для обновления сообщения
class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_readed: Optional[bool] = None

# Полная схема сообщения
class Message(MessageBase):
    id: int
    chat_id: int
    sender_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    reply_to: Optional[int] = None
    is_readed: bool = False
    is_edited: bool = False
    is_deleted: bool = False
    
    model_config = ConfigDict(from_attributes=True)

# Схема сообщения с пользователем
class MessageWithUser(Message):
    sender: Optional[User] = None