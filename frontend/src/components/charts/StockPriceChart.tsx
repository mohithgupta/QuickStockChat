import { useState, useCallback, useMemo, useRef } from 'react'
import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Brush,
  ReferenceArea
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
  enableZoom?: boolean
  enableBrush?: boolean
  brushHeight?: number
}

// Type for Recharts tooltip props
interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    payload: StockPriceData
    name?: string
    value?: number
  }>
}

// Custom tooltip component
const CustomTooltip = ({ active, payload }: CustomTooltipProps) => {
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
  showLegend,
  enableZoom,
  enableBrush,
  brushHeight
}: {
  data: StockPriceData[]
  lineColor?: string
  onDataPointClick?: (data: StockPriceData) => void
  showGrid?: boolean
  showLegend?: boolean
  enableZoom?: boolean
  enableBrush?: boolean
  brushHeight?: number
}) => {
  const [zoomArea, setZoomArea] = useState<{ startIndex?: number; endIndex?: number } | null>(null)
  const [filteredData, setFilteredData] = useState<StockPriceData[]>(data)
  const [isZoomed, setIsZoomed] = useState(false)

  const handleClick = useCallback(
    (data: StockPriceData) => {
      if (onDataPointClick && data) {
        onDataPointClick(data)
      }
    },
    [onDataPointClick]
  )

  // Type for chart event data
  interface ChartEventData {
    activeTooltipIndex?: number
  }

  // Handle zoom selection
  const handleMouseDown = useCallback((chartData: ChartEventData) => {
    if (enableZoom) {
      setZoomArea({ startIndex: chartData.activeTooltipIndex })
    }
  }, [enableZoom])

  const handleMouseMove = useCallback((chartData: ChartEventData) => {
    if (enableZoom && zoomArea && zoomArea.startIndex !== undefined) {
      setZoomArea({ ...zoomArea, endIndex: chartData.activeTooltipIndex })
    }
  }, [enableZoom, zoomArea])

  const handleMouseUp = useCallback(() => {
    if (enableZoom && zoomArea && zoomArea.startIndex !== undefined && zoomArea.endIndex !== undefined) {
      const start = Math.min(zoomArea.startIndex, zoomArea.endIndex)
      const end = Math.max(zoomArea.startIndex, zoomArea.endIndex)
      if (end - start > 1) {
        setFilteredData(data.slice(start, end + 1))
        setIsZoomed(true)
      }
    }
    setZoomArea(null)
  }, [enableZoom, zoomArea, data])

  // Reset zoom
  const handleResetZoom = useCallback(() => {
    setFilteredData(data)
    setIsZoomed(false)
  }, [data])

  // Type for brush event data
  interface BrushEventData {
    startIndex?: number
    endIndex?: number
  }

  // Handle brush change
  const handleBrushChange = useCallback((brushData: BrushEventData) => {
    if (enableBrush && brushData && brushData.startIndex !== undefined && brushData.endIndex !== undefined) {
      const start = Math.min(brushData.startIndex, brushData.endIndex)
      const end = Math.max(brushData.startIndex, brushData.endIndex)
      setFilteredData(data.slice(start, end + 1))
      setIsZoomed(true)
    }
  }, [enableBrush, data])

  const displayData = isZoomed ? filteredData : data

  return (
    <div style={{ position: 'relative' }}>
      {isZoomed && (
        <button
          onClick={handleResetZoom}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            padding: '5px 10px',
            backgroundColor: '#8884d8',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            zIndex: 10
          }}
          aria-label="Reset zoom"
        >
          Reset Zoom
        </button>
      )}
      <RechartsLineChart
        data={displayData}
        margin={{ top: 5, right: 30, left: 20, bottom: enableBrush ? (brushHeight || 40) + 10 : 5 }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
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
        {zoomArea && zoomArea.startIndex !== undefined && zoomArea.endIndex !== undefined && (
          <ReferenceArea
            x1={displayData[Math.min(zoomArea.startIndex, zoomArea.endIndex)]?.date}
            x2={displayData[Math.max(zoomArea.startIndex, zoomArea.endIndex)]?.date}
            strokeOpacity={0.3}
            fill="rgba(136, 132, 216, 0.2)"
          />
        )}
        <Line
          type="monotone"
          dataKey="close"
          stroke={lineColor || '#8884d8'}
          strokeWidth={2}
          dot={displayData.length < 50 ? { fill: lineColor || '#8884d8', r: 4 } : false}
          activeDot={{ r: 6, onClick: handleClick }}
          name="Price"
        />
        {enableBrush && !isZoomed && (
          <Brush
            dataKey="date"
            height={brushHeight || 40}
            stroke="#8884d8"
            fill="rgba(136, 132, 216, 0.1)"
            travellerWidth={10}
            onChange={handleBrushChange}
          />
        )}
      </RechartsLineChart>
    </div>
  )
}

