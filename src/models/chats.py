from sqlalchemy import (Column, Integer, String, Boolean, DateTime, ForeignKey,
                        Text, CheckConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from src.database import Base



class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(String(20), nullable=False, default='private')
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    avatar_path = Column(String(100))

    # Связи
    creator = relationship("User", back_populates="created_chats")
    members = relationship("ChatMember", back_populates="chat")
    messages = relationship("Message", back_populates="chat")
    
    __table_args__ = (
        CheckConstraint(type.in_(['private', 'group', 'channel']), name='check_chat_type'),
    )

class ChatMember(Base):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String(20), default="member")
    joined_at = Column(DateTime, default=func.now())
    lefted_at = Column(DateTime)

    # Связи
    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chat_memberships")

    __table_args__ = (
        CheckConstraint(role.in_(['owner', 'admin', 'member']), name='check_member_role'),
    )

