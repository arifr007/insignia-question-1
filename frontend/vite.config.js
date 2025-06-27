import { defineConfig, loadEnv } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [svelte()],
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:5000',
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api/, '')
        }
      }
    },
    define: {
      global: 'globalThis'
    },
    preview: {
      port: 4173,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:5000',
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api/, '')
        }
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            // Vendor chunks for large libraries
            chartjs: ['chart.js', 'chartjs-adapter-date-fns', 'date-fns'],
            katex: ['katex', 'marked-katex-extension'],
            marked: ['marked', 'dompurify'],
            axios: ['axios'],

            // UI components
            'ui-components': [
              'src/components/ui/Alert.svelte',
              'src/components/ui/Button.svelte',
              'src/components/ui/Card.svelte',
              'src/components/ui/Input.svelte',
              'src/components/ui/LoadingSpinner.svelte',
              'src/components/ui/FormField.svelte',
              'src/components/ui/DashboardCard.svelte',
              'src/components/ui/FormattedSummary.svelte'
            ]
          }
        }
      },
      // Increase chunk size warning limit to 1000kb
      chunkSizeWarningLimit: 1000
    }
  };
});
