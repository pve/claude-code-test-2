import os


def is_ci_environment():
    """
    Detect if running in CI environment.
    
    Returns:
        bool: True if running in CI, False otherwise
    """
    return any([
        os.getenv('CI'),
        os.getenv('GITHUB_ACTIONS'),
        os.getenv('JENKINS_URL'),
        os.getenv('TRAVIS'),
        os.getenv('CIRCLECI')
    ])


def get_environment_type():
    """
    Get the current environment type.
    
    Returns:
        str: Environment type (development, production, testing)
    """
    return os.environ.get('FLASK_ENV', 'development')


def is_development():
    """Check if running in development environment."""
    return get_environment_type() == 'development'


def is_production():
    """Check if running in production environment."""
    return get_environment_type() == 'production'


def is_testing():
    """Check if running in testing environment."""
    return get_environment_type() == 'testing'