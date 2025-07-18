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


@pytest.mark.unit
def test_user_string_representation():
    """Test user string representation."""
    user = User("Alice", "alice@example.com")
    assert str(user) == "User(Alice, alice@example.com)"