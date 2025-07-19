import os

from dotenv import load_dotenv
from flask import Flask

from app.utils.environment import get_environment_type, is_ci_environment
from app.utils.security import (
    configure_security_headers,
    validate_production_config,
)


def create_app(config=None):
    """Application factory pattern for Flask app creation."""
    # Load environment variables
    load_dotenv()

    # Create Flask instance
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )

    # Configure app with environment detection
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["ENV"] = get_environment_type()
    app.config["IS_CI"] = is_ci_environment()

    # Apply additional config if provided
    if config:
        app.config.update(config)

    # Environment-specific configuration
    if app.config["ENV"] == "development":
        app.config["DEBUG"] = True
    elif app.config["ENV"] == "production":
        app.config["DEBUG"] = False
        # Validate production configuration
        validate_production_config(app)

    # Configure security headers
    configure_security_headers(app)

    # Register blueprints
    from app.routes import register_blueprints

    register_blueprints(app)

    # Global error handlers  
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors globally."""
        from flask import jsonify, request
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Endpoint not found',
                'message': 'The requested API endpoint does not exist'
            }), 404
        return error

    return app
