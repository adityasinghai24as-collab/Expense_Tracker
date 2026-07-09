"""
Feature Flags Module
====================
A lightweight, environment-aware feature flag system.

Flags are loaded from the FEATURE_FLAGS environment variable (a JSON string),
which is injected by Terraform into the Cloud Run container per environment.

Usage in endpoints:
    from app.feature_flags import require_feature, get_flags

    @app.get("/receipts/scan")
    async def scan_receipt(flags: dict = Depends(get_flags)):
        require_feature("enable_receipt_scanning", flags)
        ...
"""

import json
import os
from fastapi import HTTPException, status


# ---------------------------------------------------------------------------
# Default flags — used as fallback when FEATURE_FLAGS env var is absent
# (e.g., during local development).
# ---------------------------------------------------------------------------
_DEFAULT_FLAGS: dict[str, bool] = {
    "enable_receipt_scanning": False,
    "enable_smart_categorization": False,
    "enable_debug_mode": True,
    "enable_rate_limiting": False,
}


def _load_flags() -> dict[str, bool]:
    """Load feature flags from the FEATURE_FLAGS environment variable.

    Falls back to _DEFAULT_FLAGS if the env var is missing or malformed.
    """
    raw = os.getenv("FEATURE_FLAGS")
    if not raw:
        return dict(_DEFAULT_FLAGS)
    try:
        parsed = json.loads(raw)
        # Merge: defaults first, then overrides from env
        merged = {**_DEFAULT_FLAGS, **parsed}
        return merged
    except (json.JSONDecodeError, TypeError):
        print("⚠️  FEATURE_FLAGS env var is malformed, using defaults.")
        return dict(_DEFAULT_FLAGS)


# Singleton instance — loaded once at import time.
# Re-deploy the container (or restart the process) to pick up changes.
FLAGS: dict[str, bool] = _load_flags()


def is_feature_enabled(flag_name: str) -> bool:
    """Check whether a given feature flag is enabled."""
    return FLAGS.get(flag_name, False)


def require_feature(flag_name: str, flags: dict[str, bool] | None = None):
    """Raise 404 if the feature is disabled.

    This makes gated endpoints disappear entirely for users
    when the feature is turned off, rather than returning a 403.
    """
    source = flags if flags is not None else FLAGS
    if not source.get(flag_name, False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )


def get_flags() -> dict[str, bool]:
    """FastAPI dependency — inject the current flag state into a route."""
    return FLAGS


def get_environment() -> str:
    """Return the current application environment name."""
    return os.getenv("APP_ENV", "development")
