import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  // Consult https://svelte.dev/docs#compile-time-svelte-preprocess
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  // Svelte 5 specific options
  compilerOptions: {
    // Enable modern features
    modernAst: true,
    // HMR is now integrated in Svelte 5 core
    hmr: true,
    // Updated compatibility options for Svelte 5
    compatibility: {
      componentApi: 4 // Maintain compatibility with Svelte 4 component API
    }
  }
};
