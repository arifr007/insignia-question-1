<script>
  export let message = '';
  export let type = 'error';

  const types = {
    error: 'bg-red-500/20 border-red-500/30 text-red-200',
    warning: 'bg-yellow-500/20 border-yellow-500/30 text-yellow-200',
    info: 'bg-blue-500/20 border-blue-500/30 text-blue-200',
    success: 'bg-green-500/20 border-green-500/30 text-green-200'
  };

  const icons = {
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅'
  };
</script>

{#if message}
  <div class="rounded-lg border p-4 {types[type]}">
    <div class="flex items-center space-x-2">
      <span>{icons[type]}</span>
      <span>{message}</span>
    </div>
  </div>
{/if}
