"""Rate limiting utilities for API protection."""

import time
from functools import wraps
from flask import request, jsonify, session, current_app
from collections import defaultdict, deque


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        # Store rate limit data per IP/session
        self.requests = defaultdict(deque)
        
    def is_allowed(self, key: str, window_seconds: int = 60, max_requests: int = 20) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Identifier for rate limiting (IP, session, etc.)
            window_seconds: Time window in seconds
            max_requests: Maximum requests per window
            
        Returns:
            bool: True if request is allowed
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < window_start:
            self.requests[key].popleft()
        
        # Check if under limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Record this request
        self.requests[key].append(now)
        return True
    
    def get_reset_time(self, key: str, window_seconds: int = 60) -> int:
        """Get time until rate limit resets."""
        if not self.requests[key]:
            return 0
        
        oldest_request = self.requests[key][0]
        reset_time = oldest_request + window_seconds
        return max(0, int(reset_time - time.time()))


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 20, window_seconds: int = 60, per_session: bool = True):
    """
    Rate limiting decorator for Flask routes.
    
    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds  
        per_session: If True, rate limit per session; if False, per IP
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine rate limit key
            if per_session and 'session_id' in session:
                key = f"session:{session.get('session_id', 'anonymous')}"
            else:
                # Use IP address (with proxy header support)
                ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip and ',' in ip:
                    ip = ip.split(',')[0].strip()  # First IP in chain
                key = f"ip:{ip}"
            
            # Check rate limit
            if not rate_limiter.is_allowed(key, window_seconds, max_requests):
                reset_time = rate_limiter.get_reset_time(key, window_seconds)
                
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Try again in {reset_time} seconds.',
                    'retry_after': reset_time
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(reset_time)
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Window'] = str(window_seconds)
                return response
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_client_ip() -> str:
    """Get the real client IP address, accounting for proxies."""
    # Check various proxy headers in order of preference
    proxy_headers = [
        'X-Forwarded-For',
        'X-Real-IP', 
        'X-Client-IP',
        'CF-Connecting-IP',  # Cloudflare
    ]
    
    for header in proxy_headers:
        ip = request.headers.get(header)
        if ip:
            # Handle comma-separated IPs (first is usually client)
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            return ip
    
    # Fallback to direct connection
    return request.remote_addr or 'unknown'


def session_rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Stricter rate limiting for session-based operations."""
    return rate_limit(max_requests, window_seconds, per_session=True)


def api_rate_limit(max_requests: int = 30, window_seconds: int = 60):
    """Standard API rate limiting."""
    return rate_limit(max_requests, window_seconds, per_session=False)