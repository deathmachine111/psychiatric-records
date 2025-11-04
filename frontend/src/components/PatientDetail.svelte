<script>
  import { createEventDispatcher } from 'svelte'
  import FileUpload from './FileUpload.svelte'
  import FileList from './FileList.svelte'

  export let patient = null
  export let files = []

  const dispatch = createEventDispatcher()

  async function handleFileUpload(e) {
    const uploadedFiles = e.detail

    // TODO: Connect to API to upload files
    // For now, just show toast
    console.log('Upload files:', uploadedFiles)
  }

  function handleFileDelete(e) {
    const fileId = e.detail
    // TODO: Connect to API to delete file
    console.log('Delete file:', fileId)
  }

  function handleEditClick() {
    dispatch('edit')
  }

  function handleBackClick() {
    dispatch('back')
  }
</script>

{#if patient}
  <div class="space-y-6">
    <!-- Header with patient info and actions -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="flex justify-between items-start mb-4">
        <div>
          <h2 class="text-3xl font-bold text-gray-900">{patient.name}</h2>
          <p class="text-gray-600 text-sm mt-1">
            Created: {new Date(patient.date_created).toLocaleDateString()}
          </p>
        </div>
      </div>

      {#if patient.notes}
        <div class="bg-gray-50 rounded p-4 mb-6">
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Notes</h3>
          <p class="text-gray-700">{patient.notes}</p>
        </div>
      {/if}

      <div class="flex gap-4">
        <button
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          on:click={handleEditClick}
        >
          Edit Patient
        </button>
        <button
          class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          on:click={handleBackClick}
        >
          Back to List
        </button>
      </div>
    </div>

    <!-- File Upload Section -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-6">Upload New File</h3>
      <FileUpload on:upload={handleFileUpload} on:cancel />
    </div>

    <!-- File List Section -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-6">Patient Files</h3>
      <FileList {files} on:delete={handleFileDelete} on:selectFile />
    </div>
  </div>
{:else}
  <div class="text-center py-12">
    <p class="text-gray-600">No patient selected</p>
  </div>
{/if}