// Candlestick Chart Component (simulated using custom render)
const CandlestickChartView = ({
  data,
  upColor,
  downColor: _downColor,
  onDataPointClick,
  showGrid,
  showLegend,
  enableZoom,
  enableBrush,
  brushHeight
}: {
  data: StockPriceData[]
  upColor?: string
  downColor?: string
  onDataPointClick?: (data: StockPriceData) => void
  showGrid?: boolean
  showLegend?: boolean
  enableZoom?: boolean
  enableBrush?: boolean
  brushHeight?: number
}) => {
  const handleClick = useCallback(
    (dataPoint: StockPriceData) => {
      if (onDataPointClick) {
        onDataPointClick(dataPoint)
      }
    },
    [onDataPointClick]
  )

  const [zoomArea, setZoomArea] = useState<{ startIndex?: number; endIndex?: number } | null>(null)
  const [filteredData, setFilteredData] = useState<StockPriceData[]>(data)
  const [isZoomed, setIsZoomed] = useState(false)

  // Transform data for candlestick representation using line for close prices
  const candlestickData = useMemo(() => {
    const currentData = isZoomed ? filteredData : data
    return currentData.map((item) => ({
      ...item,
      x: item.date,
      open: item.open,
      close: item.close,
      high: item.high,
      low: item.low
    }))
  }, [data, filteredData, isZoomed])

  // Handle zoom selection
  const handleMouseDown = useCallback((chartData: ChartEventData) => {
    if (enableZoom) {
      setZoomArea({ startIndex: chartData.activeTooltipIndex })
    }
  }, [enableZoom])

  const handleMouseMove = useCallback((chartData: ChartEventData) => {
    if (enableZoom && zoomArea && zoomArea.startIndex !== undefined) {
      setZoomArea({ ...zoomArea, endIndex: chartData.activeTooltipIndex })
    }
  }, [enableZoom, zoomArea])

  const handleMouseUp = useCallback(() => {
    if (enableZoom && zoomArea && zoomArea.startIndex !== undefined && zoomArea.endIndex !== undefined) {
      const start = Math.min(zoomArea.startIndex, zoomArea.endIndex)
      const end = Math.max(zoomArea.startIndex, zoomArea.endIndex)
      if (end - start > 1) {
        const newDataToFilter = isZoomed ? filteredData : data
        setFilteredData(newDataToFilter.slice(start, end + 1))
        setIsZoomed(true)
      }
    }
    setZoomArea(null)
  }, [enableZoom, zoomArea, data, filteredData, isZoomed])

  // Reset zoom
  const handleResetZoom = useCallback(() => {
    setFilteredData(data)
    setIsZoomed(false)
  }, [data])

  // Type for brush event data
  interface BrushEventData {
    startIndex?: number
    endIndex?: number
  }

  // Handle brush change
  const handleBrushChange = useCallback((brushData: BrushEventData) => {
    if (enableBrush && brushData && brushData.startIndex !== undefined && brushData.endIndex !== undefined) {
      const start = Math.min(brushData.startIndex, brushData.endIndex)
      const end = Math.max(brushData.startIndex, brushData.endIndex)
      setFilteredData(data.slice(start, end + 1))
      setIsZoomed(true)
    }
  }, [enableBrush, data])

  const displayData = isZoomed ? filteredData : data

  return (
    <div style={{ position: 'relative' }}>
      {isZoomed && (
        <button
          onClick={handleResetZoom}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            padding: '5px 10px',
            backgroundColor: '#8884d8',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            zIndex: 10
          }}
          aria-label="Reset zoom"
        >
          Reset Zoom
        </button>
      )}
      <RechartsLineChart
        data={candlestickData}
        margin={{ top: 5, right: 30, left: 20, bottom: enableBrush ? (brushHeight || 40) + 10 : 5 }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
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
        {zoomArea && zoomArea.startIndex !== undefined && zoomArea.endIndex !== undefined && (
          <ReferenceArea
            x1={displayData[Math.min(zoomArea.startIndex, zoomArea.endIndex)]?.date}
            x2={displayData[Math.max(zoomArea.startIndex, zoomArea.endIndex)]?.date}
            strokeOpacity={0.3}
            fill="rgba(136, 132, 216, 0.2)"
          />
        )}
        <Line
          type="monotone"
          dataKey="close"
          stroke={upColor || '#52ca9e'}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6, onClick: handleClick }}
          name="Close Price"
        />
        {enableBrush && !isZoomed && (
          <Brush
            dataKey="date"
            height={brushHeight || 40}
            stroke="#8884d8"
            fill="rgba(136, 132, 216, 0.1)"
            travellerWidth={10}
            onChange={handleBrushChange}
          />
        )}
      </RechartsLineChart>
    </div>
  )
}

