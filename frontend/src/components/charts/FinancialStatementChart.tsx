import { useState, useCallback, useMemo } from 'react'
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
  CartesianGrid
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

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: any) => {
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
        {label || data.label || data.name}
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
  yAxisLabel
}: {
  data: FinancialDataPoint[]
  colors?: string[]
  onDataPointClick?: (data: FinancialDataPoint) => void
  showGrid?: boolean
  showLegend?: boolean
  xAxisLabel?: string
  yAxisLabel?: string
}) => {
  const handleClick = useCallback(
    (data: any) => {
      if (onDataPointClick && data) {
        onDataPointClick(data)
      }
    },
    [onDataPointClick]
  )

  const chartColors = colors || DEFAULT_COLORS

  return (
    <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
      <Bar
        dataKey="value"
        fill={chartColors[0]}
        onClick={handleClick}
        name="Value"
      />
    </BarChart>
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
    (data: any) => {
      if (onDataPointClick && data) {
        onDataPointClick(data)
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
        label={({ label, percent }) => `${label}: ${(percent * 100).toFixed(0)}%`}
        outerRadius={80}
        fill="#8884d8"
        dataKey="value"
        onClick={handleClick}
      >
        {data.map((entry, index) => (
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
  showDataLabels = false
}: FinancialStatementChartProps) {
  const [currentChartType, setCurrentChartType] = useState<ChartType>(chartType)
  const [error, setError] = useState<string | null>(null)

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

  if (error) {
    return (
      <div
        className={`financial-statement-chart-error ${className}`}
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
    <div className={`financial-statement-chart ${className}`} style={{ width: '100%' }}>
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
              onClick={() => handleChartTypeChange('bar')}
              style={{
                padding: '5px 10px',
                marginRight: '5px',
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
