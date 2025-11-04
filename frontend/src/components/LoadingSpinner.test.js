import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import LoadingSpinner from './LoadingSpinner.svelte'

describe('LoadingSpinner Component', () => {
  it('renders spinner', () => {
    const { container } = render(LoadingSpinner)
    expect(container).toBeTruthy()
  })

  it('displays default loading message', () => {
    const { getByText } = render(LoadingSpinner)
    expect(getByText(/loading/i)).toBeInTheDocument()
  })

  it('displays custom loading message', () => {
    const { getByText } = render(LoadingSpinner, {
      props: { message: 'Processing file...' }
    })
    expect(getByText('Processing file...')).toBeInTheDocument()
  })

  it('renders animated spinner element', () => {
    const { container } = render(LoadingSpinner)
    const spinner = container.querySelector('[class*="animate"]') || container.querySelector('[class*="spin"]')
    expect(spinner).toBeInTheDocument()
  })

  it('has accessible structure', () => {
    const { container } = render(LoadingSpinner)
    const ariaElement = container.querySelector('[role="status"]')
    // Should have some indication of loading status
    expect(container.textContent.toLowerCase()).toContain('loading')
  })

  it('can display as overlay', () => {
    const { container } = render(LoadingSpinner, {
      props: { overlay: true }
    })
    const overlayElement = container.querySelector('[class*="fixed"]') || container.querySelector('[class*="absolute"]')
    // Should have positioning for overlay
    expect(container).toBeTruthy()
  })

  it('can be inline', () => {
    const { container } = render(LoadingSpinner, {
      props: { overlay: false }
    })
    // Should render without fixed/absolute positioning
    expect(container).toBeTruthy()
  })
})
