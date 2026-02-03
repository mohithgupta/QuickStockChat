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

describe('Recommendations Interaction', () => {
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

  it('should inject all four recommendation boxes', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendationBoxes = document.querySelectorAll('.recommendation-box')
        expect(recommendationBoxes).toHaveLength(4)
      },
      { timeout: 3000 }
    )
  })

  it('should render recommendation boxes with correct icons and text', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendationBoxes = document.querySelectorAll('.recommendation-box')
        expect(recommendationBoxes).toHaveLength(4)
      },
      { timeout: 3000 }
    )

    // Check first recommendation
    const firstBox = document.querySelectorAll('.recommendation-box')[0]
    expect(firstBox.querySelector('.recommendation-icon')?.textContent).toBe('📊')
    expect(firstBox.querySelector('.recommendation-text')?.textContent).toBe(
      "Analyze the Indian stock market with today's key signals"
    )

    // Check second recommendation
    const secondBox = document.querySelectorAll('.recommendation-box')[1]
    expect(secondBox.querySelector('.recommendation-icon')?.textContent).toBe('🧭')
    expect(secondBox.querySelector('.recommendation-text')?.textContent).toBe(
      'Analyse Conditions of Large, Mid and Small Cap in Indian Market'
    )

    // Check third recommendation
    const thirdBox = document.querySelectorAll('.recommendation-box')[2]
    expect(thirdBox.querySelector('.recommendation-icon')?.textContent).toBe('📰')
    expect(thirdBox.querySelector('.recommendation-text')?.textContent).toBe(
      'Track major stock market events shaping investor sentiment'
    )

    // Check fourth recommendation
    const fourthBox = document.querySelectorAll('.recommendation-box')[3]
    expect(fourthBox.querySelector('.recommendation-icon')?.textContent).toBe('🌍')
    expect(fourthBox.querySelector('.recommendation-text')?.textContent).toBe(
      'How global news connects with Indian market movements'
    )
  })

  it('should hide recommendations when clicking on first recommendation', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Click on first recommendation
    const firstBox = document.querySelectorAll('.recommendation-box')[0]
    firstBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    // Wait for the recommendation to be removed after click
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('should set programmatic interaction attribute on click', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Click on recommendation
    const firstBox = document.querySelectorAll('.recommendation-box')[0]
    firstBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    // Check if attribute was set immediately
    expect(document.body.getAttribute('data-programmatic-interaction')).toBe('true')

    // Attribute should be removed after action completes
    await waitFor(
      () => {
        expect(document.body.getAttribute('data-programmatic-interaction')).toBeNull()
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('should trigger message sending on recommendation click', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Get the input element
    const input = screen.getByTestId('chat-input') as HTMLTextAreaElement

    // Click on first recommendation
    const firstBox = document.querySelectorAll('.recommendation-box')[0]
    firstBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    // The input value should be set
    await waitFor(
      () => {
        expect(input.value).toBe("Analyze the Indian stock market with today's key signals")
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('should handle clicks on different recommendations', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Get the input element
    const input = screen.getByTestId('chat-input') as HTMLTextAreaElement

    // Test clicking second recommendation
    const secondBox = document.querySelectorAll('.recommendation-box')[1]
    secondBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    await waitFor(
      () => {
        expect(input.value).toBe('Analyse Conditions of Large, Mid and Small Cap in Indian Market')
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('should have correct accessibility attributes on recommendation boxes', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendationBoxes = document.querySelectorAll('.recommendation-box')
        expect(recommendationBoxes).toHaveLength(4)
      },
      { timeout: 3000 }
    )

    const recommendationBoxes = document.querySelectorAll('.recommendation-box')

    // Check that all boxes have role="button"
    recommendationBoxes.forEach((box) => {
      expect(box.getAttribute('role')).toBe('button')
      expect(box.getAttribute('tabindex')).toBe('0')
    })
  })

  it('should prevent default behavior on recommendation click', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    const firstBox = document.querySelectorAll('.recommendation-box')[0]

    // Create a mock click event
    let preventDefaultCalled = false
    let stopPropagationCalled = false
    let stopImmediatePropagationCalled = false

    const mockEvent = new MouseEvent('click', { bubbles: true })
    mockEvent.preventDefault = () => { preventDefaultCalled = true }
    mockEvent.stopPropagation = () => { stopPropagationCalled = true }
    Object.defineProperty(mockEvent, 'stopImmediatePropagation', {
      value: () => { stopImmediatePropagationCalled = true }
    })

    firstBox.dispatchEvent(mockEvent)

    // The event handlers should have been called
    expect(preventDefaultCalled).toBe(true)
    expect(stopPropagationCalled).toBe(true)
    expect(stopImmediatePropagationCalled).toBe(true)
  })

  it('should remove recommendations overlay when hasMessages is true', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Click on a recommendation to set hasMessages to true
    const firstBox = document.querySelectorAll('.recommendation-box')[0]
    firstBox.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    // Recommendations should be removed
    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).not.toBeInTheDocument()
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('should handle keyboard interaction with recommendation boxes', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Get the input element
    const input = screen.getByTestId('chat-input') as HTMLTextAreaElement

    // Test Enter key on first recommendation
    const firstBox = document.querySelectorAll('.recommendation-box')[0]
    firstBox.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))

    // The input value should be set
    await waitFor(
      () => {
        expect(input.value).toBe("Analyze the Indian stock market with today's key signals")
      },
      { timeout: 3000 }
    )
  }, 10000)

  it('should inject recommendations into the correct DOM location', async () => {
    render(<App />)

    await waitFor(
      () => {
        const recommendations = document.querySelector('.recommendations-overlay')
        expect(recommendations).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Verify recommendations are in the correct container structure
    const overlay = document.querySelector('.recommendations-overlay')
    expect(overlay).toBeInTheDocument()

    const container = overlay?.querySelector('.recommendations-container')
    expect(container).toBeInTheDocument()

    const boxes = container?.querySelectorAll('.recommendation-box')
    expect(boxes).toHaveLength(4)
  })
})
