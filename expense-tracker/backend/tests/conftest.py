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

@pytest.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    """Provides a client authenticated as a normal user."""
    from app.models import User
    from app.auth import hash_password, create_access_token
    
    user = User(
        email="user@test.com",
        username="user1",
        full_name="Normal User",
        hashed_password=hash_password("testpass"),
        is_verified=True,
        role="user"
    )
    db_session.add(user)
    await db_session.commit()
    
    token = create_access_token({"sub": str(user.id)})
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
async def admin_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    """Provides a client authenticated as an admin user."""
    from app.models import User
    from app.auth import hash_password, create_access_token
    
    admin = User(
        email="admin@test.com",
        username="admin1",
        full_name="Admin User",
        hashed_password=hash_password("testpass"),
        is_verified=True,
        role="admin"
    )
    db_session.add(admin)
    await db_session.commit()
    
    token = create_access_token({"sub": str(admin.id)})
    client.headers = {"Authorization": f"Bearer {token}"}
    return client
