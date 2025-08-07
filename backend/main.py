from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy import text

# Import configuration and database
from config import settings
from database import create_tables, engine

# Import API routers
from api.chat import router as chat_router
from api.conversations import router as conversations_router
from api.documents import router as documents_router

# Import schemas for responses
from schemas import ErrorResponse, HealthCheckResponse

# Import services
from services.lightrag import lightrag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up RAG System Backend...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Test LightRAG connection
        try:
            await lightrag_service.health_check()
            logger.info("LightRAG service connection verified")
        except Exception as e:
            logger.warning(f"LightRAG service not available at startup: {str(e)}")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down RAG System Backend...")
    
    try:
        # Close database connections
        engine.dispose()
        logger.info("Database connections closed")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for RAG (Retrieval-Augmented Generation) System",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this for production
)


# Middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log incoming requests and response times.
    """
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s"
        )
        raise


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.
    """
    logger.warning(f"Validation error for {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": "Invalid request data",
            "errors": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions.
    """
    logger.warning(f"HTTP exception for {request.url}: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception for {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status_code": 500
        }
    )


# Include API routers
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(documents_router)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint with basic API information.
    """
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs" if settings.debug else None
    }


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify system status.
    
    Returns:
        HealthCheckResponse with system status information
    """
    try:
        # Check database connection
        try:
            # Simple database connectivity test
            from database import SessionLocal
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_status = "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = "unhealthy"
        
        # Check LightRAG service
        try:
            await lightrag_service.health_check()
            lightrag_status = "healthy"
        except Exception as e:
            logger.warning(f"LightRAG health check failed: {str(e)}")
            lightrag_status = "unhealthy"
        
        # Determine overall status
        overall_status = "healthy" if db_status == "healthy" else "degraded"
        if lightrag_status == "unhealthy":
            overall_status = "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            services={
                "database": db_status,
                "lightrag": lightrag_status
            },
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            services={
                "database": "unknown",
                "lightrag": "unknown"
            },
            version="1.0.0"
        )


# Additional utility endpoints
@app.get("/version")
async def get_version():
    """
    Get API version information.
    """
    return {
        "version": "1.0.0",
        "name": settings.app_name,
        "debug": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI application...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    ) 