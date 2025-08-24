from sqlalchemy import (Column, Integer, String, Boolean, DateTime, ForeignKey,
                        Text, CheckConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100))
    avatar_path = Column(String(100))
    status = Column(String(20), default='offline')
    last_seen = Column(DateTime, default=func.now())

    # Связи
    created_chats = relationship("Chat", back_populates="creator")
    chat_memberships = relationship("ChatMember", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    
    __table_args__ = (
        CheckConstraint(status.in_(['offline', 'online']), name='check_user_status'),
    )