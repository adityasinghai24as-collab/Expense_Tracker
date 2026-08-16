import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

@pytest.fixture
def mock_send_email():
    with patch("app.routers.auth_routes.send_otp_email") as mock:
        yield mock

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient, db_session: AsyncSession, mock_send_email):
    # 1. Register user
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    resp = await client.post("/auth/register", json=user_data)
    assert resp.status_code == 201
    
    # 2. Get OTP from DB
    result = await db_session.execute(select(User).where(User.email == "testuser@example.com"))
    user = result.scalar_one_or_none()
    assert user is not None
    otp_code = user.otp_code
    assert otp_code is not None
    
    # 3. Verify OTP
    verify_data = {
        "email": "testuser@example.com",
        "otp_code": otp_code
    }
    resp = await client.post("/auth/verify-otp", json=verify_data)
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    
    # 4. Login
    login_data = {
        "username_or_email": "testuser@example.com",
        "password": "TestPassword123!"
    }
    resp = await client.post("/auth/login", json=login_data)
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens

    # 5. Get Me
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "testuser@example.com"
