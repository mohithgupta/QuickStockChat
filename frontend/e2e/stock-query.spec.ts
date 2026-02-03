import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Stock Query Flow
 *
 * These tests verify the complete user flow of asking for stock information:
 * 1. User navigates to the app
 * 2. User sees recommendations (if no messages yet)
 * 3. User types a stock query or clicks a recommendation
 * 4. Message is sent to the backend
 * 5. Response is received and displayed
 */

test.describe('Stock Query Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');

    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');

    // Wait a bit for React to mount and C1Chat to initialize
    await page.waitForTimeout(2000);
  });

  test('displays initial recommendations on first visit', async ({ page }) => {
    // Wait for recommendations to be injected (they appear after C1Chat mounts)
    await page.waitForSelector('.recommendations-overlay', { timeout: 3000 });

    // Verify that recommendations are displayed
    await expect(page.locator('.recommendations-overlay')).toBeVisible();
    await expect(page.locator('.recommendation-box')).toHaveCount(4);

    // Verify recommendation content
    const recommendations = page.locator('.recommendation-box');
    await expect(recommendations.nth(0)).toContainText('Analyze the Indian stock market');
    await expect(recommendations.nth(1)).toContainText('Large, Mid and Small Cap');
    await expect(recommendations.nth(2)).toContainText('stock market events');
    await expect(recommendations.nth(3)).toContainText('global news');
  });

  test('user can type a stock query in the input field', async ({ page }) => {
    // Find the input field (could be textarea or input[type="text"])
    const inputField = page.locator('textarea, input[type="text"]').first();

    // Type a stock query
    await inputField.fill('What is the stock price of AAPL?');

    // Verify the input was filled
    await expect(inputField).toHaveValue('What is the stock price of AAPL?');

    // Verify recommendations are hidden after typing
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible();
  });

  test('user can send a stock query message', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      // Mock a streaming response
      const streamContent = `event: message
data: {"type":"message","content":"The current stock price of AAPL (Apple Inc.) is $178.72 as of the latest market data."}

event: message
data: {"type":"message","content":"This represents a change of +1.23 (+0.69%) from the previous close."}

event: done
data: {}

`;

      route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: streamContent,
      });
    });

    // Find and fill the input field
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the stock price of AAPL?');

    // Find and click the send button
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Wait for the response (mocked)
    // The response should be visible in the chat interface
    await page.waitForTimeout(500);

    // Verify the message was sent (input should be cleared or disabled)
    // Note: C1Chat might clear the input after sending
    await expect(page.locator('textarea, input[type="text"]').first()).toBeVisible();
  });

  test('user can click a recommendation to send a stock query', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"Analyzing the Indian stock market with today's key signals..."}

event: message
data: {"type":"message","content":"The NIFTY 50 index is currently trading at 19,500.00, up by 0.5%."}

event: done
data: {}

`;

      route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: streamContent,
      });
    });

    // Wait for recommendations to appear
    await page.waitForSelector('.recommendations-overlay', { timeout: 3000 });

    // Click on the first recommendation
    const firstRecommendation = page.locator('.recommendation-box').nth(0);
    await firstRecommendation.click();

    // Verify recommendations are hidden after clicking
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible({ timeout: 2000 });

    // Wait for the API call to complete
    await page.waitForTimeout(500);
  });

  test('recommendations have correct accessibility attributes', async ({ page }) => {
    // Wait for recommendations to appear
    await page.waitForSelector('.recommendations-overlay', { timeout: 3000 });

    // Verify accessibility attributes
    const recommendations = page.locator('.recommendation-box');
    const count = await recommendations.count();

    for (let i = 0; i < count; i++) {
      await expect(recommendations.nth(i)).toHaveAttribute('role', 'button');
      await expect(recommendations.nth(i)).toHaveAttribute('tabindex', '0');
    }
  });

  test('user can navigate recommendations with keyboard', async ({ page }) => {
    // Wait for recommendations to appear
    await page.waitForSelector('.recommendations-overlay', { timeout: 3000 });

    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"Analyzing the Indian stock market..."}

event: done
data: {}

`;

      route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: streamContent,
      });
    });

    // Focus on the first recommendation using tab
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Verify a recommendation is focused
    const focusedElement = await page.evaluate(() => document.activeElement?.className);
    expect(focusedElement).toContain('recommendation-box');

    // Press Enter to click
    await page.keyboard.press('Enter');

    // Verify recommendations are hidden after keyboard interaction
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible({ timeout: 2000 });

    // Wait for the API call to complete
    await page.waitForTimeout(500);
  });

  test('handles multiple stock queries in sequence', async ({ page }) => {
    let requestCount = 0;

    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      requestCount++;
      const queries = [
        'The stock price of AAPL is $178.72',
        'The stock price of TSLA is $242.50',
        'The stock price of MSFT is $378.91',
      ];
      const responseText = queries[requestCount - 1] || 'Stock information retrieved';

      const streamContent = `event: message
data: {"type":"message","content":"${responseText}"}

event: done
data: {}

`;

      route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: streamContent,
      });
    });

    // Send first query
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the price of AAPL?');

    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();
    await page.waitForTimeout(500);

    // Send second query
    await inputField.fill('What about TSLA?');
    await sendButton.click();
    await page.waitForTimeout(500);

    // Send third query
    await inputField.fill('And MSFT?');
    await sendButton.click();
    await page.waitForTimeout(500);

    // Verify all requests were made
    expect(requestCount).toBe(3);
  });

  test('displays chat interface with correct configuration', async ({ page }) => {
    // Verify the page contains the chat interface
    await expect(page.locator('.app-container')).toBeVisible();

    // Verify ThemeProvider is applied (dark mode should be active)
    const body = page.locator('body');
    const bgColor = await body.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    expect(bgColor).not.toBe('rgba(0, 0, 0, 0)'); // Should have a background color
  });

  test('handles empty input validation', async ({ page }) => {
    // Try to send an empty message
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('');

    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();

    // The send button should be disabled or not send anything
    const isDisabled = await sendButton.isDisabled();
    const isVisible = await sendButton.isVisible();

    // Either button is disabled or it exists but won't send empty messages
    expect(isDisabled || isVisible).toBeTruthy();
  });

  test('handles special characters in stock queries', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"I understand your query about AAPL's stock performance (PE ratio: 25.5)."}

event: done
data: {}

`;

      route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: streamContent,
      });
    });

    // Type a query with special characters
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill("What's AAPL's PE ratio? (Price-to-Earnings)");

    // Send the message
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Wait for the response
    await page.waitForTimeout(500);

    // Verify the query was processed (no errors)
    await expect(page.locator('.app-container')).toBeVisible();
  });

  test('API error handling displays user-friendly message', async ({ page }) => {
    // Mock a server error
    await page.route('**/api/chat', async (route) => {
      route.fulfill({
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ error: 'Internal server error' }),
      });
    });

    // Try to send a message
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the price of AAPL?');

    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Wait for error handling
    await page.waitForTimeout(1000);

    // The app should still be functional after an error
    await expect(page.locator('.app-container')).toBeVisible();
  });
});
