import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import App from './App.svelte'

vi.mock('./stores/patients', () => ({
  patients: {
    subscribe: vi.fn((fn) => {
      fn([])
      return vi.fn()
    })
  }
}))

vi.mock('./stores/ui', () => ({
  ui: {
    subscribe: vi.fn((fn) => {
      fn({ toasts: [], isLoading: false })
      return vi.fn()
    }),
    addToast: vi.fn()
  }
}))

describe('App Component', () => {
  it('renders navigation', () => {
    const { container } = render(App)
    expect(container.querySelector('nav')).toBeInTheDocument()
  })

  it('displays app title in navigation', () => {
    const { getByText } = render(App)
    expect(getByText(/Psychiatric Records/)).toBeInTheDocument()
  })

  it('renders patient list on initial load', () => {
    const { getByText } = render(App)
    expect(getByText(/Patients/)).toBeInTheDocument()
  })

  it('has main content area', () => {
    const { container } = render(App)
    expect(container.querySelector('main')).toBeInTheDocument()
  })
})
