<script>
  import { onMount, afterUpdate } from 'svelte';
  import {
    currentRoomMessages,
    currentMessage,
    currentRoom,
    sidebarVisible,
    chatRoomStore
  } from '../stores/index.js';
  import api from '../services/api.js';
  import ChartComponent from './ChartJSChart.svelte';
  import ChatSidebar from './ChatSidebar.svelte';
  import DOMPurify from 'dompurify';

  let messagesContainer;
  let loading = false;
  let chartData = null;

  // Dynamic imports for markdown libraries
  let marked, katex;
  let markdownLibsLoaded = false;

  // Load markdown libraries dynamically
  async function loadMarkdownLibs() {
    if (markdownLibsLoaded) return;

    try {
      const [markedModule, katexModule] = await Promise.all([import('marked'), import('katex')]);

      marked = markedModule.marked;
      katex = katexModule.default;
      markdownLibsLoaded = true;

      // Also dynamically import KaTeX CSS
      import('katex/dist/katex.min.css');
    } catch (error) {
      console.error('Failed to load markdown libraries:', error);
    }
  }

  const suggestedQueries = [
    'Tunjukkan tren pengeluaran bulan ini',
    'Apakah ada anomali dalam data?',
    'Apa penyebab kenaikan pengeluaran?',
    'Berikan ringkasan data pengeluaran',
    'Analisis penyebab utama pembengkakan anggaran',
    'Tunjukkan rincian area fungsional',
    'Deteksi pola pengeluaran yang tidak biasa',
    'Bandingkan pengeluaran di berbagai periode',
    'Temukan outlier dalam data pengeluaran',
    'Tunjukkan total pengeluaran yang teragregasi',
    'Apa kabar hari ini?',
    'Lakukan analisis data eksplorasi'
  ];

  onMount(async () => {
    // Load markdown libraries in the background
    loadMarkdownLibs();

    // Load rooms and initialize from storage
    await chatRoomStore.loadRooms();
    await chatRoomStore.initializeFromStorage();

    // If no current room, create one
    if (!$currentRoom) {
      await createNewRoom();
    }
  });

  afterUpdate(() => {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });

  async function createNewRoom() {
    try {
      const room = await chatRoomStore.createRoom();
      if (room) {
        await chatRoomStore.selectRoom(room.id);

        // Add welcome message
        currentRoomMessages.update(messages => [
          ...messages,
          {
            type: 'bot',
            content:
              "Hello! I'm your AI Finance Analyst. I can help you analyze expense data, detect anomalies, perform root cause analysis, and create visualizations. How can I assist you today?",
            timestamp: new Date(),
            intent: 'greeting'
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to create new room:', error);
    }
  }

  async function sendMessage() {
    if (!$currentMessage.trim() || loading || !$currentRoom) return;

    loading = true;
    const message = $currentMessage;
    currentMessage.set('');

    try {
      const response = await chatRoomStore.sendMessage($currentRoom.id, message);

      // Handle chart data based on intent
      if (response.intent || response.intents) {
        const intents = Array.isArray(response.intents) ? response.intents : [response.intent];
        const intentString = intents.join(' ').toLowerCase();

        if (intentString.includes('anomaly')) {
          await loadAnomalyChart();
        } else if (intentString.includes('trend')) {
          await loadTrendChart();
        } else if (intentString.includes('comparative')) {
          await loadComparativeChart();
        } else if (intentString.includes('aggregation')) {
          await loadCategoryBreakdownChart();
        } else if (intentString.includes('rca')) {
          await loadHeatmapChart();
        }

        // Reload messages after chart is loaded to show the chart
        if ($currentRoom?.id) {
          await chatRoomStore.selectRoom($currentRoom.id);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      loading = false;
    }
  }

  async function loadChart(apiCall) {
    try {
      await apiCall($currentRoom?.id);
      // Charts are now saved to chat automatically when room_id is provided
      // Note: Messages will be reloaded in the sendMessage function
    } catch (error) {
      console.error('Failed to load chart:', error);
    }
  }

  const loadTrendChart = () => loadChart(api.getTrendChart);
  const loadAnomalyChart = () => loadChart(api.getAnomalyScatterChart.bind(null, 'ml'));
  const loadComparativeChart = () => loadChart(api.getTrendChart);
  const loadCategoryBreakdownChart = () => loadChart(api.getCategoryBreakdownChart);
  const loadHeatmapChart = () => loadChart(api.getHeatmapChart);

  function useSuggestion(suggestion) {
    currentMessage.set(suggestion);
    sendMessage();
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  async function clearCurrentRoom() {
    if (!$currentRoom || !confirm('Are you sure you want to clear this chat?')) return;

    try {
      await chatRoomStore.clearRoomMessages($currentRoom.id);
    } catch (error) {
      console.error('Failed to clear room:', error);
    }
  }

  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }

  // Intent mapping for consistent emoji and type handling
  const intentMap = {
    anomaly_detection: { emoji: '🔍', type: 'anomaly' },
    outlier_detection: { emoji: '🎯', type: 'outlier' },
    eda_summary: { emoji: '📊', type: 'eda' },
    eda_request: { emoji: '📊', type: 'eda' },
    root_cause_analysis: { emoji: '🔍', type: 'rca' },
    rca_request: { emoji: '🔍', type: 'rca' },
    trend_analysis: { emoji: '📈', type: 'trend' },
    comparative_analysis: { emoji: '⚖️', type: 'comparative' },
    aggregation_query: { emoji: '📋', type: 'category' },
    general_chat: { emoji: '💬', type: 'general' },
    chart_heatmap: { emoji: '🌡️', type: 'heatmap' },
    greeting: { emoji: '👋', type: 'greeting' }
  };

  function getIntentInfo(intent) {
    if (!intent || typeof intent !== 'string') {
      return { emoji: '💡', text: 'GENERAL' };
    }

    const intentInfo = intentMap[intent] || { emoji: '💡', type: 'general' };
    return {
      emoji: intentInfo.emoji,
      text: intent.replace(/_/g, ' ').toUpperCase()
    };
  }

  function formatIntent(intent) {
    console.log('Formatting intent:', intent);
    if (!intent || typeof intent !== 'string') {
      return 'GENERAL';
    }
    // Handle multiple intents
    if (intent.includes(',')) {
      return intent
        .split(',')
        .map(i => i.trim().replace(/_/g, ' '))
        .join(', ')
        .toUpperCase();
    }
    return intent.replace(/_/g, ' ').toUpperCase();
  }

  function formatSummary(summary) {
    if (typeof summary === 'string') {
      return summary;
    }

    if (typeof summary === 'object' && summary !== null) {
      // Handle specific summary formats
      if (summary.largest_area && summary.smallest_area && summary.total_areas) {
        const largestAmount = summary.largest_area.amount || 0;
        const smallestAmount = summary.smallest_area.amount || 0;

        return `**Financial Area Analysis:**
        
• **Largest Spending Area:** ${summary.largest_area.functional_area_name || 'Unknown'} 
  Amount: Rp ${(largestAmount / 1000000).toFixed(2)} million

• **Smallest Spending Area:** ${summary.smallest_area.functional_area_name || 'Unknown'}
  Amount: Rp ${smallestAmount < 1000000 ? smallestAmount.toLocaleString() : (smallestAmount / 1000000).toFixed(2) + ' million'}

• **Total Functional Areas:** ${summary.total_areas} areas analyzed

The spending distribution shows significant variance across functional areas, with **${summary.largest_area.functional_area_name}** representing the highest expenditure category.`;
      }

      // Handle trend summary
      if (summary.total_months && summary.average_monthly) {
        return `**Trend Analysis Summary:**

• **Total Months:** ${summary.total_months}
• **Average Monthly Spending:** Rp ${(summary.average_monthly / 1000000).toFixed(2)} million
${summary.min_month ? `• **Lowest Month:** ${summary.min_month.month_year} (Rp ${(summary.min_month.amount / 1000000).toFixed(2)} million)` : ''}
${summary.max_month ? `• **Highest Month:** ${summary.max_month.month_year} (Rp ${(summary.max_month.amount / 1000000).toFixed(2)} million)` : ''}`;
      }

      // Handle anomaly summary
      if (summary.total_anomalies !== undefined) {
        return `**Anomaly Detection Summary:**

• **Total Anomalies Detected:** ${summary.total_anomalies}
• **Detection Method:** ${summary.detection_method?.replace(/_/g, ' ').toUpperCase() || 'Unknown'}
${summary.avg_anomaly_amount ? `• **Average Anomaly Amount:** Rp ${(summary.avg_anomaly_amount / 1000000).toFixed(2)} million` : ''}
${summary.data_optimization ? `\n**Note:** ${summary.data_optimization}` : ''}`;
      }

      // Handle other array types
      if (Array.isArray(summary)) {
        return summary.map(item => `• ${item}`).join('\n');
      }

      // Format other objects nicely
      return Object.entries(summary)
        .map(([key, value]) => {
          const formattedKey = key.replace(/_/g, ' ').toUpperCase();
          const formattedValue =
            typeof value === 'number' && value > 1000000
              ? `Rp ${(value / 1000000).toFixed(2)} million`
              : value;
          return `**${formattedKey}:** ${formattedValue}`;
        })
        .join('\n');
    }

    return String(summary);
  }

  function processTextWithMath(text) {
    if (typeof text !== 'string') return text;

    // If markdown libraries aren't loaded yet, return plain text
    if (!markdownLibsLoaded || !marked) {
      return text;
    }

    try {
      // First, convert the text to markdown
      let processedText = marked(text);

      // Then find and replace mathematical formulas in brackets (only if katex is available)
      if (katex) {
        processedText = processedText.replace(/\[\s*\\text\{[^}]+\}[^[\]]*\]/g, match => {
          try {
            // Remove the outer brackets
            let formula = match.slice(1, -1);

            // Escape percentage signs for LaTeX
            formula = formula.replace(/%/g, '\\%');

            // Render with KaTeX in display mode
            return katex.renderToString(formula, {
              displayMode: true,
              throwOnError: false
            });
          } catch (e) {
            console.error('KaTeX rendering error for:', match, e);
            return match; // Return original if error
          }
        });
      }

      // Sanitize the HTML to prevent XSS attacks
      return DOMPurify.sanitize(processedText, {
        ALLOWED_TAGS: [
          'p',
          'br',
          'strong',
          'em',
          'ul',
          'ol',
          'li',
          'h1',
          'h2',
          'h3',
          'h4',
          'h5',
          'h6',
          'blockquote',
          'code',
          'pre',
          'span',
          'div'
        ],
        ALLOWED_ATTR: ['class', 'style'],
        KEEP_CONTENT: true
      });
    } catch (e) {
      console.error('Text processing error:', e);
      // Fallback to plain markdown if available, otherwise plain text
      const fallbackText = marked ? marked(text) : text;
      return DOMPurify.sanitize(fallbackText);
    }
  }

  // Helper function to safely render HTML content
  function safeHtml(content) {
    return DOMPurify.sanitize(content, {
      ALLOWED_TAGS: [
        'p',
        'br',
        'strong',
        'em',
        'ul',
        'ol',
        'li',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        'h6',
        'blockquote',
        'code',
        'pre',
        'span',
        'div'
      ],
      ALLOWED_ATTR: ['class', 'style'],
      KEEP_CONTENT: true
    });
  }
</script>

<div class="flex h-screen relative bg-gray-900 text-white font-sans">
  <!-- Sidebar -->
  <ChatSidebar />

  <!-- Main Chat Area -->
  <div
    class="flex-1 flex flex-col transition-all duration-300 {$sidebarVisible
      ? 'ml-[280px] sm:ml-[300px] md:ml-[320px] lg:ml-[360px] xl:ml-[400px]'
      : 'ml-0'}"
  >
    <header
      class="flex justify-between items-center p-4 border-b border-white/20 flex-shrink-0 bg-slate-900/80 backdrop-blur-sm"
    >
      <div class="flex items-center gap-3">
        <button
          class="p-2 rounded-md hover:bg-white/10 transition-colors"
          on:click={chatRoomStore.toggleSidebar}
          aria-label="Toggle sidebar"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            ><path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            ></path></svg
          >
        </button>
        <h1 class="text-lg font-semibold flex items-center gap-2">
          <span>{$currentRoom?.id ? '💬' : '✨'}</span>
          <span>{$currentRoom?.title || 'AI Finance Analyst'}</span>
        </h1>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button
          class="py-2 px-4 rounded-lg font-semibold transition-colors bg-blue-600 hover:bg-blue-700 text-sm flex items-center gap-2"
          on:click={createNewRoom}
        >
          <span>+</span> New Chat
        </button>
        {#if $currentRoom}
          <button
            class="py-2 px-4 rounded-lg font-semibold transition-colors bg-red-800 hover:bg-red-700 text-sm flex items-center gap-2"
            on:click={clearCurrentRoom}
          >
            <span>🗑️</span> Delete Chat
          </button>
        {/if}
      </div>
    </header>

    <!-- Suggested Queries (show when no messages or only welcome message) -->
    {#if $currentRoomMessages.length <= 1}
      <div class="p-5 border-b border-white/10 flex-shrink-0 max-h-[40vh] overflow-y-auto">
        <h3 class="mb-4 text-white/80 font-semibold">Try asking:</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {#each suggestedQueries as suggestion}
            <button
              class="p-3 bg-white/5 border border-white/10 rounded-lg text-white cursor-pointer text-left transition-all hover:bg-white/20 hover:-translate-y-px text-sm"
              on:click={() => useSuggestion(suggestion)}
            >
              {suggestion}
            </button>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Chat Messages -->
    <main
      class="flex-1 overflow-y-auto p-5 flex flex-col gap-5 min-h-0"
      bind:this={messagesContainer}
    >
      {#each $currentRoomMessages as message}
        <div
          class="flex max-w-[85%] md:max-w-[95%] {message.type === 'user'
            ? 'ml-auto'
            : 'mr-auto'} {message.type === 'error' ? 'max-w-full' : ''}"
        >
          <div
            class="p-4 rounded-2xl relative text-white {message.type === 'user'
              ? 'bg-gradient-to-br from-blue-600 to-purple-700'
              : 'bg-slate-700/50 border border-white/10'} {message.type === 'error'
              ? '!bg-red-500/20 !border-red-500/50 !text-red-400'
              : ''}"
          >
            {#if message.type === 'bot' && message.intent}
              <div class="text-xs font-semibold opacity-80 mb-2 uppercase flex items-center gap-2">
                <span>{getIntentInfo(message.intent).emoji}</span>
                <span>{formatIntent(message.intent)}</span>
              </div>
            {/if}

            <div
              class="leading-relaxed min-w-[250px] break-words prose prose-invert prose-sm max-w-none"
            >
              {#if message.chart_data}
                <!-- Message with chart data -->
                <div class="max-w-full overflow-x-auto bg-white/5 p-2 rounded-md">
                  <ChartComponent data={message.chart_data} type="line" />
                  {#if message.summary}
                    <div class="max-w-full overflow-x-hidden mt-4 p-3 bg-black/20 rounded-md">
                      <h4 class="text-sm font-semibold mb-2">Summary:</h4>
                      <div class="text-sm prose prose-invert prose-sm max-w-none">
                        {@html safeHtml(processTextWithMath(formatSummary(message.summary)))}
                      </div>
                    </div>
                  {/if}
                </div>
                <!-- Also show the text content if available -->
                {#if typeof message.content === 'string'}
                  <div class="mt-3">
                    {@html safeHtml(processTextWithMath(message.content))}
                  </div>
                {/if}
              {:else if typeof message.content === 'string'}
                {@html safeHtml(processTextWithMath(message.content))}
              {:else if !message.content}
                <div class="text-gray-400 italic">No content available</div>
              {:else if typeof message.content === 'object'}
                {#if message.content.chart_data}
                  <div class="max-w-full overflow-x-auto bg-white/5 p-2 rounded-md">
                    <ChartComponent data={message.content.chart_data} type="line" />
                    {#if message.content.summary}
                      <div class="max-w-full overflow-x-hidden mt-4 p-3 bg-black/20 rounded-md">
                        <h4 class="text-sm font-semibold mb-2">Summary:</h4>
                        <div class="text-sm prose prose-invert prose-sm max-w-none">
                          {@html safeHtml(
                            processTextWithMath(formatSummary(message.content.summary))
                          )}
                        </div>
                      </div>
                    {/if}
                  </div>
                {:else}
                  <pre
                    class="text-xs font-mono whitespace-pre-wrap break-all bg-black/20 p-3 rounded-md">{JSON.stringify(
                      message.content,
                      null,
                      2
                    )}</pre>
                {/if}
              {/if}
            </div>

            <div class="text-xs text-white/60 mt-2 text-right">
              {formatTime(message.timestamp)}
            </div>
          </div>
        </div>
      {/each}

      {#if loading}
        <div class="flex mr-auto max-w-[85%]">
          <div class="p-4 rounded-2xl relative bg-slate-700/50 border border-white/10 text-white">
            <div class="flex items-center gap-2">
              <div
                class="w-2 h-2 bg-white/50 rounded-full animate-pulse"
                style="animation-delay: 0s;"
              ></div>
              <div
                class="w-2 h-2 bg-white/50 rounded-full animate-pulse"
                style="animation-delay: 0.1s;"
              ></div>
              <div
                class="w-2 h-2 bg-white/50 rounded-full animate-pulse"
                style="animation-delay: 0.2s;"
              ></div>
            </div>
          </div>
        </div>
      {/if}
    </main>

    <!-- Chart Visualization -->
    {#if chartData}
      <div
        class="border-t border-white/20 bg-white/5 flex-shrink-0 max-h-[300px] md:max-h-[400px] overflow-y-auto"
      >
        <div
          class="flex justify-between items-stretch md:items-center flex-col md:flex-row gap-3 py-4 px-5 border-b border-white/10"
        >
          <h3>
            {#if chartData.type === 'trend'}📈 Expense Trends
            {:else if chartData.type === 'anomaly'}🔍 Anomaly Analysis
            {:else if chartData.type === 'comparative'}⚖️ Comparative Analysis
            {:else if chartData.type === 'category'}📋 Category Breakdown
            {:else if chartData.type === 'heatmap'}🌡️ Root Cause Heatmap
            {:else}📊 Visualization
            {/if}
          </h3>
          <button class="btn btn-secondary" on:click={() => (chartData = null)}> Close </button>
        </div>

        <div class="p-5">
          {#if chartData.data}
            <ChartComponent data={chartData.data} type="line" />
          {:else}
            <div class="text-center p-4 text-white/50">No chart data available</div>
          {/if}

          {#if chartData.summary}
            <div class="mt-4 p-4 bg-black/20 rounded-lg">
              <h4 class="mb-3 font-semibold">Summary:</h4>
              <pre
                class="font-mono text-xs overflow-x-auto text-white/80 bg-black/10 p-2 rounded">{JSON.stringify(
                  chartData.summary,
                  null,
                  2
                )}</pre>
            </div>
          {/if}
        </div>
      </div>
    {/if}

    <!-- Chat Input -->
    {#if $currentRoom}
      <footer
        class="p-4 border-t border-white/20 flex-shrink-0 bg-slate-900/80 backdrop-blur-sm sticky bottom-0 z-10"
      >
        <div class="flex gap-3 items-end">
          <textarea
            bind:value={$currentMessage}
            placeholder="Ask about expense trends, anomalies, root cause analysis..."
            on:keydown={handleKeyPress}
            disabled={loading}
            rows="1"
            class="flex-1 max-h-32 p-3 rounded-xl border border-white/30 bg-white/10 text-white resize-y font-sans transition-all focus:border-white/50 focus:bg-white/15 focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder-white/60"
          ></textarea>

          <button
            class="p-3 rounded-xl border-none bg-blue-600 text-white cursor-pointer text-xl transition-all min-w-[44px] h-[44px] flex items-center justify-center hover:enabled:bg-blue-700 hover:enabled:-translate-y-px disabled:opacity-50 disabled:cursor-not-allowed"
            on:click={sendMessage}
            disabled={loading || !$currentMessage.trim()}
            aria-label="Send message"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
      </footer>
    {/if}
  </div>
</div>
