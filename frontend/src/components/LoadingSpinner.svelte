<script>
  export let message = 'Loading...'
  export let overlay = false
</script>

{#if overlay}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 text-center">
      <div class="mb-4 flex justify-center">
        <div class="h-12 w-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
      <p class="text-gray-700 font-medium">{message}</p>
    </div>
  </div>
{:else}
  <div class="flex flex-col items-center justify-center py-8">
    <div class="mb-4">
      <div class="h-12 w-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
    </div>
    <p class="text-gray-600">{message}</p>
  </div>
{/if}

<style>
  :global(.animate-spin) {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
