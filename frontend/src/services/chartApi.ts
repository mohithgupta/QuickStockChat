/**
 * Chart API Service
 *
 * Provides functions to fetch chart data from the backend API for stock prices
 * and financial statements. These functions are used by chart components to
 * retrieve structured data for visualization.
 */

// API configuration from environment variables
const API_URL = import.meta.env.VITE_API_URL || 'https://marketinsight-skgl.onrender.com/api/chat'
const API_KEY = import.meta.env.VITE_API_KEY || ''

// Extract base URL for chart endpoints (remove /api/chat suffix if present)
const BASE_URL = API_URL.replace(/\/api\/chat$/, '')
const CHART_API_BASE = BASE_URL || 'https://marketinsight-skgl.onrender.com'

// =============================================================================
// TypeScript Types matching backend Pydantic models
// =============================================================================

/**
 * Single data point in a chart
 */
export interface ChartDataPoint {
  date: string
  value?: number
  open?: number
  high?: number
  low?: number
  close?: number
  volume?: number
  metadata?: Record<string, any>
}

/**
 * Complete chart response with metadata and data points
 */
export interface ChartResponse {
  ticker: string
  chart_type: string
  period: string
  data: ChartDataPoint[]
  metadata?: {
    data_points?: number
    date_range?: {
      start?: string
      end?: string
    }
    currency?: string
    statement_type?: string
    available_metrics?: string[]
  }
}

/**
 * Stock price data point for charts (maps to StockPriceData in components)
 */
export interface StockPriceData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

/**
 * Financial data point for charts (maps to FinancialDataPoint in components)
 */
export interface FinancialDataPoint {
  label: string
  value: number
  category?: string
  date?: string
}

// =============================================================================
// API Request Options
// =============================================================================

/**
 * Creates headers for API requests including API key if configured
 */
function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  }

  if (API_KEY) {
    headers['X-API-Key'] = API_KEY
  }

  return headers
}

/**
 * Handles API errors and throws descriptive error messages
 */
function handleApiError(response: Response, endpoint: string): never {
  if (response.status === 400) {
    throw new Error(`Invalid request parameters for ${endpoint}. Please check your inputs.`)
  } else if (response.status === 401) {
    throw new Error(`Authentication failed for ${endpoint}. Please check your API key.`)
  } else if (response.status === 403) {
    throw new Error(`Access denied to ${endpoint}. You may not have permission to access this resource.`)
  } else if (response.status === 404) {
    throw new Error(`Endpoint not found: ${endpoint}. The service may be unavailable.`)
  } else if (response.status === 429) {
    throw new Error(`Rate limit exceeded for ${endpoint}. Please wait and try again later.`)
  } else if (response.status >= 500) {
    throw new Error(`Server error (${response.status}) when fetching from ${endpoint}. Please try again later.`)
  } else {
    throw new Error(`Unexpected error (${response.status}) when fetching from ${endpoint}`)
  }
}

// =============================================================================
// Stock Price Chart API
// =============================================================================

/**
 * Valid time periods for stock price charts
 */
export type StockPricePeriod = '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y' | '10y' | 'ytd' | 'max'

/**
 * Parameters for fetching stock price chart data
 */
export interface StockPriceChartParams {
  ticker: string
  period?: StockPricePeriod
}

/**
 * Fetches stock price chart data from the backend API
 *
 * Provides OHLCV (Open, High, Low, Close, Volume) data for the specified
 * ticker and time period. Returns data in a format suitable for chart libraries
 * with support for line and candlestick charts.
 *
 * @param params - Chart parameters including ticker and optional period
 * @returns Promise resolving to ChartResponse with stock price data
 * @throws Error if request fails or returns invalid data
 *
 * @example
 * ```ts
 * const data = await fetchStockPriceChart({ ticker: 'AAPL', period: '1mo' })
 * console.log(`Retrieved ${data.data.length} data points for ${data.ticker}`)
 * ```
 */
export async function fetchStockPriceChart(
  params: StockPriceChartParams
): Promise<ChartResponse> {
  const { ticker, period = '1mo' } = params

  // Validate inputs
  if (!ticker || typeof ticker !== 'string') {
    throw new Error('Ticker is required and must be a string')
  }

  const validPeriods: StockPricePeriod[] = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
  if (!validPeriods.includes(period)) {
    throw new Error(`Invalid period '${period}'. Must be one of: ${validPeriods.join(', ')}`)
  }

  try {
    const url = new URL(`${CHART_API_BASE}/api/charts/stock-price`)
    url.searchParams.append('ticker', ticker)
    url.searchParams.append('period', period)

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getHeaders()
    })

    if (!response.ok) {
      handleApiError(response, 'stock-price-chart')
    }

    const data: ChartResponse = await response.json()
    return data
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error(`Failed to fetch stock price chart data for ${ticker}: ${String(error)}`)
  }
}