// Helper function to download CSV
function downloadCSV(data: StockPriceData[], filename: string): void {
  if (!data || data.length === 0) {
    return
  }

  const headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
  const rows = data.map((item) => [
    item.date,
    item.open?.toFixed(2) || '',
    item.high?.toFixed(2) || '',
    item.low?.toFixed(2) || '',
    item.close?.toFixed(2) || '',
    item.volume?.toLocaleString() || ''
  ])

  const csvContent = [headers, ...rows]
    .map((row) => row.join(','))
    .join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  link.style.visibility = 'hidden'

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  URL.revokeObjectURL(url)
}

// Helper function to download PNG
function downloadPNG(element: HTMLElement | null, filename: string): void {
  if (!element) {
    return
  }

  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  if (!ctx) {
    return
  }

  const svgElement = element.querySelector('svg')

  if (!svgElement) {
    return
  }

  const svgData = new XMLSerializer().serializeToString(svgElement)
  const svgSize = svgElement.getBoundingClientRect()

  canvas.width = svgSize.width * 2
  canvas.height = svgSize.height * 2
  ctx.scale(2, 2)

  const img = new Image()
  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)

  img.onload = () => {
    ctx.drawImage(img, 0, 0)

    const pngUrl = canvas.toDataURL('image/png')
    const link = document.createElement('a')

    link.download = `${filename}.png`
    link.href = pngUrl
    link.style.visibility = 'hidden'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(url)
  }

  img.src = url
}

// Main StockPriceChart Component
export function StockPriceChart({
  data,
  chartType = 'line',
  title,
  height = 400,
  showVolume: _showVolume,
  showLegend = true,
  showGrid = true,
  lineColor,
  upColor,
  downColor,
  onDataPointClick,
  className = '',
  enableZoom = true,
  enableBrush = true,
  brushHeight = 40
}: StockPriceChartProps) {
  const [currentChartType, setCurrentChartType] = useState<ChartType>(chartType)
  const chartRef = useRef<HTMLDivElement>(null)

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

  // Handle CSV export
  const handleExportCSV = useCallback(() => {
    const filename = title ? title.replace(/\s+/g, '-').toLowerCase() : 'stock-price-chart'
    downloadCSV(data, filename)
  }, [data, title])

  // Handle PNG export
  const handleExportPNG = useCallback(() => {
    const filename = title ? title.replace(/\s+/g, '-').toLowerCase() : 'stock-price-chart'
    downloadPNG(chartRef.current, filename)
  }, [title])

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

  return (
    <div className={`stock-price-chart ${className}`} style={{ width: '100%' }} ref={chartRef}>
      {title && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '10px',
            flexWrap: 'wrap',
            gap: '10px'
          }}
        >
          <h3 style={{ margin: 0, color: '#fff' }}>{title}</h3>
          <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
            <button
              onClick={() => handleChartTypeChange('line')}
              style={{
                padding: '5px 10px',
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
            <button
              onClick={handleExportPNG}
              style={{
                padding: '5px 10px',
                backgroundColor: '#52ca9e',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
              aria-label="Export chart as PNG"
            >
              PNG
            </button>
            <button
              onClick={handleExportCSV}
              style={{
                padding: '5px 10px',
                backgroundColor: '#ff7300',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
              aria-label="Export data as CSV"
            >
              CSV
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
            enableZoom={enableZoom}
            enableBrush={enableBrush}
            brushHeight={brushHeight}
          />
        ) : (
          <CandlestickChartView
            data={data}
            upColor={upColor}
            downColor={downColor}
            onDataPointClick={onDataPointClick}
            showGrid={showGrid}
            showLegend={showLegend}
            enableZoom={enableZoom}
            enableBrush={enableBrush}
            brushHeight={brushHeight}
          />
        )}
      </ResponsiveContainer>
    </div>
  )
}

export default StockPriceChart
