"""Input validation security tests."""

import pytest
import json


@pytest.mark.security
def test_sql_injection_prevention(client):
    """Test that SQL injection attempts are blocked."""
    malicious_inputs = [
        "'; DROP TABLE games; --",
        "1' OR '1'='1",
        "admin'/*",
        "' UNION SELECT * FROM users --",
    ]
    
    for malicious_input in malicious_inputs:
        # Test in difficulty parameter
        response = client.post('/api/game/new', 
                              json={'difficulty': malicious_input})
        # Should reject or sanitize malicious input
        if response.status_code == 200:
            data = response.get_json()
            assert data.get('game', {}).get('difficulty') != malicious_input


@pytest.mark.security
def test_xss_prevention_in_api_responses(client):
    """Test that XSS payloads are not reflected in responses."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "<img src=x onerror=alert(1)>",
        "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
        "\";alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//",
    ]
    
    for payload in xss_payloads:
        response = client.post('/api/game/new', 
                              json={'difficulty': payload})
        
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            # XSS payload should not appear in response
            assert payload not in response_text


@pytest.mark.security
def test_json_bomb_protection(client):
    """Test protection against JSON bombs (deeply nested objects)."""
    # Create deeply nested JSON
    nested_data = {'a': 'value'}
    for i in range(100):  # Create very deep nesting
        nested_data = {'nested': nested_data}
    
    response = client.post('/api/game/new', 
                          json=nested_data,
                          content_type='application/json')
    
    # Should handle gracefully, not crash
    assert response.status_code in [400, 413, 500]


@pytest.mark.security
def test_large_payload_rejection(client):
    """Test that oversized payloads are rejected."""
    # Create large payload
    large_data = {'difficulty': 'a' * 10000}  # 10KB string
    
    response = client.post('/api/game/new', 
                          json=large_data,
                          content_type='application/json')
    
    # Should reject large payloads
    assert response.status_code in [400, 413]


@pytest.mark.security
def test_invalid_json_handling(client):
    """Test handling of malformed JSON."""
    malformed_json_payloads = [
        '{"invalid": json,}',  # Trailing comma
        '{invalid: "json"}',   # Unquoted keys
        '{"unclosed": "string}',  # Unclosed string
        '{',  # Incomplete object
        'not json at all',
    ]
    
    for payload in malformed_json_payloads:
        response = client.post('/api/game/new',
                              data=payload,
                              content_type='application/json')
        
        # Should handle malformed JSON gracefully
        assert response.status_code == 400


@pytest.mark.security
def test_null_byte_injection(client):
    """Test that null byte injection is prevented."""
    null_byte_payloads = [
        "easy\x00.txt",
        "medium\x00; rm -rf /",
        "hard\x00../../../etc/passwd",
    ]
    
    for payload in null_byte_payloads:
        response = client.post('/api/game/new',
                              json={'difficulty': payload})
        
        if response.status_code == 200:
            data = response.get_json()
            # Null bytes should be stripped or rejected
            game_difficulty = data.get('game', {}).get('difficulty', '')
            assert '\x00' not in game_difficulty


@pytest.mark.security
def test_path_traversal_prevention(client):
    """Test that path traversal attempts are blocked."""
    path_traversal_payloads = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "....//....//....//etc/passwd",
    ]
    
    for payload in path_traversal_payloads:
        response = client.post('/api/game/new',
                              json={'difficulty': payload})
        
        # Should reject or sanitize path traversal attempts
        if response.status_code == 200:
            data = response.get_json()
            game_difficulty = data.get('game', {}).get('difficulty', '')
            assert not any(danger in game_difficulty.lower() 
                          for danger in ['../', '..\\', 'etc', 'passwd', 'config'])


@pytest.mark.security
def test_command_injection_prevention(client):
    """Test that command injection attempts are blocked."""
    command_injection_payloads = [
        "; ls -la",
        "| cat /etc/passwd",
        "$(rm -rf /)",
        "`whoami`",
        "&& echo 'pwned'",
    ]
    
    for payload in command_injection_payloads:
        response = client.post('/api/game/new',
                              json={'difficulty': payload})
        
        # Should reject or sanitize command injection attempts
        if response.status_code == 200:
            data = response.get_json()
            game_difficulty = data.get('game', {}).get('difficulty', '')
            assert not any(danger in game_difficulty 
                          for danger in [';', '|', '$', '`', '&&'])


@pytest.mark.security
def test_integer_overflow_handling(client):
    """Test handling of integer overflow in coordinates."""
    overflow_values = [
        2**31,     # 32-bit signed int max + 1
        2**63,     # 64-bit signed int max + 1
        -2**31-1,  # 32-bit signed int min - 1
        float('inf'),  # Infinity
        float('-inf'), # Negative infinity
    ]
    
    # Create game first
    client.post('/api/game/new')
    
    for value in overflow_values:
        try:
            response = client.post('/api/game/move',
                                  json={'row': value, 'col': 0})
        except (ValueError, OverflowError):
            # Expected behavior for extreme values
            continue
        
        # Should handle gracefully
        assert response.status_code in [400, 422]