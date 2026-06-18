# QUICK REFERENCE CARD

## PostgreSQL Connection - One-Liner Setup

```powershell
# Windows PowerShell - Copy & paste to terminal
cd .\expense-tracker\backend; pip install -r requirements.txt; python setup_db.py
```

```bash
# macOS/Linux - Copy & paste to terminal
cd expense-tracker/backend && pip install -r requirements.txt && python setup_db.py
```

---

## Essential Commands

### Check PostgreSQL Status
```powershell
# Windows
Get-Service PostgreSQL* | Select Name, Status

# macOS
brew services list | grep postgres

# Linux
sudo systemctl status postgresql
```

### Test Connection Immediately
```powershell
python test_db_connection.py
```

### Start Backend
```powershell
python main.py
```

### Verify API is Working
```powershell
# Terminal 1: Server is running
# Terminal 2: Run these checks
curl http://localhost:8000/health
curl http://localhost:8000/health/db
```

---

## Environment Variables (.env)

```env
DB_USER=postgres
DB_PASSWORD=postgres          # Change this!
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expense_tracker
```

---

## Database Creation

```bash
# Create database
psql -U postgres -c "CREATE DATABASE expense_tracker;"

# Verify it was created
psql -U postgres -l | grep expense_tracker

# Connect to it
psql -U postgres -d expense_tracker
```

---

## Troubleshooting in 60 Seconds

**"Connection refused"**
```powershell
Get-Service PostgreSQL* | Start-Service
```

**"Password authentication failed"**
```bash
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'newpass';"
# Update .env with new password
```

**"Database does not exist"**
```bash
psql -U postgres -c "CREATE DATABASE expense_tracker;"
```

---

## API Health Checks

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `GET /health` | API status | `curl http://localhost:8000/health` |
| `GET /health/db` | Database status | `curl http://localhost:8000/health/db` |
| `GET /docs` | Interactive API docs | Open in browser |

---

## Connection Details

| Component | Value |
|-----------|-------|
| Driver | asyncpg (async), psycopg2 (sync) |
| Host | localhost (default) |
| Port | 5432 (default) |
| Database | expense_tracker |
| User | postgres |
| ORM | SQLAlchemy 2.0 |

---

## File Guide

| File | Usage |
|------|-------|
| `database.py` | Import `get_db`, `check_db_connection()` in your routes |
| `models.py` | Define your SQLAlchemy models here |
| `schemas.py` | Define your Pydantic schemas here |
| `main.py` | Add your FastAPI routes here |
| `.env` | Your local credentials (never commit!) |

---

## Example: Using DB in a Route

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User

app = FastAPI()

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    # Your query here
    result = await db.execute(...)
    return result.scalars().all()
```

---

## Next Steps

1. ✅ Backend connection working
2. → Start writing models in `models.py`
3. → Create routes in `main.py`
4. → Test with `http://localhost:8000/docs`
5. → Integrate frontend (proxy already configured)
6. → Deploy to Cloudflare Workers

---

## Need Help?

- **Setup Issues**: Read `POSTGRES_SETUP.md`
- **Architecture**: Read `DB_INTEGRATION.md`
- **API Docs**: Open `http://localhost:8000/docs` when server is running
- **Code Examples**: Check `models.py` and `schemas.py`
