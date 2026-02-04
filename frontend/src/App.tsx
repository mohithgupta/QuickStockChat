import './App.css'
import { C1Chat, ThemeProvider } from '@thesysai/genui-sdk'
import '@crayonai/react-ui/styles/index.css'
import { useState, useCallback, useRef, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { StockPriceChart } from './components/charts/StockPriceChart'
import { FinancialStatementChart } from './components/charts/FinancialStatementChart'
import { fetchStockPriceChart, transformStockPriceData, fetchFinancialStatementChart, transformFinancialStatementData } from './services/chartApi'

// API configuration from environment variables
const API_URL = import.meta.env.VITE_API_URL || 'https://marketinsight-skgl.onrender.com/api/chat'
const API_KEY = import.meta.env.VITE_API_KEY || ''

// Recommendation data
const RECOMMENDATIONS = [
  {
    icon: '📊',
    text: "Analyze the Indian stock market with today's key signals"
  },
  {
    icon: '🧭',
    text: "Analyse Conditions of Large, Mid and Small Cap in Indian Market"
  },
  {
    icon: '📰',
    text: 'Track major stock market events shaping investor sentiment'
  },
  {
    icon: '🌍',
    text: 'How global news connects with Indian market movements'
  }
]

// Custom hook for sending messages programmatically
function useMessageSender() {
  const sendMessage = useCallback((text: string) => {
    // Set flag to prevent sidebar toggle
    document.body.setAttribute('data-programmatic-interaction', 'true')

    // Small delay to ensure C1Chat is ready
    setTimeout(() => {
      const inputElement = document.querySelector(
        'textarea, input[type="text"], [contenteditable="true"]'
      ) as HTMLTextAreaElement | HTMLInputElement | HTMLElement

      if (inputElement) {
        // Set the input value
        if ('value' in inputElement) {
          const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            inputElement instanceof HTMLTextAreaElement
              ? window.HTMLTextAreaElement.prototype
              : window.HTMLInputElement.prototype,
            'value'
          )?.set

          if (nativeInputValueSetter) {
            nativeInputValueSetter.call(inputElement, text)
          }

          inputElement.dispatchEvent(new Event('input', { bubbles: true }))
          inputElement.dispatchEvent(new Event('change', { bubbles: true }))
        } else if (inputElement.isContentEditable) {
          inputElement.textContent = text
          inputElement.dispatchEvent(new Event('input', { bubbles: true }))
        }

        // Don't focus input to prevent keyboard popup on mobile
        // This prevents the white space issue at the bottom

        // Send the message
        setTimeout(() => {
          const sendButton = document.querySelector(
            'button[type="submit"], button[aria-label*="send" i]'
          ) as HTMLButtonElement

          if (sendButton) {
            sendButton.click()
          } else {
            const form = inputElement.closest('form')
            if (form) {
              form.requestSubmit()
            }
          }

          // Remove flag after action completes
          setTimeout(() => {
            document.body.removeAttribute('data-programmatic-interaction')
          }, 100)
        }, 300)
      } else {
        document.body.removeAttribute('data-programmatic-interaction')
      }
    }, 100)
  }, [])

  return sendMessage
}

// Stock ticker detection pattern
const STOCK_TICKER_PATTERN = /\b([A-Z]{2,5})\b/g

// Keywords that indicate stock price queries
const STOCK_QUERY_KEYWORDS = [
  'stock price',
  'price',
  'share price',
  'current price',
  'how much',
  'what is',
  'chart',
  'graph',
  'performance',
  'trading',
  'market',
  'investment'
]

// Keywords that indicate financial statement queries
const FINANCIAL_STATEMENT_KEYWORDS = [
  'income statement',
  'balance sheet',
  'cash flow',
  'financial statement',
  'financial data',
  'revenue',
  'expenses',
  'assets',
  'liabilities',
  'equity',
  'profit',
  'loss'
]

/**
 * Detects if a message is asking about stock prices
 * and extracts stock tickers from the message
 */
function detectStockQuery(message: string): string[] | null {
  const lowerMessage = message.toLowerCase()

  // Check if message contains stock-related keywords
  const hasStockKeyword = STOCK_QUERY_KEYWORDS.some(keyword =>
    lowerMessage.includes(keyword)
  )

  if (!hasStockKeyword) {
    return null
  }

  // Extract potential stock tickers (2-5 uppercase letters)
  const matches = message.match(STOCK_TICKER_PATTERN)
  if (!matches || matches.length === 0) {
    return null
  }

  // Filter out common non-ticker words
  const excludedWords = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'WOULD', 'THERE', 'THEIR', 'ABOUT', 'COULD', 'AFTER']
  const tickers = matches.filter(match => !excludedWords.includes(match))

  return tickers.length > 0 ? tickers : null
}

