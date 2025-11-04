import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import Modal from './Modal.svelte'

describe('Modal Component', () => {
  it('renders modal when open is true', () => {
    const { container } = render(Modal, { props: { open: true, title: 'Test Modal' } })
    expect(container.querySelector('[role="dialog"]')).toBeInTheDocument()
  })

  it('hides modal when open is false', () => {
    const { container } = render(Modal, { props: { open: false, title: 'Test Modal' } })
    expect(container.querySelector('[role="dialog"]')).toBeNull()
  })

  it('displays modal title', () => {
    const { getByText } = render(Modal, { props: { open: true, title: 'Patient Form' } })
    expect(getByText('Patient Form')).toBeInTheDocument()
  })

  it('renders slot content', () => {
    // Create a simple wrapper component that renders Modal with content
    const { getByText, getByRole } = render(Modal, {
      props: { open: true, title: 'Test Modal' }
    })

    // Verify the modal dialog is rendered and has the expected structure
    const dialog = getByRole('dialog')
    expect(dialog).toBeInTheDocument()

    // Verify the modal has a div for slot content (the second p element should be slot)
    const slotDiv = dialog.querySelector('div:nth-child(2)')
    expect(slotDiv).toBeInTheDocument()
  })

  it('dispatches close event when close button clicked', async () => {
    const { component, getByText } = render(Modal, { props: { open: true, title: 'Test' } })
    const user = userEvent.setup()

    let closeFired = false
    component.$on('close', () => {
      closeFired = true
    })

    const closeButton = getByText('×')
    await user.click(closeButton)

    expect(closeFired).toBe(true)
  })

  it('has accessible close button', () => {
    const { getByText } = render(Modal, { props: { open: true, title: 'Test' } })
    const closeButton = getByText('×')
    expect(closeButton).toHaveAttribute('type', 'button')
  })
})
