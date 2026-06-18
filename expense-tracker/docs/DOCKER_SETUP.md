# Docker Setup for Expense Tracker

This document explains how to run the full stack (PostgreSQL + FastAPI backend) using Docker and Docker Compose.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Quick Start

### Start all services
```bash
# From the repository root (expense-tracker/)
docker compose up -d
```

The `-d` flag runs containers in the background (detached mode).

### Verify services are running
```bash
docker compose ps
```

You should see both `expense-tracker-postgres` and `expense-tracker-backend` running.

### Check service logs
```bash
# All services
docker compose logs -f

# Only backend
docker compose logs -f backend

# Only database
docker compose logs -f db
```

### Stop all services
```bash
docker compose down
```

### Stop and remove data (clean slate)
```bash
docker compose down -v
```

The `-v` flag removes volumes (including the database data).

---

## Service Details

### Database (db)

- **Image**: postgres:15-alpine
- **Container name**: expense-tracker-postgres
- **Port**: 5432 (host:container)
- **Credentials**:
  - Username: `admin`
  - Password: `supersecret`
  - Database: `expensedb`
- **Volume**: `postgres_data` (persists data across restarts)
- **Health check**: Verifies PostgreSQL is ready before backend connects

### Backend (backend)

- **Build context**: `./backend`
- **Dockerfile**: `./backend/Dockerfile`
- **Container name**: expense-tracker-backend
- **Port**: 8000 (host:container)
- **Depends on**: `db` service (waits for healthy status)
- **Environment Variables**:
  - `DATABASE_URL`: `postgresql+asyncpg://admin:supersecret@db:5432/expensedb`
  - `DB_USER`: `admin`
  - `DB_PASSWORD`: `supersecret`
  - `DB_HOST`: `db` (Docker internal DNS)
  - `DB_PORT`: `5432`
  - `DB_NAME`: `expensedb`

---

## Network Configuration

Both services connect through a custom bridge network: `expense-tracker-network`

**Key Feature**: Services communicate via container name (DNS):
- Backend connects to database as: `postgresql+asyncpg://admin:supersecret@db:5432/expensedb`
- The hostname `db` resolves to the database container's IP automatically

---

## Testing the Connection

### Test API health
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "message": "Expense Tracker API is running"
}
```

### Test database connection
```bash
curl http://localhost:8000/health/db
```

Response (on success):
```json
{
  "status": "ok",
  "message": "Connected successfully",
  "database": "postgresql"
}
```

### Access interactive API docs
Open in browser: `http://localhost:8000/docs`

---

## Building Images Manually

Rebuild backend image after code changes:
```bash
docker compose build backend
```

Rebuild both images:
```bash
docker compose build
```

---

## Accessing PostgreSQL Directly

### Connect with psql from host
```bash
psql -h localhost -U admin -d expensedb -p 5432
```

Password: `supersecret`

### Connect from within backend container
```bash
docker compose exec backend psql -h db -U admin -d expensedb
```

---

## Viewing Database Contents

From host machine:
```bash
docker compose exec db psql -U admin -d expensedb -c "SELECT * FROM users;"
```

Or use psql directly:
```bash
psql -h localhost -U admin -d expensedb
# Inside psql:
\dt  # list tables
SELECT * FROM users;
```

---

## Troubleshooting

### Backend can't connect to database

**Error**: `Connection refused` or `could not translate host name "db" to address`

**Solutions**:
1. Check if `db` service is healthy:
   ```bash
   docker compose ps
   ```
   Status should show "healthy"

2. Check backend logs:
   ```bash
   docker compose logs backend
   ```

3. Ensure backend depends on db:
   ```bash
   docker compose ps -a
   ```

### Port 5432 already in use
```bash
# Find what's using port 5432
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows

# Or change port in docker-compose.yml
# Change "5432:5432" to "5433:5432" to use port 5433 on host
```

### Port 8000 already in use
```bash
# Change port in docker-compose.yml
# Change "8000:8000" to "8001:8000" to use port 8001 on host
```

### Database won't start

Check database logs:
```bash
docker compose logs db
```

Common issues:
- Insufficient disk space
- Permission issues with volume directory
- Previous volume has corrupted data (use `docker compose down -v` to reset)

### Backend crashes immediately
```bash
docker compose logs backend
```

Common issues:
- Missing dependencies (rebuild image)
- Database URL format incorrect
- Waiting for database but timeout too short (increase `timeout` in healthcheck)

---

## Environment Variables

### Docker Compose vs Local Development

**Docker Compose** (automatic from docker-compose.yml):
```env
DATABASE_URL=postgresql+asyncpg://admin:supersecret@db:5432/expensedb
DB_HOST=db
```

**Local Development** (from .env file):
```env
DATABASE_URL=postgresql+asyncpg://admin:supersecret@localhost:5432/expensedb
DB_HOST=localhost
```

Backend supports both via `app/database.py` logic.

---

## Production Deployment to Koyeb

When deploying to Koyeb:

1. **Database**: Use Koyeb Postgres add-on or external managed database
2. **Backend**: Push Dockerfile to GitHub, configure Koyeb to build from it
3. **Environment Variables**: Set in Koyeb dashboard:
   - `DATABASE_URL`: Your Koyeb database URL
   - Other variables as needed

No need to modify `docker-compose.yml` for Koyeb—it's only for local development.

---

## Named Volume Management

### List volumes
```bash
docker volume ls
```

### Inspect volume
```bash
docker volume inspect expense-tracker-postgres-data
```

### Remove volume
```bash
docker volume rm expense-tracker-postgres-data
```

---

## Restart Strategies

The backend service has `restart: unless-stopped`, meaning:
- Automatically restarts if it crashes
- Won't restart if you explicitly stop it with `docker compose down`
- Respects `docker compose up` and manual stops

To remove auto-restart, edit `docker-compose.yml`:
```yaml
# Change from:
restart: unless-stopped
# To:
restart: "no"
```

---

## Next Steps

1. ✅ Docker setup complete
2. → Run `docker compose up -d` to start
3. → Test with `curl http://localhost:8000/health/db`
4. → Build features in backend using SQLAlchemy ORM
5. → Use `docker compose down` when done
6. → Deploy to Koyeb when ready
