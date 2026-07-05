"""Email validation utilities.

These are used by signup-api and billing-api for input validation.
Changes here affect multiple services — test thoroughly.
"""

import re

# RFC 5322 simplified — practical, not exhaustive
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> bool:
    """Check that email has a valid format.

    Validates:
    - Contains exactly one '@'
    - Local part is non-empty
    - Domain has at least one dot
    - No whitespace

    Returns True if valid, False otherwise.
    """
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def extract_domain(email: str) -> str | None:
    """Extract the domain part of an email address.

    Returns None if the email is invalid.
    """
    if not validate_email(email):
        return None
    return email.rsplit("@", 1)[-1]
