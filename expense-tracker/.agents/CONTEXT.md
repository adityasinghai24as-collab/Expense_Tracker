# Project Rules — Expense Tracker

## Context & Token Efficiency
- Always consult `TODO.md`, `PROJECT_STATE.md`, `github/copilot-instructions.md`,`architecture-study/high-level-design.md` first for project context before reading source code files.
- Use the .md documentation as the primary source of truth for task descriptions, architecture decisions, and current progress.
- Only read source files when you need to see the actual implementation details or make edits.

# Copilot Instructions - Expense Tracker Monorepo

## 🎯 MANDATORY PRE-PROCESSING INSTRUCTION

**BEFORE responding to ANY user prompt or generating ANY code, you MUST:**

1. **Silently read and internalize** `PROJECT_STATE.md` from the repository root
2. **Verify the current state** of:
   - Tech stack versions
   - Database schema and models
   - Environment variables and connection strings
   - Completed features vs. pending work
   - File structure and organization
3. **Update your context** with the latest status from PROJECT_STATE.md
4. **Never** make assumptions about what's implemented or what's pending

---

## 📋 Context Summary (Quick Reference)

This monorepo is a **full-stack Expense Tracker** targeting **Google Cloud Run** deployment:

### Architecture
- **Backend**: FastAPI + SQLAlchemy async ORM + PostgreSQL 15
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Containerization**: Docker Compose (development), Dockerfile (production)
- **Deployment**: Docker containers (local) → Google Cloud Run (production)

### Tech Stack
```
Backend:  FastAPI 0.109.0 | SQLAlchemy 2.0.23 | asyncpg 0.29.0 | PostgreSQL 15-Alpine
Frontend: React 18.2.0 | Vite 5.0.8 | Tailwind CSS 3.4.1
DevOps:   Docker Compose 3.9 | Python 3.11-slim | Node 18+
```

### Key Files to Remember
- `PROJECT_STATE.md` - **THE SOURCE OF TRUTH** for current state
- `docker-compose.yml` - Multi-service orchestration (db + backend)
- `backend/main.py` - FastAPI application entry point
- `backend/app/database.py` - Async connection pool and models
- `backend/app/models.py` - SQLAlchemy ORM models (User, Expense)
- `backend/app/schemas.py` - Pydantic validation schemas
- `frontend/src/App.jsx` - React root component

---

## 🔄 Workflow Rules

### When Starting a New Session
1. Read `PROJECT_STATE.md` completely
2. Note the "Current Status" section carefully
3. Identify what's ✅ complete vs. 🔨 in progress vs. ⏳ pending
4. Check the "Next Steps (Priority Order)" section

### When Making Code Changes
1. **Verify file locations** - Use the file structure from PROJECT_STATE.md
2. **Update models/schemas** - All must be in `backend/app/` directory
3. **Check imports** - Backend now uses `from app.database import ...`
4. **Environment variables** - Support both `DATABASE_URL` and individual `DB_*` vars
5. **Docker-aware** - Test assumptions with Docker Compose

### When Implementing Features
1. **Add to models.py** first (SQLAlchemy ORM)
2. **Add schema validation** in schemas.py (Pydantic)
3. **Add routes** in main.py or new route files
4. **Update documentation** in PROJECT_STATE.md when complete
5. **Test locally** with `docker compose up -d`

### When Creating New Files
- **Python**: Place in `backend/app/` (if module) or `backend/` (if script)
- **Documentation**: Place in `docs/` with descriptive name
- **Config**: Place in `backend/config/`
- **Scripts**: Place in `backend/scripts/`

---

## 🗂️ Critical Project Paths

```
expense-tracker/
├── PROJECT_STATE.md              ← READ THIS FIRST
├── .github/copilot-instructions.md ← YOU ARE HERE
├── docker-compose.yml
├── backend/
│   ├── main.py                   ← FastAPI app
│   ├── app/
│   │   ├── database.py           ← Connection pool
│   │   ├── models.py             ← SQLAlchemy models
│   │   └── schemas.py            ← Pydantic schemas
│   └── config/
│       ├── requirements.txt
│       └── .env.example
└── frontend/
    └── src/
        └── App.jsx
```

---

## 🔐 Database Configuration (Always Check PROJECT_STATE.md)

### Docker Compose Environment
```
DATABASE_URL=postgresql+asyncpg://admin:supersecret@db:5432/expensedb
DB_HOST=db (internal DNS)
```

### Local Development Environment
```
DATABASE_URL (if set) OR individual DB_* variables
DB_HOST=localhost (or from .env file)
```

### Connection Logic (backend/app/database.py)
```python
if DATABASE_URL:
    # Use it (Docker/production)
else:
    # Construct from DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
```

