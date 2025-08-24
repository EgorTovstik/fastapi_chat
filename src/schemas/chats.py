from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

from src.schemas.users import User


# Базовая схема чата
class ChatBase(BaseModel):
    name: Optional[str] = None
    type: str

# Схема для создания чата
class ChatCreate(ChatBase):
    pass

# Схема для обновления чата
class ChatUpdate(BaseModel):
    name: Optional[str] = None
    avatar_path: Optional[str] = None

# Схема участника чата
class ChatMemberBase(BaseModel):
    user_id: int
    role: str = "member"

class ChatMemberCreate(ChatMemberBase):
    pass

class ChatMember(ChatMemberBase):
    id: int
    joined_at: datetime
    lefted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Полная схема чата с участниками
class Chat(ChatBase):
    id: int
    created_by: int
    created_at: datetime
    avatar_path: Optional[str] = None
    members: List[ChatMember] = []
    
    model_config = ConfigDict(from_attributes=True)

# Схема чата с пользователями
class ChatWithUsers(Chat):
    users: List[User] = []