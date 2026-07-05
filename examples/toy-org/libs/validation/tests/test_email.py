"""Tests for email validation."""

from validation.email import extract_domain, validate_email


def test_valid_simple_email():
    assert validate_email("user@example.com") is True


def test_valid_email_with_subdomain():
    assert validate_email("test@mail.example.co.uk") is True


def test_valid_email_with_plus():
    assert validate_email("user+tag@example.com") is True


def test_invalid_no_at():
    assert validate_email("userexample.com") is False


def test_invalid_no_local_part():
    assert validate_email("@example.com") is False


def test_invalid_no_domain_dot():
    assert validate_email("user@localhost") is False


def test_invalid_empty():
    assert validate_email("") is False


def test_invalid_none():
    assert validate_email(None) is False


def test_invalid_whitespace():
    assert validate_email("user@example .com") is False


def test_valid_strips_whitespace():
    assert validate_email("  user@example.com  ") is True


def test_extract_domain_valid():
    assert extract_domain("user@example.com") == "example.com"


def test_extract_domain_invalid():
    assert extract_domain("notanemail") is None
