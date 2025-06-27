<script>
  import { isAuthenticated, currentTab } from './stores/index.js';
  import Layout from './components/layout/Layout.svelte';
  import Navbar from './components/layout/Navbar.svelte';
  import Login from './components/Login.svelte';
  import TokenMonitor from './components/TokenMonitor.svelte';
  import ServerErrorHandler from './components/ServerErrorHandler.svelte';
  import LoadingSpinner from './components/ui/LoadingSpinner.svelte';

  // Dynamic imports for route components
  let Dashboard, ChatWithRooms, AnomalyDetection, Visualizations;
  let componentPromises = {};

  // Function to lazy load components
  async function loadComponent(componentName) {
    if (componentPromises[componentName]) {
      return componentPromises[componentName];
    }

    switch (componentName) {
      case 'dashboard':
        componentPromises.dashboard = import('./components/Dashboard.svelte').then(m => {
          Dashboard = m.default;
          return Dashboard;
        });
        return componentPromises.dashboard;

      case 'chat':
        componentPromises.chat = import('./components/ChatWithRooms.svelte').then(m => {
          ChatWithRooms = m.default;
          return ChatWithRooms;
        });
        return componentPromises.chat;

      case 'anomaly':
        componentPromises.anomaly = import('./components/AnomalyDetection.svelte').then(m => {
          AnomalyDetection = m.default;
          return AnomalyDetection;
        });
        return componentPromises.anomaly;

      case 'visualizations':
        componentPromises.visualizations = import('./components/Visualizations.svelte').then(m => {
          Visualizations = m.default;
          return Visualizations;
        });
        return componentPromises.visualizations;

      default:
        return null;
    }
  }

  // Reactive statement to load component when tab changes
  $: if ($currentTab && $isAuthenticated) {
    loadComponent($currentTab);
  }
</script>

<Layout>
  <!-- Server Error Handler - always present -->
  <ServerErrorHandler />

  {#if $isAuthenticated}
    <TokenMonitor />

    {#if $currentTab !== 'chat'}
      <Navbar />
    {:else}
      <Navbar />
    {/if}

    <main class="flex-1 {$currentTab === 'chat' ? 'h-screen' : 'container mx-auto px-4 py-8'}">
      {#if $currentTab === 'dashboard'}
        {#if Dashboard}
          <svelte:component this={Dashboard} />
        {:else}
          {#await loadComponent('dashboard')}
            <div class="flex justify-center items-center py-12">
              <LoadingSpinner size="lg" />
              <span class="ml-3 text-gray-300">Loading Dashboard...</span>
            </div>
          {:then component}
            <svelte:component this={component} />
          {/await}
        {/if}
      {:else if $currentTab === 'chat'}
        {#if ChatWithRooms}
          <svelte:component this={ChatWithRooms} />
        {:else}
          {#await loadComponent('chat')}
            <div class="flex justify-center items-center py-12">
              <LoadingSpinner size="lg" />
              <span class="ml-3 text-gray-300">Loading Chat...</span>
            </div>
          {:then component}
            <svelte:component this={component} />
          {/await}
        {/if}
      {:else if $currentTab === 'anomaly'}
        {#if AnomalyDetection}
          <svelte:component this={AnomalyDetection} />
        {:else}
          {#await loadComponent('anomaly')}
            <div class="flex justify-center items-center py-12">
              <LoadingSpinner size="lg" />
              <span class="ml-3 text-gray-300">Loading Anomaly Detection...</span>
            </div>
          {:then component}
            <svelte:component this={component} />
          {/await}
        {/if}
      {:else if $currentTab === 'visualizations'}
        {#if Visualizations}
          <svelte:component this={Visualizations} />
        {:else}
          {#await loadComponent('visualizations')}
            <div class="flex justify-center items-center py-12">
              <LoadingSpinner size="lg" />
              <span class="ml-3 text-gray-300">Loading Visualizations...</span>
            </div>
          {:then component}
            <svelte:component this={component} />
          {/await}
        {/if}
      {/if}
    </main>
  {:else}
    <Login />
  {/if}
</Layout>
