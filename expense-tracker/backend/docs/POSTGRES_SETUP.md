# PostgreSQL Setup Guide

## Prerequisites

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer (recommended: keep default options)
3. Remember the password you set for the `postgres` user
4. PostgreSQL will be available at `localhost:5432`

### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

---

## Local Setup Instructions

### 1. Create Database and User

**Connect to PostgreSQL:**
```bash
# Windows (PowerShell)
psql -U postgres

# macOS/Linux
psql -U postgres
```

**Inside psql, run these commands:**
```sql
-- Create database
CREATE DATABASE expense_tracker;

-- Verify creation
\l
```

Then exit psql by typing `\q` and pressing Enter.

### 2. Configure Environment Variables

In the `backend/` directory, create a `.env` file:

```bash
# Copy the example file
copy .env.example .env          # Windows PowerShell
# or
cp .env.example .env            # macOS/Linux
```

Edit `.env` with your PostgreSQL credentials:
```env
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expense_tracker
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Test Database Connection

```bash
# From the backend directory
python test_db_connection.py
```

**Expected output:**
```
🚀 DATABASE CONNECTION TEST SUITE 🚀
============================================================
🔍 Testing SYNCHRONOUS PostgreSQL Connection
============================================================
Host: localhost:5432
Database: expense_tracker
User: postgres
------------------------------------------------------------
✅ SUCCESS: Synchronous connection established!
   Message: Connected successfully

============================================================
🔍 Testing ASYNCHRONOUS PostgreSQL Connection
============================================================
Host: localhost:5432
Database: expense_tracker
User: postgres
------------------------------------------------------------
✅ SUCCESS: Asynchronous connection established!
   Message: Connected successfully

============================================================
SUMMARY
============================================================
Synchronous: ✅ PASS
Asynchronous: ✅ PASS
============================================================

✅ All tests passed! Database is ready to use.
```

### 5. Start the Backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 6. Verify Connection via API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Database Health Check:**
```bash
curl http://localhost:8000/health/db
```

Expected response:
```json
{
  "status": "ok",
  "message": "Connected successfully",
  "database": "postgresql"
}
```

---

## Database Connection Pool Configuration

The connection uses:
- **Async driver**: `asyncpg` (high-performance async PostgreSQL client)
- **ORM**: SQLAlchemy 2.0 with async support
- **Pool**: Configured with `pool_pre_ping=True` to avoid stale connections

---

## Troubleshooting

### Error: "could not translate host name "localhost" to address"
- PostgreSQL service isn't running
- **Windows**: Check Services for PostgreSQL
- **macOS**: Run `brew services start postgresql@15`
- **Linux**: Run `sudo systemctl start postgresql`

### Error: "password authentication failed"
- Verify credentials in `.env` match your PostgreSQL setup
- Reset password: `ALTER USER postgres WITH PASSWORD 'new_password';`

### Error: "database "expense_tracker" does not exist"
- Create the database:
  ```bash
  psql -U postgres -c 'CREATE DATABASE expense_tracker;'
  ```

### Error: "port 5432 refused"
- PostgreSQL isn't listening on the configured port
- Verify `.env` has correct `DB_PORT`
- Check if another service is using port 5432

---

## Verifying PostgreSQL Installation

**Check if PostgreSQL is running:**

Windows (PowerShell):
```powershell
Get-Service | Where-Object {$_.Name -like "*postgres*"}
```

macOS:
```bash
brew services list | grep postgres
```

Linux:
```bash
sudo systemctl status postgresql
```

**Test connection with psql:**
```bash
psql -h localhost -U postgres -d expense_tracker -c "SELECT version();"
```

---

## Next Steps

1. ✅ Database connections are working
2. Define your data models in `backend/models.py`
3. Create database migrations using Alembic
4. Implement expense tracking schemas and routes
5. Add authentication and authorization

---

## Cloudflare Workers Integration

When deploying to Cloudflare Workers, use **Hyperdrive** for database connectivity:

1. Create a Hyperdrive config in Cloudflare dashboard
2. Uncomment and configure in `wrangler.toml`:
   ```toml
   [[hyperdrive]]
   id = "your_hyperdrive_id"
   binding = "DB"
   ```

3. Update your connection string in production environment variables

For more info: https://developers.cloudflare.com/hyperdrive/
