def register_blueprints(app):
    """Register all application blueprints."""
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
