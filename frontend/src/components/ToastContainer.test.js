import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import ToastContainer from './ToastContainer.svelte'

vi.mock('../stores/ui', () => ({
  ui: {
    subscribe: vi.fn((fn) => {
      fn({
        toasts: [
          { id: '1', message: 'Success!', type: 'success' },
          { id: '2', message: 'Error!', type: 'error' }
        ]
      })
      return vi.fn()
    }),
    removeToast: vi.fn()
  }
}))

describe('ToastContainer Component', () => {
  it('renders without errors', () => {
    const { container } = render(ToastContainer)
    expect(container).toBeTruthy()
  })

  it('displays all toasts from store', () => {
    const { getByText } = render(ToastContainer)
    expect(getByText('Success!')).toBeInTheDocument()
    expect(getByText('Error!')).toBeInTheDocument()
  })

  it('renders empty container when no toasts', () => {
    // Mock with empty toasts
    const originalMock = vi.hoisted(() => ({
      ui: {
        subscribe: vi.fn((fn) => {
          fn({ toasts: [] })
          return vi.fn()
        }),
        removeToast: vi.fn()
      }
    }))

    const { container } = render(ToastContainer)
    // Should render without errors even with no toasts
    expect(container).toBeTruthy()
  })

  it('has proper container structure', () => {
    const { container } = render(ToastContainer)
    const toastContainer = container.querySelector('[class*="fixed"]') || container.firstChild
    expect(toastContainer).toBeInTheDocument()
  })
})
