from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import (
    get_db,
    check_db_connection,
    check_db_connection_sync,
    init_db,
)

app = FastAPI(title="Expense Tracker API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    message: str


class DBHealthResponse(BaseModel):
    status: str
    message: str
    database: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Expense Tracker API is running"}


@app.get("/health/db", response_model=DBHealthResponse)
async def db_health_check():
    """Check database connection status"""
    is_connected, message = await check_db_connection()
    return {
        "status": "ok" if is_connected else "error",
        "message": message,
        "database": "postgresql",
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_db()
        is_connected, message = await check_db_connection()
        if is_connected:
            print("✅ Database initialized and connected successfully")
        else:
            print(f"⚠️ Database connection failed: {message}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# ==========================================
# TODO: SDE-2 Task 18 - User Endpoints
# ==========================================
# 1. Create POST /users to register a new user
# 2. Create GET /users to list users
# 3. Create GET /users/{user_id} to get a specific user
# Use the UserCreate and UserResponse schemas for validation.

# ==========================================
# TODO: SDE-2 Task 19 - Expense Endpoints
# ==========================================
# 1. Create POST /expenses to add a new expense
# 2. Create GET /expenses to list all expenses (add pagination!)
# 3. Create GET /expenses/{expense_id} to get a specific expense
# 4. Create PUT /expenses/{expense_id} to update an expense
# 5. Create DELETE /expenses/{expense_id} to delete an expense

# ==========================================
# TODO: SDE-2 Task 14 - Create Auth Endpoints
# ==========================================
# 1. POST /auth/register
# 2. POST /auth/login
# 3. POST /auth/refresh
# 4. POST /auth/logout
# 5. GET /auth/me
# 6. Secure the expense endpoints using the get_current_user dependency

# ==========================================
# TODO: SDE-2 Task 26 - Load & Unit Testing
# ==========================================
# 1. Integrate robust unit testing for all endpoints using pytest.
# 2. Create load testing scripts (e.g., Locust or k6) to simulate 1000s of concurrent users.
# 3. Optimize DB connection pooling and analyze slow queries if load tests reveal bottlenecks.

# ==========================================
# TODO: SDE-2 Task 28 - Enterprise Readiness (Observability & Security)
# ==========================================
# 1. Integrate structured JSON logging (e.g., using structlog).
# 2. Add an exception tracking middleware (like Sentry).
# 3. Implement rate limiting using Redis (e.g., with fastapi-limiter).
# 4. Implement an audit log for critical write operations in the database.


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
