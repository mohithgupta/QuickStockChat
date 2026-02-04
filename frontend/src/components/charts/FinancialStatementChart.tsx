import { useState, useCallback, useMemo, useRef } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Brush,
  ReferenceArea
} from 'recharts'

// Types for financial statement data
export interface FinancialDataPoint {
  label: string
  value: number
  category?: string
  date?: string
}

export interface FinancialSeriesData {
  name: string
  data: FinancialDataPoint[]
  color?: string
}

export type ChartType = 'bar' | 'pie'

export interface FinancialStatementChartProps {
  data: FinancialDataPoint[] | FinancialSeriesData[]
  chartType?: ChartType
  title?: string
  height?: number
  showLegend?: boolean
  showGrid?: boolean
  colors?: string[]
  onDataPointClick?: (data: FinancialDataPoint) => void
  className?: string
  xAxisLabel?: string
  yAxisLabel?: string
  showDataLabels?: boolean
  enableZoom?: boolean
  enableBrush?: boolean
  brushHeight?: number
}

// Default colors for charts
const DEFAULT_COLORS = [
  '#8884d8',
  '#82ca9d',
  '#ffc658',
  '#ff7300',
  '#0088fe',
  '#00c49f',
  '#ffbb28',
  '#ff8042',
  '#8dd1e1',
  '#d0ed57'
]

// Type for Recharts tooltip props
interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    payload: FinancialDataPoint
    name?: string
    value?: number
  }>
  label?: string
}

// Type for chart event data
interface ChartEventData {
  activeTooltipIndex?: number | string | null
}

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
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
      <p style={{ margin: 0, fontWeight: 'bold' }}>
        {label || data.label}
      </p>
      <p style={{ margin: '5px 0 0 0', color: '#8884d8' }}>
        Value: {data.value?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </p>
      {data.category && (
        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#aaa' }}>
          {data.category}
        </p>
      )}
    </div>
  )
}

