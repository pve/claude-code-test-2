import re


def validate_email(email):
    """
    Validate email address format.

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None


def sanitize_input(input_string):
    """
    Sanitize user input to prevent XSS and other issues.

    Args:
        input_string (str): Input to sanitize

    Returns:
        str: Sanitized input
    """
    if input_string is None:
        return ""

    if not isinstance(input_string, str):
        input_string = str(input_string)

    # Strip whitespace
    sanitized = input_string.strip()

    # Convert to lowercase for consistency
    sanitized = sanitized.lower()

    # Remove HTML tags completely
    sanitized = re.sub(r"<[^>]*>", "", sanitized)

    # Remove script content
    sanitized = re.sub(r"script[^>]*", "", sanitized)

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[&<>"\']', "", sanitized)

    # Remove common XSS patterns
    sanitized = re.sub(
        r"(javascript|alert|eval|expression)\s*\(", "", sanitized
    )

    return sanitized


def validate_string_length(string, min_length=0, max_length=255):
    """
    Validate string length constraints.

    Args:
        string (str): String to validate
        min_length (int): Minimum allowed length
        max_length (int): Maximum allowed length

    Returns:
        bool: True if within constraints, False otherwise
    """
    if not isinstance(string, str):
        return False

    return min_length <= len(string) <= max_length
