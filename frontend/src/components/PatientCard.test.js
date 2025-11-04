import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import PatientCard from './PatientCard.svelte'

describe('PatientCard Component', () => {
  const mockPatient = {
    id: 1,
    name: 'John Doe',
    notes: 'Test notes',
    date_created: '2025-01-01T00:00:00Z'
  }

  it('displays patient name', () => {
    const { getByText } = render(PatientCard, { props: { patient: mockPatient } })
    expect(getByText('John Doe')).toBeInTheDocument()
  })

  it('displays patient notes', () => {
    const { getByText } = render(PatientCard, { props: { patient: mockPatient } })
    expect(getByText('Test notes')).toBeInTheDocument()
  })

  it('displays creation date', () => {
    const { getByText } = render(PatientCard, { props: { patient: mockPatient } })
    expect(getByText(/Created:/)).toBeInTheDocument()
  })

  it('does not display notes when empty', () => {
    const patient = { ...mockPatient, notes: '' }
    const { queryByText } = render(PatientCard, { props: { patient } })
    expect(queryByText('Test notes')).toBeNull()
  })

  it('has delete button', () => {
    const { getByText } = render(PatientCard, { props: { patient: mockPatient } })
    expect(getByText('Delete')).toBeInTheDocument()
  })

  it('dispatches select event when card clicked', async () => {
    const { component, container } = render(PatientCard, { props: { patient: mockPatient } })
    const user = userEvent.setup()

    let selectedPatient = null
    component.$on('select', (event) => {
      selectedPatient = event.detail
    })

    const card = container.querySelector('[role="button"]')
    await user.click(card)

    expect(selectedPatient).toEqual(mockPatient)
  })

  it('dispatches delete event when delete button clicked', async () => {
    const { component, getByText } = render(PatientCard, { props: { patient: mockPatient } })
    const user = userEvent.setup()

    let deletedId = null
    component.$on('delete', (event) => {
      deletedId = event.detail
    })

    global.confirm = () => true

    await user.click(getByText('Delete'))

    expect(deletedId).toBe(mockPatient.id)
  })

  it('shows confirmation before delete', async () => {
    const { getByText } = render(PatientCard, { props: { patient: mockPatient } })
    const user = userEvent.setup()

    const confirmCalled = { value: false }
    global.confirm = (message) => {
      confirmCalled.value = true
      expect(message).toContain('John Doe')
      return false
    }

    await user.click(getByText('Delete'))

    expect(confirmCalled.value).toBe(true)
  })
})
