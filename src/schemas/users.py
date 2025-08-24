from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# Базовая схема пользователя
class UserBase(BaseModel):
    username: str
    name: str

# Схема для создания пользователя
class UserCreate(UserBase):
    password: str

# Схема для обновления пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    avatar_path: Optional[str] = None
    status: Optional[str] = None

# Схема пользователя для ответа (без пароля)
class User(UserBase):
    id: int
    avatar_path: Optional[str] = None
    status: str = "offline"
    last_seen: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Схема для аутентификации
class UserLogin(BaseModel):
    username: str
    password: str

# Схема с токеном
class UserWithToken(User):
    access_token: str