// Bar Chart Component
const BarChartView = ({
  data,
  colors,
  onDataPointClick,
  showGrid,
  showLegend,
  xAxisLabel,
  yAxisLabel,
  enableZoom,
  enableBrush,
  brushHeight
}: {
  data: FinancialDataPoint[]
  colors?: string[]
  onDataPointClick?: (data: FinancialDataPoint) => void
  showGrid?: boolean
  showLegend?: boolean
  xAxisLabel?: string
  yAxisLabel?: string
  enableZoom?: boolean
  enableBrush?: boolean
  brushHeight?: number
}) => {
  const handleClick = useCallback(
    (event: any) => {
      if (onDataPointClick && event && event.payload) {
        onDataPointClick(event.payload as FinancialDataPoint)
      }
    },
    [onDataPointClick]
  )

  const [zoomArea, setZoomArea] = useState<{ startIndex?: number; endIndex?: number } | null>(null)
  const [filteredData, setFilteredData] = useState<FinancialDataPoint[]>(data)
  const [isZoomed, setIsZoomed] = useState(false)

  const chartColors = colors || DEFAULT_COLORS

  // Handle zoom selection
  const handleMouseDown = useCallback((chartData: ChartEventData) => {
    if (enableZoom) {
      const index = typeof chartData.activeTooltipIndex === 'number' ? chartData.activeTooltipIndex : undefined
      setZoomArea({ startIndex: index })
    }
  }, [enableZoom])

  const handleMouseMove = useCallback((chartData: ChartEventData) => {
    if (enableZoom && zoomArea && zoomArea.startIndex !== undefined) {
      const index = typeof chartData.activeTooltipIndex === 'number' ? chartData.activeTooltipIndex : undefined
      setZoomArea({ ...zoomArea, endIndex: index })
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
      <BarChart
        data={displayData}
        margin={{ top: 5, right: 30, left: 20, bottom: enableBrush ? (brushHeight || 40) + 10 : 5 }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#333" />}
        <XAxis
          dataKey="label"
          stroke="#888"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#888' }}
          label={xAxisLabel ? { value: xAxisLabel, position: 'insideBottom', offset: -5, fill: '#888' } : undefined}
        />
        <YAxis
          stroke="#888"
          style={{ fontSize: '12px' }}
          tick={{ fill: '#888' }}
          label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', fill: '#888' } : undefined}
        />
        <Tooltip content={<CustomTooltip />} />
        {showLegend && <Legend />}
        {zoomArea && zoomArea.startIndex !== undefined && zoomArea.endIndex !== undefined && (
          <ReferenceArea
            x1={displayData[Math.min(zoomArea.startIndex, zoomArea.endIndex)]?.label}
            x2={displayData[Math.max(zoomArea.startIndex, zoomArea.endIndex)]?.label}
            strokeOpacity={0.3}
            fill="rgba(136, 132, 216, 0.2)"
          />
        )}
        <Bar
          dataKey="value"
          fill={chartColors[0]}
          onClick={handleClick}
          name="Value"
        />
        {enableBrush && !isZoomed && data.length > 10 && (
          <Brush
            dataKey="label"
            height={brushHeight || 40}
            stroke="#8884d8"
            fill="rgba(136, 132, 216, 0.1)"
            travellerWidth={10}
            onChange={handleBrushChange}
          />
        )}
      </BarChart>
    </div>
  )
}

// Pie Chart Component
const PieChartView = ({
  data,
  colors,
  onDataPointClick,
  showLegend
}: {
  data: FinancialDataPoint[]
  colors?: string[]
  onDataPointClick?: (data: FinancialDataPoint) => void
  showLegend?: boolean
}) => {
  const handleClick = useCallback(
    (event: any) => {
      if (onDataPointClick && event && event.payload) {
        onDataPointClick(event.payload as FinancialDataPoint)
      }
    },
    [onDataPointClick]
  )

  const chartColors = colors || DEFAULT_COLORS

  return (
    <PieChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        labelLine={false}
        label={(props: { label?: string; percent?: number }) => {
          const { label, percent } = props
          return `${label}: ${((percent || 0) * 100).toFixed(0)}%`
        }}
        outerRadius={80}
        fill="#8884d8"
        dataKey="value"
        onClick={handleClick}
      >
        {data.map((_entry, index) => (
          <Cell
            key={`cell-${index}`}
            fill={chartColors[index % chartColors.length]}
          />
        ))}
      </Pie>
      <Tooltip content={<CustomTooltip />} />
      {showLegend && <Legend />}
    </PieChart>
  )
}

// Helper function to download CSV
function downloadFinancialCSV(data: FinancialDataPoint[], filename: string): void {
  if (!data || data.length === 0) {
    return
  }

  const headers = ['Label', 'Value', 'Category', 'Date']
  const rows = data.map((item) => [
    item.label || '',
    item.value?.toFixed(2) || '',
    item.category || '',
    item.date || ''
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
function downloadFinancialPNG(element: HTMLElement | null, filename: string): void {
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

// Main FinancialStatementChart Component
export function FinancialStatementChart({
  data,
  chartType = 'bar',
  title,
  height = 400,
  showLegend = true,
  showGrid = true,
  colors,
  onDataPointClick,
  className = '',
  xAxisLabel,
  yAxisLabel,
  enableZoom = true,
  enableBrush = true,
  brushHeight = 40
}: FinancialStatementChartProps) {
  const [currentChartType, setCurrentChartType] = useState<ChartType>(chartType)
  const chartRef = useRef<HTMLDivElement>(null)

  // Normalize data to FinancialDataPoint[] format
  const normalizedData = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) {
      return []
    }

    // Check if it's an array of series data (FinancialSeriesData[])
    if ('data' in data[0]) {
      // For now, we'll just use the first series
      // This could be enhanced to support multiple series in grouped bar charts
      return (data as FinancialSeriesData[])[0].data
    }

    return data as FinancialDataPoint[]
  }, [data])

  // Validate data
  const isValidData = useMemo(() => {
    if (!Array.isArray(normalizedData) || normalizedData.length === 0) {
      return false
    }

    // Check if all required fields are present
    return normalizedData.every(
      (item) =>
        item.label &&
        typeof item.value === 'number' &&
        !isNaN(item.value)
    )
  }, [normalizedData])

  // Handle chart type change
  const handleChartTypeChange = useCallback((type: ChartType) => {
    setCurrentChartType(type)
  }, [])

  // Handle CSV export
  const handleExportCSV = useCallback(() => {
    const filename = title ? title.replace(/\s+/g, '-').toLowerCase() : 'financial-chart'
    downloadFinancialCSV(normalizedData, filename)
  }, [normalizedData, title])

  // Handle PNG export
  const handleExportPNG = useCallback(() => {
    const filename = title ? title.replace(/\s+/g, '-').toLowerCase() : 'financial-chart'
    downloadFinancialPNG(chartRef.current, filename)
  }, [title])

  // Handle errors
  if (!isValidData) {
    return (
      <div
        className={`financial-statement-chart-error ${className}`}
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
            Please provide valid financial data with labels and values
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={`financial-statement-chart ${className}`} style={{ width: '100%' }} ref={chartRef}>
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
              onClick={() => handleChartTypeChange('bar')}
              style={{
                padding: '5px 10px',
                backgroundColor: currentChartType === 'bar' ? '#8884d8' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
              aria-label="Switch to bar chart"
            >
              Bar
            </button>
            <button
              onClick={() => handleChartTypeChange('pie')}
              style={{
                padding: '5px 10px',
                backgroundColor: currentChartType === 'pie' ? '#8884d8' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
              aria-label="Switch to pie chart"
            >
              Pie
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
        {currentChartType === 'bar' ? (
          <BarChartView
            data={normalizedData}
            colors={colors}
            onDataPointClick={onDataPointClick}
            showGrid={showGrid}
            showLegend={showLegend}
            xAxisLabel={xAxisLabel}
            yAxisLabel={yAxisLabel}
            enableZoom={enableZoom}
            enableBrush={enableBrush}
            brushHeight={brushHeight}
          />
        ) : (
          <PieChartView
            data={normalizedData}
            colors={colors}
            onDataPointClick={onDataPointClick}
            showLegend={showLegend}
          />
        )}
      </ResponsiveContainer>
    </div>
  )
}

export default FinancialStatementChart
