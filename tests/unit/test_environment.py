import os
import pytest

from app.utils.environment import (
    is_ci_environment,
    get_environment_type,
    is_development,
    is_production,
    is_testing,
)


@pytest.mark.unit
def test_is_ci_environment_github_actions(monkeypatch):
    """Test CI detection with GitHub Actions."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    assert is_ci_environment() is True


@pytest.mark.unit
def test_is_ci_environment_ci_flag(monkeypatch):
    """Test CI detection with CI flag."""
    monkeypatch.setenv("CI", "true")
    assert is_ci_environment() is True


@pytest.mark.unit
def test_is_ci_environment_jenkins(monkeypatch):
    """Test CI detection with Jenkins."""
    monkeypatch.setenv("JENKINS_URL", "http://jenkins.example.com")
    assert is_ci_environment() is True


@pytest.mark.unit
def test_is_ci_environment_travis(monkeypatch):
    """Test CI detection with Travis CI."""
    monkeypatch.setenv("TRAVIS", "true")
    assert is_ci_environment() is True


@pytest.mark.unit
def test_is_ci_environment_circleci(monkeypatch):
    """Test CI detection with CircleCI."""
    monkeypatch.setenv("CIRCLECI", "true")
    assert is_ci_environment() is True


@pytest.mark.unit
def test_is_ci_environment_local(monkeypatch):
    """Test CI detection in local environment."""
    # Clear all CI environment variables
    for env_var in ["CI", "GITHUB_ACTIONS", "JENKINS_URL", "TRAVIS", "CIRCLECI"]:
        monkeypatch.delenv(env_var, raising=False)
    
    assert is_ci_environment() is False


@pytest.mark.unit
def test_get_environment_type_default(monkeypatch):
    """Test environment type detection with default."""
    monkeypatch.delenv("FLASK_ENV", raising=False)
    assert get_environment_type() == "development"


@pytest.mark.unit
def test_get_environment_type_production(monkeypatch):
    """Test environment type detection for production."""
    monkeypatch.setenv("FLASK_ENV", "production")
    assert get_environment_type() == "production"


@pytest.mark.unit
def test_get_environment_type_testing(monkeypatch):
    """Test environment type detection for testing."""
    monkeypatch.setenv("FLASK_ENV", "testing")
    assert get_environment_type() == "testing"


@pytest.mark.unit
def test_is_development_true(monkeypatch):
    """Test development environment detection when true."""
    monkeypatch.setenv("FLASK_ENV", "development")
    assert is_development() is True


@pytest.mark.unit
def test_is_development_false(monkeypatch):
    """Test development environment detection when false."""
    monkeypatch.setenv("FLASK_ENV", "production")
    assert is_development() is False


@pytest.mark.unit
def test_is_production_true(monkeypatch):
    """Test production environment detection when true."""
    monkeypatch.setenv("FLASK_ENV", "production")
    assert is_production() is True


@pytest.mark.unit
def test_is_production_false(monkeypatch):
    """Test production environment detection when false."""
    monkeypatch.setenv("FLASK_ENV", "development")
    assert is_production() is False


@pytest.mark.unit
def test_is_testing_true(monkeypatch):
    """Test testing environment detection when true."""
    monkeypatch.setenv("FLASK_ENV", "testing")
    assert is_testing() is True


@pytest.mark.unit
def test_is_testing_false(monkeypatch):
    """Test testing environment detection when false."""
    monkeypatch.setenv("FLASK_ENV", "development")
    assert is_testing() is False