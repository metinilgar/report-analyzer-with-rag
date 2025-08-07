from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
import os
import shutil
from pathlib import Path
import mimetypes
from uuid import uuid4

from dependencies import get_db, internal_server_error_exception, bad_request_exception
from schemas import DocumentUploadResponse, DocumentListResponse, ErrorResponse
from services.lightrag import lightrag_service
from config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)

# Allowed file extensions for document upload
ALLOWED_EXTENSIONS = {
    '.pdf', '.txt', '.doc', '.docx', '.md', '.rtf',
    '.csv', '.xlsx', '.xls', '.ppt', '.pptx'
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'text/plain',
    'text/markdown',
    'text/csv',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
}


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file type and size.
    
    Args:
        file: The uploaded file
        
    Raises:
        HTTPException: If file is invalid
    """
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise bad_request_exception(
            f"File size {file.size} exceeds maximum allowed size {settings.max_file_size}"
        )
    
    # Check file extension
    if file.filename:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise bad_request_exception(
                f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # Check MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise bad_request_exception(
            f"MIME type {file.content_type} not allowed"
        )


def save_uploaded_file(file: UploadFile, save_path: Path) -> None:
    """
    Save uploaded file to local storage.
    
    Args:
        file: The uploaded file
        save_path: Path where to save the file
        
    Raises:
        Exception: If file saving fails
    """
    try:
        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File saved to: {save_path}")
        
    except Exception as e:
        logger.error(f"Failed to save file {save_path}: {str(e)}")
        raise


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    db: Session = Depends(get_db)
):
    """
    Upload a document file and forward it to LightRAG for processing.
    
    This endpoint:
    1. Validates the uploaded file
    2. Saves the file locally for serving
    3. Forwards the file to LightRAG server for indexing
    4. Returns upload status
    
    Args:
        file: The uploaded document file
        db: Database session dependency
        
    Returns:
        DocumentUploadResponse with upload status
        
    Raises:
        HTTPException: 
            - 400 for invalid file types or sizes
            - 500 for internal server errors
            - 503 if LightRAG service is unavailable
    """
    try:
        logger.info(f"Uploading document: {file.filename}")
        
        # Validate file
        validate_file(file)
        
        # Generate unique filename while preserving original name
        original_filename = file.filename or "unknown_file"
        original_name_without_ext = Path(original_filename).stem
        file_ext = Path(original_filename).suffix
        unique_id = str(uuid4())[:8]  # Use first 8 characters of UUID for shorter name
        unique_filename = f"{original_name_without_ext}_{unique_id}{file_ext}"
        
        # Save file locally for serving
        local_save_path = Path(settings.documents_dir) / unique_filename
        
        # Read file content for LightRAG
        file_content = await file.read()
        file_size = len(file_content)
        
        # Reset file pointer for local saving
        file.file.seek(0)
        
        # Save file locally
        save_uploaded_file(file, local_save_path)
        
        # Forward to LightRAG
        try:
            lightrag_response = await lightrag_service.upload_document(
                file_content=file_content,
                filename=unique_filename
            )
            
            logger.info(f"Document forwarded to LightRAG: {unique_filename}")
            
            return DocumentUploadResponse(
                status="success",
                message=f"File '{unique_filename}' uploaded successfully and sent to RAG system",
                filename=unique_filename,  # Return the unique filename for future reference
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"LightRAG upload failed: {str(e)}")
            # Delete locally saved file if LightRAG upload fails
            if local_save_path.exists():
                local_save_path.unlink()
            
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is currently unavailable. Please try again later."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to upload document"
        )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents(
    db: Session = Depends(get_db)
):
    """
    Get a list of uploaded documents available for serving.
    
    Returns:
        DocumentListResponse with list of available documents
        
    Raises:
        HTTPException: 500 for internal server errors
    """
    try:
        logger.info("Listing available documents")
        
        documents = []
        documents_dir = Path(settings.documents_dir)
        
        if documents_dir.exists():
            for file_path in documents_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    documents.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "url": f"/api/documents/{file_path.name}"
                    })
        
        logger.info(f"Found {len(documents)} documents")
        
        return DocumentListResponse(documents=documents)
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to list documents"
        )


@router.get("/{filename}")
async def serve_document(filename: str):
    """
    Serve a document file for download or viewing.
    
    This endpoint serves PDF files and other documents that were
    previously uploaded to the system.
    
    Args:
        filename: Name of the file to serve
        
    Returns:
        FileResponse with the requested file
        
    Raises:
        HTTPException: 
            - 404 if file not found
            - 500 for internal server errors
    """
    try:
        logger.info(f"Serving document: {filename}")
        
        # Construct file path
        file_path = Path(settings.documents_dir) / filename
        
        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{filename}' not found"
            )
        
        # Determine media type
        media_type, _ = mimetypes.guess_type(str(file_path))
        if not media_type:
            media_type = "application/octet-stream"
        
        logger.info(f"Serving file: {file_path} with media type: {media_type}")
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving document {filename}: {str(e)}", exc_info=True)
        raise internal_server_error_exception(
            detail="Failed to serve document"
        )


@router.post("/scan")
async def trigger_document_scan(db: Session = Depends(get_db)):
    """
    Trigger document scanning on LightRAG server.
    
    This endpoint forwards the scan request to the LightRAG server
    to process any new documents in its input directory.
    
    Returns:
        Dictionary with scan status from LightRAG
        
    Raises:
        HTTPException: 
            - 503 if LightRAG service is unavailable
            - 500 for internal server errors
    """
    try:
        logger.info("Triggering document scan on LightRAG")
        
        # Forward scan request to LightRAG
        scan_result = await lightrag_service.scan_documents()
        
        logger.info("Document scan triggered successfully")
        return scan_result
        
    except Exception as e:
        logger.error(f"Document scan failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is currently unavailable. Please try again later."
        )


@router.get("/pipeline/status")
async def get_pipeline_status(db: Session = Depends(get_db)):
    """
    Get the current document processing pipeline status from LightRAG.
    
    Returns:
        Dictionary with pipeline status information
        
    Raises:
        HTTPException: 
            - 503 if LightRAG service is unavailable
            - 500 for internal server errors
    """
    try:
        logger.info("Getting pipeline status from LightRAG")
        
        # Get pipeline status from LightRAG
        status_result = await lightrag_service.get_pipeline_status()
        
        return status_result
        
    except Exception as e:
        logger.error(f"Pipeline status request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG service is currently unavailable. Please try again later."
        ) 