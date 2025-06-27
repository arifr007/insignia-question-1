<script>
  export let label = '';
  export let error = '';
  export let required = false;
  export let id = '';
</script>

<div class="space-y-2">
  {#if label}
    <label for={id} class="block text-sm font-medium text-white">
      {label}
      {#if required}<span class="text-red-400">*</span>{/if}
    </label>
  {/if}

  <slot />

  {#if error}
    <p class="text-sm text-red-400">{error}</p>
  {/if}
</div>
