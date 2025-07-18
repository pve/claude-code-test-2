import os
from flask import Flask
from dotenv import load_dotenv


def create_app(config=None):
    """Application factory pattern for Flask app creation."""
    # Load environment variables
    load_dotenv()
    
    # Create Flask instance
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
    
    # Apply additional config if provided
    if config:
        app.config.update(config)
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Environment-specific configuration
    if app.config['ENV'] == 'development':
        app.config['DEBUG'] = True
    
    return app