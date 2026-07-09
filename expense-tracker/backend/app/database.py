import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import asyncpg
from dotenv import load_dotenv

# ---------------------------------------------------------------
# Environment Selection
# ---------------------------------------------------------------
# APP_ENV controls which .env file is loaded.
#   local (default) → backend/.env
#   val             → config/.env.val
#   prod            → config/.env.prod
#
# Set APP_ENV in your shell or CI/CD pipeline before running:
#   $env:APP_ENV="val"    (PowerShell)
#   export APP_ENV=val    (bash)
# ---------------------------------------------------------------
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

_config_dir = Path(__file__).resolve().parents[2] / "config"
_env_file_map = {
    "development": _config_dir / ".env.development",
    "val":         _config_dir / ".env.val",
    "prod":        _config_dir / ".env.prod",
}

_env_file = _env_file_map.get(APP_ENV, _env_file_map["development"])
load_dotenv(dotenv_path=_env_file, override=True)
print(f"[config] APP_ENV={APP_ENV!r} → loaded {_env_file.name}")

# TODO: SDE-2 Task 1 - Database Configuration
# 1. Read the database URL from environment variables (e.g., DATABASE_URL).
# 2. Implement logic to handle individual env vars (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
#    if DATABASE_URL is not provided.
# 3. Create SYNC_DATABASE_URL and ASYNC_DATABASE_URL strings.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production environments (Docker, cloud hosting) often provide a single DATABASE_URL
    SYNC_DATABASE_URL = DATABASE_URL
    # Ensure it uses postgresql instead of the older postgres scheme
    if SYNC_DATABASE_URL.startswith("postgres://"):
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    # Derive the async URL from the sync one
    ASYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    # Local development uses individual variables from .env
    user = os.getenv("DB_USER", "admin")
    password = os.getenv("DB_PASSWORD", "supersecret")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "expensedb")
    
    SYNC_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    ASYNC_DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

# TODO: SDE-2 Task 2 - Database Engines and Sessions
# 1. Create an async_engine using create_async_engine and ASYNC_DATABASE_URL.
# 2. Create an AsyncSessionLocal session factory using sessionmaker and the async_engine.
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for FastAPI endpoints to get database session"""
    # TODO: SDE-2 Task 3 - Dependency Injection
    # 1. Implement a generator that yields an async database session from AsyncSessionLocal.
    # 2. Ensure the session is properly closed after use (e.g., using a try/finally block).
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection():
    """Test async connection to PostgreSQL"""
    # TODO: SDE-2 Task 4 - Async Connection Check
    # 1. Implement logic to test the async connection to the database (e.g., using asyncpg).
    # 2. Return a tuple (True, "Connected successfully") on success, or (False, error_message) on failure.
    try:
        conn = await asyncpg.connect(SYNC_DATABASE_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


def check_db_connection_sync():
    """Test sync connection to PostgreSQL"""
    # TODO: SDE-2 Task 5 - Sync Connection Check
    # 1. Implement logic to test the sync connection to the database (e.g., using SQLAlchemy engine).
    # 2. Return a tuple (True, "Connected successfully") on success, or (False, error_message) on failure.
    try:
        engine = create_engine(SYNC_DATABASE_URL, poolclass=NullPool)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


async def init_db():
    """Initialize database tables"""
    # TODO: SDE-2 Task 6 - Database Initialization
    # 1. Implement logic to create all tables defined in your models using the async_engine.
    #    Hint: use `conn.run_sync(Base.metadata.create_all)`.
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
