import pytest
import os
from app import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Test configuration
    test_config = {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
    }
    
    app = create_app(test_config)
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="session")
def is_ci():
    """Check if running in CI environment."""
    return any([os.getenv('CI'), os.getenv('GITHUB_ACTIONS')])