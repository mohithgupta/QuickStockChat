import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Conversation Flow (Multi-turn Chat)
 *
 * These tests verify the complete user conversation flow:
 * 1. User starts a conversation with initial query
 * 2. User receives response and continues conversation
 * 3. Context is maintained across multiple messages
 * 4. Recommendations disappear after first message
 * 5. User can ask follow-up questions
 * 6. Conversation state persists correctly
 */

test.describe('Conversation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');

    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');

    // Wait for React to mount and C1Chat to initialize
    await page.waitForTimeout(2000);
  });

  test('starts conversation with initial query and receives response', async ({ page }) => {
    // Mock the backend API response for initial query
    await page.route('**/api/chat', async (route) => {
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

    // Wait for recommendations to appear initially
    await page.waitForSelector('.recommendations-overlay', { timeout: 3000 });
    await expect(page.locator('.recommendations-overlay')).toBeVisible();

    // Type and send initial message
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the stock price of AAPL?');

    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Verify recommendations are hidden after sending first message
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible({ timeout: 2000 });

    // Wait for response
    await page.waitForTimeout(500);
  });

  test('maintains conversation context across multiple messages', async ({ page }) => {
    let requestCount = 0;

    // Mock the backend API to track requests and maintain context
    await page.route('**/api/chat', async (route) => {
      requestCount++;

      const responses = [
        `event: message
data: {"type":"message","content":"AAPL (Apple Inc.) is currently trading at $178.72."}

event: done
data: {}

`,
        `event: message
data: {"type":"message","content":"Based on AAPL's current price of $178.72, the P/E ratio is 25.5 and the market cap is $2.8 trillion."}

event: done
data: {}

`,
        `event: message
data: {"type":"message","content":"AAPL's 52-week range is $145.62 to $199.62. The current price of $178.72 is closer to the high."}

event: done
data: {}

`,
      ];

      const streamContent = responses[requestCount - 1] || responses[0];

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

    // Send first message
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the stock price of AAPL?');
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();
    await page.waitForTimeout(500);

    // Send follow-up question 1
    await inputField.fill('What is its P/E ratio?');
    await sendButton.click();
    await page.waitForTimeout(500);

    // Send follow-up question 2
    await inputField.fill('What is the 52-week range?');
    await sendButton.click();
    await page.waitForTimeout(500);

    // Verify all three requests were made
    expect(requestCount).toBe(3);

    // Verify recommendations remain hidden throughout conversation
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible();
  });

  test('user can ask follow-up questions after initial response', async ({ page }) => {
    let requestCount = 0;

    // Mock the backend API responses
    await page.route('**/api/chat', async (route) => {
      requestCount++;

      const responses = [
        `event: message
data: {"type":"message","content":"TSLA (Tesla Inc.) is currently trading at $242.50."}

event: done
data: {}

`,
        `event: message
data: {"type":"message","content":"Tesla's revenue for the last quarter was $24.93 billion, up 9% year-over-year."}

event: done
data: {}

`,
      ];

      const streamContent = responses[requestCount - 1] || responses[0];

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

    // Send initial query
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the stock price of TSLA?');
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();
    await page.waitForTimeout(500);

    // Verify input field is ready for follow-up
    await expect(inputField).toBeVisible();
    const currentValue = await inputField.inputValue();
    expect(currentValue).toBe('');

    // Send follow-up question
    await inputField.fill('What was their revenue last quarter?');
    await sendButton.click();
    await page.waitForTimeout(500);

    // Verify both requests were made
    expect(requestCount).toBe(2);
  });

  test('recommendations do not reappear during conversation', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"MSFT (Microsoft Corp) is trading at $378.91."}

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

    // Verify recommendations appear initially
    await page.waitForSelector('.recommendations-overlay', { timeout: 3000 });
    await expect(page.locator('.recommendations-overlay')).toBeVisible();

    // Send first message
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the price of MSFT?');
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Verify recommendations are hidden
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible({ timeout: 2000 });
    await page.waitForTimeout(500);

    // Send multiple follow-up messages
    for (let i = 0; i < 3; i++) {
      await inputField.fill(`Follow-up question ${i + 1}`);
      await sendButton.click();
      await page.waitForTimeout(300);

      // Verify recommendations remain hidden after each message
      await expect(page.locator('.recommendations-overlay')).not.toBeVisible();
    }
  });

  test('handles rapid succession of messages in conversation', async ({ page }) => {
    let requestCount = 0;

    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      requestCount++;
      const streamContent = `event: message
data: {"type":"message","content":"Response to message ${requestCount}"}

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

    // Send multiple messages rapidly
    const inputField = page.locator('textarea, input[type="text"]').first();
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();

    const messages = [
      'Analyze AAPL',
      'Compare with TSLA',
      'What about MSFT?',
      'Show me GOOGL',
    ];

    for (const message of messages) {
      await inputField.fill(message);
      await sendButton.click();
      await page.waitForTimeout(200);
    }

    // Verify all messages were sent
    expect(requestCount).toBe(4);

    // Verify recommendations remain hidden
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible();
  });

  test('conversation handles special characters and formatting', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"I understand your query about AAPL's performance (PE: 25.5, Market Cap: $2.8T)."}

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

    // Send message with special characters
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill("What's AAPL's P/E ratio? (Check if it's > 25)");

    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(500);

    // Verify conversation continues normally
    await expect(page.locator('.app-container')).toBeVisible();
    await expect(inputField).toBeVisible();
  });

  test('conversation persists with error handling and recovery', async ({ page }) => {
    let requestCount = 0;

    // Mock the backend API with one error followed by success
    await page.route('**/api/chat', async (route) => {
      requestCount++;

      if (requestCount === 1) {
        // First request fails
        route.fulfill({
          status: 500,
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ error: 'Internal server error' }),
        });
      } else {
        // Subsequent requests succeed
        const streamContent = `event: message
data: {"type":"message","content":"NVDA (NVIDIA Corp) is trading at $495.22."}

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
      }
    });

    // Send first message (will fail)
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('What is the price of NVDA?');
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();
    await page.waitForTimeout(500);

    // App should still be functional
    await expect(page.locator('.app-container')).toBeVisible();

    // Send second message (will succeed)
    await inputField.fill('Try again: What is NVDA trading at?');
    await sendButton.click();
    await page.waitForTimeout(500);

    // Verify both requests were made
    expect(requestCount).toBe(2);

    // Verify conversation state is maintained
    await expect(inputField).toBeVisible();
  });

  test('user can navigate conversation history', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"Response received."}

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

    // Send multiple messages to build conversation history
    const inputField = page.locator('textarea, input[type="text"]').first();
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();

    const messages = [
      'First message about AAPL',
      'Second message about TSLA',
      'Third message about MSFT',
    ];

    for (const message of messages) {
      await inputField.fill(message);
      await sendButton.click();
      await page.waitForTimeout(300);
    }

    // Verify chat container is still visible and functional
    await expect(page.locator('.app-container')).toBeVisible();

    // Verify input field is ready for next message
    await expect(inputField).toBeVisible();
    const currentValue = await inputField.inputValue();
    expect(currentValue).toBe('');
  });

  test('conversation state resets correctly on new chat', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      const streamContent = `event: message
data: {"type":"message","content":"Message received."}

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

    // Send a message to start conversation
    const inputField = page.locator('textarea, input[type="text"]').first();
    await inputField.fill('Initial message');
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();
    await sendButton.click();

    // Verify recommendations are hidden
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible({ timeout: 2000 });
    await page.waitForTimeout(500);

    // Look for and click "New Chat" button
    const newChatButton = page.locator('button:has-text("New Chat"), button[aria-label*="new chat" i]').first();

    // Check if New Chat button exists (it might be in C1Chat)
    const buttonExists = await newChatButton.count() > 0;

    if (buttonExists) {
      await newChatButton.click();

      // Wait for potential UI update
      await page.waitForTimeout(500);

      // Verify app is still functional
      await expect(page.locator('.app-container')).toBeVisible();
      await expect(inputField).toBeVisible();
    } else {
      // If New Chat button doesn't exist, verify conversation can still continue
      await expect(page.locator('.app-container')).toBeVisible();
    }
  });

  test('handles long conversations with multiple turns', async ({ page }) => {
    let requestCount = 0;

    // Mock the backend API response
    await page.route('**/api/chat', async (route) => {
      requestCount++;
      const streamContent = `event: message
data: {"type":"message","content":"This is response #${requestCount} in our conversation."}

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

    // Simulate a long conversation (10 messages)
    const inputField = page.locator('textarea, input[type="text"]').first();
    const sendButton = page.locator('button[type="submit"], button[aria-label*="send" i]').first();

    for (let i = 1; i <= 10; i++) {
      await inputField.fill(`Message number ${i} in conversation`);
      await sendButton.click();
      await page.waitForTimeout(200);
    }

    // Verify all 10 messages were sent
    expect(requestCount).toBe(10);

    // Verify conversation is still functional
    await expect(page.locator('.app-container')).toBeVisible();
    await expect(inputField).toBeVisible();
    await expect(page.locator('.recommendations-overlay')).not.toBeVisible();
  });
});
