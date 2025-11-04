<script>
  export let message = 'An error occurred'
  export let inline = false
</script>

<div class={inline ? 'inline-error' : 'alert-error'} role="alert">
  <div class="flex items-start gap-3">
    <span class="text-2xl flex-shrink-0">⚠</span>
    <p class="flex-1">{message}</p>
  </div>
</div>

<style>
  .alert-error {
    background-color: #fee;
    border: 1px solid #fcc;
    border-radius: 0.5rem;
    padding: 1rem;
    color: #c33;
    margin: 1rem 0;
  }

  .inline-error {
    color: #c33;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
</style>
