import pytest
from httpx import AsyncClient
from app.models import Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

@pytest.fixture
async def sample_category(db_session: AsyncSession):
    cat = Category(name="TestCat", icon="?", color="#000", user_id=None)
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)
    return cat

@pytest.mark.asyncio
async def test_create_expense(auth_client: AsyncClient, sample_category):
    expense_data = {
        "amount": 100.50,
        "description": "Lunch",
        "category_id": sample_category.id,
        "date": "2023-10-01"
    }
    resp = await auth_client.post("/expenses", json=expense_data)
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 100.50
    assert data["description"] == "Lunch"

@pytest.mark.asyncio
async def test_get_expenses(auth_client: AsyncClient, sample_category):
    expense_data = {
        "amount": 50.0,
        "description": "Coffee",
        "category_id": sample_category.id,
        "date": "2023-10-02"
    }
    await auth_client.post("/expenses", json=expense_data)
    
    resp = await auth_client.get("/expenses")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["amount"] == 50.0

@pytest.mark.asyncio
async def test_delete_expense(auth_client: AsyncClient, sample_category):
    expense_data = {
        "amount": 10.0,
        "description": "Test",
        "category_id": sample_category.id,
        "date": "2023-10-03"
    }
    create_resp = await auth_client.post("/expenses", json=expense_data)
    expense_id = create_resp.json()["id"]
    
    del_resp = await auth_client.delete(f"/expenses/{expense_id}")
    assert del_resp.status_code == 204
    
    get_resp = await auth_client.get(f"/expenses/{expense_id}")
    assert get_resp.status_code == 404
