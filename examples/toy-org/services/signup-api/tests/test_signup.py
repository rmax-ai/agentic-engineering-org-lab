"""Unit tests for signup-api validators."""

from signup_api.validators import validate_email, validate_name, validate_password


def test_validate_email_valid():
    assert validate_email("user@example.com") is True
    assert validate_email("a@b.co") is True
    assert validate_email("test.user+tag@domain.co.uk") is True


def test_validate_email_no_at():
    assert validate_email("userexample.com") is False


def test_validate_email_no_domain():
    assert validate_email("user@") is False


def test_validate_email_no_dot_in_domain():
    assert validate_email("user@localhost") is False


def test_validate_email_empty_local():
    assert validate_email("@example.com") is False


def test_validate_password_valid():
    assert validate_password("12345678") is True
    assert validate_password("abcdefgh") is True
    assert validate_password("longenough") is True


def test_validate_password_too_short():
    assert validate_password("short") is False
    assert validate_password("7chars!") is False


def test_validate_password_exact_min():
    assert validate_password("12345678") is True  # exactly 8


def test_validate_name_valid():
    assert validate_name("Alice") is True
    assert validate_name("A") is True
    assert validate_name("a" * 100) is True


def test_validate_name_empty():
    assert validate_name("") is False


def test_validate_name_too_long():
    assert validate_name("a" * 101) is False
