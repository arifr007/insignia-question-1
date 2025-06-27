<script>
  import { onMount, onDestroy } from 'svelte';
  import apiService from '../services/api.js';

  let serverError = null;
  let isCheckingHealth = false;

  onMount(() => {
    // Listen for server error events
    window.addEventListener('server:error', handleServerError);
  });

  onDestroy(() => {
    window.removeEventListener('server:error', handleServerError);
  });

  function handleServerError(event) {
    const { message, type } = event.detail;

    serverError = {
      message: message || 'Server is experiencing issues',
      type: type || 'server_error',
      timestamp: new Date()
    };

    // Auto-clear error after 10 seconds
    setTimeout(() => {
      if (serverError && serverError.timestamp === event.detail.timestamp) {
        serverError = null;
      }
    }, 10000);
  }

  function dismissError() {
    serverError = null;
  }

  async function checkServerHealth() {
    if (isCheckingHealth) return;

    isCheckingHealth = true;
    try {
      await apiService.checkServerHealth();

      // If health check passes, clear any existing errors
      serverError = null;
    } catch (_error) {
      // Health check failed, update error message
      serverError = {
        message: 'Server is still experiencing issues. Please try again later.',
        type: 'health_check_failed',
        timestamp: new Date()
      };
    } finally {
      isCheckingHealth = false;
    }
  }
</script>

{#if serverError}
  <div class="fixed top-4 right-4 z-50 max-w-md">
    <div class="bg-red-600 text-white p-4 rounded-lg shadow-lg border border-red-500">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h4 class="font-semibold mb-2">🚨 Server Error</h4>
          <p class="text-sm">{serverError.message}</p>

          {#if serverError.type === 'database_error'}
            <p class="text-xs mt-2 opacity-90">
              The application is having trouble connecting to the database. Please wait a moment and
              try again.
            </p>
          {/if}
        </div>

        <button
          class="ml-3 text-white/80 hover:text-white"
          on:click={dismissError}
          aria-label="Dismiss error"
        >
          ✕
        </button>
      </div>

      <div class="mt-3 flex gap-2">
        <button
          class="text-xs bg-white/20 hover:bg-white/30 px-3 py-1 rounded transition-colors"
          on:click={checkServerHealth}
          disabled={isCheckingHealth}
        >
          {isCheckingHealth ? 'Checking...' : 'Check Status'}
        </button>

        <button
          class="text-xs bg-white/20 hover:bg-white/30 px-3 py-1 rounded transition-colors"
          on:click={() => window.location.reload()}
        >
          Reload Page
        </button>
      </div>
    </div>
  </div>
{/if}
