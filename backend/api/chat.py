from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import uuid

from dependencies import get_db, internal_server_error_exception
from schemas import ChatRequest, ChatResponse, ConversationCreate, ErrorResponse
import crud
from services.lightrag import lightrag_service

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Handle chat interaction with the RAG system.
    
    This endpoint:
    1. Creates a new conversation if conversation_id is not provided
    2. Saves the user's message to the database
    3. Retrieves conversation history for context
    4. Sends the query to LightRAG server
    5. Saves the AI's response to the database
    6. Returns the AI response with metadata
    
    Args:
        request: ChatRequest containing message and optional conversation_id
        db: Database session dependency
        
    Returns:
        ChatResponse with AI response and conversation metadata
        
    Raises:
        HTTPException: 
            - 404 if conversation_id is provided but doesn't exist
            - 500 for internal server errors
            - 503 if LightRAG service is unavailable
    """
    try:
        conversation_id = request.conversation_id
        
        # Step 1: Handle conversation creation or validation
        if conversation_id is None:
            # Create a new conversation
            logger.info("Creating new conversation")
            conversation_data = ConversationCreate(
                title=None,  # Will be auto-generated later
                user_id="default_user"  # TODO: Get from authentication
            )
            conversation = crud.create_conversation(db, conversation_data)
            conversation_id = conversation.id
            logger.info(f"Created new conversation: {conversation_id}")
        else:
            # Validate existing conversation
            conversation = crud.get_conversation(db, conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation {conversation_id} not found"
                )
            logger.info(f"Using existing conversation: {conversation_id}")
        
        # Step 2: Save user's message
        user_message = crud.create_user_message(
            db=db,
            conversation_id=conversation_id,
            content=request.message
        )
        logger.info(f"Saved user message: {user_message.id}")
        
        # Step 3: Get conversation history for context
        conversation_history = crud.get_conversation_history_for_lightrag(
            db=db,
            conversation_id=conversation_id,
            max_messages=10  # Get last 10 messages for context
        )
        
        # Step 4: Send query to LightRAG
        try:
            logger.info(f"Sending query to LightRAG: {request.message[:100]}...")
            lightrag_response = await lightrag_service.query(
                query=request.message,
                mode="hybrid",  # Default mode, can be made configurable
                conversation_history=conversation_history[:-1] if conversation_history else None,  # Exclude the just-added message
                response_type="Multiple Paragraphs",
                top_k=20,
                max_token_for_text_unit=4000,
                max_token_for_global_context=4000,
                max_token_for_local_context=4000
            )
            
            ai_response_text = lightrag_response.response
            logger.info("Received response from LightRAG")
            
        except Exception as e:
            logger.error(f"LightRAG service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is currently unavailable. Please try again later."
            )
        
        # Step 5: Extract sources (if any) from the response
        # TODO: Parse sources from LightRAG response when available
        sources = None  # Placeholder for now
        
        # Step 6: Save AI's response
        ai_message = crud.create_ai_message(
            db=db,
            conversation_id=conversation_id,
            content=ai_response_text,
            sources=sources
        )
        logger.info(f"Saved AI message: {ai_message.id}")
        
        # Step 7: Auto-generate conversation title if this is the first exchange
        if not conversation.title:
            generated_title = crud.generate_conversation_title(db, conversation_id)
            if generated_title:
                crud.update_conversation_title(db, conversation_id, generated_title)
                logger.info(f"Generated conversation title: {generated_title}")
        
        # Step 8: Return response
        return ChatResponse(
            conversation_id=conversation_id,
            ai_message=ai_response_text,
            sources=sources,
            user_message_id=user_message.id,
            ai_message_id=ai_message.id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="An unexpected error occurred while processing your message"
        )


@router.post("/stream")
async def chat_stream():
    """
    Handle streaming chat interaction (future implementation).
    
    This endpoint would provide real-time streaming responses
    from the RAG system for better user experience.
    
    Currently returns a placeholder response.
    """
    # TODO: Implement streaming chat functionality
    # This would connect to LightRAG's streaming endpoint
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Streaming chat is not yet implemented"
    ) 