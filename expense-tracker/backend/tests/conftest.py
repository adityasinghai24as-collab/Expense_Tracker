import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from app.database import async_engine, Base, get_db
from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
def mock_rate_limiter():
    """Mock fastapi_limiter so tests don't require a Redis instance or hit rate limits."""
    with patch("app.rate_limiter.PatchedRateLimiter.__call__", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture(autouse=True, scope="session")
async def setup_database():
    """Create tables before running tests."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # No teardown needed as we run against local DB with nested transaction rollback

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture that creates a nested transaction and rolls it back after the test completes.
    This ensures the database state is pristine for each test.
    """
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        
        async_session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"
        )
        
        yield async_session
        
        await async_session.close()
        await transaction.rollback()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates an HTTP client for the FastAPI app, overriding the 
    database dependency to use our transactional session.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()
