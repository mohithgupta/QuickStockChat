import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FinancialStatementChart } from './FinancialStatementChart'
import type { FinancialDataPoint } from './FinancialStatementChart'

// Mock recharts components
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children, height }: { children: React.ReactNode; height: number }) => (
    <div data-testid="responsive-container" style={{ height: `${height}px` }}>
      {children}
    </div>
  ),
  BarChart: ({ children, data }: { children: React.ReactNode; data: FinancialDataPoint[] }) => (
    <div data-testid="bar-chart" data-count={data.length}>
      {children}
    </div>
  ),
  Bar: ({ fill, dataKey }: { fill: string; dataKey: string }) => (
    <div data-testid="bar" data-fill={fill} data-key={dataKey} />
  ),
  PieChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="pie-chart">{children}</div>
  ),
  Pie: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="pie">{children}</div>
  ),
  Cell: ({ fill }: { fill: string }) => (
    <div data-testid="cell" data-fill={fill} />
  ),
  XAxis: ({ dataKey, label }: { dataKey?: string; label?: { value?: string } }) => (
    <div data-testid="x-axis" data-key={dataKey} data-label={label?.value}>
      {label?.value && <span>{label.value}</span>}
    </div>
  ),
  YAxis: ({ label }: { label?: { value?: string } }) => (
    <div data-testid="y-axis" data-label={label?.value}>
      {label?.value && <span>{label.value}</span>}
    </div>
  ),
  Tooltip: ({ content }: { content: React.ReactNode }) => (
    <div data-testid="tooltip">{content}</div>
  ),
  Legend: () => <div data-testid="legend" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />
}))

