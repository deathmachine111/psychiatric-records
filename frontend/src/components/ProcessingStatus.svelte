<script>
  export let status = 'pending'
  export let errorMessage = ''

  function getStatusIcon(s) {
    const icons = {
      pending: '⏳',
      processing: '⚙️',
      completed: '✅',
      failed: '❌'
    }
    return icons[s] || '📎'
  }

  function getStatusColor(s) {
    const colors = {
      pending: 'bg-blue-100 text-blue-800',
      processing: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    }
    return colors[s] || 'bg-gray-100 text-gray-800'
  }

  function getStatusLabel(s) {
    return s.charAt(0).toUpperCase() + s.slice(1)
  }
</script>

<div class="flex items-start gap-3">
  <span class="text-2xl">{getStatusIcon(status)}</span>
  <div class="flex-1">
    <div class="flex items-center gap-2">
      <span class="inline-block px-3 py-1 text-xs font-medium rounded {getStatusColor(status)}">
        {getStatusLabel(status)}
      </span>
    </div>
    {#if errorMessage}
      <p class="text-red-600 text-sm mt-2">{errorMessage}</p>
    {/if}
  </div>
</div>
