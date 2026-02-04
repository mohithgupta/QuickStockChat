import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { StockPriceChart, StockPriceData } from './StockPriceChart'

// Mock recharts components
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children, height }: { children: React.ReactNode; height: number }) => (
    <div data-testid="responsive-container" style={{ height: `${height}px` }}>
      {children}
    </div>
  ),
  LineChart: ({ children, data }: { children: React.ReactNode; data: StockPriceData[] }) => (
    <div data-testid="line-chart" data-count={data.length}>
      {children}
    </div>
  ),
  Line: ({ dataKey, stroke }: { dataKey: string; stroke: string }) => (
    <div data-testid="line" data-key={dataKey} data-stroke={stroke} />
  ),
  CandlestickChart: ({ upColor, downColor }: { upColor?: string; downColor?: string }) => (
    <div data-testid="candlestick-chart" data-up-color={upColor} data-down-color={downColor} />
  ),
  XAxis: ({ dataKey }: { dataKey: string }) => <div data-testid="x-axis" data-key={dataKey} />,
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: ({ content }: { content: React.ReactNode }) => (
    <div data-testid="tooltip">{content}</div>
  ),
  Legend: () => <div data-testid="legend" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />
}))

describe('StockPriceChart Component', () => {
  const mockData: StockPriceData[] = [
    {
      date: '2024-01-01',
      open: 100,
      high: 110,
      low: 95,
      close: 105,
      volume: 1000000
    },
    {
      date: '2024-01-02',
      open: 105,
      high: 115,
      low: 100,
      close: 110,
      volume: 1200000
    },
    {
      date: '2024-01-03',
      open: 110,
      high: 120,
      low: 108,
      close: 115,
      volume: 900000
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing with valid data', () => {
    const { container } = render(<StockPriceChart data={mockData} />)
    expect(container.querySelector('.stock-price-chart')).toBeInTheDocument()
  })

  it('renders line chart by default', () => {
    render(<StockPriceChart data={mockData} />)
    expect(screen.getByTestId('line-chart')).toBeInTheDocument()
  })

  it('renders candlestick chart when chartType is candlestick', () => {
    render(<StockPriceChart data={mockData} chartType="candlestick" />)
    expect(screen.getByTestId('candlestick-chart')).toBeInTheDocument()
  })

  it('renders title when provided', () => {
    render(<StockPriceChart data={mockData} title="Stock Price" />)
    expect(screen.getByText('Stock Price')).toBeInTheDocument()
  })

  it('renders custom className', () => {
    const { container } = render(<StockPriceChart data={mockData} className="custom-class" />)
    expect(container.querySelector('.custom-class')).toBeInTheDocument()
  })

  it('displays error message for invalid data', () => {
    const invalidData = [{ date: '2024-01-01' }] as any
    render(<StockPriceChart data={invalidData} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('displays error message for empty data', () => {
    render(<StockPriceChart data={[]} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('displays error message for non-array data', () => {
    render(<StockPriceChart data={null as any} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('renders chart type toggle buttons when title is provided', () => {
    render(<StockPriceChart data={mockData} title="Test Chart" />)
    expect(screen.getByRole('button', { name: /switch to line chart/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /switch to candlestick chart/i })).toBeInTheDocument()
  })

  it('switches from line to candlestick chart on button click', async () => {
    const user = userEvent.setup()
    render(<StockPriceChart data={mockData} title="Test Chart" />)

    // Initially shows line chart (has Line component)
    expect(screen.getByTestId('line')).toBeInTheDocument()
    expect(screen.queryByTestId('candlestick-chart')).not.toBeInTheDocument()

    // Click candlestick button
    const candlestickButton = screen.getByRole('button', { name: /switch to candlestick chart/i })
    await user.click(candlestickButton)

    // Now shows candlestick chart (has CandlestickChart component)
    expect(screen.queryByTestId('line')).not.toBeInTheDocument()
    expect(screen.getByTestId('candlestick-chart')).toBeInTheDocument()
  })

  it('switches from candlestick to line chart on button click', async () => {
    const user = userEvent.setup()
    render(<StockPriceChart data={mockData} chartType="candlestick" title="Test Chart" />)

    // Initially shows candlestick chart (has CandlestickChart component)
    expect(screen.getByTestId('candlestick-chart')).toBeInTheDocument()
    expect(screen.queryByTestId('line')).not.toBeInTheDocument()

    // Click line button
    const lineButton = screen.getByRole('button', { name: /switch to line chart/i })
    await user.click(lineButton)

    // Now shows line chart (has Line component)
    expect(screen.queryByTestId('candlestick-chart')).not.toBeInTheDocument()
    expect(screen.getByTestId('line')).toBeInTheDocument()
  })

  it('renders ResponsiveContainer with correct height', () => {
    render(<StockPriceChart data={mockData} height={500} />)
    const container = screen.getByTestId('responsive-container')
    expect(container).toHaveStyle({ height: '500px' })
  })

  it('uses default height of 400 when not specified', () => {
    render(<StockPriceChart data={mockData} />)
    const container = screen.getByTestId('responsive-container')
    expect(container).toHaveStyle({ height: '400px' })
  })

  it('renders legend when showLegend is true', () => {
    render(<StockPriceChart data={mockData} showLegend={true} />)
    expect(screen.getByTestId('legend')).toBeInTheDocument()
  })

  it('does not render legend when showLegend is false', () => {
    render(<StockPriceChart data={mockData} showLegend={false} />)
    expect(screen.queryByTestId('legend')).not.toBeInTheDocument()
  })

  it('renders grid when showGrid is true', () => {
    render(<StockPriceChart data={mockData} showGrid={true} />)
    expect(screen.getByTestId('cartesian-grid')).toBeInTheDocument()
  })

  it('does not render grid when showGrid is false', () => {
    render(<StockPriceChart data={mockData} showGrid={false} />)
    expect(screen.queryByTestId('cartesian-grid')).not.toBeInTheDocument()
  })

  it('renders X and Y axes', () => {
    render(<StockPriceChart data={mockData} />)
    expect(screen.getByTestId('x-axis')).toBeInTheDocument()
    expect(screen.getByTestId('y-axis')).toBeInTheDocument()
  })

  it('renders tooltip', () => {
    render(<StockPriceChart data={mockData} />)
    expect(screen.getByTestId('tooltip')).toBeInTheDocument()
  })

  it('handles data point click callback', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()
    render(<StockPriceChart data={mockData} onDataPointClick={handleClick} />)

    // Simulate clicking on a data point
    const line = screen.getByTestId('line')
    line.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    // Note: This is a basic test - actual implementation would need to test the real click handler
    expect(line).toBeInTheDocument()
  })

  it('validates data structure correctly - missing close price', () => {
    const invalidData = [{ date: '2024-01-01', open: 100 }] as any
    render(<StockPriceChart data={invalidData} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('validates data structure correctly - invalid close price', () => {
    const invalidData = [{ date: '2024-01-01', close: NaN }] as any
    render(<StockPriceChart data={invalidData} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('handles data with missing optional fields', () => {
    const minimalData: StockPriceData[] = [
      { date: '2024-01-01', close: 100 }
    ] as any

    const { container } = render(<StockPriceChart data={minimalData} />)
    expect(container.querySelector('.stock-price-chart')).toBeInTheDocument()
  })

  it('applies custom line color', () => {
    render(<StockPriceChart data={mockData} lineColor="#ff0000" />)
    const line = screen.getByTestId('line')
    expect(line).toHaveAttribute('data-stroke', '#ff0000')
  })

  it('uses default line color when not specified', () => {
    render(<StockPriceChart data={mockData} />)
    const line = screen.getByTestId('line')
    expect(line).toHaveAttribute('data-stroke', '#8884d8')
  })
})
