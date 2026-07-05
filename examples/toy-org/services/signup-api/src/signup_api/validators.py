"""Validation utilities for signup-api."""


def validate_email(email: str) -> bool:
    """Check email contains @ with a domain part containing a dot."""
    if "@" not in email:
        return False
    local, domain = email.rsplit("@", 1)
    if not local or "." not in domain:
        return False
    return True


def validate_password(password: str) -> bool:
    """Check password is at least 8 characters."""
    return len(password) >= 8


def validate_name(name: str) -> bool:
    """Check name is non-empty and ≤100 characters."""
    return 0 < len(name) <= 100
