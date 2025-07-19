"""CSRF protection utilities."""

import secrets
import hmac
import hashlib
from functools import wraps
from flask import request, session, jsonify, current_app


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


def validate_csrf_token(token: str) -> bool:
    """
    Validate CSRF token against session.
    
    Args:
        token: CSRF token to validate
        
    Returns:
        bool: True if token is valid
    """
    if not token:
        return False
    
    session_token = session.get('csrf_token')
    if not session_token:
        return False
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(token, session_token)


def csrf_protect(f):
    """
    Decorator to protect routes from CSRF attacks.
    
    Checks for CSRF token in:
    1. X-CSRFToken header
    2. X-CSRF-Token header  
    3. CSRFToken form field
    4. csrf_token JSON field
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF for GET, HEAD, OPTIONS requests (safe methods)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)
        
        # Skip in testing if explicitly disabled
        if current_app.config.get('WTF_CSRF_ENABLED', True) is False:
            return f(*args, **kwargs)
        
        # Get CSRF token from various sources
        token = None
        
        # Check headers first
        token = (request.headers.get('X-CSRFToken') or 
                request.headers.get('X-CSRF-Token'))
        
        # Check form data
        if not token and request.form:
            token = request.form.get('csrf_token')
        
        # Check JSON data
        if not token and request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                token = json_data.get('csrf_token')
        
        # Validate token
        if not validate_csrf_token(token):
            return jsonify({
                'error': 'CSRF token validation failed',
                'message': 'Invalid or missing CSRF token'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_csrf_token() -> str:
    """Get CSRF token for current session."""
    return generate_csrf_token()


class CSRFProtection:
    """CSRF protection class for Flask app."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection for Flask app."""
        app.jinja_env.globals['csrf_token'] = get_csrf_token
        
        # Add CSRF token to all form responses
        @app.context_processor
        def inject_csrf_token():
            return dict(csrf_token=get_csrf_token)


def require_csrf(f):
    """Simplified CSRF requirement decorator."""
    return csrf_protect(f)