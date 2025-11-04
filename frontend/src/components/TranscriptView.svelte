<script>
  import { createEventDispatcher } from 'svelte'
  import ProcessingStatus from './ProcessingStatus.svelte'

  export let file = null

  const dispatch = createEventDispatcher()

  function getFileTypeLabel(fileType) {
    const labels = {
      audio: 'Audio',
      image: 'Image',
      text: 'Text',
      video: 'Video'
    }
    return labels[fileType] || 'File'
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  function handleCopy() {
    if (file?.transcribed_content) {
      navigator.clipboard.writeText(file.transcribed_content)
    }
  }

  function handleBack() {
    dispatch('back')
  }
</script>

{#if file}
  <div class="space-y-6">
    <!-- File Header -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <h2 class="text-3xl font-bold text-gray-900">{file.filename}</h2>
          <div class="flex gap-4 text-sm text-gray-600 mt-2">
            <span>{getFileTypeLabel(file.file_type)}</span>
            <span>{formatDate(file.upload_date)}</span>
          </div>
        </div>
      </div>

      <div class="mt-4">
        <ProcessingStatus
          status={file.processing_status}
          filename={file.filename}
          errorMessage={file.error_message}
        />
      </div>

      <div class="flex gap-4 mt-6">
        <button
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          on:click={handleCopy}
          disabled={!file.transcribed_content}
        >
          Copy Transcript
        </button>
        <button
          class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          on:click={handleBack}
        >
          Back
        </button>
      </div>
    </div>

    <!-- Transcript Content -->
    {#if file.transcribed_content}
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Transcript</h3>
        <div class="bg-gray-50 rounded-lg p-6 max-h-96 overflow-y-auto">
          <p class="text-gray-800 whitespace-pre-wrap leading-relaxed">
            {file.transcribed_content}
          </p>
        </div>
      </div>
    {:else if file.processing_status === 'processing'}
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <p class="text-blue-800">Processing file... Transcript will appear here once complete.</p>
      </div>
    {:else if file.processing_status === 'failed'}
      <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p class="text-red-800">Failed to process file. Please try again.</p>
      </div>
    {:else}
      <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <p class="text-gray-600">Transcript not yet processed.</p>
      </div>
    {/if}
  </div>
{:else}
  <div class="text-center py-12">
    <p class="text-gray-600">No file selected</p>
  </div>
{/if}
