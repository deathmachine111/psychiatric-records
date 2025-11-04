<script>
  import { createEventDispatcher } from 'svelte'

  export let files = []

  const dispatch = createEventDispatcher()

  function getFileTypeIcon(fileType) {
    const icons = {
      audio: '🎵',
      image: '🖼️',
      text: '📄',
      video: '🎬'
    }
    return icons[fileType] || '📎'
  }

  function getFileTypeLabel(fileType) {
    const labels = {
      audio: 'Audio',
      image: 'Image',
      text: 'Text',
      video: 'Video'
    }
    return labels[fileType] || 'File'
  }

  function formatFileSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
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

  function handleSelectFile(file) {
    dispatch('selectFile', file)
  }

  function handleDelete(file) {
    if (confirm(`Delete ${file.filename}?`)) {
      dispatch('delete', file.id)
    }
  }

  function getStatusBadgeColor(status) {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      processing: 'bg-yellow-100 text-yellow-800',
      pending: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }
</script>

<div class="space-y-4">
  <div class="flex justify-between items-center">
    <h3 class="text-xl font-semibold text-gray-900">
      Files {files.length > 0 ? `(${files.length})` : ''}
    </h3>
  </div>

  {#if files.length === 0}
    <div class="bg-gray-100 border border-gray-300 text-gray-700 px-4 py-8 rounded text-center">
      <p class="text-gray-600">No files uploaded yet</p>
      <p class="text-sm text-gray-500 mt-2">Upload audio, image, or text files to get started</p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each files as file (file.id)}
        <div class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer" on:click={() => handleSelectFile(file)}>
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <span class="text-2xl">{getFileTypeIcon(file.file_type)}</span>
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900">{file.filename}</h4>
                  <div class="flex gap-4 text-sm text-gray-500 mt-1">
                    <span>{getFileTypeLabel(file.file_type)}</span>
                    {#if file.file_size}
                      <span>{formatFileSize(file.file_size)}</span>
                    {/if}
                    {#if file.upload_date}
                      <span>{formatDate(file.upload_date)}</span>
                    {/if}
                  </div>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-3 ml-4">
              {#if file.processing_status}
                <span class="inline-block px-3 py-1 text-xs font-medium rounded {getStatusBadgeColor(file.processing_status)}">
                  {file.processing_status}
                </span>
              {/if}
              <button
                type="button"
                on:click={() => handleDelete(file)}
                class="text-red-600 hover:text-red-800 hover:bg-red-50 px-3 py-2 rounded transition"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
