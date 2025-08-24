from sqlalchemy import (Column, Integer, String, Boolean, DateTime, ForeignKey,
                        Text, CheckConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from src.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    msg_type = Column(String(20), default="text")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    reply_to = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"))
    is_readed = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Связи
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    
    __table_args__ = (
        CheckConstraint(msg_type.in_(['text', 'image', 'file', 'system', 'stiker']), name='check_msg_type'),
    )