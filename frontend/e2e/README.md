# E2E Tests

This directory contains end-to-end tests for the stock query flow using Playwright.

## Prerequisites

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Install Playwright browsers:
   ```bash
   npx playwright install
   ```

## Running E2E Tests

### Option 1: Manual Server Start (Recommended)

1. Start the dev server in one terminal:
   ```bash
   cd frontend
   npm run dev
   ```

2. Run tests in another terminal:
   ```bash
   cd frontend
   npx playwright test
   ```

### Option 2: Auto-Start Server

Uncomment the `webServer` section in `playwright.config.ts`:
```ts
webServer: {
  command: 'npm run dev',
  url: 'http://localhost:3000',
  reuseExistingServer: true,
  timeout: 120000,
},
```

Then run:
```bash
npx playwright test
```

## Running Specific Tests

Run only the stock query tests:
```bash
npx playwright test stock-query.spec.ts
```

Run a specific test:
```bash
npx playwright test stock-query.spec.ts --grep "user can type a stock query"
```

## Test Files

- `stock-query.spec.ts` - Tests for stock query flow including:
  - Displaying initial recommendations
  - Typing and sending stock queries
  - Clicking recommendations
  - Keyboard navigation
  - Multiple sequential queries
  - Error handling

## Viewing Test Results

After running tests:
- HTML Report: `npx playwright show-report`
- Test Results: `playwright-report/index.html`

## Debugging Tests

Run tests in headed mode:
```bash
npx playwright test stock-query.spec.ts --headed
```

Run tests with UI:
```bash
npx playwright test stock-query.spec.ts --ui
```

## Notes

- Tests are configured to run on Chromium, Firefox, and WebKit
- Screenshots are captured automatically on test failure
- Traces are captured on test retry
- Default timeout is 30 seconds per test
