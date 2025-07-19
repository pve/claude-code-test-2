# Claude Code Test 2

A Flask web application built following comprehensive development standards with modern tooling and best practices.

## Features

- **Flask Application Factory Pattern** - Modular, testable application structure
- **Blueprint Organization** - Logical separation of routes and functionality
- **Comprehensive Testing** - Unit, integration, and end-to-end test suites
- **UV Dependency Management** - Fast, reliable Python package management
- **Docker Support** - Containerized deployment with health checks
- **Quality Tools** - Automated formatting, linting, and security scanning
- **Responsive Web Interface** - Clean, mobile-friendly design

## Quick Start

### Prerequisites

- Python 3.9+ 
- [UV](https://docs.astral.sh/uv/) package manager
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd claude-code-test-2
   cp .env.example .env
   ```

2. **Install dependencies**:
   ```bash
   uv sync --extra dev
   ```

3. **Run tests to verify setup**:
   ```bash
   # Quick tests (recommended before commits)
   uv run pytest -m "not e2e"
   
   # Full test suite
   uv run pytest
   ```

4. **Start the development server**:
   ```bash
   uv run python run.py
   ```

5. **Open your browser** to `http://127.0.0.1:5001`

## Development Commands

### Essential Commands

```bash
# Start development server
uv run python run.py

# Run quick tests (before commits)
uv run pytest -m "not e2e"

# Run all tests
uv run pytest

# Check test coverage
uv run pytest --cov=app --cov-report=term-missing

# Generate coverage with XML (for Codecov)
uv run pytest --cov=app --cov-report=term-missing --cov-report=xml

# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8

# Security scan
uv run detect-secrets scan
```

### Dependency Management

```bash
# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade

# Install dependencies (after git pull)
uv sync
```

### Docker Commands

```bash
# Build Docker image
docker build -t claude-code-test-2 .

# Run containerized application
docker run --rm -p 5001:5001 claude-code-test-2

# Test Docker build process
docker build -t test . && docker run --rm -p 5001:5001 test
```

## Project Structure

```
claude-code-test-2/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models/            # Business logic and data models
│   └── routes/            # Blueprint modules
│       ├── __init__.py    # Blueprint registration
│       └── main.py        # Main routes
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   └── index.html        # Home page
├── static/               # Static assets
│   └── css/              # Stylesheets
├── tests/                # Test suites
│   ├── conftest.py       # Pytest fixtures
│   ├── unit/             # Unit tests
│   ├── integration/      # API tests
│   └── e2e/             # End-to-end tests
├── run.py               # Development server
├── wsgi.py              # Production WSGI entry point
└── pyproject.toml       # Project configuration
```

## How to Modify the Application

### Adding New Routes

1. **Create or modify a blueprint** in `app/routes/`:
   ```python
   # app/routes/api.py
   from flask import Blueprint, jsonify
   
   api_bp = Blueprint('api', __name__, url_prefix='/api')
   
   @api_bp.route('/users')
   def get_users():
       return jsonify({'users': []})
   ```

2. **Register the blueprint** in `app/routes/__init__.py`:
   ```python
   def register_blueprints(app):
       from app.routes.main import main_bp
       from app.routes.api import api_bp  # Add this
       
       app.register_blueprint(main_bp)
       app.register_blueprint(api_bp)    # Add this
   ```

### Adding Business Logic

1. **Create models** in `app/models/`:
   ```python
   # app/models/user.py
   class User:
       def __init__(self, name, email):
           self.name = name
           self.email = email
   ```

2. **Use in routes**:
   ```python
   from app.models.user import User
   
   @api_bp.route('/users', methods=['POST'])
   def create_user():
       user = User(name="John", email="john@example.com")
       return jsonify({'user': user.name})
   ```

### Adding Templates

1. **Create template** in `templates/`:
   ```html
   <!-- templates/users.html -->
   {% extends "base.html" %}
   
   {% block title %}Users{% endblock %}
   
   {% block content %}
   <h2>Users</h2>
   <!-- Your content here -->
   {% endblock %}
   ```

2. **Render in route**:
   ```python
   @main_bp.route('/users')
   def users():
       return render_template('users.html')
   ```

### Adding Tests

1. **Unit tests** in `tests/unit/`:
   ```python
   # tests/unit/test_user.py
   import pytest
   from app.models.user import User
   
   @pytest.mark.unit
   def test_user_creation():
       user = User("John", "john@example.com")
       assert user.name == "John"
   ```

2. **Integration tests** in `tests/integration/`:
   ```python
   # tests/integration/test_api.py
   import pytest
   
   @pytest.mark.integration
   def test_get_users(client):
       response = client.get('/api/users')
       assert response.status_code == 200
   ```

### Running Tests with Proper Environment

For integration and E2E tests, set PYTHONPATH to ensure imports work correctly:

```bash
# Run integration tests
PYTHONPATH=. uv run pytest -m integration -v

# Run E2E tests  
PYTHONPATH=. uv run pytest -m e2e -v

# Run full test suite with coverage
PYTHONPATH=. uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=95
```

### Environment Configuration

1. **Add new environment variables** to `.env.example`:
   ```
   # New feature configuration
   FEATURE_ENABLED=true
   API_TIMEOUT=30
   ```

2. **Use in application**:
   ```python
   import os
   
   def create_app(config=None):
       app = Flask(__name__)
       app.config['FEATURE_ENABLED'] = os.environ.get('FEATURE_ENABLED', 'false').lower() == 'true'
       app.config['API_TIMEOUT'] = int(os.environ.get('API_TIMEOUT', 30))
   ```

## Development Workflow

### Before Making Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Run tests to ensure starting point is clean**:
   ```bash
   uv run pytest -m "not e2e"
   ```

### During Development

1. **Make your changes** following the project structure
2. **Add tests** for new functionality
3. **Run tests frequently**:
   ```bash
   uv run pytest -m "not e2e" --tb=short
   ```

### Before Committing

1. **Run quality checks**:
   ```bash
   # Format code
   uv run black .
   uv run isort .
   
   # Check for issues
   uv run flake8
   uv run detect-secrets scan
   ```

2. **Run tests**:
   ```bash
   uv run pytest -m "not e2e"
   ```

3. **Verify Docker build**:
   ```bash
   docker build -t test .
   ```

### Git Workflow

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add user management feature

- Add User model with validation
- Add API endpoints for CRUD operations  
- Add user management templates
- Add comprehensive test coverage"

# Push to feature branch
git push origin feature/your-feature-name
```

## API Endpoints

- `GET /` - Home page
- `GET /health` - Health check (returns JSON status)
- `GET /api/status` - API status information

## Configuration

The application uses environment variables for configuration:

- `FLASK_ENV` - Environment (development/production)
- `FLASK_HOST` - Host to bind (default: 127.0.0.1)
- `FLASK_PORT` - Port to bind (default: 5001)
- `SECRET_KEY` - Flask secret key (required for production)

## Troubleshooting

### Common Issues

**Import errors**: Ensure you're running commands with `uv run` and dependencies are installed:
```bash
uv sync --extra dev
```

**Test failures**: Check that you're in the project root and using the correct test markers:
```bash
PYTHONPATH=. uv run pytest -m "not e2e" -v
```

**Docker build issues**: Ensure UV lock file is up to date:
```bash
uv lock --upgrade
docker build -t test .
```

### Getting Help

- Check the [CLAUDE.md](CLAUDE.md) file for comprehensive development standards
- Review test files for usage examples
- Consult Flask documentation: https://flask.palletsprojects.com/
- UV documentation: https://docs.astral.sh/uv/

## License

This project is licensed under the MIT License.