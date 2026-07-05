"""String sanitization and validation utilities.

Used by billing-api for input sanitization.
"""


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize a string by stripping whitespace and truncating.

    Returns the cleaned string. Never raises.
    """
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def validate_length(value: str, min_len: int = 1, max_len: int = 1000) -> bool:
    """Check that a string's length is within bounds.

    Returns True if valid, False otherwise.
    """
    if not isinstance(value, str):
        return False
    return min_len <= len(value.strip()) <= max_len


def normalize_whitespace(value: str) -> str:
    """Collapse multiple whitespace characters into single spaces.

    Returns the normalized string. Never raises.
    """
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())
