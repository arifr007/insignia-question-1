<script>
  import Card from './Card.svelte';

  export let title;
  export let items = [];
  export let valueColor = 'text-accent';
  export let formatValue = (value, _key = '') => value;
  export let formatKey = key => key;
  export let maxHeight = false;
  export let itemClass = 'p-3';

  $: valueColorClass = typeof valueColor === 'function' ? '' : valueColor;
</script>

<Card>
  <h3 class="text-lg font-semibold text-primary mb-4">{title}</h3>
  <div
    class={`space-y-2 ${maxHeight ? 'max-h-64 overflow-y-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-300 hover:scrollbar-thumb-gray-400 [scrollbar-gutter:stable] [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar]:h-1.5' : ''}`}
  >
    {#if items?.length === 0}
      <div class="text-center text-green-600 font-medium py-4 text-sm">No data available</div>
    {:else}
      {#each items as [key, value]}
        <div class="flex justify-between items-center {itemClass} bg-gray-50 rounded-lg">
          <span class="font-medium text-gray-900 text-sm truncate mr-2" title={key}
            >{formatKey(key)}</span
          >
          <span
            class={`font-semibold text-sm ${typeof valueColor === 'function' ? valueColor(key, value) : valueColorClass}`}
            >{formatValue(value, key)}</span
          >
        </div>
      {/each}
    {/if}
    <slot />
  </div>
</Card>
