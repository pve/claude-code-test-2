"""Advanced input sanitization and validation."""

import re
import json
import html
from typing import Any, Dict, List, Optional, Union
from flask import request


class InputSanitizer:
    """Advanced input sanitization and validation."""
    
    # Common XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<link[^>]*>.*?</link>',
        r'<meta[^>]*>.*?</meta>',
        r'eval\s*\(',
        r'expression\s*\(',
        r'alert\s*\(',
        r'confirm\s*\(',
        r'prompt\s*\(',
    ]
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r'(union|select|insert|update|delete|drop|create|alter|exec)\s+',
        r'[\'";]\s*(or|and)\s+[\'"]?\d',
        r'[\'";]\s*(or|and)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+',
        r'--\s*$',
        r'/\*.*?\*/',
        r'@@\w+',
        r'char\s*\(',
        r'cast\s*\(',
        r'convert\s*\(',
    ]
    
    # Command injection patterns  
    COMMAND_PATTERNS = [
        r'[;&|`$]',
        r'\$\(',
        r'`[^`]*`',
        r'\|\s*\w+',
        r';\s*\w+',
        r'&&\s*\w+',
        r'\|\|\s*\w+',
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        Sanitize a string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]
        
        # HTML escape
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove or escape dangerous patterns
        for pattern in cls.XSS_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        for pattern in cls.SQL_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        for pattern in cls.COMMAND_PATTERNS:
            value = re.sub(pattern, '', value)
        
        return value.strip()
    
    @classmethod
    def sanitize_json(cls, data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """
        Recursively sanitize JSON data.
        
        Args:
            data: JSON data to sanitize
            max_depth: Maximum nesting depth allowed
            
        Returns:
            dict: Sanitized data
        """
        if max_depth <= 0:
            raise ValueError("JSON nesting too deep")
        
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            clean_key = cls.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = cls.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                # Validate numeric ranges
                if isinstance(value, (int, float)):
                    if abs(value) > 1e10:  # Prevent huge numbers
                        raise ValueError(f"Number too large: {value}")
                sanitized[clean_key] = value
            elif isinstance(value, dict):
                sanitized[clean_key] = cls.sanitize_json(value, max_depth - 1)
            elif isinstance(value, list):
                sanitized[clean_key] = cls.sanitize_list(value, max_depth - 1)
            elif value is None:
                sanitized[clean_key] = None
            else:
                # Convert unknown types to string and sanitize
                sanitized[clean_key] = cls.sanitize_string(str(value))
        
        return sanitized
    
    @classmethod
    def sanitize_list(cls, data: List[Any], max_depth: int = 10) -> List[Any]:
        """
        Sanitize list data.
        
        Args:
            data: List to sanitize
            max_depth: Maximum nesting depth
            
        Returns:
            list: Sanitized list
        """
        if max_depth <= 0:
            raise ValueError("JSON nesting too deep")
        
        if len(data) > 1000:  # Prevent huge arrays
            raise ValueError("Array too large")
        
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_string(item))
            elif isinstance(item, (int, float, bool)):
                if isinstance(item, (int, float)) and abs(item) > 1e10:
                    raise ValueError(f"Number too large: {item}")
                sanitized.append(item)
            elif isinstance(item, dict):
                sanitized.append(cls.sanitize_json(item, max_depth - 1))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item, max_depth - 1))
            elif item is None:
                sanitized.append(None)
            else:
                sanitized.append(cls.sanitize_string(str(item)))
        
        return sanitized
    
    @classmethod
    def validate_difficulty(cls, difficulty: str) -> str:
        """
        Validate and sanitize difficulty setting.
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            str: Valid difficulty level
            
        Raises:
            ValueError: If difficulty is invalid
        """
        if not isinstance(difficulty, str):
            raise ValueError("Difficulty must be a string")
        
        # Sanitize input
        clean_difficulty = cls.sanitize_string(difficulty, max_length=20).lower()
        
        # Validate against allowed values
        allowed_difficulties = ['easy', 'medium', 'hard']
        if clean_difficulty not in allowed_difficulties:
            raise ValueError(f"Invalid difficulty. Must be one of: {allowed_difficulties}")
        
        return clean_difficulty
    
    @classmethod
    def validate_coordinates(cls, row: Any, col: Any) -> tuple[int, int]:
        """
        Validate and sanitize game coordinates.
        
        Args:
            row: Row coordinate
            col: Column coordinate
            
        Returns:
            tuple: (row, col) as integers
            
        Raises:
            ValueError: If coordinates are invalid
        """
        try:
            row = int(row)
            col = int(col)
        except (ValueError, TypeError):
            raise ValueError("Coordinates must be integers")
        
        # Validate range (0-2 for tic-tac-toe)
        if not (0 <= row <= 2) or not (0 <= col <= 2):
            raise ValueError("Coordinates must be between 0 and 2")
        
        return row, col
    
    @classmethod
    def validate_request_size(cls, max_size: int = 1024) -> None:
        """
        Validate request content length.
        
        Args:
            max_size: Maximum allowed size in bytes
            
        Raises:
            ValueError: If request is too large
        """
        content_length = request.content_length
        if content_length and content_length > max_size:
            raise ValueError(f"Request too large: {content_length} bytes > {max_size} bytes")


def sanitize_input(data: Any) -> Any:
    """Convenience function for input sanitization."""
    if isinstance(data, dict):
        return InputSanitizer.sanitize_json(data)
    elif isinstance(data, list):
        return InputSanitizer.sanitize_list(data)
    elif isinstance(data, str):
        return InputSanitizer.sanitize_string(data)
    else:
        return data