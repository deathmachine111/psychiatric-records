<script>
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()

  let fileInput
  let selectedFiles = []
  let error = ''

  function handleFileSelect(event) {
    const files = event.target.files
    selectedFiles = Array.from(files).map((file) => ({
      name: file.name,
      size: file.size,
      type: file.type
    }))
    error = ''
  }

  function handleUpload() {
    if (selectedFiles.length === 0) {
      error = 'Please select files before uploading'
      return
    }

    // Get actual File objects from input
    const files = Array.from(fileInput.files)

    dispatch('upload', files)

    // Clear the input and selected files
    fileInput.value = ''
    selectedFiles = []
    error = ''
  }

  function handleCancel() {
    fileInput.value = ''
    selectedFiles = []
    error = ''
    dispatch('cancel')
  }

  function handleDragOver(e) {
    e.preventDefault()
    e.currentTarget.classList.add('drag-over')
  }

  function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over')
  }

  function handleDrop(e) {
    e.preventDefault()
    e.currentTarget.classList.remove('drag-over')

    const files = e.dataTransfer.files
    // Programmatically set the file input
    const dataTransfer = new DataTransfer()
    Array.from(files).forEach((file) => {
      dataTransfer.items.add(file)
    })
    fileInput.files = dataTransfer.files

    // Trigger change event manually
    fileInput.dispatchEvent(new Event('change', { bubbles: true }))
  }
</script>

<div
  class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition"
  on:dragover={handleDragOver}
  on:dragleave={handleDragLeave}
  on:drop={handleDrop}
  role="region"
  aria-label="File upload area"
>
  <input
    type="file"
    bind:this={fileInput}
    on:change={handleFileSelect}
    multiple
    accept="audio/*,image/*,.txt,.pdf"
    class="hidden"
    id="file-input"
  />

  <label for="file-input" class="cursor-pointer">
    <div class="text-gray-600 mb-3">
      <svg
        class="mx-auto w-12 h-12 mb-2"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 4v16m8-8H4"
        />
      </svg>
      <p class="font-medium">Drag files here or click to select</p>
      <p class="text-sm text-gray-500">Audio (MP3, WAV), Images (JPG, PNG), Text (TXT, PDF)</p>
    </div>
  </label>

  {#if selectedFiles.length > 0}
    <div class="mt-6 bg-blue-50 rounded-lg p-4">
      <h4 class="font-semibold text-gray-900 mb-3">Selected Files ({selectedFiles.length})</h4>
      <ul class="space-y-2">
        {#each selectedFiles as file}
          <li class="text-sm text-gray-700 text-left bg-white p-2 rounded flex justify-between items-center">
            <span>{file.name}</span>
            <span class="text-xs text-gray-500">{(file.size / 1024).toFixed(2)} KB</span>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  {#if error}
    <div class="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      {error}
    </div>
  {/if}
</div>

<div class="flex gap-3 justify-end mt-6">
  <button
    type="button"
    on:click={handleCancel}
    class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 font-medium text-gray-700"
  >
    Cancel
  </button>
  <button
    type="button"
    on:click={handleUpload}
    disabled={selectedFiles.length === 0}
    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
  >
    Upload {selectedFiles.length > 0 ? `(${selectedFiles.length})` : ''}
  </button>
</div>

<style>
  :global(.drag-over) {
    @apply border-blue-500 bg-blue-50;
  }
</style>
