<script>
  export let variant = 'default';
  let className = '';
  export { className as class };

  const variants = {
    default: 'bg-white/10 backdrop-blur-sm border border-white/20',
    elevated: 'bg-white/15 backdrop-blur-md border border-white/30 shadow-xl',
    glass: 'bg-white/5 backdrop-blur-lg border border-white/10'
  };
</script>

<div class="rounded-2xl p-6 {variants[variant]} {className}">
  <slot />
</div>
