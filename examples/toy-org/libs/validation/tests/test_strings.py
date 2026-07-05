"""Tests for string sanitization and validation."""

from validation.strings import normalize_whitespace, sanitize_string, validate_length


def test_sanitize_strips_whitespace():
    assert sanitize_string("  hello  ") == "hello"


def test_sanitize_truncates():
    assert sanitize_string("a" * 2000, max_length=10) == "a" * 10


def test_sanitize_non_string():
    assert sanitize_string(123) == ""


def test_sanitize_none():
    assert sanitize_string(None) == ""


def test_sanitize_empty():
    assert sanitize_string("") == ""


def test_validate_length_valid():
    assert validate_length("hello", min_len=1, max_len=100) is True


def test_validate_length_too_short():
    assert validate_length("", min_len=1, max_len=100) is False


def test_validate_length_too_long():
    assert validate_length("a" * 101, min_len=1, max_len=100) is False


def test_validate_length_non_string():
    assert validate_length(None) is False


def test_validate_length_whitespace_only():
    # "   " stripped has length 0, so fails min_len=1
    assert validate_length("   ", min_len=1) is False


def test_normalize_whitespace_collapses():
    assert normalize_whitespace("hello   world") == "hello world"


def test_normalize_whitespace_strips_ends():
    assert normalize_whitespace("  hello world  ") == "hello world"


def test_normalize_whitespace_non_string():
    assert normalize_whitespace(None) == ""
