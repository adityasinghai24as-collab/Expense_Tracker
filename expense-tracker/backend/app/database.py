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

_config_dir = Path(__file__).resolve().parents[1] / "config"
_env_file_map = {
    "development": _config_dir / ".env.development",
    "val":         _config_dir / ".env.val",
    "prod":        _config_dir / ".env.prod",
}

_env_file = _env_file_map.get(APP_ENV, _env_file_map["development"])
load_dotenv(dotenv_path=_env_file, override=False)
print(f"[config] APP_ENV={APP_ENV!r} → loaded {_env_file.name}")


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Production environments (Docker, cloud hosting) often provide a single DATABASE_URL
    # Normalize: strip any driver suffix to get a clean sync URL first
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    # Ensure it uses postgresql instead of the older postgres scheme
    if SYNC_DATABASE_URL.startswith("postgres://"):
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    # Derive the async URL from the clean sync one
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

# Optimize connection pooling for high concurrency (e.g. Locust load testing)
# Conditionally disable SQL echoing if not in development to avoid console bottleneck
is_development = APP_ENV == "development"

# Task 2 - Create the Async Engine and Session Factory (Completed)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=is_development, 
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

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
        conn = await asyncpg.connect(SYNC_DATABASE_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


def check_db_connection_sync():
    """Test sync connection to PostgreSQL"""

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

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed default categories if none exist
    from sqlalchemy import select, delete
    from .models import Category
    
    async with AsyncSessionLocal() as session:
        # Cleanup: Remove any old categories that don't have an icon
        await session.execute(delete(Category).where(Category.icon.is_(None)))
        await session.commit()
        
        # Sync global categories with the frontend (categoryDetector.js)
        desired_categories = [
            {"name": "Food", "color": "#EF4444", "icon": "🍔"},
            {"name": "Transport", "color": "#3B82F6", "icon": "🚗"},
            {"name": "Utilities", "color": "#EAB308", "icon": "🏠"},
            {"name": "Entertainment", "color": "#A855F7", "icon": "🎬"},
            {"name": "Groceries", "color": "#10B981", "icon": "🛒"},
            {"name": "Healthcare", "color": "#EC4899", "icon": "🏥"},
            {"name": "Shopping", "color": "#F97316", "icon": "🛍️"},
            {"name": "Travel", "color": "#06B6D4", "icon": "✈️"},
            {"name": "Education", "color": "#8B5CF6", "icon": "📚"},
            {"name": "Fitness", "color": "#84CC16", "icon": "💪"},
            {"name": "Subscriptions", "color": "#6366F1", "icon": "📱"},
            {"name": "Dining", "color": "#F43F5E", "icon": "🍽️"},
            {"name": "Other", "color": "#6B7280", "icon": "📌"},
        ]
        
        for cat_data in desired_categories:
            result = await session.execute(select(Category).where(Category.name == cat_data["name"], Category.user_id.is_(None)))
            existing = result.scalar_one_or_none()
            if not existing:
                session.add(Category(name=cat_data["name"], color=cat_data["color"], icon=cat_data["icon"], user_id=None))
                
        await session.commit()
