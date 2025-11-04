<script>
  import { createEventDispatcher } from 'svelte'

  export let mode = 'create' // 'create' or 'edit'
  export let data = null // For edit mode: { name, notes }

  const dispatch = createEventDispatcher()

  let formData = {
    name: data?.name || '',
    notes: data?.notes || ''
  }

  let errors = {
    name: ''
  }

  function validateForm() {
    errors.name = ''

    if (!formData.name.trim()) {
      errors.name = 'Patient name is required'
      return false
    }

    return true
  }

  function handleSubmit() {
    if (!validateForm()) {
      return
    }

    dispatch('submit', {
      name: formData.name,
      notes: formData.notes
    })

    // Reset form after submit
    formData = {
      name: '',
      notes: ''
    }
    errors.name = ''
  }

  function handleCancel() {
    formData = {
      name: data?.name || '',
      notes: data?.notes || ''
    }
    errors.name = ''
    dispatch('cancel')
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4">
  <div>
    <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
      Patient Name <span class="text-red-600">*</span>
    </label>
    <input
      type="text"
      id="name"
      bind:value={formData.name}
      placeholder="Enter patient name"
      class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      on:blur={() => validateForm()}
    />
    {#if errors.name}
      <p class="text-red-600 text-sm mt-1">{errors.name}</p>
    {/if}
  </div>

  <div>
    <label for="notes" class="block text-sm font-medium text-gray-700 mb-1">
      Notes (Optional)
    </label>
    <textarea
      id="notes"
      bind:value={formData.notes}
      placeholder="Add any notes about this patient"
      rows="4"
      class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>

  <div class="flex gap-3 justify-end">
    <button
      type="button"
      on:click={handleCancel}
      class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 font-medium text-gray-700"
    >
      Cancel
    </button>
    <button
      type="submit"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
    >
      {mode === 'create' ? 'Create Patient' : 'Save Patient'}
    </button>
  </div>
</form>
