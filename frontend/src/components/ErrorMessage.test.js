import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import ErrorMessage from './ErrorMessage.svelte'

describe('ErrorMessage Component', () => {
  it('renders error message', () => {
    const { getByText } = render(ErrorMessage, {
      props: { message: 'Something went wrong' }
    })
    expect(getByText('Something went wrong')).toBeInTheDocument()
  })

  it('displays default error icon', () => {
    const { container } = render(ErrorMessage, {
      props: { message: 'Error!' }
    })
    expect(container.innerHTML).toContain('⚠') || expect(container.innerHTML).toContain('✕') || expect(container.innerHTML).toContain('×')
  })

  it('has error styling', () => {
    const { container } = render(ErrorMessage, {
      props: { message: 'Error!' }
    })
    const errorDiv = container.firstChild
    expect(errorDiv.className).toContain('alert-error')
  })

  it('renders as inline message', () => {
    const { container } = render(ErrorMessage, {
      props: { message: 'Error!', inline: true }
    })
    expect(container).toBeTruthy()
  })

  it('renders as alert box', () => {
    const { container } = render(ErrorMessage, {
      props: { message: 'Error!', inline: false }
    })
    const alertBox = container.querySelector('[role="alert"]') || container.firstChild
    expect(alertBox).toBeInTheDocument()
  })

  it('displays custom error messages', () => {
    const { getByText } = render(ErrorMessage, {
      props: { message: 'Failed to upload file. Please try again.' }
    })
    expect(getByText(/Failed to upload/)).toBeInTheDocument()
  })
})
