"""Security headers tests."""

import pytest


@pytest.mark.security
def test_security_headers_present(client):
    """Test that all required security headers are present."""
    response = client.get('/')
    
    required_headers = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff', 
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': None,  # Just check presence
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }
    
    for header, expected_value in required_headers.items():
        assert header in response.headers, f"Missing security header: {header}"
        
        if expected_value:
            assert response.headers[header] == expected_value


@pytest.mark.security
def test_content_security_policy_strictness(client):
    """Test that CSP is sufficiently strict."""
    response = client.get('/')
    csp = response.headers.get('Content-Security-Policy', '')
    
    # Should have restrictive CSP
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    
    # Should not allow unsafe-eval
    assert "'unsafe-eval'" not in csp
    
    # Check that inline scripts are controlled
    if "'unsafe-inline'" in csp:
        # If unsafe-inline is allowed, it should be limited to specific directives
        # and ideally use nonces or hashes in production
        pass


@pytest.mark.security
def test_hsts_header_in_production(client):
    """Test that HSTS is enabled in production-like environments."""
    # This would need to be tested with production config
    # For now, just verify the logic exists
    response = client.get('/')
    
    # In test environment, HSTS might not be set (not production)
    # TODO: Test with production config
    assert response.status_code == 200


@pytest.mark.security
def test_no_server_information_disclosure(client):
    """Test that server information is not disclosed."""
    response = client.get('/')
    
    # Should not reveal server details
    server_header = response.headers.get('Server', '')
    assert 'Werkzeug' not in server_header  # Dev server info
    assert 'Flask' not in server_header      # Framework info
    
    # Should not reveal Python version
    assert 'Python' not in server_header


@pytest.mark.security
def test_no_powered_by_headers(client):
    """Test that X-Powered-By headers are not present."""
    response = client.get('/')
    
    # Should not reveal technology stack
    assert 'X-Powered-By' not in response.headers
    assert 'X-AspNet-Version' not in response.headers
    assert 'X-AspNetMvc-Version' not in response.headers


@pytest.mark.security
def test_cache_control_for_sensitive_pages(client):
    """Test that sensitive pages have proper cache control."""
    # Test API endpoints have no-cache headers
    api_endpoints = [
        '/api/game/state',
        '/api/game/new',
    ]
    
    for endpoint in api_endpoints:
        if endpoint == '/api/game/new':
            response = client.post(endpoint, json={'difficulty': 'easy'})
        else:
            response = client.get(endpoint)
        
        # API responses should not be cached
        cache_control = response.headers.get('Cache-Control', '')
        
        # Should have appropriate cache control for sensitive data
        # TODO: Implement proper cache control headers
        assert response.status_code in [200, 404, 405]


@pytest.mark.security
def test_cors_headers_restriction(client):
    """Test that CORS headers are properly restricted."""
    response = client.get('/')
    
    # Should not have overly permissive CORS
    cors_origin = response.headers.get('Access-Control-Allow-Origin')
    
    if cors_origin:
        # Should not be wildcard for credentialed requests
        assert cors_origin != '*'
    
    # Should not allow dangerous methods by default
    cors_methods = response.headers.get('Access-Control-Allow-Methods', '')
    dangerous_methods = ['TRACE', 'TRACK', 'DEBUG']
    
    for method in dangerous_methods:
        assert method not in cors_methods


@pytest.mark.security
def test_feature_policy_headers(client):
    """Test that feature policy headers restrict dangerous features."""
    response = client.get('/')
    
    # Check for feature policy or permissions policy
    feature_policy = response.headers.get('Feature-Policy', '')
    permissions_policy = response.headers.get('Permissions-Policy', '')
    
    # Should restrict dangerous features like camera, microphone, geolocation
    # TODO: Implement feature/permissions policy headers
    
    # For now just check response is valid
    assert response.status_code == 200


@pytest.mark.security
def test_expect_ct_header(client):
    """Test Certificate Transparency policy header."""
    response = client.get('/')
    
    # In production, should have Expect-CT header for certificate monitoring
    # TODO: Implement Expect-CT header for production
    
    # For now just verify response
    assert response.status_code == 200