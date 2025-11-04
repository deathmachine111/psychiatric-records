<script>
  import { createEventDispatcher } from 'svelte'

  export let id = ''
  export let message = ''
  export let type = 'info' // 'success', 'error', 'info'

  const dispatch = createEventDispatcher()

  function getIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      info: 'ℹ'
    }
    return icons[type] || '•'
  }

  function getColors(type) {
    const colors = {
      success: {
        bg: 'bg-green-50',
        border: 'border-green-200',
        icon: 'text-green-600',
        text: 'text-green-800'
      },
      error: {
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: 'text-red-600',
        text: 'text-red-800'
      },
      info: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: 'text-blue-600',
        text: 'text-blue-800'
      }
    }
    return colors[type] || colors.info
  }

  function handleClose() {
    dispatch('close', id)
  }

  $: colors = getColors(type)
</script>

<div class="fixed bottom-4 right-4 max-w-sm animate-slide-in {colors.bg} border {colors.border} rounded-lg p-4 shadow-lg">
  <div class="flex items-start gap-3">
    <span class="text-xl {colors.icon} flex-shrink-0">{getIcon(type)}</span>
    <p class="flex-1 {colors.text}">{message}</p>
    <button
      type="button"
      on:click={handleClose}
      class="flex-shrink-0 {colors.text} hover:opacity-75 ml-2"
      aria-label="Close notification"
    >
      ×
    </button>
  </div>
</div>

<style>
  @keyframes slide-in {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  :global(.animate-slide-in) {
    animation: slide-in 0.3s ease-out;
  }
</style>
