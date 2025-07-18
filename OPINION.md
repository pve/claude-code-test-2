# AI Assistant Development Standards

Reference guide for coding assistants working on Python Flask web applications. Optimized for autonomous development with error recovery guidance.

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

## Testing Standards

### Test Categories
- **Unit tests**: 70% of tests, business logic focus
- **Integration tests**: 20% of tests, API endpoints  
- **E2E tests**: 10% of tests, critical user journeys
- **Coverage target**: 90% (realistic and valuable)

### Quick Tests for Commits
Run before every commit to prevent CI failures:
- Static analysis (flake8, imports)
- Unit tests only (no browser dependencies)
- Docker build validation
- Basic server startup test

### E2E Testing
- Run locally during development
- Execute in CI pipeline
- Use Page Object Model for maintainability
- Headless by default, detect CI environments

## Development Workflow

### Git Commit Strategy
1. Run quick tests: `uv run pytest -m "not e2e"`
2. Verify Docker builds: `docker build -t test .`
3. Commit only after passing
4. Full validation happens in CI

### Pre-commit Hooks (Lightweight)
**Fast quality gates** (2-10 seconds total):
- Code formatting (black, isort)
- Basic linting (flake8)
- Security scanning (detect-secrets)
- Configuration validation

**NOT in pre-commit**: Full test suite, E2E tests, comprehensive coverage analysis.

### Dependency Management
**Use UV exclusively** for 10-100x faster dependency resolution:
- `pyproject.toml` for dependencies
- `uv.lock` for reproducible builds
- UV commands for all operations

## Environment Management

### Configuration Pattern
- **python-dotenv** for environment variables
- **`.env`** files for local development (gitignored)
- **`.env.example`** as template
- **Environment variables** in production

### Multi-Environment Adaptation
Code should detect and adapt to environments:
```python
is_ci = any([os.getenv('CI'), os.getenv('GITHUB_ACTIONS')])
```

## Quality Standards

### Code Quality Metrics
- **Test coverage**: 90% minimum
- **Function complexity**: McCabe < 10
- **Exception handling**: No bare `except:` statements
- **Line length**: 88 characters (Black standard)

### Automated Quality Gates
- **Pre-commit**: Fast checks for immediate feedback
- **CI pipeline**: Comprehensive validation
- **Quality gates**: All checks must pass before merge

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

## CI/CD Pipeline

### Pipeline Structure
1. **Quick validation**: Lint, format, unit tests
2. **Build validation**: Docker image creation
3. **Full testing**: Integration and E2E tests
4. **Deployment**: On main branch only

### Environment Detection
Tests adapt automatically to CI vs local environments for browser configuration, timeouts, and resource constraints.

## Key Insights for Assistants

### Phased Quality Implementation
Implement quality improvements gradually:
1. **Core quality**: Formatting, basic linting
2. **Code standards**: Complexity limits, coverage
3. **Advanced quality**: Type checking, security scanning
4. **Team standards**: Full workflow integration

### UV Performance Benefits
- Dramatically faster dependency resolution
- Global caching reduces redundant operations
- Consistent tool versions across environments
- Better conflict resolution than pip

### Coverage Reality
- 90% is achievable and valuable
- Focus on business logic, not test utilities
- Unit tests contribute most to useful coverage
- E2E tests validate functionality but don't improve coverage meaningfully

### Exception Handling
Always specify exception types - bare `except:` masks serious errors like KeyboardInterrupt and SystemExit.

### Tool Configuration Hierarchy
1. **pyproject.toml** - Central Python tool config
2. **Dedicated files** - When tools require it
3. **Environment variables** - For environment differences

### Browser Environment Complexity
- Different environments need different configurations
- Plan for graceful degradation when browser tests fail
- Separate test categories to prevent browser issues blocking core validation

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

### When to Escalate Issues
- **Persistent CI failures** after following standard troubleshooting
- **Performance degradation** in test suites
- **Security vulnerabilities** in dependencies
- **Environment-specific issues** not covered by standard patterns

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

This reference prioritizes coding assistant autonomy while providing safety nets for complex scenarios. Focus on the decision frameworks and error recovery patterns when encountering situations not explicitly covered.