/**
 * Detects if a message is asking about financial statements
 * and extracts the statement type and ticker
 */
function detectFinancialStatementQuery(message: string): { ticker: string; statementType: 'income' | 'balance' | 'cash_flow' } | null {
  const lowerMessage = message.toLowerCase()

  // Check if message contains financial statement keywords
  const hasFinancialKeyword = FINANCIAL_STATEMENT_KEYWORDS.some(keyword =>
    lowerMessage.includes(keyword)
  )

  if (!hasFinancialKeyword) {
    return null
  }

  // Determine statement type from message
  let statementType: 'income' | 'balance' | 'cash_flow' = 'income'
  if (lowerMessage.includes('balance sheet')) {
    statementType = 'balance'
  } else if (lowerMessage.includes('cash flow')) {
    statementType = 'cash_flow'
  }

  // Extract potential stock tickers (2-5 uppercase letters)
  const matches = message.match(STOCK_TICKER_PATTERN)
  if (!matches || matches.length === 0) {
    return null
  }

  // Filter out common non-ticker words
  const excludedWords = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HAS', 'HAVE', 'BEEN', 'WITH', 'THIS', 'THAT', 'FROM', 'THEY', 'WOULD', 'THERE', 'THEIR', 'ABOUT', 'COULD', 'AFTER']
  const tickers = matches.filter(match => !excludedWords.includes(match))

  if (tickers.length === 0) {
    return null
  }

  return { ticker: tickers[0], statementType }
}

/**
 * Creates a chart container and renders the StockPriceChart component
 */
function renderChartForTicker(
  ticker: string,
  messageElement: HTMLElement,
  existingChartContainers: Map<string, HTMLElement>,
  existingRoots: Map<string, ReturnType<typeof createRoot>>
): void {
  // Check if we already rendered a chart for this message
  const messageId = messageElement.getAttribute('data-message-id') || `${Date.now()}-${Math.random()}`
  messageElement.setAttribute('data-message-id', messageId)

  if (existingChartContainers.has(messageId)) {
    return
  }

  // Create a container for the chart
  const chartContainer = document.createElement('div')
  chartContainer.className = 'stock-chart-container'
  chartContainer.style.cssText = `
    margin-top: 16px;
    margin-bottom: 16px;
    padding: 16px;
    background-color: #1a1a1a;
    border-radius: 8px;
    border: 1px solid #333;
  `

  // Insert the chart container after the message content
  messageElement.appendChild(chartContainer)
  existingChartContainers.set(messageId, chartContainer)

  // Create a React root and render the chart
  const root = createRoot(chartContainer)
  existingRoots.set(messageId, root)

  // Fetch chart data and render
  fetchStockPriceChart({ ticker, period: '1mo' })
    .then(response => {
      const stockData = transformStockPriceData(response)

      if (stockData.length > 0) {
        root.render(
          <StockPriceChart
            data={stockData}
            title={`${ticker} Stock Price`}
            height={300}
            showVolume={false}
            showLegend={true}
            showGrid={true}
            enableZoom={true}
            enableBrush={true}
          />
        )
      } else {
        root.unmount()
        chartContainer.remove()
        existingChartContainers.delete(messageId)
        existingRoots.delete(messageId)
      }
    })
    .catch(() => {
      // Silently fail - don't show error to user
      root.unmount()
      chartContainer.remove()
      existingChartContainers.delete(messageId)
      existingRoots.delete(messageId)
    })
}

/**
 * Creates a chart container and renders the FinancialStatementChart component
 */
function renderFinancialStatementChart(
  ticker: string,
  statementType: 'income' | 'balance' | 'cash_flow',
  messageElement: HTMLElement,
  existingChartContainers: Map<string, HTMLElement>,
  existingRoots: Map<string, ReturnType<typeof createRoot>>
): void {
  // Check if we already rendered a chart for this message
  const messageId = messageElement.getAttribute('data-financial-chart-id') || `${Date.now()}-${Math.random()}`
  messageElement.setAttribute('data-financial-chart-id', messageId)

  if (existingChartContainers.has(messageId)) {
    return
  }

  // Create a container for the chart
  const chartContainer = document.createElement('div')
  chartContainer.className = 'financial-chart-container'
  chartContainer.style.cssText = `
    margin-top: 16px;
    margin-bottom: 16px;
    padding: 16px;
    background-color: #1a1a1a;
    border-radius: 8px;
    border: 1px solid #333;
  `

  // Insert the chart container after the message content
  messageElement.appendChild(chartContainer)
  existingChartContainers.set(messageId, chartContainer)

  // Create a React root and render the chart
  const root = createRoot(chartContainer)
  existingRoots.set(messageId, root)

  // Determine title based on statement type
  const statementTypeLabels: Record<string, string> = {
    income: 'Income Statement',
    balance: 'Balance Sheet',
    cash_flow: 'Cash Flow Statement'
  }
  const title = `${ticker} ${statementTypeLabels[statementType]}`

  // Fetch chart data and render
  fetchFinancialStatementChart({ ticker, statementType })
    .then(response => {
      const financialData = transformFinancialStatementData(response)

      if (financialData.length > 0) {
        root.render(
          <FinancialStatementChart
            data={financialData}
            chartType="bar"
            title={title}
            height={300}
            showLegend={true}
            showGrid={true}
            enableZoom={true}
            enableBrush={true}
          />
        )
      } else {
        root.unmount()
        chartContainer.remove()
        existingChartContainers.delete(messageId)
        existingRoots.delete(messageId)
      }
    })
    .catch(() => {
      // Silently fail - don't show error to user
      root.unmount()
      chartContainer.remove()
      existingChartContainers.delete(messageId)
      existingRoots.delete(messageId)
    })
}

