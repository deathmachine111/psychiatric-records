<script>
  import Navigation from './components/Navigation.svelte'
  import PatientList from './routes/PatientList.svelte'
  import { onMount } from 'svelte'

  let currentPage = 'list'
  let selectedPatient = null

  onMount(() => {
    // App initialization
    console.log('App mounted')
  })

  function handleSelectPatient(patient) {
    selectedPatient = patient
    currentPage = 'detail'
  }

  function handleBackToList() {
    currentPage = 'list'
    selectedPatient = null
  }
</script>

<div class="min-h-screen bg-gray-50">
  <Navigation
    on:backToList={handleBackToList}
    showBack={currentPage === 'detail'}
  />

  <main class="max-w-6xl mx-auto p-6">
    {#if currentPage === 'list'}
      <PatientList on:selectPatient={(e) => handleSelectPatient(e.detail)} />
    {:else if currentPage === 'detail' && selectedPatient}
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold mb-4">{selectedPatient.name}</h2>
        <p class="text-gray-700 mb-6">{selectedPatient.notes || 'No notes'}</p>
        <div class="flex gap-4">
          <button
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            on:click={handleBackToList}
          >
            Back to List
          </button>
        </div>
      </div>
    {/if}
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>
