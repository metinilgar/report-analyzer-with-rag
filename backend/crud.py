from sqlalchemy.orm import Session
from sqlalchemy import desc, func, select, text
from typing import List, Optional, Dict, Any
from uuid import UUID
import uuid

from models import Conversation, Message, MessageSender
from schemas import ConversationCreate, MessageCreate, ConversationSummary


# === CONVERSATION CRUD OPERATIONS ===

def create_conversation(db: Session, conversation: ConversationCreate) -> Conversation:
    """
    Create a new conversation in the database.
    
    Args:
        db: Database session
        conversation: ConversationCreate schema with conversation data
        
    Returns:
        Created Conversation model instance
    """
    db_conversation = Conversation(
        title=conversation.title,
        user_id=conversation.user_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_conversation(db: Session, conversation_id: UUID) -> Optional[Conversation]:
    """
    Get a conversation by ID.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        
    Returns:
        Conversation model instance or None if not found
    """
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    return db.execute(stmt).scalar_one_or_none()


def get_conversations(
    db: Session, 
    user_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Conversation]:
    """
    Get a list of conversations, optionally filtered by user_id.
    
    Args:
        db: Database session
        user_id: Optional user ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Conversation model instances
    """
    stmt = select(Conversation)
    
    if user_id:
        stmt = stmt.where(Conversation.user_id == user_id)
    
    stmt = stmt.order_by(desc(Conversation.created_at)).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def get_conversations_with_summary(
    db: Session, 
    user_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get conversations with summary information (message count, last message time).
    
    Args:
        db: Database session
        user_id: Optional user ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of dictionaries with conversation summary data
    """
    stmt = select(
        Conversation.id,
        Conversation.title,
        Conversation.created_at,
        func.count(Message.id).label('message_count'),
        func.max(Message.timestamp).label('last_message_at')
    ).outerjoin(Message).group_by(Conversation.id)
    
    if user_id:
        stmt = stmt.where(Conversation.user_id == user_id)
    
    stmt = stmt.order_by(desc(Conversation.created_at)).offset(skip).limit(limit)
    result = db.execute(stmt).all()
    
    return [
        {
            'id': row.id,
            'title': row.title,
            'created_at': row.created_at,
            'message_count': row.message_count or 0,
            'last_message_at': row.last_message_at
        }
        for row in result
    ]


def update_conversation_title(db: Session, conversation_id: UUID, title: str) -> Optional[Conversation]:
    """
    Update a conversation's title.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        title: New title for the conversation
        
    Returns:
        Updated Conversation model instance or None if not found
    """
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    db_conversation = db.execute(stmt).scalar_one_or_none()
    if db_conversation:
        db_conversation.title = title
        db.commit()
        db.refresh(db_conversation)
    return db_conversation


def delete_conversation(db: Session, conversation_id: UUID) -> bool:
    """
    Delete a conversation and all its messages.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation to delete
        
    Returns:
        True if deleted successfully, False if not found
    """
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    db_conversation = db.execute(stmt).scalar_one_or_none()
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
        return True
    return False


# === MESSAGE CRUD OPERATIONS ===

def create_message(db: Session, message: MessageCreate) -> Message:
    """
    Create a new message in the database.
    
    Args:
        db: Database session
        message: MessageCreate schema with message data
        
    Returns:
        Created Message model instance
    """
    db_message = Message(
        conversation_id=message.conversation_id,
        sender=message.sender,
        content=message.content,
        sources=message.sources
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def create_user_message(db: Session, conversation_id: UUID, content: str) -> Message:
    """
    Convenience function to create a user message.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        content: Message content
        
    Returns:
        Created Message model instance
    """
    message_data = MessageCreate(
        conversation_id=conversation_id,
        sender=MessageSender.USER,
        content=content,
        sources=None
    )
    return create_message(db, message_data)


def create_ai_message(
    db: Session, 
    conversation_id: UUID, 
    content: str, 
    sources: Optional[List[Dict[str, Any]]] = None
) -> Message:
    """
    Convenience function to create an AI message.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        content: Message content
        sources: Optional list of source documents
        
    Returns:
        Created Message model instance
    """
    message_data = MessageCreate(
        conversation_id=conversation_id,
        sender=MessageSender.AI,
        content=content,
        sources=sources
    )
    return create_message(db, message_data)


def get_message(db: Session, message_id: UUID) -> Optional[Message]:
    """
    Get a message by ID.
    
    Args:
        db: Database session
        message_id: UUID of the message
        
    Returns:
        Message model instance or None if not found
    """
    stmt = select(Message).where(Message.id == message_id)
    return db.execute(stmt).scalar_one_or_none()


def get_messages_by_conversation(
    db: Session, 
    conversation_id: UUID,
    skip: int = 0,
    limit: int = 1000
) -> List[Message]:
    """
    Get all messages for a specific conversation.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Message model instances ordered by timestamp
    """
    stmt = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def get_conversation_history_for_lightrag(
    db: Session, 
    conversation_id: UUID,
    max_messages: int = 10
) -> List[Dict[str, str]]:
    """
    Get conversation history formatted for LightRAG API.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        max_messages: Maximum number of recent messages to include
        
    Returns:
        List of dictionaries with 'role' and 'content' keys for LightRAG
    """
    stmt = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.timestamp)).limit(max_messages)
    messages = db.execute(stmt).scalars().all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    history = []
    for message in messages:
        role = "user" if message.sender == MessageSender.USER else "assistant"
        history.append({
            "role": role,
            "content": message.content
        })
    
    return history


def delete_message(db: Session, message_id: UUID) -> bool:
    """
    Delete a specific message.
    
    Args:
        db: Database session
        message_id: UUID of the message to delete
        
    Returns:
        True if deleted successfully, False if not found
    """
    stmt = select(Message).where(Message.id == message_id)
    db_message = db.execute(stmt).scalar_one_or_none()
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False


def get_conversation_message_count(db: Session, conversation_id: UUID) -> int:
    """
    Get the number of messages in a conversation.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        
    Returns:
        Number of messages in the conversation
    """
    stmt = select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    return db.execute(stmt).scalar()


# === UTILITY FUNCTIONS ===

def conversation_exists(db: Session, conversation_id: UUID) -> bool:
    """
    Check if a conversation exists.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        
    Returns:
        True if conversation exists, False otherwise
    """
    stmt = select(Conversation.id).where(Conversation.id == conversation_id)
    return db.execute(stmt).scalar() is not None


def generate_conversation_title(db: Session, conversation_id: UUID) -> Optional[str]:
    """
    Generate a title for a conversation based on the first user message.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        
    Returns:
        Generated title or None if no messages found
    """
    stmt = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.sender == MessageSender.USER
    ).order_by(Message.timestamp)
    first_message = db.execute(stmt).scalar()
    
    if first_message:
        # Use first 50 characters of the first message as title
        title = first_message.content[:50].strip()
        if len(first_message.content) > 50:
            title += "..."
        return title
    
    return None 