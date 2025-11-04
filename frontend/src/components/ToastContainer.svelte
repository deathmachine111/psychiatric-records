<script>
  import Toast from './Toast.svelte'
  import { ui } from '../stores/ui'
</script>

<div class="fixed bottom-0 right-0 p-4 pointer-events-none z-50">
  <div class="flex flex-col gap-2">
    {#each $ui.toasts as toast (toast.id)}
      <div class="pointer-events-auto">
        <Toast
          id={toast.id}
          message={toast.message}
          type={toast.type}
          on:close={(e) => ui.removeToast(e.detail)}
        />
      </div>
    {/each}
  </div>
</div>
