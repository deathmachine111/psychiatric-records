<script>
  import { createEventDispatcher } from 'svelte'

  export let open = false
  export let title = ''

  const dispatch = createEventDispatcher()

  function handleClose() {
    dispatch('close')
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
      handleClose()
    }
  }
</script>

{#if open}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    on:click={handleBackdropClick}
    role="presentation"
  >
    <div
      class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div class="flex justify-between items-center p-6 border-b border-gray-200">
        <h2 id="modal-title" class="text-xl font-semibold text-gray-900">
          {title}
        </h2>
        <button
          type="button"
          class="text-gray-500 hover:text-gray-700 text-2xl leading-none"
          on:click={handleClose}
          aria-label="Close modal"
        >
          ×
        </button>
      </div>
      <div class="p-6">
        <slot />
      </div>
    </div>
  </div>
{/if}

<style>
  /* Prevent body scroll when modal is open */
  :global(body.modal-open) {
    overflow: hidden;
  }
</style>
