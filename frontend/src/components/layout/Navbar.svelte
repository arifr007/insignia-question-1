<script>
  import { currentTab, auth } from '../../stores/index.js';

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'chat', label: 'AI Chat', icon: '💬' },
    { id: 'anomaly', label: 'Anomalies', icon: '🔍' },
    { id: 'visualizations', label: 'Charts', icon: '📈' }
  ];

  function setTab(tabId) {
    currentTab.set(tabId);
  }

  function handleLogout() {
    auth.logout();
  }
</script>

<nav class="bg-slate-800/50 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <div class="flex items-center">
        <h1 class="text-xl font-bold text-white">💼 Finance Analytics</h1>
      </div>

      <div class="hidden md:block">
        <div class="flex space-x-1">
          {#each tabs as tab}
            <button
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2
                     {$currentTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:text-white hover:bg-white/10'}"
              on:click={() => setTab(tab.id)}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="flex items-center space-x-4">
        <button class="btn btn-secondary text-sm" on:click={handleLogout}> Logout </button>
      </div>
    </div>

    <div class="md:hidden pb-3">
      <div class="grid grid-cols-2 gap-2">
        {#each tabs as tab}
          <button
            class="px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center space-x-2
                   {$currentTab === tab.id
              ? 'bg-blue-600 text-white'
              : 'text-gray-300 hover:text-white hover:bg-white/10'}"
            on:click={() => setTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span class="hidden sm:inline">{tab.label}</span>
          </button>
        {/each}
      </div>
    </div>
  </div>
</nav>
