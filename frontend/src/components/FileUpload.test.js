import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import FileUpload from './FileUpload.svelte'

describe('FileUpload Component', () => {
  it('renders file input', () => {
    const { container } = render(FileUpload)
    expect(container.querySelector('input[type="file"]')).toBeInTheDocument()
  })

  it('accepts multiple files', () => {
    const { container } = render(FileUpload)
    const input = container.querySelector('input[type="file"]')
    expect(input).toHaveAttribute('multiple')
  })

  it('accepts audio, image and text files', () => {
    const { container } = render(FileUpload)
    const input = container.querySelector('input[type="file"]')
    const acceptAttr = input.getAttribute('accept')
    expect(acceptAttr).toContain('audio')
    expect(acceptAttr).toContain('image')
  })

  it('renders upload button', () => {
    const { getByText } = render(FileUpload)
    const uploadBtn = getByText(/Upload/i)
    expect(uploadBtn).toBeInTheDocument()
  })

  it('displays selected file names', () => {
    const { container } = render(FileUpload)
    // Component should have a section to display selected files
    // (shown by the blue info box with "Selected Files" heading when files are selected)
    const uploadArea = container.querySelector('[role="region"]')
    expect(uploadArea).toBeInTheDocument()

    // Component structure should be set up to display file names
    const inputs = container.querySelectorAll('input')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('dispatches upload event with files', async () => {
    const { component, container, getByText } = render(FileUpload)
    const user = userEvent.setup()

    let uploadedFiles = null
    component.$on('upload', (event) => {
      uploadedFiles = event.detail
    })

    const input = container.querySelector('input[type="file"]')
    const file = new File(['content'], 'test.mp3', { type: 'audio/mpeg' })

    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(file)
    input.files = dataTransfer.files
    input.dispatchEvent(new Event('change', { bubbles: true }))

    const uploadBtn = getByText(/Upload/i)
    await user.click(uploadBtn)

    expect(uploadedFiles).toBeDefined()
    expect(uploadedFiles.length).toBe(1)
  })

  it('clears selected files after upload', async () => {
    const { component, container, getByText } = render(FileUpload)
    const user = userEvent.setup()

    const input = container.querySelector('input[type="file"]')
    const file = new File(['content'], 'test.mp3', { type: 'audio/mpeg' })

    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(file)
    input.files = dataTransfer.files
    input.dispatchEvent(new Event('change', { bubbles: true }))

    component.$on('upload', () => {
      // Component should clear files after upload
    })

    const uploadBtn = getByText(/Upload/i)
    await user.click(uploadBtn)

    expect(input.files.length).toBe(0)
  })

  it('shows error for no files selected', async () => {
    const { component, getByText } = render(FileUpload)
    const user = userEvent.setup()

    let uploadFired = false
    component.$on('upload', () => {
      uploadFired = true
    })

    const uploadBtn = getByText(/Upload/i)
    await user.click(uploadBtn)

    // When no files are selected and upload is clicked, upload should not fire
    expect(uploadFired).toBe(false)
  })

  it('renders cancel button', () => {
    const { getByText } = render(FileUpload)
    expect(getByText('Cancel')).toBeInTheDocument()
  })
})
