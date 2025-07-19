def register_blueprints(app):
    """Register all application blueprints."""
    from app.routes.main import main_bp
    from app.routes.game import game_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(game_bp)