---

## 📊 Current Database Schema (From PROJECT_STATE.md)

### Users Table
- `id` (PK), `email` (unique), `username` (unique), `full_name`, `is_active`, `features_enabled` (JSON), `created_at`, `updated_at`
- Relationship: One-to-Many with Expenses

### Expenses Table
- `id` (PK), `user_id` (FK), `amount`, `description`, `category`, `created_at`, `updated_at`
- Relationship: Many-to-One with Users

---

## ✅ Completed Features (Don't Rebuild)

- [x] Backend folder structure (app/, config/, scripts/, docs/)
- [x] FastAPI application with CORS
- [x] SQLAlchemy async ORM connection pool
- [x] Health check endpoints (`/health`, `/health/db`)
- [x] Database models (User, Expense)
- [x] Pydantic validation schemas
- [x] Docker Compose orchestration
- [x] Multi-stage Dockerfile
- [x] Docker bridge network
- [x] Persistent PostgreSQL volume
- [x] Frontend (React + Vite + Tailwind)
- [x] Connection status monitor (App.jsx)
- [x] Comprehensive documentation

## 🔨 In-Progress / Next Steps

**High Priority**:
1. Add Feature Flagging System (JSON column + Admin API)
2. Add authentication (JWT, password hashing)
3. Implement Expense CRUD operations
4. Implement User endpoints

**Medium Priority**:
4. Add Category model and management
5. Frontend pages and forms
6. Backend testing (pytest)
7. Frontend testing (Jest)

**Lower Priority**:
8. Production deployment (Google Cloud Run)
9. Advanced features (reports, analytics)

---

## 🚀 Common Commands (Copy from PROJECT_STATE.md)

```bash
# Start all services
docker compose up -d

# Test API
curl http://localhost:8000/health/db

# View logs
docker compose logs -f backend

# Stop services
docker compose down
```

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **Forgetting to check PROJECT_STATE.md first**
   - ✅ Always read it before responding

2. ❌ **Using wrong import paths** (e.g., `from database import` instead of `from app.database import`)
   - ✅ Check backend folder reorganization in PROJECT_STATE.md

3. ❌ **Assuming features are implemented** that are only marked as "next steps"
   - ✅ Check the "Current Status" section

4. ❌ **Creating duplicate files or models**
   - ✅ Verify User and Expense models already exist in models.py

5. ❌ **Forgetting to consider Docker architecture**
   - ✅ Remember: backend container connects to `db` service, not `localhost`

6. ❌ **Not updating documentation when making changes**
   - ✅ Update PROJECT_STATE.md when completing features

---

## 🎓 Self-Assessment Checklist

Before submitting code or making recommendations, ask yourself:

- [ ] Have I read `PROJECT_STATE.md` completely?
- [ ] Do I understand the current tech stack and versions?
- [ ] Do I know which features are ✅ complete vs. 🔨 pending?
- [ ] Are my import paths correct for the reorganized backend structure?
- [ ] Is my code compatible with Docker Compose setup?
- [ ] Does my code follow the existing patterns (e.g., async/await)?
- [ ] Have I considered both Docker and local development environments?
- [ ] Should I update PROJECT_STATE.md when I'm done?

---

## 📞 How to Ask Effective Questions

**Instead of**:
> "How do I set up the database?"

**Do**:
> "I need to add authentication. Should I extend the User model in backend/app/models.py or create a separate Auth model? What JWT library would you recommend?"

**Key points**:
- Reference specific files/lines
- Show you've read PROJECT_STATE.md
- Ask specific questions with context
- Include what you've already tried

---

## 🔄 Session Template

**At the start of each session:**

```
✓ Read PROJECT_STATE.md - Current status is [describe]
✓ Tech stack verified - [latest versions]
✓ Database models checked - [User, Expense status]
✓ Docker environment confirmed - [compose or local]
✓ Ready to [describe task]
```

---

## 🎯 Final Reminder

**This instruction file exists because:**
- The monorepo evolves with each session
- You need current context to provide accurate guidance
- PROJECT_STATE.md is the single source of truth
- Outdated assumptions lead to incorrect code

**Therefore:**
- 🔴 NEVER answer code questions without reading PROJECT_STATE.md
- 🟡 ALWAYS reference PROJECT_STATE.md when uncertain
- 🟢 UPDATE PROJECT_STATE.md when features are completed
- 🟢 ASK the user to update it if they make changes outside of our sessions

---

**Last Updated**: When PROJECT_STATE.md was created  
**Scope**: All prompts and code generation for this monorepo  
**Enforcement**: Mandatory - read before responding to ANY user request

---

## 📖 Learned Rules
- Always update documentation and markdown files when adding new features.