// Main App Component
function App() {
  const [showRecommendations, setShowRecommendations] = useState(true)
  const [hasMessages, setHasMessages] = useState(false)
  const sendMessage = useMessageSender()
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const chartContainerRef = useRef<Map<string, HTMLElement>>(new Map())
  const chartRootsRef = useRef<Map<string, ReturnType<typeof createRoot>>>(new Map())

  const handleRecommendationClick = useCallback((text: string) => {
    setShowRecommendations(false)
    setHasMessages(true)
    sendMessage(text)
  }, [sendMessage])

  // Watch for user input to hide recommendations
  useEffect(() => {
    const handleInput = () => {
      // Hide recommendations as soon as user starts typing
      if (showRecommendations) {
        setHasMessages(true)
        setShowRecommendations(false)
      }
    }

    const handleSubmit = () => {
      // Ensure recommendations stay hidden after message is sent
      setHasMessages(true)
      setShowRecommendations(false)
    }

    // Start monitoring after a delay to ensure C1Chat is mounted
    const timeout = setTimeout(() => {
      // Monitor input elements
      const inputElement = document.querySelector('textarea, input[type="text"]')
      if (inputElement) {
        inputElement.addEventListener('input', handleInput)
        inputElement.addEventListener('keydown', handleInput)
      }

      // Monitor form submissions
      const form = document.querySelector('form')
      if (form) {
        form.addEventListener('submit', handleSubmit)
      }

      // Also monitor for any button clicks that might send messages
      document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement
        if (
          target.matches('button[type="submit"], button[aria-label*="send" i]') ||
          target.closest('button[type="submit"], button[aria-label*="send" i]')
        ) {
          handleSubmit()
        }
      })
    }, 500)

    return () => {
      clearTimeout(timeout)
      const inputElement = document.querySelector('textarea, input[type="text"]')
      if (inputElement) {
        inputElement.removeEventListener('input', handleInput)
        inputElement.removeEventListener('keydown', handleInput)
      }
      const form = document.querySelector('form')
      if (form) {
        form.removeEventListener('submit', handleSubmit)
      }
    }
  }, [showRecommendations])

  // Watch for new chat events to show recommendations again
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (
        target.textContent?.toLowerCase().includes('new chat') ||
        target.getAttribute('aria-label')?.toLowerCase().includes('new chat')
      ) {
        // Reset states to show recommendations again
        setHasMessages(false)
        setTimeout(() => setShowRecommendations(true), 100)

        // Close menu/sidebar on mobile after clicking New Chat
        setTimeout(() => {
          // Try to find and click the menu close button or backdrop
          const menuButton = document.querySelector('[aria-label*="menu" i], [aria-label*="close" i]') as HTMLElement
          const backdrop = document.querySelector('[class*="backdrop" i], [class*="overlay" i]') as HTMLElement

          if (menuButton && window.innerWidth < 768) {
            menuButton.click()
          } else if (backdrop && window.innerWidth < 768) {
            backdrop.click()
          }
        }, 200)
      }
    }

    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  // Inject recommendations into C1Chat DOM
  useEffect(() => {
    if (!showRecommendations || hasMessages) {
      const injected = document.querySelector('.recommendations-overlay')
      if (injected) {
        injected.remove()
      }
      return
    }

    const injectRecommendations = () => {
      if (document.querySelector('.recommendations-overlay')) {
        return
      }

      const inputElement = document.querySelector('textarea, input[type="text"]')
      if (!inputElement) {
        return
      }

      const targetContainer = inputElement.closest('[class*="container"], [class*="wrapper"], form, div') as HTMLElement
      if (!targetContainer) {
        return
      }

      // Create overlay container
      const overlay = document.createElement('div')
      overlay.className = 'recommendations-overlay'

      const container = document.createElement('div')
      container.className = 'recommendations-container'

      RECOMMENDATIONS.forEach((rec) => {
        const box = document.createElement('div')
        box.className = 'recommendation-box'
        box.setAttribute('role', 'button')
        box.setAttribute('tabindex', '0')

        const icon = document.createElement('span')
        icon.className = 'recommendation-icon'
        icon.textContent = rec.icon

        const text = document.createElement('p')
        text.className = 'recommendation-text'
        text.textContent = rec.text

        box.appendChild(icon)
        box.appendChild(text)

        box.addEventListener('click', (e) => {
          e.preventDefault()
          e.stopPropagation()
          e.stopImmediatePropagation()
          handleRecommendationClick(rec.text)
        }, { capture: true })

        container.appendChild(box)
      })

      overlay.appendChild(container)
      targetContainer.insertAdjacentElement('beforebegin', overlay)
    }

    const timeout1 = setTimeout(injectRecommendations, 500)
    const timeout2 = setTimeout(injectRecommendations, 1000)

    return () => {
      clearTimeout(timeout1)
      clearTimeout(timeout2)
      const injected = document.querySelector('.recommendations-overlay')
      if (injected) {
        injected.remove()
      }
    }
  }, [showRecommendations, hasMessages, handleRecommendationClick])

  // Monitor chat messages for stock queries and financial statement queries and render charts
  useEffect(() => {
    const checkMessagesAndRenderCharts = () => {
      // Find all message elements in the chat
      const messageElements = document.querySelectorAll('[class*="message"], [class*="Message"], [role="presentation"]')

      messageElements.forEach(element => {
        const messageElement = element as HTMLElement

        // Skip if we've already processed this message
        if (messageElement.hasAttribute('data-chart-processed')) {
          return
        }

        // Get the text content of the message
        const textContent = messageElement.textContent || ''
        if (!textContent || textContent.length < 10) {
          return
        }

        // Check if this is a user message or assistant message containing financial statement query
        const financialQuery = detectFinancialStatementQuery(textContent)
        if (financialQuery) {
          // Mark as processed
          messageElement.setAttribute('data-chart-processed', 'true')

          // Render financial statement chart
          renderFinancialStatementChart(
            financialQuery.ticker,
            financialQuery.statementType,
            messageElement,
            chartContainerRef.current,
            chartRootsRef.current
          )
        } else {
          // Check if this is a stock price query
          const tickers = detectStockQuery(textContent)
          if (tickers && tickers.length > 0) {
            // Mark as processed
            messageElement.setAttribute('data-chart-processed', 'true')

            // Render chart for the first ticker found
            const ticker = tickers[0]
            renderChartForTicker(ticker, messageElement, chartContainerRef.current, chartRootsRef.current)
          } else {
            // Mark as processed even if no query found
            messageElement.setAttribute('data-chart-processed', 'true')
          }
        }
      })
    }

    // Set up MutationObserver to watch for new messages
    const observer = new MutationObserver(() => {
      checkMessagesAndRenderCharts()
    })

    // Start observing after a delay to ensure chat is mounted
    const timeout = setTimeout(() => {
      const chatContainer = document.querySelector('[class*="chat"], [class*="Chat"], [class*="conversation"], [class*="messages"]')
      if (chatContainer) {
        observer.observe(chatContainer, {
          childList: true,
          subtree: true
        })
      }

      // Initial check
      checkMessagesAndRenderCharts()
    }, 1000)

    // Also check periodically as a fallback
    const interval = setInterval(checkMessagesAndRenderCharts, 3000)

    // Capture ref values for cleanup
    const chartRoots = chartRootsRef.current
    const chartContainers = chartContainerRef.current

    return () => {
      clearTimeout(timeout)
      clearInterval(interval)
      observer.disconnect()

      // Clean up chart roots first to properly unmount React components
      chartRoots.forEach(root => {
        root.unmount()
      })
      chartRoots.clear()

      // Then remove the containers
      chartContainers.forEach(container => {
        container.remove()
      })
      chartContainers.clear()
    }
  }, [])

  // Prepare chat configuration
  const chatConfig = {
    apiUrl: API_URL,
    agentName: "Market Insight",
    logoUrl: "/icon.png",
    formFactor: "full-page" as const,
  }

  // Add API key if configured (optional authentication)
  const configWithAuth = API_KEY
    ? { ...chatConfig, customHeaders: { "X-API-Key": API_KEY } }
    : chatConfig

  return (
    <div className="app-container" ref={chatContainerRef}>
      <ThemeProvider mode="dark">
        <C1Chat {...configWithAuth} />
      </ThemeProvider>
    </div>
  )
}

export default App