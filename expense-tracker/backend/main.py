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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
