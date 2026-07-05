"""Validation utilities for signup-api.

Email validation is delegated to the shared validation library.
Password and name validation are signup-specific.
"""

from validation.email import validate_email  # noqa: F401 — re-exported


def validate_password(password: str) -> bool:
    """Check password is at least 8 characters."""
    return len(password) >= 8


def validate_name(name: str) -> bool:
    """Check name is non-empty and ≤100 characters."""
    return 0 < len(name) <= 100
