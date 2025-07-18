# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Flask Development Standards

This repository follows comprehensive development standards for Python Flask web applications, optimized for autonomous development with error recovery guidance.

## Project Architecture

### Flask Application Factory Pattern
**Always use** - enables testing isolation and configuration flexibility.
```python
def create_app(config=None):
    app = Flask(__name__, template_folder='../templates')
    # Register blueprints, return app
```

### Blueprint Organization
**Start with blueprints** even for small apps. Structure: `app/routes/` with logical separation.

### Session-Based State
**Avoid global state** - use Flask sessions for user data. Enables multi-user support and testability.

## Development Commands

### Dependency Management (UV)
**Use UV exclusively** for 10-100x faster dependency resolution:
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Update dependencies
uv lock --upgrade

# Run commands in virtual environment
uv run python app.py
uv run pytest
```

### Testing Commands
```bash
# Quick tests (before commits)
uv run pytest -m "not e2e"

# Full test suite
uv run pytest

# Coverage analysis
uv run pytest --cov=app --cov-report=term-missing

# E2E tests only
uv run pytest -m e2e
```

### Docker Commands
```bash
# Build and validate
docker build -t test .

# Run with port mapping
docker run --rm -p 5000:5000 test
```

### Quality Checks
```bash
# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8

# Security scan
uv run detect-secrets scan
```

## Testing Standards

### Test Categories
- **Unit tests**: 70% of tests, business logic focus
- **Integration tests**: 20% of tests, API endpoints  
- **E2E tests**: 10% of tests, critical user journeys
- **Coverage target**: 90% (realistic and valuable)

### Git Commit Strategy
1. Run quick tests: `uv run pytest -m "not e2e"`
2. Verify Docker builds: `docker build -t test .`
3. Commit only after passing
4. Full validation happens in CI

## File Organization

### Standard Structure
```
app/
├── __init__.py          # Application factory
├── models/              # Business logic
└── routes/              # Blueprint modules
tests/
├── conftest.py          # Shared fixtures
├── unit/               # Fast tests
├── integration/        # API tests
└── e2e/               # Browser tests
```

### Naming Conventions
- Test files: `test_*.py`
- Model files: Singular nouns
- Route files: Match blueprint names
- Fixtures: Descriptive, scope-appropriate

## Environment Management

### Configuration Pattern
- **python-dotenv** for environment variables
- **`.env`** files for local development (gitignored)
- **`.env.example`** as template
- **Environment variables** in production

### Environment Setup
```bash
# Copy template
cp .env.example .env

# Check Python version
python --version

# Verify UV installation
uv --version
```

## Quality Standards

### Code Quality Metrics
- **Test coverage**: 90% minimum
- **Function complexity**: McCabe < 10
- **Exception handling**: No bare `except:` statements
- **Line length**: 88 characters (Black standard)

### Pre-commit Hooks (Lightweight)
**Fast quality gates** (2-10 seconds total):
- Code formatting (black, isort)
- Basic linting (flake8)
- Security scanning (detect-secrets)
- Configuration validation

## Error Recovery Guidance

### Common CI/CD Failures

**Docker build failures**:
- Check UV lock file sync: `uv lock --upgrade`
- Verify base image compatibility
- Review COPY paths and file existence

**Test failures in CI**:
- Environment differences: Check headless browser setup
- Missing environment variables: Verify CI secrets
- Timing issues: Add appropriate waits for E2E tests

**Coverage failures**:
- Run locally: `uv run pytest --cov=app --cov-report=term-missing`
- Focus on business logic, not test utilities
- Use `# pragma: no cover` for defensive code

### Browser Testing Issues

**Local development**:
- WebDriver path problems: Use webdriver-manager
- Permission issues: Check Chrome installation
- Port conflicts: Use dynamic port allocation

**CI environments**:
- Add headless flags: `--headless --no-sandbox`
- Include display options: `--disable-dev-shm-usage`
- Verify browser installation in CI image

### Environment Setup Problems

**Missing dependencies**:
- Regenerate lock file: `uv lock`
- Check Python version compatibility
- Verify system dependencies (Chrome, etc.)

**Configuration issues**:
- Copy `.env.example` to `.env`
- Check required environment variables
- Validate secret key generation

## Decision Frameworks

### When to Add Tests
- **Always**: New business logic, API endpoints
- **Usually**: Bug fixes, refactored code
- **Sometimes**: Configuration changes, UI tweaks
- **Rarely**: Test utilities, temporary code

### When to Run Full Test Suite
- **Before pull requests**
- **In CI pipeline always**
- **After significant changes**
- **NOT before every commit** (use quick tests instead)

### When to Update Dependencies
- **Security updates**: Immediately
- **Minor updates**: Regularly in development
- **Major updates**: Planned upgrades with testing
- **Lock file**: Regenerate after any dependency changes

## Troubleshooting Commands

**Quick diagnostics**:
```bash
# Dependency issues
uv lock --upgrade

# Test isolation
uv run pytest -m "not e2e" -v

# Coverage analysis
uv run pytest --cov=app --cov-report=term-missing

# Docker validation
docker build -t test . && docker run --rm -p 5000:5000 test
```

**Environment validation**:
- Check Python version: `python --version`
- Verify UV installation: `uv --version`
- Test environment variables: Check `.env` file exists
- Browser availability: Chrome installed and accessible

## Key Principles for Claude Code

### Multi-Environment Adaptation
Code should detect and adapt to environments:
```python
is_ci = any([os.getenv('CI'), os.getenv('GITHUB_ACTIONS')])
```

### Exception Handling
Always specify exception types - bare `except:` masks serious errors like KeyboardInterrupt and SystemExit.

### Tool Configuration Hierarchy
1. **pyproject.toml** - Central Python tool config
2. **Dedicated files** - When tools require it
3. **Environment variables** - For environment differences

This reference prioritizes coding assistant autonomy while providing safety nets for complex scenarios. Focus on the decision frameworks and error recovery patterns when encountering situations not explicitly covered.