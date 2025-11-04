import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import PatientDetail from './PatientDetail.svelte'

vi.mock('../stores/patients', () => ({
  patients: {
    subscribe: vi.fn((fn) => {
      fn({
        updatePatient: vi.fn(async () => {}),
        uploadFile: vi.fn(async () => {})
      })
      return vi.fn()
    })
  }
}))

vi.mock('../stores/ui', () => ({
  ui: {
    subscribe: vi.fn((fn) => {
      fn({ toasts: [] })
      return vi.fn()
    }),
    addToast: vi.fn()
  }
}))

describe('PatientDetail Component', () => {
  const mockPatient = {
    id: 1,
    name: 'John Doe',
    notes: 'Test patient',
    date_created: '2025-01-01'
  }

  const mockFiles = [
    {
      id: 1,
      filename: 'session1.mp3',
      file_type: 'audio',
      upload_date: '2025-01-01T10:00:00Z',
      processing_status: 'completed'
    }
  ]

  it('displays patient name', () => {
    const { getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    expect(getByText('John Doe')).toBeInTheDocument()
  })

  it('displays patient notes', () => {
    const { getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    expect(getByText('Test patient')).toBeInTheDocument()
  })

  it('renders edit patient button', () => {
    const { getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    expect(getByText('Edit Patient')).toBeInTheDocument()
  })

  it('renders back to list button', () => {
    const { getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    expect(getByText('Back to List')).toBeInTheDocument()
  })

  it('displays file list when files provided', () => {
    const { getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    expect(getByText('session1.mp3')).toBeInTheDocument()
  })

  it('renders file upload section', () => {
    const { container } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    // Should have file upload area
    const uploadArea = container.querySelector('[role="region"]')
    expect(uploadArea).toBeInTheDocument()
  })

  it('dispatches back event when back button clicked', async () => {
    const { component, getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    const user = userEvent.setup()

    let backFired = false
    component.$on('back', () => {
      backFired = true
    })

    await user.click(getByText('Back to List'))
    expect(backFired).toBe(true)
  })

  it('dispatches edit event when edit button clicked', async () => {
    const { component, getByText } = render(PatientDetail, {
      props: { patient: mockPatient, files: mockFiles }
    })
    const user = userEvent.setup()

    let editFired = false
    component.$on('edit', () => {
      editFired = true
    })

    await user.click(getByText('Edit Patient'))
    expect(editFired).toBe(true)
  })
})
