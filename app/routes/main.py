from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({'status': 'healthy', 'service': 'claude-code-test-2'})


@main_bp.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        'api_version': '1.0',
        'status': 'operational'
    })