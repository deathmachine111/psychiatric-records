<script>
  import { createEventDispatcher } from 'svelte'

  export let patient = {
    id: null,
    name: '',
    notes: '',
    date_created: new Date().toISOString()
  }

  const dispatch = createEventDispatcher()

  function handleDelete(e) {
    e.stopPropagation()
    if (confirm(`Delete patient ${patient.name}?`)) {
      dispatch('delete', patient.id)
    }
  }

  function handleSelect() {
    dispatch('select', patient)
  }
</script>

<div
  class="bg-white rounded-lg shadow hover:shadow-md cursor-pointer transition p-6"
  on:click={handleSelect}
  on:keydown={(e) => e.key === 'Enter' && handleSelect()}
  role="button"
  tabindex="0"
>
  <div class="flex justify-between items-start">
    <div class="flex-1">
      <h3 class="text-xl font-semibold text-gray-900">{patient.name}</h3>
      {#if patient.notes}
        <p class="text-gray-600 text-sm mt-1">{patient.notes}</p>
      {/if}
      <p class="text-gray-400 text-xs mt-2">
        Created: {new Date(patient.date_created).toLocaleDateString()}
      </p>
    </div>
    <button
      class="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-sm whitespace-nowrap ml-4"
      on:click={handleDelete}
    >
      Delete
    </button>
  </div>
</div>

<style>
  div {
    border: 1px solid transparent;
  }

  div:hover {
    border-color: #e5e7eb;
  }
</style>
