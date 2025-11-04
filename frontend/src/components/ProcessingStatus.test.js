import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import ProcessingStatus from './ProcessingStatus.svelte'

describe('ProcessingStatus Component', () => {
  it('shows loading spinner when status is processing', () => {
    const { container } = render(ProcessingStatus, {
      props: { status: 'processing', filename: 'test.mp3' }
    })
    expect(container.textContent).toContain('Processing')
  })

  it('shows success icon when status is completed', () => {
    const { container } = render(ProcessingStatus, {
      props: { status: 'completed', filename: 'test.mp3' }
    })
    expect(container.textContent).toContain('Completed')
  })

  it('shows error icon when status is failed', () => {
    const { container } = render(ProcessingStatus, {
      props: { status: 'failed', filename: 'test.mp3' }
    })
    expect(container.textContent).toContain('Failed')
  })

  it('displays error message when provided', () => {
    const { getByText } = render(ProcessingStatus, {
      props: {
        status: 'failed',
        filename: 'test.mp3',
        errorMessage: 'File too large'
      }
    })
    expect(getByText('File too large')).toBeInTheDocument()
  })

  it('shows pending state with appropriate styling', () => {
    const { container } = render(ProcessingStatus, {
      props: { status: 'pending', filename: 'test.mp3' }
    })
    expect(container.textContent).toContain('Pending')
  })
})
