"""
Supabase client configuration and initialization.

Handles:
- Connection pooling
- Environment variable management
- Error handling and retry logic
- Storage bucket configuration

Environment Variables Required:
    - SUPABASE_URL: Project URL (https://xxxxx.supabase.co)
    - SUPABASE_KEY: Service role key (for server-side operations)
    - SUPABASE_ANON_KEY: Anonymous key (for client-side operations)
    - DATABASE_URL: PostgreSQL connection string

Usage:
    from app.core.supabase import supabase, get_db_session
    
    # Using Supabase Python client (for storage, auth, etc.)
    response = supabase.table("exams").select("*").execute()
    
    # Using SQLAlchemy session (for ORM operations)
    with get_db_session() as session:
        user = session.query(User).filter(User.email == "test@test.com").first()
"""

import os
import logging
from typing import Optional, Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker, Session
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseConfig:
    """Configuration for Supabase connection."""
    
    # Environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Service role key
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Storage buckets
    EXAM_PDFS_BUCKET = "exam-pdfs"
    ANSWER_IMAGES_BUCKET = "answer-images"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate all required environment variables are set."""
        required = ["SUPABASE_URL", "SUPABASE_KEY", "DATABASE_URL"]
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            return False
        
        logger.info("[SUCCESS] Supabase configuration validated")
        return True


# Validate configuration on module load
if not SupabaseConfig.validate():
    raise RuntimeError(
        "Supabase configuration invalid. Check .env file and ensure all required "
        "environment variables are set (SUPABASE_URL, SUPABASE_KEY, DATABASE_URL)"
    )


# Initialize Supabase client
supabase: Client = create_client(
    SupabaseConfig.SUPABASE_URL,
    SupabaseConfig.SUPABASE_KEY  # Service role key for server-side operations
)

logger.info(f"[SUCCESS] Supabase client initialized: {SupabaseConfig.SUPABASE_URL}")


# SQLAlchemy engine for database operations
# Using connection pooling for better performance
engine = create_engine(
    SupabaseConfig.DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Debug SQL queries if needed
    poolclass=pool.QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
    }
)

logger.info("[SUCCESS] SQLAlchemy engine created with connection pooling")


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.
    
    Usage in FastAPI:
        @app.get("/exams")
        def get_exams(session: Session = Depends(get_db_session)):
            return session.query(Exam).all()
    
    Yields:
        SQLAlchemy Session instance
    
    Raises:
        SQLAlchemy exceptions if connection fails
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db() as session:
            user = session.query(User).filter(User.email == "test@test.com").first()
    
    Yields:
        SQLAlchemy Session instance
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction error: {str(e)}")
        raise
    finally:
        session.close()


async def check_db_connection() -> bool:
    """
    Health check for database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_db() as session:
            session.execute(text("SELECT 1"))
        logger.info("[SUCCESS] Database connection check passed")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Database connection check failed: {str(e)}")
        return False


async def check_supabase_storage() -> bool:
    """
    Health check for Supabase Storage connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        # Try to list buckets
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        required_buckets = [
            SupabaseConfig.EXAM_PDFS_BUCKET,
            SupabaseConfig.ANSWER_IMAGES_BUCKET,
        ]
        
        missing = [b for b in required_buckets if b not in bucket_names]
        if missing:
            logger.warning(f"[ERROR] Missing storage buckets: {missing}")
            return False
        
        logger.info("[SUCCESS] Supabase Storage connection check passed")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Supabase Storage connection check failed: {str(e)}")
        return False


async def health_check() -> dict:
    """
    Complete health check for all Supabase components.
    
    Returns:
        Dictionary with status of each component
    """
    return {
        "database": await check_db_connection(),
        "storage": await check_supabase_storage(),
    }

