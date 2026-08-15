# 🚀 LaunchDarkly Integration Guide

This guide provides step-by-step instructions for integrating LaunchDarkly into the Expense Tracker application to provide enterprise-grade feature flag management, kill switches, and canary releases.

## 1. Environment Setup (LaunchDarkly Dashboard)

Before writing code, configure your environments in the LaunchDarkly UI.

1. **Create Environments**: Ensure you have exactly three environments mapping to our infrastructure: `Production`, `Staging`, and `Development`.
2. **SDK Keys**: For each environment, you will need to retrieve:
   - **SDK Key**: (Backend) Server-side SDK key for FastAPI.
   - **Client-side ID**: (Frontend) Client-side ID for React/Vite.
3. **Set Environment Variables**: Add these keys to your `.env` files (e.g., `backend/config/.env.development` and `frontend/.env.development`).
   ```env
   # Backend
   LD_SDK_KEY=sdk-xxxx-xxxx
   # Frontend
   VITE_LD_CLIENT_ID=client-xxxx-xxxx
   ```

---

## 2. Backend Integration (FastAPI / Python)

The backend must use the **Server-Side SDK** to perform local evaluations with low latency.

### 2.1 Initialization (Singleton Pattern)
LaunchDarkly's Python SDK must be initialized as a singleton when the FastAPI application starts to prevent memory leaks and ensure the ruleset is cached locally.

*   **Install**: `pip install launchdarkly-server-sdk`
*   **Implementation**: Create an `app/launchdarkly_client.py` module. Initialize the `ldclient` instance on `startup` events and gracefully close it on `shutdown`.

```python
# Pseudo-code Example
import ldclient
from ldclient.config import Config

def init_ld():
    ldclient.set_config(Config(os.getenv("LD_SDK_KEY")))
    if not ldclient.get().is_initialized():
        print("LaunchDarkly initialization failed")
```

### 2.2 Local Evaluation & Contexts
When evaluating a flag (e.g., a "Kill Switch" to pause expense creation), always pass a robust Context.
*   The Context should map to our `users` table: `key=user.id`, `email=user.email`, `plan=user.role`.
*   Replace our custom `require_feature` dependency with a LaunchDarkly evaluation: `ldclient.get().variation("enable-ai", context, False)`.

---

## 3. Frontend Integration (React / Vite)

The frontend requires the **Client-Side SDK** (`launchdarkly-react-client-sdk`).

### 3.1 Initialization (React Context)
*   **Install**: `npm install launchdarkly-react-client-sdk`
*   **Implementation**: Wrap your `<App />` in the `withLDProvider` Higher-Order Component (HOC) or the `LDProvider` context at the root level (`main.jsx`).

### 3.2 Dynamic Context Updates
*   When a user logs in, use the `useLDClient()` hook to call `ldClient.identify(context)` to fetch the feature flags specifically evaluated for their user role (Free vs Pro).

---

## 4. Testing & Local Development Best Practices

### Local Development (Offline Mode)
Developers should not need active internet connections or real LaunchDarkly keys to develop locally.
*   **Backend**: Use the LaunchDarkly `TestData` data source. This allows you to define flag values in a local JSON file (`ld-flags.json`) for local development without hitting the live LaunchDarkly servers.
*   **Frontend**: Use the `LDProvider` with a mock client or pass static flag maps during local development.

### Naming Conventions & Lifecycle
*   **Naming**: Use kebab-case. Prefix flags logically: `feat-` (new features), `kill-` (kill switches), `ops-` (infrastructure toggles).
*   **Lifecycle**: Feature flags incur technical debt. Once a `feat-` flag is fully rolled out to 100% of users, schedule a Jira ticket to remove the flag from both LaunchDarkly and the codebase.

---

## 🔗 See Also

- [RBAC](RBAC.md) — Subscription tier gating (complements LaunchDarkly global flags)
- [Feature Flags & RBAC (Deprecated)](FEATURE_FLAGS_AND_RBAC.md) — Previous static implementation
- [High-Level Design](../architecture-study/high-level-design.md) — System architecture (§ Feature Flag Service)
- [TODO.md](../TODO.md) — Phase 12 (Tasks 62-66) for LaunchDarkly implementation
- **Key code files**: [`backend/app/feature_flags.py`](../backend/app/feature_flags.py), [`frontend/src/context/FeatureFlagContext.jsx`](../frontend/src/context/FeatureFlagContext.jsx), [`backend/main.py`](../backend/main.py) (startup/shutdown lifecycle)
