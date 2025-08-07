from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator
from database import get_database
import logging

# Set up logging
logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.
    
    This is the main dependency used throughout the application
    to inject database sessions into route handlers.
    
    Yields:
        Database session
        
    Raises:
        HTTPException: If database connection fails
    """
    try:
        db = next(get_database())
        yield db
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    finally:
        if 'db' in locals():
            db.close()


def get_current_user_id() -> str:
    """
    Dependency to get current user ID.
    
    This is a placeholder for future authentication implementation.
    Currently returns a default user ID.
    
    Returns:
        User ID string
    """
    # TODO: Implement proper authentication
    # For now, return a default user ID
    return "default_user"


def validate_conversation_access(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Dependency to validate that a user has access to a conversation.
    
    This is a placeholder for future authorization implementation.
    Currently allows access to all conversations.
    
    Args:
        conversation_id: ID of the conversation to validate
        current_user_id: Current user's ID
        db: Database session
        
    Returns:
        The conversation_id if access is allowed
        
    Raises:
        HTTPException: If access is denied or conversation not found
    """
    # TODO: Implement proper authorization
    # For now, just return the conversation_id
    return conversation_id


class DatabaseDependency:
    """
    Class-based dependency for database session management.
    
    This can be used as an alternative to the function-based get_db dependency
    for more complex scenarios or when you need to maintain state.
    """
    
    def __init__(self):
        self.db: Session = None
    
    def __call__(self) -> Session:
        """
        Get database session.
        
        Returns:
            Database session
        """
        try:
            self.db = next(get_database())
            return self.db
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )
    
    def close(self):
        """Close the database session if it exists."""
        if self.db:
            self.db.close()
            self.db = None


# Common HTTP exception responses
def not_found_exception(detail: str = "Resource not found"):
    """
    Create a standardized 404 Not Found exception.
    
    Args:
        detail: Error detail message
        
    Returns:
        HTTPException with 404 status
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def bad_request_exception(detail: str = "Bad request"):
    """
    Create a standardized 400 Bad Request exception.
    
    Args:
        detail: Error detail message
        
    Returns:
        HTTPException with 400 status
    """
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def internal_server_error_exception(detail: str = "Internal server error"):
    """
    Create a standardized 500 Internal Server Error exception.
    
    Args:
        detail: Error detail message
        
    Returns:
        HTTPException with 500 status
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail
    )


def service_unavailable_exception(detail: str = "Service unavailable"):
    """
    Create a standardized 503 Service Unavailable exception.
    
    Args:
        detail: Error detail message
        
    Returns:
        HTTPException with 503 status
    """
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail
    ) 