/**
 * Transforms backend ChartResponse to StockPriceData[] for StockPriceChart component
 *
 * @param response - ChartResponse from backend API
 * @returns Array of StockPriceData suitable for chart components
 */
export function transformStockPriceData(response: ChartResponse): StockPriceData[] {
  if (!response || !response.data || !Array.isArray(response.data)) {
    return []
  }

  return response.data
    .filter((point): point is ChartDataPoint & { close: number } => {
      // Filter out data points without required close price
      return typeof point.close === 'number' && !isNaN(point.close)
    })
    .map((point) => ({
      date: point.date,
      open: point.open ?? point.close ?? 0,
      high: point.high ?? point.close ?? 0,
      low: point.low ?? point.close ?? 0,
      close: point.close,
      volume: point.volume
    }))
}

// =============================================================================
// Financial Statement Chart API
// =============================================================================

/**
 * Valid financial statement types
 */
export type StatementType = 'income' | 'balance' | 'cash_flow'

/**
 * Parameters for fetching financial statement chart data
 */
export interface FinancialStatementChartParams {
  ticker: string
  statementType: StatementType
}

/**
 * Fetches financial statement chart data from the backend API
 *
 * Provides financial statement data (income statement, balance sheet, or cash flow)
 * for the specified ticker. Returns data in a format suitable for chart libraries
 * with support for bar charts and time-series analysis.
 *
 * @param params - Chart parameters including ticker and statement type
 * @returns Promise resolving to ChartResponse with financial statement data
 * @throws Error if request fails or returns invalid data
 *
 * @example
 * ```ts
 * const data = await fetchFinancialStatementChart({ ticker: 'AAPL', statementType: 'income' })
 * console.log(`Retrieved ${data.data.length} data points for income statement`)
 * ```
 */
export async function fetchFinancialStatementChart(
  params: FinancialStatementChartParams
): Promise<ChartResponse> {
  const { ticker, statementType } = params

  // Validate inputs
  if (!ticker || typeof ticker !== 'string') {
    throw new Error('Ticker is required and must be a string')
  }

  const validStatementTypes: StatementType[] = ['income', 'balance', 'cash_flow']
  if (!validStatementTypes.includes(statementType)) {
    throw new Error(`Invalid statement type '${statementType}'. Must be one of: ${validStatementTypes.join(', ')}`)
  }

  try {
    const url = new URL(`${CHART_API_BASE}/api/charts/financial-statement`)
    url.searchParams.append('ticker', ticker)
    url.searchParams.append('statement_type', statementType)

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getHeaders()
    })

    if (!response.ok) {
      handleApiError(response, 'financial-statement-chart')
    }

    const data: ChartResponse = await response.json()
    return data
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error(`Failed to fetch financial statement chart data for ${ticker}: ${String(error)}`)
  }
}

/**
 * Transforms backend ChartResponse to FinancialDataPoint[] for FinancialStatementChart component
 *
 * @param response - ChartResponse from backend API
 * @returns Array of FinancialDataPoint suitable for chart components
 */
export function transformFinancialStatementData(response: ChartResponse): FinancialDataPoint[] {
  if (!response || !response.data || !Array.isArray(response.data)) {
    return []
  }

  return response.data
    .filter((point): point is ChartDataPoint & { value: number } => {
      // Filter out data points without required value
      return typeof point.value === 'number' && !isNaN(point.value)
    })
    .map((point, index) => ({
      label: point.date,
      value: point.value,
      category: response.metadata?.statement_type || response.chart_type,
      date: point.date
    }))
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Formats a date string for display in chart labels
 *
 * @param dateString - ISO format date string
 * @returns Formatted date string (e.g., "Jan 15, 2024")
 */
export function formatChartDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    // Check if date is invalid
    if (isNaN(date.getTime())) {
      return dateString
    }
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  } catch {
    return dateString
  }
}

/**
 * Validates if a ChartResponse contains valid chart data
 *
 * @param response - ChartResponse to validate
 * @returns True if response contains valid data, false otherwise
 */
export function isValidChartResponse(response: unknown): response is ChartResponse {
  if (!response || typeof response !== 'object') {
    return false
  }

  const chartResponse = response as Partial<ChartResponse>

  return (
    typeof chartResponse.ticker === 'string' &&
    typeof chartResponse.chart_type === 'string' &&
    typeof chartResponse.period === 'string' &&
    Array.isArray(chartResponse.data) &&
    chartResponse.data.length > 0
  )
}
