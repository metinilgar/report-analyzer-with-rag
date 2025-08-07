from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class MessageSenderEnum(str, Enum):
    """Enum for message sender types"""
    USER = "user"
    AI = "ai"


# Base schemas for common fields
class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields"""
    created_at: datetime
    
    class Config:
        from_attributes= True


# === CONVERSATION SCHEMAS ===

class ConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    title: Optional[str] = Field(None, max_length=255, description="Optional conversation title")
    user_id: Optional[str] = Field(None, max_length=255, description="Optional user identifier")


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: UUID = Field(..., description="Unique conversation identifier")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(..., description="When the conversation was created")
    user_id: Optional[str] = Field(None, description="User identifier")
    message_count: Optional[int] = Field(None, description="Number of messages in conversation")
    
    class Config:
        from_attributes= True


class ConversationSummary(BaseModel):
    """Schema for conversation list item (summary view)"""
    id: UUID
    title: Optional[str]
    created_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    
    class Config:
        from_attributes= True


# === MESSAGE SCHEMAS ===

class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    conversation_id: UUID = Field(..., description="ID of the conversation this message belongs to")
    sender: MessageSenderEnum = Field(..., description="Who sent the message")
    content: str = Field(..., min_length=1, description="Message content")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents for AI responses")


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: UUID = Field(..., description="Unique message identifier")
    conversation_id: UUID = Field(..., description="Conversation ID")
    sender: MessageSenderEnum = Field(..., description="Message sender")
    content: str = Field(..., description="Message content")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents")
    timestamp: datetime = Field(..., description="When the message was sent")
    
    class Config:
        from_attributes= True


# === CHAT SCHEMAS ===

class ChatRequest(BaseModel):
    """Schema for chat endpoint request"""
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID, or None to create new")
    message: str = Field(..., min_length=1, max_length=10000, description="User's message")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or just whitespace')
        return v.strip()


class ChatResponse(BaseModel):
    """Schema for chat endpoint response"""
    conversation_id: UUID = Field(..., description="Conversation ID (new or existing)")
    ai_message: str = Field(..., description="AI's response")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents used for the response")
    user_message_id: UUID = Field(..., description="ID of the user's message")
    ai_message_id: UUID = Field(..., description="ID of the AI's message")


# === DOCUMENT SCHEMAS ===

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    filename: Optional[str] = Field(None, description="Uploaded filename")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class DocumentListResponse(BaseModel):
    """Schema for listing documents"""
    documents: List[Dict[str, Any]] = Field(..., description="List of available documents")


# === LIGHTRAG INTEGRATION SCHEMAS ===

class LightRAGQueryRequest(BaseModel):
    """Schema for LightRAG query request (based on OpenAPI spec)"""
    query: str = Field(..., min_length=1, description="The query text")
    mode: str = Field(default="hybrid", description="Query mode")
    only_need_context: Optional[bool] = Field(None, description="If True, only returns context")
    only_need_prompt: Optional[bool] = Field(None, description="If True, only returns prompt")
    response_type: Optional[str] = Field(None, description="Response format")
    top_k: Optional[int] = Field(None, ge=1, description="Number of top items to retrieve")
    max_token_for_text_unit: Optional[int] = Field(None, gt=1, description="Max tokens per text unit")
    max_token_for_global_context: Optional[int] = Field(None, gt=1, description="Max tokens for global context")
    max_token_for_local_context: Optional[int] = Field(None, gt=1, description="Max tokens for local context")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Conversation history")
    history_turns: Optional[int] = Field(None, ge=0, description="Number of history turns")
    ids: Optional[List[str]] = Field(None, description="List of IDs to filter results")
    user_prompt: Optional[str] = Field(None, description="User-provided prompt")


class LightRAGQueryResponse(BaseModel):
    """Schema for LightRAG query response"""
    response: str = Field(..., description="The generated response")


class LightRAGUploadResponse(BaseModel):
    """Schema for LightRAG upload response"""
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")


# === ERROR SCHEMAS ===

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel):
    """Schema for simple success responses"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")


# === HEALTH CHECK SCHEMA ===

class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    services: Dict[str, str] = Field(..., description="Status of dependent services")
    version: str = Field(..., description="API version") 