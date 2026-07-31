import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import HealthGauge from '../components/HealthGauge'

describe('HealthGauge Component', () => {
  it('should render with correct score', () => {
    render(<HealthGauge score={75} />)
    const scoreElement = screen.getByText('75')
    expect(scoreElement).toBeInTheDocument()
  })

  it('should render with high score', () => {
    render(<HealthGauge score={90} />)
    const scoreElement = screen.getByText('90')
    expect(scoreElement).toBeInTheDocument()
  })

  it('should render with low score', () => {
    render(<HealthGauge score={30} />)
    const scoreElement = screen.getByText('30')
    expect(scoreElement).toBeInTheDocument()
  })

  it('should render with zero score', () => {
    render(<HealthGauge score={0} />)
    const scoreElement = screen.getByText('0')
    expect(scoreElement).toBeInTheDocument()
  })

  it('should render with perfect score', () => {
    render(<HealthGauge score={100} />)
    const scoreElement = screen.getByText('100')
    expect(scoreElement).toBeInTheDocument()
  })
})
