# app/models/__init__.py
from src.models.users import User
from src.models.chats import Chat, ChatMember
from src.models.messages import Message

# Экспортируем все модели для удобного импорта
__all__ = ['User', 'Chat', 'ChatMember', 'Message']