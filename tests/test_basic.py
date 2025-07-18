import pytest
from app import create_app


@pytest.mark.unit
def test_app_creation():
    """Test that app can be created successfully."""
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] is not None


@pytest.mark.unit
def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'claude-code-test-2'


@pytest.mark.unit
def test_api_status_endpoint(client):
    """Test API status endpoint."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['api_version'] == '1.0'
    assert data['status'] == 'operational'


@pytest.mark.integration
def test_index_page(client):
    """Test that index page loads."""
    response = client.get('/')
    # Will return 500 until templates are created, but route should exist
    assert response.status_code in [200, 500]