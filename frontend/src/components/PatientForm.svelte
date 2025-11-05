<script>
  import { createEventDispatcher } from 'svelte'

  export let mode = 'create' // 'create' or 'edit'
  export let data = null // For edit mode: { name, notes }

  const dispatch = createEventDispatcher()

  let formData = {
    name: data?.name || '',
    patient_description: data?.patient_description || ''
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
      patient_description: formData.patient_description
    })

    // Reset form after submit
    formData = {
      name: '',
      patient_description: ''
    }
    errors.name = ''
  }

  function handleCancel() {
    formData = {
      name: data?.name || '',
      patient_description: data?.patient_description || ''
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
    <label for="patient_description" class="block text-sm font-medium text-gray-700 mb-1">
      Patient Description (Optional)
    </label>
    <textarea
      id="patient_description"
      bind:value={formData.patient_description}
      placeholder="Add description about this patient"
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
