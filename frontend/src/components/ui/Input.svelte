<script>
  export let type = 'text';
  export let placeholder = '';
  export let value = '';
  export let disabled = false;
</script>

{#if type === 'text'}
  <input
    type="text"
    {placeholder}
    {disabled}
    bind:value
    class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50
           focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none
           disabled:opacity-50 disabled:cursor-not-allowed"
    {...$$restProps}
  />
{:else if type === 'password'}
  <input
    type="password"
    {placeholder}
    {disabled}
    bind:value
    class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/50
           focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none
           disabled:opacity-50 disabled:cursor-not-allowed"
    {...$$restProps}
  />
{/if}
