from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from uuid import UUID

from dependencies import get_db, not_found_exception, internal_server_error_exception
from schemas import (
    ConversationCreate, ConversationResponse, ConversationSummary,
    MessageResponse, ErrorResponse, SuccessResponse
)
import crud

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/conversations",
    tags=["conversations"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post("/new", response_model=ConversationResponse)
async def create_new_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.
    
    Args:
        conversation: ConversationCreate schema with optional title and user_id
        db: Database session dependency
        
    Returns:
        ConversationResponse with the created conversation details
        
    Raises:
        HTTPException: 500 for internal server errors
    """
    try:
        logger.info(f"Creating new conversation with title: {conversation.title}")
        
        # Create the conversation
        db_conversation = crud.create_conversation(db, conversation)
        
        # Get message count (should be 0 for new conversation)
        message_count = crud.get_conversation_message_count(db, db_conversation.id)
        
        logger.info(f"Created conversation: {db_conversation.id}")
        
        return ConversationResponse(
            id=db_conversation.id,
            title=db_conversation.title,
            created_at=db_conversation.created_at,
            user_id=db_conversation.user_id,
            message_count=message_count
        )
        
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to create conversation"
        )


@router.get("/", response_model=List[ConversationSummary])
async def get_conversations(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum conversations to return"),
    db: Session = Depends(get_db)
):
    """
    Get a list of conversations with summary information.
    
    Args:
        user_id: Optional user ID to filter conversations
        skip: Number of conversations to skip (for pagination)
        limit: Maximum number of conversations to return
        db: Database session dependency
        
    Returns:
        List of ConversationSummary objects
        
    Raises:
        HTTPException: 500 for internal server errors
    """
    try:
        logger.info(f"Getting conversations for user: {user_id}, skip: {skip}, limit: {limit}")
        
        # Get conversations with summary data
        conversations_data = crud.get_conversations_with_summary(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format
        conversations = [
            ConversationSummary(
                id=conv['id'],
                title=conv['title'],
                created_at=conv['created_at'],
                last_message_at=conv['last_message_at'],
                message_count=conv['message_count']
            )
            for conv in conversations_data
        ]
        
        logger.info(f"Retrieved {len(conversations)} conversations")
        return conversations
        
    except Exception as e:
        logger.error(f"Error retrieving conversations: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to retrieve conversations"
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    
    Args:
        conversation_id: UUID of the conversation
        db: Database session dependency
        
    Returns:
        ConversationResponse with conversation details
        
    Raises:
        HTTPException: 
            - 404 if conversation not found
            - 500 for internal server errors
    """
    try:
        logger.info(f"Getting conversation: {conversation_id}")
        
        # Get the conversation
        conversation = crud.get_conversation(db, conversation_id)
        if not conversation:
            raise not_found_exception(f"Conversation {conversation_id} not found")
        
        # Get message count
        message_count = crud.get_conversation_message_count(db, conversation_id)
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            user_id=conversation.user_id,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to retrieve conversation"
        )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum messages to return"),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a specific conversation.
    
    Args:
        conversation_id: UUID of the conversation
        skip: Number of messages to skip (for pagination)
        limit: Maximum number of messages to return
        db: Database session dependency
        
    Returns:
        List of MessageResponse objects ordered by timestamp
        
    Raises:
        HTTPException: 
            - 404 if conversation not found
            - 500 for internal server errors
    """
    try:
        logger.info(f"Getting messages for conversation: {conversation_id}")
        
        # Verify conversation exists
        if not crud.conversation_exists(db, conversation_id):
            raise not_found_exception(f"Conversation {conversation_id} not found")
        
        # Get messages
        messages = crud.get_messages_by_conversation(
            db=db,
            conversation_id=conversation_id,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format
        message_responses = [
            MessageResponse(
                id=message.id,
                conversation_id=message.conversation_id,
                sender=message.sender,
                content=message.content,
                sources=message.sources,
                timestamp=message.timestamp
            )
            for message in messages
        ]
        
        logger.info(f"Retrieved {len(message_responses)} messages")
        return message_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving messages for conversation {conversation_id}: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to retrieve messages"
        )


@router.patch("/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: UUID,
    title: str = Query(..., min_length=1, max_length=255, description="New conversation title"),
    db: Session = Depends(get_db)
):
    """
    Update a conversation's title.
    
    Args:
        conversation_id: UUID of the conversation
        title: New title for the conversation
        db: Database session dependency
        
    Returns:
        ConversationResponse with updated conversation details
        
    Raises:
        HTTPException: 
            - 404 if conversation not found
            - 500 for internal server errors
    """
    try:
        logger.info(f"Updating title for conversation {conversation_id}: {title}")
        
        # Update the conversation title
        updated_conversation = crud.update_conversation_title(db, conversation_id, title)
        if not updated_conversation:
            raise not_found_exception(f"Conversation {conversation_id} not found")
        
        # Get message count
        message_count = crud.get_conversation_message_count(db, conversation_id)
        
        logger.info(f"Updated conversation title: {conversation_id}")
        
        return ConversationResponse(
            id=updated_conversation.id,
            title=updated_conversation.title,
            created_at=updated_conversation.created_at,
            user_id=updated_conversation.user_id,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title {conversation_id}: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to update conversation title"
        )


@router.delete("/{conversation_id}", response_model=SuccessResponse)
async def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: UUID of the conversation to delete
        db: Database session dependency
        
    Returns:
        SuccessResponse confirming deletion
        
    Raises:
        HTTPException: 
            - 404 if conversation not found
            - 500 for internal server errors
    """
    try:
        logger.info(f"Deleting conversation: {conversation_id}")
        
        # Delete the conversation
        deleted = crud.delete_conversation(db, conversation_id)
        if not deleted:
            raise not_found_exception(f"Conversation {conversation_id} not found")
        
        logger.info(f"Deleted conversation: {conversation_id}")
        
        return SuccessResponse(
            success=True,
            message=f"Conversation {conversation_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to delete conversation"
        ) 