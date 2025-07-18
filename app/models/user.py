import re


class User:
    """User model for the application."""
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def is_valid(self):
        """Validate user data."""
        if not self.name or not self.email:
            return False
        
        # Simple email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email) is not None
    
    def __str__(self):
        return f"User({self.name}, {self.email})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'email': self.email
        }