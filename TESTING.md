# Testing Guide

This document provides comprehensive information about testing in StockQuickChat, including how to run tests, write new tests, and understand test coverage.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Backend Testing](#backend-testing)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Running Backend Tests](#running-backend-tests)
  - [Coverage Reports](#coverage-reports)
- [Frontend Testing](#frontend-testing)
  - [Unit/Component Tests](#unitcomponent-tests)
  - [E2E Tests](#e2e-tests)
  - [Running Frontend Tests](#running-frontend-tests)
- [CI/CD Integration](#cicd-integration)
- [Writing New Tests](#writing-new-tests)
  - [Backend Test Patterns](#backend-test-patterns)
  - [Frontend Test Patterns](#frontend-test-patterns)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Overview

StockQuickChat uses a comprehensive testing approach with three types of tests:

- **Unit Tests**: Test individual functions, classes, and components in isolation
- **Integration Tests**: Test interactions between components and API endpoints
- **E2E Tests**: Test complete user flows in a browser environment

**Current Coverage**: 95% (Backend), 80%+ (Frontend) ✓
**Test Execution Time**: < 5 minutes ✓

## Test Structure

```
stockQuickChat/
├── tests/                          # Backend tests
│   ├── unit/                       # Unit tests
│   │   ├── test_config.py          # Configuration models
│   │   ├── test_logger.py          # Logger utility
│   │   ├── test_tools_1_4.py       # Financial tools 1-4
│   │   ├── test_tools_5_8.py       # Financial tools 5-8
│   │   ├── test_tools_9_12.py      # Financial tools 9-12
│   │   └── test_tools_13_16.py     # Financial tools 13-16
│   ├── integration/                # Integration tests
│   │   ├── test_health_endpoint.py # Health endpoint
│   │   ├── test_chat_endpoint.py   # Chat endpoint
│   │   └── test_agent_workflow.py  # Agent workflow
│   ├── e2e/                        # E2E tests (placeholder)
│   └── conftest.py                 # Pytest configuration and fixtures
├── frontend/
│   ├── src/
│   │   ├── *.test.tsx              # Component tests
│   │   └── *.test.ts               # Hook tests
│   └── e2e/                        # E2E tests
│       ├── stock-query.spec.ts     # Stock query flow
│       └── conversation.spec.ts    # Conversation flow
├── pytest.ini                      # Pytest configuration
├── frontend/vitest.config.ts       # Vitest configuration
└── frontend/playwright.config.ts   # Playwright configuration
```

## Backend Testing

Backend tests use **pytest** with the following key dependencies:

- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for testing

### Unit Tests

Unit tests focus on testing individual components in isolation:

- **Config Models** (`test_config.py`): RequestObject, PromptObject
- **Logger** (`test_logger.py`): Logging utility functionality
- **Financial Tools** (`test_tools_*.py`): All 16 financial tools
  - Tools 1-4: Stock price, historical data, news, balance sheet
  - Tools 5-8: Income statement, cash flow, company info, dividends
  - Tools 9-12: Splits, institutional holders, shareholders, mutual funds
  - Tools 13-16: Insider transactions, analyst recommendations, ticker resolution

### Integration Tests

Integration tests verify component interactions:

- **Health Endpoint** (`test_health_endpoint.py`): 10 tests
  - Status checks, response structure, CORS headers, performance
- **Chat Endpoint** (`test_chat_endpoint.py`): 23 tests
  - Streaming responses, request validation, content handling
- **Agent Workflow** (`test_agent_workflow.py`): 18 tests
  - Tool invocation, memory management, conversation context

### Running Backend Tests

#### Run All Backend Tests
```bash
# Run all tests with coverage
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

#### Run Specific Test Files
```bash
# Test specific file
pytest tests/unit/test_config.py -v

# Test specific function
pytest tests/unit/test_config.py::TestRequestObject::test_valid_initialization -v
```

#### Run with Coverage
```bash
# Generate coverage report
pytest --cov=. --cov-report=term-missing --cov-report=html tests/

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v

# Run only slow tests
pytest -m slow -v
```

### Coverage Reports

Coverage reports are automatically generated when running tests with `--cov` flag:

- **Terminal**: Shows coverage summary with missing lines
- **HTML**: Detailed report in `htmlcov/index.html`
- **XML**: For CI/CD integration (coverage.xml)
- **JSON**: For programmatic access (coverage.json)

**Minimum Coverage**: 80% (enforced in CI/CD)
**Current Coverage**: 95%

## Frontend Testing

Frontend tests use two frameworks:

- **Vitest**: Unit and component tests
- **Playwright**: End-to-end browser tests

### Unit/Component Tests

Component tests verify React components and hooks:

- **App Component** (`App.test.tsx`): 11 tests
  - Rendering, theme provider, chat interface, recommendations
- **Recommendations** (`Recommendations.test.tsx`): 11 tests
  - DOM injection, click interactions, keyboard navigation
- **useMessageSender Hook** (`useMessageSender.test.ts`): 16 tests
  - Message sending, input handling, button interactions

### E2E Tests

E2E tests verify complete user workflows in a browser:

- **Stock Query** (`stock-query.spec.ts`): 11 tests
  - Initial recommendations, typing queries, sending messages
  - Keyboard navigation, accessibility, error handling
- **Conversation** (`conversation.spec.ts`): 10 tests
  - Multi-turn conversations, context maintenance, follow-up questions

### Running Frontend Tests

#### Run Unit/Component Tests
```bash
cd frontend

# Run all tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run specific test file
npm test -- App.test.tsx
```

#### Run with Coverage
```bash
cd frontend

# Generate coverage report
npm run test:run -- --coverage

# View HTML coverage report
open coverage/index.html  # macOS
```

#### Run E2E Tests
```bash
cd frontend

# Make sure dev server is running first
npm run dev

# In another terminal, run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run E2E tests in headed mode (show browser)
npm run test:e2e:headed

# Run specific E2E test file
npx playwright test stock-query.spec.ts

# Run E2E tests in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

#### Run E2E Tests in Debug Mode
```bash
cd frontend

# Debug with Playwright Inspector
npx playwright test --debug

# Debug with headed mode and pause on failure
npx playwright test --headed --debug
```

## CI/CD Integration

Tests run automatically on GitHub Actions for every push and pull request:

### Backend Workflow (`.github/workflows/test-backend.yml`)

- **Triggers**: Push/PR to main/develop with backend changes
- **Python Version**: 3.13
- **Timeout**: 5 minutes
- **Steps**:
  1. Install dependencies
  2. Run unit tests with coverage
  3. Run integration tests with coverage
  4. Check minimum 80% coverage
  5. Upload coverage to Codecov
  6. Generate execution time summary
  7. Fail if timeout exceeded

### Frontend Workflow (`.github/workflows/test-frontend.yml`)

- **Triggers**: Push/PR to main/develop with frontend changes
- **Node Version**: 20
- **Timeout**: 5 minutes
- **Steps**:
  1. Install dependencies
  2. Run unit tests with coverage
  3. Check minimum 80% coverage
  4. Upload coverage to Codecov
  5. Generate execution time summary
  6. Fail if timeout exceeded

### Coverage Badges

Coverage is tracked via Codecov and displayed in README and pull requests.

## Writing New Tests

### Backend Test Patterns

#### Unit Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    """Test suite for MyComponent"""

    def test_valid_input(self):
        """Test with valid input"""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = my_function(input_data)

        # Assert
        assert result is not None
        assert result.status == "success"

    def test_invalid_input_raises_error(self):
        """Test that invalid input raises error"""
        with pytest.raises(ValueError):
            my_function(None)

    @patch('module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependency"""
        mock_dep.return_value = "mocked_value"
        result = my_function()
        assert result == "mocked_value"
```

#### Integration Test Structure

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoint_returns_success():
    """Test endpoint returns success response"""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_endpoint_with_request_body():
    """Test endpoint with request body"""
    response = client.post(
        "/api/endpoint",
        json={"prompt": "test", "threadId": "123"}
    )
    assert response.status_code == 200
```

### Frontend Test Patterns

#### Component Test Structure

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  it('renders without crashing', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('handles user interaction', () => {
    const handleClick = vi.fn()
    render(<MyComponent onClick={handleClick} />)

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

#### Hook Test Structure

```typescript
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import useMyHook from './useMyHook'

describe('useMyHook', () => {
  it('returns initial state', () => {
    const { result } = renderHook(() => useMyHook())
    expect(result.current.value).toBe('initial')
  })

  it('updates state on action', () => {
    const { result } = renderHook(() => useMyHook())
    act(() => {
      result.current.update('new value')
    })
    expect(result.current.value).toBe('new value')
  })
})
```

#### E2E Test Structure

```typescript
import { test, expect } from '@playwright/test'

test.describe('User Flow', () => {
  test('completes multi-step process', async ({ page }) => {
    await page.goto('/')
    await page.fill('[data-testid="input"]', 'test query')
    await page.click('[data-testid="submit"]')

    await expect(page.locator('[data-testid="result"]'))
      .toBeVisible()
  })
})
```

### Test Naming Conventions

- **Files**: `test_<name>.py` (backend), `<name>.test.ts/tsx` (frontend)
- **Classes**: `Test<ClassName>` (backend), `describe('<ComponentName>')` (frontend)
- **Functions**: `test_<what_is_being_tested>` (backend), `it('<what is being tested>')` (frontend)

### Fixtures and Mocks

#### Backend Fixtures (conftest.py)

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

@pytest.fixture
def mock_ticker():
    with patch('yfinance.Ticker') as mock:
        mock.return_value.info = {"symbol": "AAPL"}
        yield mock
```

#### Frontend Setup (src/test/setup.ts)

```typescript
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})
```

## Test Coverage

### Current Coverage Status

| Module | Coverage | Status |
|--------|----------|--------|
| **MarketInsight/components/agent.py** | 100% | ✓ Fully covered |
| **MarketInsight/utils/logger.py** | 100% | ✓ Fully covered |
| **MarketInsight/utils/tools.py** | 96% | ✓ Excellent |
| **config/config.py** | 100% | ✓ Fully covered |
| **main.py** | 84% | ✓ Good |
| **TOTAL (Backend)** | **95%** | **✓ Excellent** |
| **Frontend** | 80%+ | ✓ Meets requirement |

### Coverage Goals

- **Minimum**: 80% (enforced in CI/CD)
- **Target**: 90%+
- **Excellence**: 95%+

### View Coverage Reports

```bash
# Backend
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html

# Frontend
cd frontend
npm run test:run -- --coverage
open coverage/index.html
```

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'MarketInsight'`

**Solution**:
```bash
# Make sure you're in the project root
cd /path/to/stockQuickChat

# Install dependencies
pip install -r requirements.txt

# Run tests from project root
pytest tests/
```

#### Missing Dependencies

**Problem**: Tests fail due to missing packages

**Solution**:
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### Port Already in Use

**Problem**: E2E tests fail because port 3000 is in use

**Solution**:
```bash
# Kill process on port 3000 (macOS/Linux)
lsof -ti:3000 | xargs kill -9

# Or use a different port
VITE_PORT=3001 npm run dev
``#### Timeout in CI/CD

**Problem**: Tests exceed 5-minute timeout

**Solution**:
- Optimize slow tests
- Use mocks instead of real API calls
- Run expensive tests in parallel
- Consider increasing timeout for legitimate long-running tests

#### Flaky Tests

**Problem**: Tests pass locally but fail in CI

**Solution**:
- Check for timing issues (add explicit waits)
- Ensure tests are isolated (no shared state)
- Mock external dependencies
- Use deterministic test data
- Increase retries in CI (configured in workflows)

#### Browser Tests Fail

**Problem**: Playwright tests fail to find elements

**Solution**:
```typescript
// Add explicit waits
await page.waitForSelector('[data-testid="element"]')

// Use data-testid attributes instead of CSS classes
<input data-testid="username-input" />

// Check if element is visible before interacting
await expect(element).toBeVisible()
```

### Debug Mode

#### Backend
```bash
# Run with verbose output
pytest -vv tests/

# Run with pdb debugger
pytest --pdb tests/

# Run with ipdb debugger
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb --pdb tests/
```

#### Frontend
```bash
# Run Vitest in watch mode with file monitoring
npm test -- --watch

# Run Vitest with UI for interactive debugging
npm run test:ui

# Run Playwright in debug mode
npx playwright test --debug
```

### Getting Help

If you encounter issues not covered here:

1. Check the test output for specific error messages
2. Review the test files for examples of similar tests
3. Consult the framework documentation:
   - [Pytest](https://docs.pytest.org/)
   - [Vitest](https://vitest.dev/)
   - [Playwright](https://playwright.dev/)
4. Check GitHub Actions logs for CI/CD failures
5. Review the implementation plan: `.auto-claude/specs/002-comprehensive-test-suite/`

## Best Practices

### Writing Good Tests

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One Assertion Per Test**: Keep tests focused
3. **Descriptive Names**: Make test names self-documenting
4. **Test Behavior, Not Implementation**: Focus on what, not how
5. **Mock External Dependencies**: Avoid real API calls
6. **Use Fixtures**: Reuse test setup code
7. **Test Edge Cases**: Don't just test the happy path
8. **Keep Tests Fast**: Slow tests won't be run
9. **Isolate Tests**: No dependencies between tests
10. **Review Coverage**: Aim for high coverage, but quality matters more

### Anti-Patterns to Avoid

1. ❌ Testing private methods directly
2. ❌ Multiple assertions in one test without clear grouping
3. ❌ Not cleaning up after tests (side effects)
4. ❌ Hardcoding values that should be configurable
5. ❌ Testing implementation details instead of behavior
6. ❌ brittle selectors (CSS classes, XPath)
7. ❌ Sleep-based waiting (use explicit waits)
8. ❌ Sharing state between tests
9. ❌ Not mocking external services
10. ❌ Writing tests that are too complex to understand

---

**Last Updated**: 2026-02-03
**Maintained By**: Development Team
**Related Docs**: [README.md](README.md), [COVERAGE_SUMMARY.md](COVERAGE_SUMMARY.md)
