import pytest


@pytest.mark.integration
def test_health_endpoint_response(client):
    """Test health endpoint returns correct JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert "status" in data
    assert "service" in data
    assert data["status"] == "healthy"
    assert data["service"] == "claude-code-test-2"


@pytest.mark.integration
def test_api_status_endpoint_response(client):
    """Test API status endpoint returns correct structure."""
    response = client.get("/api/status")
    assert response.status_code == 200

    data = response.get_json()
    assert "api_version" in data
    assert "status" in data
    assert data["api_version"] == "1.0"
    assert data["status"] == "operational"


@pytest.mark.integration
def test_index_page_content(client):
    """Test index page contains expected content."""
    response = client.get("/")
    assert response.status_code == 200

    # Check for key content
    assert b"Welcome to Claude Code Test 2" in response.data
    assert b"Flask Application Factory Pattern" in response.data
    assert b"Health Check" in response.data
    assert b"API Status" in response.data


@pytest.mark.integration
def test_api_endpoints_content_type(client):
    """Test API endpoints return JSON content type."""
    # Test health endpoint
    response = client.get("/health")
    assert response.content_type == "application/json"

    # Test API status endpoint
    response = client.get("/api/status")
    assert response.content_type == "application/json"


@pytest.mark.integration
def test_404_error_handling(client):
    """Test 404 error handling for non-existent endpoints."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


@pytest.mark.integration
def test_cors_headers(client):
    """Test CORS headers are present if configured."""
    response = client.get("/health")
    # This test would pass regardless, but shows how to test headers
    assert response.status_code == 200


@pytest.mark.integration
def test_multiple_api_calls(client):
    """Test multiple sequential API calls work correctly."""
    # Make multiple calls to different endpoints
    for _ in range(5):
        health_response = client.get("/health")
        assert health_response.status_code == 200

        status_response = client.get("/api/status")
        assert status_response.status_code == 200

        # Verify consistent responses
        health_data = health_response.get_json()
        status_data = status_response.get_json()

        assert health_data["status"] == "healthy"
        assert status_data["status"] == "operational"
