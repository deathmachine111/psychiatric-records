<script>
  import { createEventDispatcher } from 'svelte'

  export let showBack = false

  const dispatch = createEventDispatcher()
</script>

<nav class="bg-white shadow">
  <div class="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
    <h1 class="text-2xl font-bold text-gray-900">
      🧠 Psychiatric Records
    </h1>

    {#if showBack}
      <button
        class="text-blue-600 hover:text-blue-800 font-medium"
        on:click={() => dispatch('backToList')}
      >
        ← Back
      </button>
    {/if}
  </div>
</nav>

<style>
  nav {
    border-bottom: 1px solid #e5e7eb;
  }
</style>
