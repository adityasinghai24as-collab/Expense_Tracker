"""
Feature Flags Module (DEPRECATED)
=================================

The custom JSON environment variable feature flag system has been REMOVED.
This project has migrated to LaunchDarkly for enterprise feature management.

See docs/launchdarkly-integration-guide.md for the new implementation details.
"""

from fastapi import HTTPException, status
import os

def is_feature_enabled(flag_name: str) -> bool:
    raise NotImplementedError("Feature flags have migrated to LaunchDarkly. Please implement the LaunchDarkly Server-Side SDK.")

def require_feature(flag_name: str, flags: dict | None = None, user=None):
    """
    Role-Based Access Control (RBAC) check.
    
    NOTE: Global Feature Flags have migrated to LaunchDarkly (Task 63).
    Until LaunchDarkly is implemented, this dependency only enforces user subscription tiers.
    """
    # 1. Global Release Toggle (PENDING LAUNCHDARKLY MIGRATION)
    # TODO: Implement ldclient.get().variation(flag_name, context, False) here
    
    # 2. Role-Based Access Control (Subscription Tiers)
    if user is not None:
        if not user.features_enabled.get(flag_name, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your current subscription plan does not include access to this feature. Please upgrade your plan.",
            )

def get_flags() -> dict:
    return {}

def get_environment() -> str:
    return os.getenv("APP_ENV", "development")
