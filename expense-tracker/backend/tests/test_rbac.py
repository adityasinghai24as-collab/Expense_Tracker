import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rbac_user_access_admin_route_forbidden(auth_client: AsyncClient):
    resp = await auth_client.get("/users")
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_rbac_admin_access_admin_route_success(admin_client: AsyncClient):
    resp = await admin_client.get("/users")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_rbac_user_cannot_update_roles(auth_client: AsyncClient):
    # Try to upgrade own role
    resp = await auth_client.put("/users/1/role?role=admin")
    assert resp.status_code == 403
