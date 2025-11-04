import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import TranscriptView from './TranscriptView.svelte'

describe('TranscriptView Component', () => {
  const mockFile = {
    id: 1,
    filename: 'session1.mp3',
    file_type: 'audio',
    upload_date: '2025-01-01T10:00:00Z',
    processing_status: 'completed',
    transcribed_content: 'This is a test transcript of the therapy session...'
  }

  it('displays filename', () => {
    const { getByText } = render(TranscriptView, { props: { file: mockFile } })
    expect(getByText('session1.mp3')).toBeInTheDocument()
  })

  it('displays file type', () => {
    const { container } = render(TranscriptView, { props: { file: mockFile } })
    expect(container.textContent).toContain('Audio')
  })

  it('displays upload date', () => {
    const { container } = render(TranscriptView, { props: { file: mockFile } })
    expect(container.textContent).toContain('2025')
  })

  it('displays processing status', () => {
    const { container } = render(TranscriptView, { props: { file: mockFile } })
    expect(container.textContent).toContain('Completed')
  })

  it('displays transcribed content', () => {
    const { getByText } = render(TranscriptView, { props: { file: mockFile } })
    expect(getByText(/This is a test transcript/)).toBeInTheDocument()
  })

  it('renders back link', () => {
    const { getByText } = render(TranscriptView, { props: { file: mockFile } })
    expect(getByText(/Back|Close/i)).toBeInTheDocument()
  })
})
