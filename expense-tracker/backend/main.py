from fastapi import FastAPI, Depends, Request
import os
import sentry_sdk
from starlette.datastructures import MutableHeaders
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import (
    get_db,
    check_db_connection,
    check_db_connection_sync,
    init_db,
)
from app.routers import auth_routes, user_routes, expense_routes, category_routes
from app.exceptions import register_exception_handlers
from app.logger import setup_logging

# ==========================================
# Task 23 - Observability (Logging & Sentry) Completed
# ==========================================
# Initialize structured logging
setup_logging()

# Initialize Sentry if configured
sentry_dsn = os.environ.get("SENTRY_DSN", "")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
    )

app = FastAPI(title="Expense Tracker API", version="1.0.0")

# Register Error Handlers
register_exception_handlers(app)

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


@app.get(
    "/health", 
    response_model=HealthResponse,
    responses={
        200: {"description": "API is healthy and running"}
    }
)
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Expense Tracker API is running"}


@app.get(
    "/health/db", 
    response_model=DBHealthResponse,
    responses={
        200: {"description": "Database connection status checked (can be 'ok' or 'error' depending on the database state)"}
    }
)
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

# User Endpoints (Task 18 Completed)
app.include_router(user_routes.router, prefix="/users", tags=["Users"])

# Expense Endpoints (Task 19 Completed)
app.include_router(expense_routes.router, prefix="/expenses", tags=["Expenses"])

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])

# Error Handling (Task 20 Completed)

# Category Endpoints (Task 21 Completed)
app.include_router(category_routes.router, prefix="/categories", tags=["Categories"])

# TODO: Task 37 - Backend Feature Flags: Add GET /admin/feature-flags endpoint
# TODO: Task 38 - Production Hardening: Add rate limiting
# TODO: Task 46 - Rate Limiting: Implement Rate Limiting on the backend API


# ==========================================
# Task 22 - Security Headers (Completed)
# ==========================================
class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-Frame-Options", "DENY")
                headers.append("X-XSS-Protection", "1; mode=block")
                headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
                headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
                headers.append("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com;")
            await send(message)

        await self.app(scope, receive, send_wrapper)

app.add_middleware(SecurityHeadersMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