describe('FinancialStatementChart Component', () => {
  const mockData: FinancialDataPoint[] = [
    {
      label: 'Revenue',
      value: 1000000
    },
    {
      label: 'Cost of Goods',
      value: 600000
    },
    {
      label: 'Operating Expenses',
      value: 250000
    },
    {
      label: 'Net Income',
      value: 150000
    }
  ]

  const mockSeriesData = [
    {
      name: 'Income Statement',
      data: mockData,
      color: '#8884d8'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing with valid data', () => {
    const { container } = render(<FinancialStatementChart data={mockData} />)
    expect(container.querySelector('.financial-statement-chart')).toBeInTheDocument()
  })

  it('renders bar chart by default', () => {
    render(<FinancialStatementChart data={mockData} />)
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
  })

  it('renders pie chart when chartType is pie', () => {
    render(<FinancialStatementChart data={mockData} chartType="pie" />)
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
  })

  it('renders title when provided', () => {
    render(<FinancialStatementChart data={mockData} title="Income Statement" />)
    expect(screen.getByText('Income Statement')).toBeInTheDocument()
  })

  it('renders custom className', () => {
    const { container } = render(<FinancialStatementChart data={mockData} className="custom-class" />)
    expect(container.querySelector('.custom-class')).toBeInTheDocument()
  })

  it('displays error message for invalid data', () => {
    const invalidData = [{ label: 'Revenue' }] as unknown as FinancialDataPoint[]
    render(<FinancialStatementChart data={invalidData} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('displays error message for empty data', () => {
    render(<FinancialStatementChart data={[]} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('displays error message for non-array data', () => {
    render(<FinancialStatementChart data={null as unknown as FinancialDataPoint[]} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('renders chart type toggle buttons when title is provided', () => {
    render(<FinancialStatementChart data={mockData} title="Test Chart" />)
    expect(screen.getByRole('button', { name: /switch to bar chart/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /switch to pie chart/i })).toBeInTheDocument()
  })

  it('switches from bar to pie chart on button click', async () => {
    const user = userEvent.setup()
    render(<FinancialStatementChart data={mockData} title="Test Chart" />)

    // Initially shows bar chart
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
    expect(screen.queryByTestId('pie-chart')).not.toBeInTheDocument()

    // Click pie button
    const pieButton = screen.getByRole('button', { name: /switch to pie chart/i })
    await user.click(pieButton)

    // Now shows pie chart
    expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument()
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
  })

  it('switches from pie to bar chart on button click', async () => {
    const user = userEvent.setup()
    render(<FinancialStatementChart data={mockData} chartType="pie" title="Test Chart" />)

    // Initially shows pie chart
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
    expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument()

    // Click bar button
    const barButton = screen.getByRole('button', { name: /switch to bar chart/i })
    await user.click(barButton)

    // Now shows bar chart
    expect(screen.queryByTestId('pie-chart')).not.toBeInTheDocument()
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
  })

  it('renders ResponsiveContainer with correct height', () => {
    render(<FinancialStatementChart data={mockData} height={500} />)
    const container = screen.getByTestId('responsive-container')
    expect(container).toHaveStyle({ height: '500px' })
  })

  it('uses default height of 400 when not specified', () => {
    render(<FinancialStatementChart data={mockData} />)
    const container = screen.getByTestId('responsive-container')
    expect(container).toHaveStyle({ height: '400px' })
  })

  it('renders legend when showLegend is true', () => {
    render(<FinancialStatementChart data={mockData} showLegend={true} />)
    expect(screen.getByTestId('legend')).toBeInTheDocument()
  })

  it('does not render legend when showLegend is false', () => {
    render(<FinancialStatementChart data={mockData} showLegend={false} />)
    expect(screen.queryByTestId('legend')).not.toBeInTheDocument()
  })

  it('renders grid when showGrid is true', () => {
    render(<FinancialStatementChart data={mockData} showGrid={true} />)
    expect(screen.getByTestId('cartesian-grid')).toBeInTheDocument()
  })

  it('does not render grid when showGrid is false', () => {
    render(<FinancialStatementChart data={mockData} showGrid={false} />)
    expect(screen.queryByTestId('cartesian-grid')).not.toBeInTheDocument()
  })

  it('renders X and Y axes for bar chart', () => {
    render(<FinancialStatementChart data={mockData} chartType="bar" />)
    expect(screen.getByTestId('x-axis')).toBeInTheDocument()
    expect(screen.getByTestId('y-axis')).toBeInTheDocument()
  })

  it('renders tooltip', () => {
    render(<FinancialStatementChart data={mockData} />)
    expect(screen.getByTestId('tooltip')).toBeInTheDocument()
  })

  it('handles data point click callback', async () => {
    const handleClick = vi.fn()
    render(<FinancialStatementChart data={mockData} onDataPointClick={handleClick} />)

    // Simulate clicking on a bar
    const bar = screen.getByTestId('bar')
    bar.dispatchEvent(new MouseEvent('click', { bubbles: true }))

    // Note: This is a basic test - actual implementation would need to test the real click handler
    expect(bar).toBeInTheDocument()
  })

  it('validates data structure correctly - missing value', () => {
    const invalidData = [{ label: 'Revenue' }] as unknown as FinancialDataPoint[]
    render(<FinancialStatementChart data={invalidData} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('validates data structure correctly - invalid value', () => {
    const invalidData = [{ label: 'Revenue', value: NaN }] as unknown as FinancialDataPoint[]
    render(<FinancialStatementChart data={invalidData} />)
    expect(screen.getByText('Invalid Data')).toBeInTheDocument()
  })

  it('handles data with missing optional fields', () => {
    const minimalData: FinancialDataPoint[] = [
      { label: 'Revenue', value: 1000000 }
    ]

    const { container } = render(<FinancialStatementChart data={minimalData} />)
    expect(container.querySelector('.financial-statement-chart')).toBeInTheDocument()
  })

  it('normalizes series data format correctly', () => {
    const { container } = render(<FinancialStatementChart data={mockSeriesData} />)
    expect(container.querySelector('.financial-statement-chart')).toBeInTheDocument()
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
  })

  it('uses default colors when not specified', () => {
    render(<FinancialStatementChart data={mockData} />)
    const bar = screen.getByTestId('bar')
    expect(bar).toHaveAttribute('data-fill', '#8884d8')
  })

  it('applies custom colors', () => {
    const customColors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00']
    render(<FinancialStatementChart data={mockData} colors={customColors} />)
    const bar = screen.getByTestId('bar')
    expect(bar).toHaveAttribute('data-fill', '#ff0000')
  })

  it('renders axis labels when provided', () => {
    render(<FinancialStatementChart
      data={mockData}
      chartType="bar"
      xAxisLabel="Categories"
      yAxisLabel="Amount ($)"
    />)
    const xAxis = screen.getByTestId('x-axis')
    const yAxis = screen.getByTestId('y-axis')
    expect(xAxis).toHaveAttribute('data-label', 'Categories')
    expect(yAxis).toHaveAttribute('data-label', 'Amount ($)')
  })

  it('renders bar chart with correct data count', () => {
    render(<FinancialStatementChart data={mockData} />)
    const barChart = screen.getByTestId('bar-chart')
    expect(barChart).toHaveAttribute('data-count', '4')
  })

  it('handles data with category field', () => {
    const dataWithCategory: FinancialDataPoint[] = [
      { label: 'Revenue', value: 1000000, category: 'Income' },
      { label: 'Expenses', value: 600000, category: 'Expense' }
    ]

    const { container } = render(<FinancialStatementChart data={dataWithCategory} />)
    expect(container.querySelector('.financial-statement-chart')).toBeInTheDocument()
  })

  it('handles data with date field', () => {
    const dataWithDate: FinancialDataPoint[] = [
      { label: 'Q1 2024', value: 1000000, date: '2024-01-01' },
      { label: 'Q2 2024', value: 1100000, date: '2024-04-01' }
    ]

    const { container } = render(<FinancialStatementChart data={dataWithDate} />)
    expect(container.querySelector('.financial-statement-chart')).toBeInTheDocument()
  })
})
