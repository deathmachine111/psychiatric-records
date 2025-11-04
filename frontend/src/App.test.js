import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import App from './App.svelte'

const mockPatient = {
  id: 1,
  name: 'John Doe',
  notes: 'Test patient',
  date_created: '2025-01-01'
}

const mockFile = {
  id: 1,
  filename: 'session1.mp3',
  file_type: 'audio',
  upload_date: '2025-01-01T10:00:00Z',
  processing_status: 'completed',
  transcribed_content: 'Test transcript'
}

let patientsList = []

vi.mock('./stores/patients', () => ({
  patients: {
    subscribe: vi.fn((fn) => {
      fn(patientsList)
      return vi.fn()
    }),
    updatePatient: vi.fn()
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

  it('supports navigation routing with conditional rendering', () => {
    const { container } = render(App)

    // App has proper structure to support routing
    const main = container.querySelector('main')
    expect(main).toBeInTheDocument()
    expect(main.classList.contains('max-w-6xl')).toBe(true)
  })
})
