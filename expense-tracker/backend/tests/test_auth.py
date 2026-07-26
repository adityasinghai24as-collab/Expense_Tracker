import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch
from fastapi import BackgroundTasks
from app.models import User

@pytest.mark.asyncio
@patch.object(BackgroundTasks, 'add_task')
async def test_register_user(mock_add_task, client: AsyncClient, db_session: AsyncSession):
    # Test valid registration
    response = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "SecurePassword123!"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    
    # Verify user was created in the database
    stmt = select(User).where(User.email == "testuser@example.com")
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.is_verified is False
    assert user.otp_code is not None
    mock_add_task.assert_called_once()

@pytest.mark.asyncio
@patch.object(BackgroundTasks, 'add_task')
async def test_register_duplicate_user(mock_add_task, client: AsyncClient):
    # First registration
    await client.post("/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "SecurePassword123!"
    })
    
    # Second registration should fail
    response = await client.post("/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "SecurePassword123!"
    })
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
