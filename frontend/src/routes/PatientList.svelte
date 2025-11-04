<script>
  import { onMount, createEventDispatcher } from 'svelte'
  import { patients } from '../stores/patients'
  import { ui } from '../stores/ui'

  const dispatch = createEventDispatcher()

  let patientsList = []
  let loading = true
  let error = null
  let showForm = false
  let formData = { name: '', notes: '' }

  onMount(async () => {
    await loadPatients()
  })

  async function loadPatients() {
    loading = true
    error = null
    try {
      await patients.loadPatients()
    } catch (err) {
      error = 'Failed to load patients'
      ui.addToast(error, 'error')
    } finally {
      loading = false
    }
  }

  patients.subscribe((p) => {
    patientsList = p
  })

  async function handleCreatePatient() {
    if (!formData.name.trim()) {
      ui.addToast('Patient name is required', 'error')
      return
    }

    try {
      await patients.createPatient(formData)
      ui.addToast('Patient created successfully', 'success')
      formData = { name: '', notes: '' }
      showForm = false
    } catch (err) {
      ui.addToast('Failed to create patient', 'error')
    }
  }

  function handleSelectPatient(patient) {
    dispatch('selectPatient', patient)
  }

  async function handleDeletePatient(e, id) {
    e.stopPropagation()
    if (confirm('Are you sure?')) {
      try {
        await patients.deletePatient(id)
        ui.addToast('Patient deleted', 'success')
      } catch (err) {
        ui.addToast('Failed to delete patient', 'error')
      }
    }
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h2 class="text-3xl font-bold text-gray-900">Patients</h2>
    <button
      class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      on:click={() => (showForm = !showForm)}
    >
      {showForm ? 'Cancel' : '+ New Patient'}
    </button>
  </div>

  {#if showForm}
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-xl font-semibold mb-4">Create New Patient</h3>
      <form on:submit|preventDefault={handleCreatePatient} class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Patient Name
          </label>
          <input
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter patient name"
            bind:value={formData.name}
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            class="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter notes (optional)"
            rows="3"
            bind:value={formData.notes}
          />
        </div>

        <button
          type="submit"
          class="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create Patient
        </button>
      </form>
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-12">
      <p class="text-gray-600">Loading patients...</p>
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      {error}
    </div>
  {:else if patientsList.length === 0}
    <div class="bg-gray-100 border border-gray-300 text-gray-700 px-4 py-3 rounded text-center">
      No patients yet. Create one to get started!
    </div>
  {:else}
    <div class="grid gap-4">
      {#each patientsList as patient (patient.id)}
        <div
          class="bg-white rounded-lg shadow hover:shadow-md cursor-pointer transition p-6"
          on:click={() => handleSelectPatient(patient)}
          role="button"
          tabindex="0"
        >
          <div class="flex justify-between items-start">
            <div>
              <h3 class="text-xl font-semibold text-gray-900">{patient.name}</h3>
              {#if patient.notes}
                <p class="text-gray-600 text-sm mt-1">{patient.notes}</p>
              {/if}
              <p class="text-gray-400 text-xs mt-2">
                Created: {new Date(patient.date_created).toLocaleDateString()}
              </p>
            </div>
            <button
              class="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-sm"
              on:click={(e) => handleDeletePatient(e, patient.id)}
            >
              Delete
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
