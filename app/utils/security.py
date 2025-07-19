from flask import Flask, request


def configure_security_headers(app: Flask):
    """
    Configure security headers for the Flask application.

    Args:
        app: Flask application instance
    """

    @app.after_request
    def set_security_headers(response):
        """Set security headers on all responses."""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS in production
        if app.config.get("ENV") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Content Security Policy (stricter)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers["Content-Security-Policy"] = csp

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        # Permissions Policy (Feature Policy replacement)
        permissions_policy = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "accelerometer=(), "
            "gyroscope=(), "
            "magnetometer=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy
        
        # Cache control for sensitive endpoints
        if request.path.startswith('/api/'):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response


def generate_secret_key():
    """
    Generate a secure secret key for Flask sessions.

    Returns:
        str: A secure random secret key
    """
    import secrets

    return secrets.token_urlsafe(32)


def validate_production_config(app: Flask):
    """
    Validate that production configuration is secure.

    Args:
        app: Flask application instance

    Raises:
        ValueError: If production configuration is insecure
    """
    if app.config.get("ENV") == "production":
        # Check secret key
        secret_key = app.config.get("SECRET_KEY")
        if (
            not secret_key
            or secret_key == "dev-secret-key-change-in-production"
        ):
            raise ValueError(
                "SECRET_KEY must be set to a secure value in production"
            )

        if len(secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long in production"
            )

        # Ensure debug is disabled
        if app.config.get("DEBUG"):
            raise ValueError("DEBUG must be False in production")

        # Check for development-specific configurations
        if app.config.get("TESTING"):
            raise ValueError("TESTING must be False in production")
