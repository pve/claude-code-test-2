import os

import pytest

from app.utils.environment import get_environment_type, is_ci_environment
from app.utils.validation import sanitize_input, validate_email, validate_string_length


@pytest.mark.unit
def test_ci_environment_detection():
    """Test CI environment detection utility."""
    # Test with CI environment variable set
    os.environ["CI"] = "true"
    assert is_ci_environment() is True

    # Clean up
    del os.environ["CI"]

    # Test with GitHub Actions environment
    os.environ["GITHUB_ACTIONS"] = "true"
    assert is_ci_environment() is True

    # Clean up
    del os.environ["GITHUB_ACTIONS"]

    # Test without CI environment
    assert is_ci_environment() is False


@pytest.mark.unit
def test_environment_type_detection():
    """Test environment type detection."""
    # Test development environment
    os.environ["FLASK_ENV"] = "development"
    assert get_environment_type() == "development"

    # Test production environment
    os.environ["FLASK_ENV"] = "production"
    assert get_environment_type() == "production"

    # Test default environment
    del os.environ["FLASK_ENV"]
    assert get_environment_type() == "development"  # Default


@pytest.mark.unit
def test_email_validation():
    """Test email validation utility."""
    # Valid emails
    assert validate_email("test@example.com") is True
    assert validate_email("user.name@domain.co.uk") is True
    assert validate_email("test+tag@example.org") is True

    # Invalid emails
    assert validate_email("invalid-email") is False
    assert validate_email("test@") is False
    assert validate_email("@example.com") is False
    assert validate_email("") is False
    assert validate_email(None) is False


@pytest.mark.unit
def test_input_sanitization():
    """Test input sanitization utility."""
    # Test basic sanitization
    assert sanitize_input("  hello world  ") == "hello world"
    assert sanitize_input("UPPERCASE") == "uppercase"

    # Test special characters
    result = sanitize_input('hello<script>alert("xss")</script>')
    assert "<script>" not in result
    assert "alert" not in result

    result2 = sanitize_input("test & encode")
    assert "&" not in result2

    # Test None and empty inputs
    assert sanitize_input(None) == ""
    assert sanitize_input("") == ""


@pytest.mark.unit
def test_sanitize_input_non_string():
    """Test input sanitization with non-string inputs."""
    # Test non-string input (should be converted to string)
    assert sanitize_input(123) == "123"
    assert sanitize_input(True) == "true"


@pytest.mark.unit
def test_validate_string_length():
    """Test string length validation utility."""
    # Test valid lengths
    assert validate_string_length("hello", 0, 10) is True
    assert validate_string_length("test", 4, 4) is True
    assert validate_string_length("", 0, 5) is True
    
    # Test invalid lengths
    assert validate_string_length("toolong", 0, 5) is False
    assert validate_string_length("short", 10, 20) is False
    
    # Test non-string input
    assert validate_string_length(123, 0, 10) is False
    assert validate_string_length(None, 0, 10) is False
