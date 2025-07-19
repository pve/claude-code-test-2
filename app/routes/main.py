from flask import Blueprint, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Main page with tic-tac-toe game."""
    return render_template("tictactoe.html")


@main_bp.route("/tictactoe")
def tictactoe():
    """Tic-tac-toe game page (alias for backward compatibility)."""
    return render_template("tictactoe.html")


@main_bp.route("/welcome")
def welcome():
    """Original welcome page."""
    return render_template("welcome.html")


@main_bp.route("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "healthy", "service": "claude-code-test-2"})


@main_bp.route("/api/status")
def api_status():
    """API status endpoint."""
    return jsonify({"api_version": "1.0", "status": "operational"})
