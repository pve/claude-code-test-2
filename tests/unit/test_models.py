import pytest

from app.models.user import User


@pytest.mark.unit
def test_user_creation():
    """Test user model creation."""
    user = User("John Doe", "john@example.com")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"


@pytest.mark.unit
def test_user_validation():
    """Test user input validation."""
    # Valid user
    user = User("Jane Smith", "jane@example.com")
    assert user.is_valid()

    # Invalid email
    user_invalid = User("Bob", "invalid-email")
    assert not user_invalid.is_valid()
    
    # Empty name
    user_no_name = User("", "test@example.com")
    assert not user_no_name.is_valid()
    
    # Empty email
    user_no_email = User("Test User", "")
    assert not user_no_email.is_valid()
    
    # Both empty
    user_empty = User("", "")
    assert not user_empty.is_valid()


@pytest.mark.unit
def test_user_string_representation():
    """Test user string representation."""
    user = User("Alice", "alice@example.com")
    assert str(user) == "User(Alice, alice@example.com)"


@pytest.mark.unit
def test_user_to_dict():
    """Test user dictionary conversion."""
    user = User("Charlie", "charlie@example.com")
    expected_dict = {"name": "Charlie", "email": "charlie@example.com"}
    assert user.to_dict() == expected_dict
