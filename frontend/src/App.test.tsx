import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

// Mock the genui-sdk components
vi.mock('@thesysai/genui-sdk', () => ({
  ThemeProvider: ({ children, mode }: { children: React.ReactNode; mode: string }) => (
    <div data-testid="theme-provider" data-mode={mode}>
      {children}
    </div>
  ),
  C1Chat: ({ apiUrl, agentName, logoUrl, formFactor }: {
    apiUrl: string
    agentName: string
    logoUrl: string
    formFactor: string
  }) => (
    <div
      data-testid="c1-chat"
      data-api-url={apiUrl}
      data-agent-name={agentName}
      data-logo-url={logoUrl}
      data-form-factor={formFactor}
    >
      <textarea data-testid="chat-input" aria-label="Chat input" />
      <form data-testid="chat-form">
        <button type="submit" aria-label="Send message">Send</button>
      </form>
    </div>
  ),
}))

// Mock the CSS import
vi.mock('@crayonai/react-ui/styles/index.css', () => ({}))
vi.mock('./App.css', () => ({}))

describe('App Component', () => {
  beforeEach(() => {
    // Clear DOM before each test
    document.body.innerHTML = ''
    // Clear all mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    // Clean up any timers
    vi.restoreAllMocks()
  })

  it('renders without crashing', () => {
    const { container } = render(<App />)
    const appContainer = container.querySelector('.app-container')
    expect(appContainer).toBeInTheDocument()
  })

  it('renders ThemeProvider with dark mode', () => {
    render(<App />)
    const themeProvider = screen.getByTestId('theme-provider')
    expect(themeProvider).toBeInTheDocument()
    expect(themeProvider).toHaveAttribute('data-mode', 'dark')
  })

  it('renders C1Chat with correct props', () => {
    render(<App />)
    const c1Chat = screen.getByTestId('c1-chat')
    expect(c1Chat).toBeInTheDocument()
    expect(c1Chat).toHaveAttribute('data-api-url', 'https://marketinsight-skgl.onrender.com/api/chat')
    expect(c1Chat).toHaveAttribute('data-agent-name', 'Market Insight')
    expect(c1Chat).toHaveAttribute('data-logo-url', '/icon.png')
    expect(c1Chat).toHaveAttribute('data-form-factor', 'full-page')
  })

  it('has correct app container structure', () => {
    const { container } = render(<App />)
    const appContainer = container.querySelector('.app-container')
    expect(appContainer).toBeInTheDocument()
  })

  it('renders chat input and form elements', () => {
    render(<App />)
    expect(screen.getByTestId('chat-input')).toBeInTheDocument()
    expect(screen.getByTestId('chat-form')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument()
  })

  it('injects recommendations when mounted', async () => {
    render(<App />)

    // Wait for the injection timeouts
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('creates recommendation boxes with correct content', async () => {
    render(<App />)

    // Wait for injection
    await waitFor(
      () => {
        const recommendationBoxes = document.querySelectorAll('.recommendation-box')
        expect(recommendationBoxes).toHaveLength(4)
      },
      { timeout: 3000 }
    )

    // Check first recommendation
    const firstBox = document.querySelector('.recommendation-box')
    expect(firstBox).toBeInTheDocument()
    expect(firstBox?.querySelector('.recommendation-icon')?.textContent).toBe('📊')
    expect(firstBox?.querySelector('.recommendation-text')?.textContent).toBe(
      "Analyze the Indian stock market with today's key signals"
    )
  }, 10000)

  it('removes recommendations when user starts typing', async () => {
    const user = userEvent.setup({ delay: null })

    render(<App />)

    // Wait for initial injection
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Simulate user typing
    const input = screen.getByTestId('chat-input') as HTMLTextAreaElement
    await user.type(input, 'test message')

    // Trigger input event
    input.dispatchEvent(new Event('input', { bubbles: true }))

    // Wait for cleanup
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('handles recommendation click correctly', async () => {
    render(<App />)

    // Wait for injection
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Click on first recommendation
    const firstBox = document.querySelector('.recommendation-box')
    expect(firstBox).toBeInTheDocument()

    if (firstBox) {
      firstBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

      // Wait for the recommendation to be removed after click
      await waitFor(
        () => {
          const recommendations = document.querySelector('.recommendations-overlay')
          expect(recommendations).not.toBeInTheDocument()
        },
        { timeout: 3000 }
      )
    }
  }, 10000)

  it('cleans up recommendations on unmount', async () => {
    const { unmount } = render(<App />)

    // Wait for injection
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Unmount component
    unmount()

    // Recommendations should be removed
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('sets programmatic interaction attribute when sending message', async () => {
    render(<App />)

    // Wait for injection
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Click recommendation
    const firstBox = document.querySelector('.recommendation-box')
    if (firstBox) {
      firstBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

      // Check if attribute was set (it should be set immediately)
      await waitFor(
        () => {
          expect(document.body.getAttribute('data-programmatic-interaction')).toBe('true')
        },
        { timeout: 3000 }
      )

      // Attribute should be removed after action completes
      await waitFor(
        () => {
          expect(document.body.getAttribute('data-programmatic-interaction')).toBeNull()
        },
        { timeout: 3000 }
      )
    }
  }, 10000)
})
