from flask import Flask


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

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

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
