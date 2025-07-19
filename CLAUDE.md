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
docker run --rm -p 5001:5001 test
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
- **Coverage target**: 92% (achievable and valuable)

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
- **Test coverage**: 92% minimum
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
docker build -t test . && docker run --rm -p 5001:5001 test
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

## Lessons Learned: CI/CD Debugging & Development Speed

### Critical Debugging Workflows

**CI Failure Investigation Pattern**:
1. Check latest CI run immediately: `gh run list --limit=3`
2. View specific failures: `gh run view <run-id> --log`
3. Monitor CI in real-time: `gh run watch <run-id>`
4. Focus on first failure - fix sequentially, not in parallel

**E2E Test Debugging Methodology**:
- Always run locally first: `PYTHONPATH=. uv run pytest -m e2e -v`
- Check browser configuration consistency (headless vs GUI)
- Verify message text expectations match actual JavaScript output
- Use dynamic port allocation to avoid conflicts: `port = find_free_port()`
- Debug timing issues with explicit waits, not sleeps

### JavaScript/Frontend Integration Gotchas

**Message Text Mismatches**:
- E2E tests often fail due to expecting wrong message text
- Check actual JavaScript messages in source code, not assumptions
- Common mismatch: expecting "Your turn!" vs actual "Game started! Make your move."

**Button State Management**:
- JavaScript constructors must call `updateButtons()` to set initial state
- Tests expecting disabled buttons will fail if initialization is missing
- Always initialize UI state explicitly, don't rely on HTML defaults

**Selenium Method Names**:
- Use `EC.text_to_be_present_in_element()` not `..._element_locator()`
- Common typos in expected conditions cause AttributeError failures

### Coverage Strategy Insights

**Realistic vs Aspirational Targets**:
- 92% coverage is achievable and valuable for production systems
- 95%+ often requires testing defensive error paths that add little value
- Focus coverage on business logic, not error handling boilerplate
- Set CI thresholds to current achievable levels to maintain green builds

**Coverage Gap Analysis**:
- Missing coverage is typically in exception handling blocks
- Lines like `except Exception as e:` are hard to test reliably
- Use `# pragma: no cover` sparingly for unreachable defensive code
- Prioritize integration tests over forcing unit test coverage

### Browser Test Configuration

**Consistency Requirements**:
- Always run headless for CI compatibility: `chrome_options.add_argument("--headless")`
- Include required flags: `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`
- Use consistent window sizes: `--window-size=1920,1080`
- Remove conditional logic - consistent behavior beats flexibility

**Port Management**:
- Never hardcode port 5000 (conflicts with macOS AirPlay)
- Implement dynamic port finding for all test fixtures
- Clean up ports properly in fixture teardown

### CI Pipeline Optimization

**Parallelization Strategy**:
- Run test categories in parallel: unit → integration → e2e
- Early exit on first failure saves time
- Separate security/quality checks from core functionality tests

**Monitoring and Feedback**:
- Use `gh run watch` for real-time debugging
- Commit frequently with descriptive messages for CI history
- Fix issues incrementally - don't batch multiple unrelated fixes

### Development Velocity Principles

**Test-First Debugging**:
- Reproduce failures locally before fixing
- Write failing test case that demonstrates the issue
- Fix implementation, verify test passes, run full suite

**Configuration Consistency**:
- Align documentation, CI configuration, and local settings
- Keep one source of truth for standards (CLAUDE.md)
- Update all references when changing thresholds or standards

**Error Recovery Speed**:
- Focus on getting CI green quickly with pragmatic solutions
- Perfect coverage can be achieved incrementally later
- Maintainable CI is more valuable than perfect metrics

### Action Notes

Always read PLANNING.md at the start of every new conversation, check TASKS.md before starting your work, mark completed tasks to TASKS.md immediately, and add newly discovered tasks to TASKS.md when found.

**CI Debugging Checklist**:
1. Check CI status: `gh run list --limit=1`
2. Run tests locally: `PYTHONPATH=. uv run pytest -m "not e2e" --tb=short`
3. Test E2E separately: `PYTHONPATH=. uv run pytest -m e2e -v`
4. Check coverage: `uv run pytest --cov=app --cov-report=term-missing`
5. Commit incrementally with clear descriptions
6. Monitor CI: `gh run watch <run-id>`