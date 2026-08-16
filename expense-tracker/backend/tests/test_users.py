import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_me(auth_client: AsyncClient):
    resp = await auth_client.get("/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user@test.com"
    assert data["username"] == "user1"

@pytest.mark.asyncio
async def test_update_me(auth_client: AsyncClient):
    resp = await auth_client.put("/users/me", json={"full_name": "Updated Name"})
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Updated Name"

@pytest.mark.asyncio
async def test_delete_me(auth_client: AsyncClient):
    resp = await auth_client.delete("/users/me")
    assert resp.status_code == 204
    
    # Verify user is deleted by failing to get profile
    resp = await auth_client.get("/users/me")
    assert resp.status_code == 401  # Token no longer valid / user not found

@pytest.mark.asyncio
async def test_list_users_admin(admin_client: AsyncClient):
    resp = await admin_client.get("/users")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@pytest.mark.asyncio
async def test_list_users_forbidden(auth_client: AsyncClient):
    resp = await auth_client.get("/users")
    assert resp.status_code == 403
