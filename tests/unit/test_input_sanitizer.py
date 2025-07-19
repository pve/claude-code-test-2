"""Tests for input sanitization functionality."""

import pytest
from unittest.mock import patch, MagicMock
from app.utils.input_sanitizer import InputSanitizer, sanitize_input


class TestInputSanitizer:
    """Test the InputSanitizer class."""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        result = InputSanitizer.sanitize_string("hello world")
        assert result == "hello world"
    
    def test_sanitize_string_html_escape(self):
        """Test HTML escaping."""
        result = InputSanitizer.sanitize_string("<script>alert('xss')</script>")
        # After sanitization, dangerous content should be removed or escaped
        assert "<script>" not in result
        assert "alert" not in result or "script" not in result
    
    def test_sanitize_string_max_length(self):
        """Test string length truncation."""
        long_string = "a" * 2000
        result = InputSanitizer.sanitize_string(long_string, max_length=100)
        assert len(result) <= 100
    
    def test_sanitize_string_sql_injection(self):
        """Test SQL injection pattern removal."""
        malicious = "admin'; DROP TABLE users; --"
        result = InputSanitizer.sanitize_string(malicious)
        # Key dangerous SQL keywords should be removed
        assert "drop" not in result.lower()
        # Note: "table" might remain as it's a common word, but dangerous patterns should be gone
    
    def test_sanitize_json_basic(self):
        """Test basic JSON sanitization."""
        data = {"name": "John", "age": 30}
        result = InputSanitizer.sanitize_json(data)
        assert result["name"] == "John"
        assert result["age"] == 30
    
    def test_sanitize_json_nested(self):
        """Test nested JSON sanitization."""
        data = {
            "user": {
                "name": "John",
                "settings": {"theme": "dark"}
            }
        }
        result = InputSanitizer.sanitize_json(data, max_depth=5)
        assert result["user"]["name"] == "John"
        assert result["user"]["settings"]["theme"] == "dark"
    
    def test_sanitize_json_max_depth_exceeded(self):
        """Test JSON depth limit enforcement."""
        deep_data = {"level1": {"level2": {"level3": "value"}}}
        
        with pytest.raises(ValueError, match="JSON nesting too deep"):
            InputSanitizer.sanitize_json(deep_data, max_depth=2)
    
    def test_sanitize_json_large_numbers(self):
        """Test large number validation."""
        data = {"big_number": 1e20}
        
        with pytest.raises(ValueError, match="Number too large"):
            InputSanitizer.sanitize_json(data)
    
    def test_sanitize_list_basic(self):
        """Test basic list sanitization."""
        data = ["hello", 123, True]
        result = InputSanitizer.sanitize_list(data)
        assert result == ["hello", 123, True]
    
    def test_sanitize_list_too_large(self):
        """Test list size limit."""
        large_list = list(range(2000))
        
        with pytest.raises(ValueError, match="Array too large"):
            InputSanitizer.sanitize_list(large_list)
    
    def test_validate_difficulty_valid(self):
        """Test valid difficulty validation."""
        assert InputSanitizer.validate_difficulty("easy") == "easy"
        assert InputSanitizer.validate_difficulty("MEDIUM") == "medium"
        assert InputSanitizer.validate_difficulty("Hard") == "hard"
    
    def test_validate_difficulty_invalid(self):
        """Test invalid difficulty rejection."""
        with pytest.raises(ValueError, match="Invalid difficulty"):
            InputSanitizer.validate_difficulty("impossible")
    
    def test_validate_coordinates_valid(self):
        """Test valid coordinate validation."""
        row, col = InputSanitizer.validate_coordinates(1, 2)
        assert row == 1
        assert col == 2
    
    def test_validate_coordinates_invalid_range(self):
        """Test invalid coordinate range."""
        with pytest.raises(ValueError, match="must be between 0 and 2"):
            InputSanitizer.validate_coordinates(5, 1)
    
    def test_validate_coordinates_non_integer(self):
        """Test non-integer coordinates."""
        with pytest.raises(ValueError, match="must be integers"):
            InputSanitizer.validate_coordinates("a", "b")
    
    def test_validate_request_size_valid(self):
        """Test valid request size."""
        request_mock = MagicMock()
        request_mock.content_length = 500
        
        with patch('app.utils.input_sanitizer.request', request_mock):
            # Should not raise exception
            InputSanitizer.validate_request_size(max_size=1024)
    
    def test_validate_request_size_too_large(self):
        """Test request size too large."""
        request_mock = MagicMock()
        request_mock.content_length = 2048
        
        with patch('app.utils.input_sanitizer.request', request_mock):
            with pytest.raises(ValueError, match="Request too large"):
                InputSanitizer.validate_request_size(max_size=1024)


class TestSanitizeInputFunction:
    """Test the convenience sanitize_input function."""
    
    def test_sanitize_input_string(self):
        """Test sanitizing string input."""
        result = sanitize_input("hello world")
        assert result == "hello world"
    
    def test_sanitize_input_dict(self):
        """Test sanitizing dictionary input."""
        data = {"key": "value"}
        result = sanitize_input(data)
        assert result == {"key": "value"}
    
    def test_sanitize_input_list(self):
        """Test sanitizing list input."""
        data = ["item1", "item2"]
        result = sanitize_input(data)
        assert result == ["item1", "item2"]
    
    def test_sanitize_input_other_type(self):
        """Test sanitizing other types."""
        result = sanitize_input(123)
        assert result == 123