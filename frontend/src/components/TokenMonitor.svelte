<script>
  import { onMount, onDestroy } from 'svelte';
  import { isAuthenticated, auth } from '../stores/index.js';
  import api from '../services/api.js';

  let interval;
  let isLoggingOut = false;

  onMount(() => {
    if ($isAuthenticated) {
      startTokenMonitoring();
    }
  });

  onDestroy(() => {
    stopTokenMonitoring();
  });

  function startTokenMonitoring() {
    // Clear any existing interval first
    stopTokenMonitoring();

    interval = setInterval(async () => {
      // Prevent multiple logout calls
      if (isLoggingOut) return;

      const token = api.getAccessToken();
      if (token) {
        const timeRemaining = api.getTokenTimeRemaining(token);

        if (timeRemaining < 120 && timeRemaining > 0) {
          try {
            await api.ensureValidToken();
          } catch (error) {
            console.error('Token refresh failed:', error);
            handleLogout();
          }
        } else if (timeRemaining <= 0) {
          console.log('Token expired, logging out');
          handleLogout();
        }
      } else if ($isAuthenticated) {
        console.log('No token found but user appears authenticated, logging out');
        handleLogout();
      }
    }, 30000);
  }

  function stopTokenMonitoring() {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
  }

  function handleLogout() {
    if (isLoggingOut || !$isAuthenticated) return;

    isLoggingOut = true;
    stopTokenMonitoring();

    try {
      auth.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Reset flag after a delay to prevent rapid re-triggering
      setTimeout(() => {
        isLoggingOut = false;
      }, 1000);
    }
  }

  $: if ($isAuthenticated && !interval) {
    startTokenMonitoring();
  } else if (!$isAuthenticated && interval) {
    stopTokenMonitoring();
  }
</script>
