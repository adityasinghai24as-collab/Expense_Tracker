import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Database configuration - support both DATABASE_URL and individual env vars
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Use DATABASE_URL if provided (Docker/production)
    ASYNC_DATABASE_URL = DATABASE_URL
    SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
else:
    # Fall back to individual environment variables (local development)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "expense_tracker")
    
    SYNC_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Export for debugging
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "expense_tracker")

# Async engine and session factory
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for FastAPI endpoints to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection():
    """Test async connection to PostgreSQL"""
    try:
        connection = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=int(DB_PORT),
        )
        result = await connection.fetchval("SELECT 1")
        await connection.close()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


def check_db_connection_sync():
    """Test sync connection to PostgreSQL"""
    try:
        engine = create_engine(
            SYNC_DATABASE_URL,
            echo=False,
            poolclass=NullPool,
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
