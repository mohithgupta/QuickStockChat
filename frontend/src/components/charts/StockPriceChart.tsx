import { useState, useCallback, useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  Line,
  CandlestickChart,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts'

// Types for stock price data
export interface StockPriceData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

export type ChartType = 'line' | 'candlestick'

export interface StockPriceChartProps {
  data: StockPriceData[]
  chartType?: ChartType
  title?: string
  height?: number
  showVolume?: boolean
  showLegend?: boolean
  showGrid?: boolean
  lineColor?: string
  upColor?: string
  downColor?: string
  onDataPointClick?: (data: StockPriceData) => void
  className?: string
}

// Custom tooltip component
const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload || !payload.length) {
    return null
  }

  const data = payload[0].payload
  return (
    <div
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        color: '#fff',
        padding: '10px',
        borderRadius: '4px',
        border: '1px solid #333'
      }}
    >
      <p style={{ margin: 0, fontWeight: 'bold' }}>{data.date}</p>
      <p style={{ margin: '5px 0 0 0', color: '#8884d8' }}>
        Open: {data.open?.toFixed(2)}
      </p>
      <p style={{ margin: '5px 0', color: '#82ca9d' }}>
        High: {data.high?.toFixed(2)}
      </p>
      <p style={{ margin: '5px 0', color: '#ffc658' }}>
        Low: {data.low?.toFixed(2)}
      </p>
      <p style={{ margin: '5px 0', color: '#ff7300' }}>
        Close: {data.close?.toFixed(2)}
      </p>
      {data.volume && (
        <p style={{ margin: '5px 0 0 0', color: '#aaa' }}>
          Volume: {data.volume.toLocaleString()}
        </p>
      )}
    </div>
  )
}

// Line Chart Component
const LineChartView = ({
  data,
  lineColor,
  onDataPointClick,
  showGrid,
  showLegend
}: {
  data: StockPriceData[]
  lineColor?: string
  onDataPointClick?: (data: StockPriceData) => void
  showGrid?: boolean
  showLegend?: boolean
}) => {
  const handleClick = useCallback(
    (data: any) => {
      if (onDataPointClick && data) {
        onDataPointClick(data)
      }
    },
    [onDataPointClick]
  )

  return (
    <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
      {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#333" />}
      <XAxis
        dataKey="date"
        stroke="#888"
        style={{ fontSize: '12px' }}
        tick={{ fill: '#888' }}
      />
      <YAxis
        stroke="#888"
        style={{ fontSize: '12px' }}
        tick={{ fill: '#888' }}
        domain={['auto', 'auto']}
      />
      <Tooltip content={<CustomTooltip />} />
      {showLegend && <Legend />}
      <Line
        type="monotone"
        dataKey="close"
        stroke={lineColor || '#8884d8'}
        strokeWidth={2}
        dot={{ fill: lineColor || '#8884d8', r: 4 }}
        activeDot={{ r: 6, onClick: handleClick }}
        name="Price"
      />
    </RechartsLineChart>
  )
}

// Candlestick Chart Component (simulated using custom render)
const CandlestickChartView = ({
  data,
  upColor,
  downColor,
  onDataPointClick,
  showGrid,
  showLegend
}: {
  data: StockPriceData[]
  upColor?: string
  downColor?: string
  onDataPointClick?: (data: StockPriceData) => void
  showGrid?: boolean
  showLegend?: boolean
}) => {
  const handleClick = useCallback(
    (dataPoint: StockPriceData) => {
      if (onDataPointClick) {
        onDataPointClick(dataPoint)
      }
    },
    [onDataPointClick]
  )

  // Transform data for recharts CandlestickChart
  const candlestickData = useMemo(() => {
    return data.map((item) => ({
      ...item,
      x: item.date,
      open: item.open,
      close: item.close,
      high: item.high,
      low: item.low
    }))
  }, [data])

  return (
    <RechartsLineChart data={candlestickData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
      {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#333" />}
      <XAxis
        dataKey="date"
        stroke="#888"
        style={{ fontSize: '12px' }}
        tick={{ fill: '#888' }}
      />
      <YAxis
        stroke="#888"
        style={{ fontSize: '12px' }}
        tick={{ fill: '#888' }}
        domain={['auto', 'auto']}
      />
      <Tooltip content={<CustomTooltip />} />
      {showLegend && <Legend />}
      <CandlestickChart
        upColor={upColor || '#52ca9e'}
        downColor={downColor || '#ff7300'}
        onClick={handleClick}
      />
    </RechartsLineChart>
  )
}

// Main StockPriceChart Component
export function StockPriceChart({
  data,
  chartType = 'line',
  title,
  height = 400,
  showVolume = false,
  showLegend = true,
  showGrid = true,
  lineColor,
  upColor,
  downColor,
  onDataPointClick,
  className = ''
}: StockPriceChartProps) {
  const [currentChartType, setCurrentChartType] = useState<ChartType>(chartType)
  const [error, setError] = useState<string | null>(null)

  // Validate data
  const isValidData = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) {
      return false
    }

    // Check if all required fields are present
    return data.every(
      (item) =>
        item.date &&
        typeof item.close === 'number' &&
        !isNaN(item.close)
    )
  }, [data])

  // Handle chart type change
  const handleChartTypeChange = useCallback((type: ChartType) => {
    setCurrentChartType(type)
  }, [])

  // Handle errors
  if (!isValidData) {
    return (
      <div
        className={`stock-price-chart-error ${className}`}
        style={{
          height: `${height}px`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ff7300',
          border: '1px dashed #ff7300',
          borderRadius: '4px',
          padding: '20px'
        }}
      >
        <div>
          <p style={{ margin: 0, fontWeight: 'bold' }}>Invalid Data</p>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#888' }}>
            Please provide valid stock price data with date and close prices
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div
        className={`stock-price-chart-error ${className}`}
        style={{
          height: `${height}px`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ff7300'
        }}
      >
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div className={`stock-price-chart ${className}`} style={{ width: '100%' }}>
      {title && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '10px'
          }}
        >
          <h3 style={{ margin: 0, color: '#fff' }}>{title}</h3>
          <div>
            <button
              onClick={() => handleChartTypeChange('line')}
              style={{
                padding: '5px 10px',
                marginRight: '5px',
                backgroundColor: currentChartType === 'line' ? '#8884d8' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
              aria-label="Switch to line chart"
            >
              Line
            </button>
            <button
              onClick={() => handleChartTypeChange('candlestick')}
              style={{
                padding: '5px 10px',
                backgroundColor: currentChartType === 'candlestick' ? '#8884d8' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
              aria-label="Switch to candlestick chart"
            >
              Candlestick
            </button>
          </div>
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        {currentChartType === 'line' ? (
          <LineChartView
            data={data}
            lineColor={lineColor}
            onDataPointClick={onDataPointClick}
            showGrid={showGrid}
            showLegend={showLegend}
          />
        ) : (
          <CandlestickChartView
            data={data}
            upColor={upColor}
            downColor={downColor}
            onDataPointClick={onDataPointClick}
            showGrid={showGrid}
            showLegend={showLegend}
          />
        )}
      </ResponsiveContainer>
    </div>
  )
}

export default StockPriceChart
