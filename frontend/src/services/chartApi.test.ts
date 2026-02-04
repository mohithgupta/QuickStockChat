import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  fetchStockPriceChart,
  fetchFinancialStatementChart,
  transformStockPriceData,
  transformFinancialStatementData,
  formatChartDate,
  isValidChartResponse,
  type ChartResponse
} from './chartApi'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('chartApi Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Set default environment variables
    import.meta.env.VITE_API_URL = 'https://marketinsight-skgl.onrender.com/api/chat'
    import.meta.env.VITE_API_KEY = ''
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('fetchStockPriceChart', () => {
    it('should fetch stock price data successfully', async () => {
      const mockResponse: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'line',
        period: '1mo',
        data: [
          {
            date: '2024-01-15',
            open: 150.0,
            high: 155.0,
            low: 149.0,
            close: 154.0,
            volume: 1000000
          },
          {
            date: '2024-01-16',
            open: 154.0,
            high: 158.0,
            low: 153.0,
            close: 157.0,
            volume: 1200000
          }
        ],
        metadata: {
          data_points: 2,
          date_range: {
            start: '2024-01-15',
            end: '2024-01-16'
          },
          currency: 'USD'
        }
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response)

      const result = await fetchStockPriceChart({ ticker: 'AAPL', period: '1mo' })

      expect(result).toEqual(mockResponse)
      expect(mockFetch).toHaveBeenCalledTimes(1)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/charts/stock-price?ticker=AAPL&period=1mo'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should validate ticker parameter', async () => {
      await expect(fetchStockPriceChart({ ticker: '' })).rejects.toThrow('Ticker is required')
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      await expect(fetchStockPriceChart({ ticker: null as any })).rejects.toThrow('Ticker is required')
    })

    it('should validate period parameter', async () => {
      await expect(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        fetchStockPriceChart({ ticker: 'AAPL', period: 'invalid' as any })
      ).rejects.toThrow("Invalid period 'invalid'")
    })

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400
      } as Response)

      await expect(fetchStockPriceChart({ ticker: 'INVALID' })).rejects.toThrow('Invalid request parameters')
    })

    it('should handle 401 authentication errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      } as Response)

      await expect(fetchStockPriceChart({ ticker: 'AAPL' })).rejects.toThrow('Authentication failed')
    })

    it('should handle 429 rate limit errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429
      } as Response)

      await expect(fetchStockPriceChart({ ticker: 'AAPL' })).rejects.toThrow('Rate limit exceeded')
    })

    it('should handle 500 server errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      } as Response)

      await expect(fetchStockPriceChart({ ticker: 'AAPL' })).rejects.toThrow('Server error')
    })

    it('should handle request with headers', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ticker: 'AAPL', chart_type: 'line', period: '1mo', data: [] })
      } as Response)

      await fetchStockPriceChart({ ticker: 'AAPL' })

      // Verify that headers are included in the request
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should use default period when not provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ticker: 'AAPL', chart_type: 'line', period: '1mo', data: [] })
      } as Response)

      await fetchStockPriceChart({ ticker: 'AAPL' })

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('period=1mo'),
        expect.any(Object)
      )
    })
  })

  describe('fetchFinancialStatementChart', () => {
    it('should fetch financial statement data successfully', async () => {
      const mockResponse: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'bar',
        period: 'income',
        data: [
          {
            date: '2023-12-31',
            value: 383285000000,
            metadata: { 'Total Revenue': 383285000000 }
          },
          {
            date: '2022-12-31',
            value: 365817000000,
            metadata: { 'Total Revenue': 365817000000 }
          }
        ],
        metadata: {
          data_points: 2,
          date_range: {
            start: '2022-12-31',
            end: '2023-12-31'
          },
          statement_type: 'income',
          available_metrics: ['Total Revenue', 'Net Income']
        }
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      } as Response)

      const result = await fetchFinancialStatementChart({
        ticker: 'AAPL',
        statementType: 'income'
      })

      expect(result).toEqual(mockResponse)
      expect(mockFetch).toHaveBeenCalledTimes(1)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/charts/financial-statement?ticker=AAPL&statement_type=income'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should validate ticker parameter', async () => {
      await expect(
        fetchFinancialStatementChart({ ticker: '', statementType: 'income' })
      ).rejects.toThrow('Ticker is required')
    })

    it('should validate statement type parameter', async () => {
      await expect(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        fetchFinancialStatementChart({ ticker: 'AAPL', statementType: 'invalid' as any })
      ).rejects.toThrow("Invalid statement type 'invalid'")
    })

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400
      } as Response)

      await expect(
        fetchFinancialStatementChart({ ticker: 'INVALID', statementType: 'income' })
      ).rejects.toThrow('Invalid request parameters')
    })

    it('should support all valid statement types', async () => {
      const statementTypes = ['income', 'balance', 'cash_flow'] as const

      for (const statementType of statementTypes) {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ticker: 'AAPL',
            chart_type: 'bar',
            period: statementType,
            data: []
          })
        } as Response)

        await expect(
          fetchFinancialStatementChart({ ticker: 'AAPL', statementType })
        ).resolves.toBeDefined()
      }
    })
  })

  describe('transformStockPriceData', () => {
    it('should transform ChartResponse to StockPriceData[]', () => {
      const response: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'candlestick',
        period: '1mo',
        data: [
          {
            date: '2024-01-15',
            open: 150.0,
            high: 155.0,
            low: 149.0,
            close: 154.0,
            volume: 1000000
          }
        ]
      }

      const result = transformStockPriceData(response)

      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        date: '2024-01-15',
        open: 150.0,
        high: 155.0,
        low: 149.0,
        close: 154.0,
        volume: 1000000
      })
    })

    it('should filter out data points without close price', () => {
      const response: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'line',
        period: '1mo',
        data: [
          {
            date: '2024-01-15',
            close: 154.0
          },
          {
            date: '2024-01-16',
            close: NaN
          },
          {
            date: '2024-01-17'
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
          } as any
        ]
      }

      const result = transformStockPriceData(response)

      expect(result).toHaveLength(1)
      expect(result[0].date).toBe('2024-01-15')
    })

    it('should handle missing OHLC data by using close price', () => {
      const response: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'line',
        period: '1mo',
        data: [
          {
            date: '2024-01-15',
            close: 154.0
          }
        ]
      }

      const result = transformStockPriceData(response)

      expect(result[0]).toEqual({
        date: '2024-01-15',
        open: 154.0,
        high: 154.0,
        low: 154.0,
        close: 154.0,
        volume: undefined
      })
    })

    it('should return empty array for invalid data', () => {
      /* eslint-disable @typescript-eslint/no-explicit-any */
      expect(transformStockPriceData(null as any)).toEqual([])
      expect(transformStockPriceData(undefined as any)).toEqual([])
      expect(transformStockPriceData({ data: null } as any)).toEqual([])
      expect(transformStockPriceData({ data: [] } as any)).toEqual([])
      /* eslint-enable @typescript-eslint/no-explicit-any */
    })
  })

  describe('transformFinancialStatementData', () => {
    it('should transform ChartResponse to FinancialDataPoint[]', () => {
      const response: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'bar',
        period: 'income',
        data: [
          {
            date: '2023-12-31',
            value: 383285000000,
            metadata: { 'Total Revenue': 383285000000 }
          }
        ],
        metadata: {
          statement_type: 'income'
        }
      }

      const result = transformFinancialStatementData(response)

      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        label: '2023-12-31',
        value: 383285000000,
        category: 'income',
        date: '2023-12-31'
      })
    })

    it('should filter out data points without value', () => {
      const response: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'bar',
        period: 'income',
        data: [
          {
            date: '2023-12-31',
            value: 383285000000
          },
          {
            date: '2022-12-31',
            value: NaN
          },
          {
            date: '2021-12-31'
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
          } as any
        ]
      }

      const result = transformFinancialStatementData(response)

      expect(result).toHaveLength(1)
      expect(result[0].label).toBe('2023-12-31')
    })

    it('should use chart_type as category if statement_type not in metadata', () => {
      const response: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'pie',
        period: 'balance',
        data: [
          {
            date: '2023-12-31',
            value: 100000000
          }
        ]
      }

      const result = transformFinancialStatementData(response)

      expect(result[0].category).toBe('pie')
    })

    it('should return empty array for invalid data', () => {
      /* eslint-disable @typescript-eslint/no-explicit-any */
      expect(transformFinancialStatementData(null as any)).toEqual([])
      expect(transformFinancialStatementData(undefined as any)).toEqual([])
      expect(transformFinancialStatementData({ data: null } as any)).toEqual([])
      expect(transformFinancialStatementData({ data: [] } as any)).toEqual([])
      /* eslint-enable @typescript-eslint/no-explicit-any */
    })
  })

  describe('formatChartDate', () => {
    it('should format ISO date string correctly', () => {
      const result = formatChartDate('2024-01-15')
      expect(result).toMatch(/Jan 15, 2024/)
    })

    it('should handle invalid date strings', () => {
      const result = formatChartDate('invalid-date')
      expect(result).toBe('invalid-date')
    })

    it('should handle various date formats', () => {
      expect(formatChartDate('2024-12-31')).toMatch(/Dec 31, 2024/)
      expect(formatChartDate('2024-02-05')).toMatch(/Feb 5, 2024/)
    })
  })

  describe('isValidChartResponse', () => {
    it('should return true for valid ChartResponse', () => {
      const validResponse: ChartResponse = {
        ticker: 'AAPL',
        chart_type: 'line',
        period: '1mo',
        data: [
          {
            date: '2024-01-15',
            close: 154.0
          }
        ]
      }

      expect(isValidChartResponse(validResponse)).toBe(true)
    })

    it('should return false for invalid responses', () => {
      expect(isValidChartResponse(null)).toBe(false)
      expect(isValidChartResponse(undefined)).toBe(false)
      expect(isValidChartResponse({})).toBe(false)
      expect(isValidChartResponse({ ticker: 'AAPL' })).toBe(false)
      expect(isValidChartResponse({ ticker: 'AAPL', chart_type: 'line', period: '1mo', data: [] })).toBe(false)
      expect(isValidChartResponse({ ticker: 'AAPL', chart_type: 'line', period: '1mo' } as unknown)).toBe(false)
    })

    it('should validate all required fields', () => {
      const missingTicker = { chart_type: 'line', period: '1mo', data: [{}] }
      const missingChartType = { ticker: 'AAPL', period: '1mo', data: [{}] }
      const missingPeriod = { ticker: 'AAPL', chart_type: 'line', data: [{}] }
      const missingData = { ticker: 'AAPL', chart_type: 'line', period: '1mo' }

      expect(isValidChartResponse(missingTicker as unknown)).toBe(false)
      expect(isValidChartResponse(missingChartType as unknown)).toBe(false)
      expect(isValidChartResponse(missingPeriod as unknown)).toBe(false)
      expect(isValidChartResponse(missingData as unknown)).toBe(false)
    })
  })
})
