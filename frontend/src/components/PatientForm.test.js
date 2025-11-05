import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import PatientForm from './PatientForm.svelte'

describe('PatientForm Component', () => {
  it('renders form with name input', () => {
    const { container } = render(PatientForm, { props: { mode: 'create' } })
    expect(container.querySelector('input[type="text"]')).toBeInTheDocument()
  })

  it('renders form with patient description textarea', () => {
    const { container } = render(PatientForm, { props: { mode: 'create' } })
    expect(container.querySelector('textarea')).toBeInTheDocument()
  })

  it('renders submit button', () => {
    const { getByText } = render(PatientForm, { props: { mode: 'create' } })
    expect(getByText(/Save|Create/)).toBeInTheDocument()
  })

  it('renders cancel button', () => {
    const { getByText } = render(PatientForm, { props: { mode: 'create' } })
    expect(getByText('Cancel')).toBeInTheDocument()
  })

  it('populates form with initial data in edit mode', () => {
    const initialData = { name: 'John Doe', patient_description: 'Initial notes' }
    const { container } = render(PatientForm, {
      props: { mode: 'edit', data: initialData }
    })
    const nameInput = container.querySelector('input[type="text"]')
    const descriptionTextarea = container.querySelector('textarea')

    expect(nameInput.value).toBe('John Doe')
    expect(descriptionTextarea.value).toBe('Initial notes')
  })

  it('dispatches submit event with form data', async () => {
    const { component, container, getByText } = render(PatientForm, {
      props: { mode: 'create' }
    })
    const user = userEvent.setup()

    let submitData = null
    component.$on('submit', (event) => {
      submitData = event.detail
    })

    const nameInput = container.querySelector('input[type="text"]')
    const descriptionTextarea = container.querySelector('textarea')

    await user.type(nameInput, 'Jane Smith')
    await user.type(descriptionTextarea, 'Test notes')
    await user.click(getByText(/Save|Create/))

    expect(submitData).toEqual({
      name: 'Jane Smith',
      patient_description: 'Test notes'
    })
  })

  it('dispatches cancel event when cancel button clicked', async () => {
    const { component, getByText } = render(PatientForm, { props: { mode: 'create' } })
    const user = userEvent.setup()

    let cancelFired = false
    component.$on('cancel', () => {
      cancelFired = true
    })

    await user.click(getByText('Cancel'))
    expect(cancelFired).toBe(true)
  })

  it('shows validation error for empty name', async () => {
    const { component, getByText, container } = render(PatientForm, { props: { mode: 'create' } })
    const user = userEvent.setup()

    let submitFired = false
    component.$on('submit', () => {
      submitFired = true
    })

    await user.click(getByText(/Save|Create/))
    expect(submitFired).toBe(false)

    // Look specifically for the error message in the p tag
    const errorMessage = container.querySelector('p.text-red-600')
    expect(errorMessage).toBeInTheDocument()
    expect(errorMessage.textContent).toContain('required')
  })

  it('clears form after successful submit', async () => {
    const { component, container, getByText } = render(PatientForm, {
      props: { mode: 'create' }
    })
    const user = userEvent.setup()

    const nameInput = container.querySelector('input[type="text"]')
    const notesTextarea = container.querySelector('textarea')

    await user.type(nameInput, 'Test Patient')
    await user.type(notesTextarea, 'Test notes')

    component.$on('submit', () => {
      // Form should reset after submit
    })

    await user.click(getByText(/Save|Create/))

    expect(nameInput.value).toBe('')
    expect(notesTextarea.value).toBe('')
  })
})
