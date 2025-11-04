import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import FileList from './FileList.svelte'

describe('FileList Component', () => {
  const mockFiles = [
    {
      id: 1,
      filename: 'session1.mp3',
      file_type: 'audio',
      upload_date: '2025-01-01T10:00:00Z',
      processing_status: 'completed'
    },
    {
      id: 2,
      filename: 'intake_form.jpg',
      file_type: 'image',
      upload_date: '2025-01-02T11:00:00Z',
      processing_status: 'pending'
    }
  ]

  it('renders file list heading', () => {
    const { getByText } = render(FileList, { props: { files: mockFiles } })
    expect(getByText(/files/i)).toBeInTheDocument()
  })

  it('displays file count', () => {
    const { container } = render(FileList, { props: { files: mockFiles } })
    // Component shows file count in heading like "Files (2)"
    expect(container.textContent).toContain('(2)')
  })

  it('renders file names', () => {
    const { getByText } = render(FileList, { props: { files: mockFiles } })
    expect(getByText('session1.mp3')).toBeInTheDocument()
    expect(getByText('intake_form.jpg')).toBeInTheDocument()
  })

  it('displays file types', () => {
    const { getByText } = render(FileList, { props: { files: mockFiles } })
    expect(getByText(/audio/i)).toBeInTheDocument()
    expect(getByText(/image/i)).toBeInTheDocument()
  })

  it('shows file upload date', () => {
    const { container } = render(FileList, { props: { files: mockFiles } })
    // Should contain formatted date
    expect(container.innerHTML).toContain('2025')
  })

  it('displays processing status', () => {
    const { container } = render(FileList, { props: { files: mockFiles } })
    // Check for processing status in component
    expect(container.textContent).toContain('completed')
    expect(container.textContent).toContain('pending')
  })

  it('renders delete button for each file', () => {
    const { getAllByText } = render(FileList, { props: { files: mockFiles } })
    const deleteButtons = getAllByText('Delete')
    expect(deleteButtons.length).toBeGreaterThanOrEqual(2)
  })

  it('shows empty state when no files', () => {
    const { getByText } = render(FileList, { props: { files: [] } })
    expect(getByText(/no files|empty/i)).toBeInTheDocument()
  })

  it('dispatches delete event when delete button clicked', async () => {
    const { component, getAllByText } = render(FileList, { props: { files: mockFiles } })
    const user = userEvent.setup()

    let deletedFileId = null
    component.$on('delete', (event) => {
      deletedFileId = event.detail
    })

    global.confirm = () => true

    const deleteButtons = getAllByText('Delete')
    await user.click(deleteButtons[0])

    expect(deletedFileId).toBe(1)
  })

  it('shows confirmation before delete', async () => {
    const { getAllByText } = render(FileList, { props: { files: mockFiles } })
    const user = userEvent.setup()

    const confirmCalled = { value: false }
    global.confirm = (message) => {
      confirmCalled.value = true
      expect(message).toContain('session1.mp3')
      return false
    }

    const deleteButtons = getAllByText('Delete')
    await user.click(deleteButtons[0])

    expect(confirmCalled.value).toBe(true)
  })
})
