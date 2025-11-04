import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import Toast from './Toast.svelte'

describe('Toast Component', () => {
  it('renders toast message', () => {
    const { getByText } = render(Toast, {
      props: {
        id: '1',
        message: 'Success!',
        type: 'success'
      }
    })
    expect(getByText('Success!')).toBeInTheDocument()
  })

  it('displays success toast with green styling', () => {
    const { container } = render(Toast, {
      props: {
        id: '1',
        message: 'Success!',
        type: 'success'
      }
    })
    const toast = container.firstChild
    expect(toast.textContent).toContain('Success!')
    expect(toast.className).toContain('bg-green') || expect(toast.className).toContain('success')
  })

  it('displays error toast with red styling', () => {
    const { container } = render(Toast, {
      props: {
        id: '1',
        message: 'Error occurred',
        type: 'error'
      }
    })
    const toast = container.firstChild
    expect(toast.textContent).toContain('Error occurred')
    expect(toast.className).toContain('bg-red') || expect(toast.className).toContain('error')
  })

  it('displays info toast with blue styling', () => {
    const { container } = render(Toast, {
      props: {
        id: '1',
        message: 'Information',
        type: 'info'
      }
    })
    const toast = container.firstChild
    expect(toast.textContent).toContain('Information')
    expect(toast.className).toContain('bg-blue') || expect(toast.className).toContain('info')
  })

  it('has close button', () => {
    const { getByRole } = render(Toast, {
      props: {
        id: '1',
        message: 'Test',
        type: 'success'
      }
    })
    const closeButton = getByRole('button', { name: /close|×/i })
    expect(closeButton).toBeInTheDocument()
  })

  it('dispatches close event when close button clicked', async () => {
    const { component, getByRole } = render(Toast, {
      props: {
        id: '1',
        message: 'Test',
        type: 'success'
      }
    })
    const user = userEvent.setup()

    let closedId = null
    component.$on('close', (event) => {
      closedId = event.detail
    })

    const closeButton = getByRole('button', { name: /close|×/i })
    await user.click(closeButton)

    expect(closedId).toBe('1')
  })

  it('renders with icon for success', () => {
    const { container } = render(Toast, {
      props: {
        id: '1',
        message: 'Success!',
        type: 'success'
      }
    })
    expect(container.innerHTML).toContain('✓') || expect(container.innerHTML).toContain('✔')
  })

  it('renders with icon for error', () => {
    const { container } = render(Toast, {
      props: {
        id: '1',
        message: 'Error',
        type: 'error'
      }
    })
    expect(container.innerHTML).toContain('✕') || expect(container.innerHTML).toContain('✗') || expect(container.innerHTML).toContain('×')
  })

  it('renders with icon for info', () => {
    const { container } = render(Toast, {
      props: {
        id: '1',
        message: 'Info',
        type: 'info'
      }
    })
    expect(container.innerHTML).toContain('ℹ') || expect(container.innerHTML).toContain('ⓘ') || expect(container.innerHTML).toContain('i')
  })
})
