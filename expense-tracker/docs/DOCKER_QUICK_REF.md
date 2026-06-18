# Docker Quick Reference - Expense Tracker

## Essential Commands

### Start Services (Background)
```bash
docker compose up -d
```
Both `db` and `backend` start. Backend waits for DB to be healthy.

### Stop Services
```bash
docker compose down
```
Stops containers but preserves data in volumes.

### Stop & Remove Everything (Including Data)
```bash
docker compose down -v
```
Use `-v` to remove volumes. Data is lost.

### View Running Services
```bash
docker compose ps
```

### View Logs
```bash
docker compose logs -f              # All services
docker compose logs -f backend      # Backend only
docker compose logs -f db           # Database only
docker compose logs --tail=50 backend  # Last 50 lines
```

---

## Testing Endpoints

### API Health
```bash
curl http://localhost:8000/health
```

### Database Connection
```bash
curl http://localhost:8000/health/db
```

### Interactive API Docs
```
http://localhost:8000/docs
```

---

## Accessing Containers

### Execute command in backend
```bash
docker compose exec backend ls -la
docker compose exec backend python -m pip list
```

### Access PostgreSQL from backend
```bash
docker compose exec backend psql -h db -U admin -d expensedb
```

### Access PostgreSQL from host
```bash
psql -h localhost -U admin -d expensedb -p 5432
```
Password: `supersecret`

---

## Building & Rebuilding

### Rebuild backend image
```bash
docker compose build backend
```

### Rebuild all images
```bash
docker compose build
```

### Build without cache
```bash
docker compose build --no-cache backend
```

---

## Database Operations

### List tables
```bash
docker compose exec db psql -U admin -d expensedb -c "\\dt"
```

### View specific table
```bash
docker compose exec db psql -U admin -d expensedb -c "SELECT * FROM users;"
```

### Run SQL file
```bash
docker compose exec -T db psql -U admin -d expensedb < schema.sql
```

### Create database backup
```bash
docker compose exec db pg_dump -U admin expensedb > backup.sql
```

### Restore database from backup
```bash
docker compose exec -T db psql -U admin -d expensedb < backup.sql
```

---

## Debugging

### Inspect container details
```bash
docker compose ps
docker inspect expense-tracker-backend
docker inspect expense-tracker-postgres
```

### Check network
```bash
docker network ls
docker network inspect expense-tracker-network
```

### Tail logs in real-time
```bash
docker compose logs -f --timestamps backend
```

### Check container resource usage
```bash
docker stats
```

---

## Volume Management

### List volumes
```bash
docker volume ls | grep expense
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

## Cleanup

### Remove stopped containers
```bash
docker compose down
docker container prune
```

### Remove unused images
```bash
docker image prune
```

### Remove unused volumes
```bash
docker volume prune
```

### Full cleanup (careful!)
```bash
docker system prune -a --volumes
```

---

## Port Forwarding (if needed)

### Change backend port (if 8000 is in use)
Edit `docker-compose.yml`:
```yaml
backend:
  ports:
    - "8001:8000"  # Use 8001 on host, 8000 in container
```

### Change database port (if 5432 is in use)
Edit `docker-compose.yml`:
```yaml
db:
  ports:
    - "5433:5432"  # Use 5433 on host, 5432 in container
```

Then rebuild:
```bash
docker compose up -d
```

---

## Environment Variables

### View backend environment
```bash
docker compose exec backend env | grep -E "(DATABASE|DB_)"
```

### Temporarily override variables
```bash
DB_HOST=localhost docker compose up -d backend
```

---

## Deployment Checklist

Before deploying to Koyeb:
- [ ] Test locally: `docker compose up -d`
- [ ] Verify health: `curl http://localhost:8000/health/db`
- [ ] Check logs: `docker compose logs backend`
- [ ] Stop cleanly: `docker compose down`
- [ ] Push to GitHub (Dockerfile + code)
- [ ] Configure Koyeb DATABASE_URL env var
- [ ] Deploy via Koyeb dashboard

---

## Common Issues & Solutions

| Issue | Command |
|-------|---------|
| Backend won't connect to DB | `docker compose logs backend` |
| Port already in use | Edit `docker-compose.yml` and change port |
| Data lost after down | Use `docker compose stop` instead of `down` |
| Want to reset database | `docker compose down -v && docker compose up -d` |
| Need to rebuild after code change | `docker compose build backend && docker compose up -d` |
| Container exited | `docker compose logs service_name` |

---

## Useful Docker Files

- `docker-compose.yml` - Defines both services
- `backend/Dockerfile` - Builds backend image
- `backend/.dockerignore` - Excludes files from build context
- `docs/DOCKER_SETUP.md` - Full documentation
