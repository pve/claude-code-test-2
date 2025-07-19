import pytest
from flask import Flask

from app.utils.security import (
    configure_security_headers,
    generate_secret_key,
    validate_production_config,
)


@pytest.mark.unit
def test_configure_security_headers_development():
    """Test security headers configuration in development mode."""
    app = Flask(__name__)
    app.config["ENV"] = "development"
    
    configure_security_headers(app)
    
    with app.test_client() as client:
        response = client.get("/")
        
        # Basic security headers should always be set
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Content-Security-Policy" in response.headers
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        
        # HSTS should NOT be set in development
        assert "Strict-Transport-Security" not in response.headers


@pytest.mark.unit
def test_configure_security_headers_production():
    """Test security headers configuration in production mode."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    
    configure_security_headers(app)
    
    with app.test_client() as client:
        response = client.get("/")
        
        # All headers including HSTS should be set in production
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Content-Security-Policy" in response.headers
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"


@pytest.mark.unit
def test_generate_secret_key():
    """Test secret key generation."""
    key1 = generate_secret_key()
    key2 = generate_secret_key()
    
    # Keys should be strings
    assert isinstance(key1, str)
    assert isinstance(key2, str)
    
    # Keys should be different
    assert key1 != key2
    
    # Keys should be sufficiently long (URL-safe base64 with 32 bytes = ~43 chars)
    assert len(key1) >= 40
    assert len(key2) >= 40


@pytest.mark.unit
def test_validate_production_config_development():
    """Test production config validation in development mode."""
    app = Flask(__name__)
    app.config["ENV"] = "development"
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    
    # Should not raise any errors in development
    validate_production_config(app)


@pytest.mark.unit
def test_validate_production_config_production_valid():
    """Test production config validation with valid production config."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    app.config["SECRET_KEY"] = "a-very-secure-secret-key-that-is-definitely-long-enough"
    app.config["DEBUG"] = False
    app.config["TESTING"] = False
    
    # Should not raise any errors with valid config
    validate_production_config(app)


@pytest.mark.unit
def test_validate_production_config_missing_secret_key():
    """Test production config validation with missing secret key."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    
    with pytest.raises(ValueError, match="SECRET_KEY must be set to a secure value"):
        validate_production_config(app)


@pytest.mark.unit
def test_validate_production_config_dev_secret_key():
    """Test production config validation with development secret key."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    
    with pytest.raises(ValueError, match="SECRET_KEY must be set to a secure value"):
        validate_production_config(app)


@pytest.mark.unit
def test_validate_production_config_short_secret_key():
    """Test production config validation with too short secret key."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    app.config["SECRET_KEY"] = "short"
    
    with pytest.raises(ValueError, match="SECRET_KEY must be at least 32 characters"):
        validate_production_config(app)


@pytest.mark.unit
def test_validate_production_config_debug_enabled():
    """Test production config validation with debug enabled."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    app.config["SECRET_KEY"] = "a-very-secure-secret-key-that-is-definitely-long-enough"
    app.config["DEBUG"] = True
    
    with pytest.raises(ValueError, match="DEBUG must be False in production"):
        validate_production_config(app)


@pytest.mark.unit
def test_validate_production_config_testing_enabled():
    """Test production config validation with testing enabled."""
    app = Flask(__name__)
    app.config["ENV"] = "production"
    app.config["SECRET_KEY"] = "a-very-secure-secret-key-that-is-definitely-long-enough"
    app.config["DEBUG"] = False
    app.config["TESTING"] = True
    
    with pytest.raises(ValueError, match="TESTING must be False in production"):
        validate_production_config(app)