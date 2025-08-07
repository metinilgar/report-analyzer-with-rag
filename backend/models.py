import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class MessageSender(str, enum.Enum):
    """Enum for message sender types"""
    USER = "user"
    AI = "ai"


class Conversation(Base):
    """
    SQLAlchemy model for storing conversation metadata.
    
    A conversation represents a chat session between a user and the AI.
    It can contain multiple messages and has an optional title.
    """
    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    title = Column(
        String(255),
        nullable=True,
        comment="Optional conversation title, can be auto-generated or user-provided"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    user_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Optional user identifier for multi-user support in the future"
    )

    # Relationship to messages
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.timestamp"
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', created_at={self.created_at})>"


class Message(Base):
    """
    SQLAlchemy model for storing individual messages within conversations.
    
    Each message belongs to a conversation and can be from either the user or AI.
    Messages can include source information for AI responses.
    """
    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender = Column(
        Enum(MessageSender),
        nullable=False,
        comment="Who sent the message: 'user' or 'ai'"
    )
    content = Column(
        Text,
        nullable=False,
        comment="The actual message content"
    )
    sources = Column(
        JSON,
        nullable=True,
        comment="JSON array of source documents for AI responses, e.g., [{'document_name': '...', 'page_number': ..., 'url': '...'}]"
    )
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender}, conversation_id={self.conversation_id}, timestamp={self.timestamp})>" 