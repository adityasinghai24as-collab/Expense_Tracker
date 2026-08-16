import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_categories(auth_client: AsyncClient):
    resp = await auth_client.get("/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Global categories should be populated
    assert len(data) > 0

@pytest.mark.asyncio
async def test_create_category(auth_client: AsyncClient):
    cat_data = {
        "name": "Custom Category",
        "icon": "?",
        "color": "#123456"
    }
    resp = await auth_client.post("/categories", json=cat_data)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Custom Category"

@pytest.mark.asyncio
async def test_create_duplicate_category_name(auth_client: AsyncClient):
    cat_data = {
        "name": "Dup Category",
        "icon": "A",
        "color": "#fff"
    }
    resp1 = await auth_client.post("/categories", json=cat_data)
    assert resp1.status_code == 201
    
    resp2 = await auth_client.post("/categories", json=cat_data)
    assert resp2.status_code == 400
