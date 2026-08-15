# 🛡️ Role-Based Access Control (RBAC)

While global feature rollouts are managed by [LaunchDarkly](launchdarkly-integration-guide.md), **user-level permissions** are managed internally via our Subscription Tier system (RBAC).

Even if a feature is globally turned on in LaunchDarkly, a user must have the appropriate subscription tier to access it.

## Available Tiers & Feature Mapping

Users are assigned a `role` in the PostgreSQL database (`users.role`).

*   **`free` (Basic Plan)**: Basic Expense CRUD, Category Management, Dashboard.
*   **`pro` (Pro Plan)**: Unlocks Receipt Scanning (OCR), Advanced Analytics (PDF/CSV Exports), and Budgets & Alerts.
*   **`enterprise` (Enterprise Plan)**: Unlocks the Autonomous Agentic AI, Local RAG, and Shared Wallets.
*   **`admin`**: Has full access to all features globally.

## How to Upgrade a User Role (For Local Testing)

To test features locked behind the `pro` or `enterprise` tiers, you must manually upgrade your test user in the PostgreSQL database.

**Via Docker (psql):**
```bash
# 1. Access the database container
docker exec -it expense-tracker-postgres-1 psql -U admin -d expensedb

# 2. Update your user's role to 'enterprise'
UPDATE users SET role = 'enterprise' WHERE email = 'your.email@example.com';

# 3. Type \q to exit
\q
```

## How to Enforce RBAC in FastAPI

Use the `require_feature` dependency in your routers. This dependency evaluates the user's `features_enabled` property (defined in `backend/app/models.py`).

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.feature_flags import require_feature
from app.models import User

router = APIRouter()

@router.post("/ai/chat")
async def chat_with_agent(
    prompt: str,
    current_user: User = Depends(get_current_user)
):
    # This automatically throws a 403 Forbidden if the user is on the Free tier!
    require_feature("enable_autonomous_agent", user=current_user)
    
    return {"reply": "Agent response..."}
```

---

## 🔗 See Also

- [LaunchDarkly Integration Guide](launchdarkly-integration-guide.md) — Global feature flag management (complements RBAC)
- [Feature Flags & RBAC (Deprecated)](FEATURE_FLAGS_AND_RBAC.md) — Previous implementation (now redirects here)
- [Security Checklist](../architecture-study/security-checklist.md) — Authentication & Authorization requirements
- [User Guide](USER_GUIDE.md) — User-facing feature tier descriptions
- [TODO.md](../TODO.md) — Phase 12 (LaunchDarkly + RBAC integration)
- **Key code files**: [`backend/app/feature_flags.py`](../backend/app/feature_flags.py) (`require_feature`), [`backend/app/models.py`](../backend/app/models.py) (`features_enabled` property), [`backend/app/auth.py`](../backend/app/auth.py)
