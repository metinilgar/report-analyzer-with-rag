from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    echo=settings.debug,  # Log SQL statements in debug mode
    pool_pre_ping=True,  # Verify connections before use
    connect_args={
        "client_encoding": "utf8",  # Force UTF-8 encoding
        "options": "-c client_encoding=utf8 -c lc_messages=C -c lc_monetary=C -c lc_numeric=C -c lc_time=C"
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()


def get_database():
    """
    Database session dependency.
    Used with FastAPI's Depends() to inject database sessions into route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables defined by SQLAlchemy models.
    This should be called at application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all tables. Use with caution!
    This is mainly for development/testing purposes.
    """
    Base.metadata.drop_all(bind=engine) 