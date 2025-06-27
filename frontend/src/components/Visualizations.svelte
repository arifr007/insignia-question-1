<script>
  import { onMount } from 'svelte';
  import api from '../services/api.js';
  import ChartComponent from './ChartJSChart.svelte';
  import Card from './ui/Card.svelte';
  import Button from './ui/Button.svelte';
  import LoadingSpinner from './ui/LoadingSpinner.svelte';
  import Alert from './ui/Alert.svelte';

  let charts = {
    trend: null,
    breakdown: null,
    heatmap: null,
    anomaly: null
  };

  let loading = {
    trend: false,
    breakdown: false,
    heatmap: false,
    anomaly: false
  };

  let errors = {
    trend: null,
    breakdown: null,
    heatmap: null,
    anomaly: null
  };

  let selectedCharts = ['trend', 'breakdown'];

  const availableCharts = [
    {
      id: 'trend',
      title: '📈 Monthly Expense Trends',
      description: 'Time series analysis of expense patterns over months'
    },
    {
      id: 'breakdown',
      title: '🍰 Functional Area Breakdown',
      description: 'Distribution of expenses across functional areas'
    },
    {
      id: 'heatmap',
      title: '🔥 Cost Center Heatmap',
      description: 'Visual representation of spending intensity by cost centers'
    },
    {
      id: 'anomaly',
      title: '🔍 Anomaly Scatter Plot',
      description: 'Visualization of detected anomalies and outliers'
    }
  ];

  onMount(() => {
    loadSelectedCharts();
  });

  async function loadChart(chartType) {
    loading[chartType] = true;
    errors[chartType] = null;

    try {
      let data;

      switch (chartType) {
        case 'trend':
          data = await api.getTrendChart();
          break;
        case 'breakdown':
          data = await api.getCategoryBreakdownChart();
          break;
        case 'heatmap':
          data = await api.getHeatmapChart();
          break;
        case 'anomaly':
          data = await api.getAnomalyScatterChart();
          break;
        default:
          throw new Error(`Unknown chart type: ${chartType}`);
      }

      charts[chartType] = data.data;
    } catch (err) {
      errors[chartType] = err.response?.data?.error || `Failed to load ${chartType} chart`;
    } finally {
      loading[chartType] = false;
    }
  }

  function toggleChart(chartId) {
    if (selectedCharts.includes(chartId)) {
      selectedCharts = selectedCharts.filter(id => id !== chartId);
      charts[chartId] = null;
    } else {
      selectedCharts = [...selectedCharts, chartId];
      loadChart(chartId);
    }
  }

  function loadSelectedCharts() {
    selectedCharts.forEach(chartId => {
      loadChart(chartId);
    });
  }

  function refreshAllCharts() {
    selectedCharts.forEach(chartId => {
      loadChart(chartId);
    });
  }

  function formatCurrency(amount) {
    if (typeof amount !== 'number') return 'N/A';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount);
  }

  function formatNumber(num) {
    if (typeof num !== 'number') return 'N/A';
    return new Intl.NumberFormat('id-ID').format(num);
  }

  function getChartType(chartId) {
    switch (chartId) {
      case 'trend':
        return 'line';
      case 'breakdown':
        return 'pie';
      case 'heatmap':
        return 'bar';
      case 'anomaly':
        return 'scatter';
      default:
        return 'line';
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <div class="text-center mb-8">
    <h1 class="text-3xl lg:text-4xl font-bold text-primary mb-2">📊 Data Visualizations</h1>
    <p class="text-gray-600">Interactive charts and graphs for expense analysis</p>
  </div>

  <!-- Chart Selection -->
  <Card class="mb-8">
    <h2 class="text-xl font-semibold text-primary mb-6">Select Charts to Display</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {#each availableCharts as chart}
        <label
          for="chart-{chart.id}"
          class="flex items-start gap-3 p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
        >
          <input
            id="chart-{chart.id}"
            type="checkbox"
            class="mt-1 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            checked={selectedCharts.includes(chart.id)}
            on:change={() => toggleChart(chart.id)}
          />
          <div class="flex-1">
            <div class="font-medium text-gray-900 text-sm">{chart.title}</div>
            <div class="text-xs text-gray-600 mt-1">{chart.description}</div>
          </div>
        </label>
      {/each}
    </div>

    <div class="text-center">
      <Button variant="primary" on:click={refreshAllCharts}>🔄 Refresh All Charts</Button>
    </div>
  </Card>

  <!-- Charts Display -->
  <div class="space-y-8">
    {#each selectedCharts as chartId}
      {@const chartInfo = availableCharts.find(c => c.id === chartId)}
      <Card>
        <div class="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4 mb-6">
          <h2 class="text-xl font-semibold text-primary">{chartInfo.title}</h2>
          <div class="flex gap-2">
            <Button
              variant="secondary"
              on:click={() => loadChart(chartId)}
              disabled={loading[chartId]}
            >
              {loading[chartId] ? '⏳' : '🔄'}
            </Button>
            <Button variant="secondary" on:click={() => toggleChart(chartId)}>✕</Button>
          </div>
        </div>

        {#if loading[chartId]}
          <div class="flex flex-col items-center justify-center py-16">
            <LoadingSpinner size="large" />
            <p class="text-gray-600 mt-4">Loading {chartInfo.title.toLowerCase()}...</p>
          </div>
        {:else if errors[chartId]}
          <Alert type="error" error={errors[chartId]}>
            <Button slot="action" variant="primary" on:click={() => loadChart(chartId)}>
              Try Again
            </Button>
          </Alert>
        {:else if charts[chartId]}
          <div>
            <ChartComponent data={charts[chartId]} type={getChartType(chartId)} />

            {#if charts[chartId].summary}
              <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                <h3 class="text-lg font-semibold text-primary mb-4">📋 Summary</h3>
                <div>
                  {#if chartId === 'trend' && charts[chartId].summary}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Total Months:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{charts[chartId].summary.total_months}</span
                        >
                      </div>
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Average Monthly:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{formatCurrency(charts[chartId].summary.average_monthly)}</span
                        >
                      </div>
                      {#if charts[chartId].summary.min_month}
                        <div class="flex justify-between items-center p-2 border-b border-gray-200">
                          <span class="text-sm font-medium text-gray-700">Lowest Month:</span>
                          <span class="text-sm font-semibold text-accent">
                            {charts[chartId].summary.min_month.month_year}
                            ({formatCurrency(charts[chartId].summary.min_month.amount)})
                          </span>
                        </div>
                      {/if}
                      {#if charts[chartId].summary.max_month}
                        <div class="flex justify-between items-center p-2 border-b border-gray-200">
                          <span class="text-sm font-medium text-gray-700">Highest Month:</span>
                          <span class="text-sm font-semibold text-accent">
                            {charts[chartId].summary.max_month.month_year}
                            ({formatCurrency(charts[chartId].summary.max_month.amount)})
                          </span>
                        </div>
                      {/if}
                    </div>
                  {:else if chartId === 'breakdown' && charts[chartId].summary}
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Total Areas:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{charts[chartId].summary.total_functional_areas}</span
                        >
                      </div>
                      {#if charts[chartId].summary.largest_area}
                        <div class="flex justify-between items-center p-2 border-b border-gray-200">
                          <span class="text-sm font-medium text-gray-700">Largest Area:</span>
                          <span class="text-sm font-semibold text-accent">
                            {charts[chartId].summary.largest_area.name}
                            ({charts[chartId].summary.largest_area.percentage.toFixed(2)}%)
                          </span>
                        </div>
                      {/if}
                      {#if charts[chartId].summary.smallest_area}
                        <div class="flex justify-between items-center p-2 border-b border-gray-200">
                          <span class="text-sm font-medium text-gray-700">Smallest Area:</span>
                          <span class="text-sm font-semibold text-accent">
                            {charts[chartId].summary.smallest_area.name}
                            ({charts[chartId].summary.smallest_area.percentage.toFixed(2)}%)
                          </span>
                        </div>
                      {/if}
                    </div>
                  {:else if chartId === 'heatmap' && charts[chartId].summary}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Cost Centers Analyzed:</span
                        >
                        <span class="text-sm font-semibold text-accent"
                          >{charts[chartId].summary.cost_centers_shown}</span
                        >
                      </div>
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Months Covered:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{charts[chartId].summary.months_covered}</span
                        >
                      </div>

                      <div class="md:col-span-2 lg:col-span-3">
                        <div class="p-3 bg-blue-50 rounded-lg">
                          <h4 class="text-sm font-semibold text-blue-900 mb-2">
                            Highest Spending Cost Center
                          </h4>
                          <div class="space-y-2">
                            <div class="flex justify-between items-center">
                              <span class="text-sm text-blue-800">ID:</span>
                              <span class="text-sm font-medium text-blue-900"
                                >{charts[chartId].summary.highest_spending.cost_center_id}</span
                              >
                            </div>
                            <div class="flex justify-between items-center">
                              <span class="text-sm text-blue-800">Name:</span>
                              <span class="text-sm font-medium text-blue-900"
                                >{charts[chartId].summary.highest_spending.cost_center_name}</span
                              >
                            </div>
                            <div class="flex justify-between items-center">
                              <span class="text-sm text-blue-800">Total Amount:</span>
                              <span class="text-sm font-semibold text-blue-900"
                                >{formatCurrency(
                                  charts[chartId].summary.highest_spending.amount
                                )}</span
                              >
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  {:else if chartId === 'anomaly' && charts[chartId].summary}
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Detection Method:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{charts[chartId].summary.detection_method
                            ?.replace(/_/g, ' ')
                            .toUpperCase()}</span
                        >
                      </div>
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Total Anomalies:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{formatNumber(charts[chartId].summary.total_anomalies)}</span
                        >
                      </div>
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Displayed Anomalies:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{formatNumber(charts[chartId].summary.displayed_anomalies)}</span
                        >
                      </div>
                      <div class="flex justify-between items-center p-2 border-b border-gray-200">
                        <span class="text-sm font-medium text-gray-700">Avg Anomaly Amount:</span>
                        <span class="text-sm font-semibold text-accent"
                          >{formatCurrency(charts[chartId].summary.avg_anomaly_amount)}</span
                        >
                      </div>
                      <div class="md:col-span-2 lg:col-span-3">
                        <div class="p-3 bg-red-50 rounded-lg">
                          <h4 class="text-sm font-semibold text-red-900 mb-2">Data Optimization</h4>
                          <p class="text-sm text-red-800">
                            {charts[chartId].summary.data_optimization}
                          </p>
                        </div>
                      </div>
                    </div>
                  {:else}
                    <pre
                      class="text-xs text-gray-700 bg-white p-4 rounded border max-h-48 overflow-y-auto">{JSON.stringify(
                        charts[chartId].summary,
                        null,
                        2
                      )}</pre>
                  {/if}
                </div>
              </div>
            {/if}

            {#if charts[chartId].raw_data && chartId === 'trend'}
              <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                <h3 class="text-lg font-semibold text-primary mb-4">📊 Raw Data</h3>
                <div class="text-sm">
                  <div
                    class="grid grid-cols-2 gap-4 font-medium text-gray-700 pb-2 border-b-2 border-gray-300 mb-2"
                  >
                    <div>Month</div>
                    <div>Amount</div>
                  </div>
                  {#each charts[chartId].raw_data.slice(0, 10) as dataPoint}
                    <div class="grid grid-cols-2 gap-4 py-2 border-b border-gray-200">
                      <div class="text-gray-900">{dataPoint.month_year}</div>
                      <div class="text-gray-900">{formatCurrency(dataPoint.amount)}</div>
                    </div>
                  {/each}
                  {#if charts[chartId].raw_data.length > 10}
                    <div class="text-center text-gray-600 italic py-3">
                      ... and {charts[chartId].raw_data.length - 10} more records
                    </div>
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <div class="text-center py-16">
            <div class="text-5xl opacity-50 mb-4">📊</div>
            <p class="text-gray-600">Click refresh to load {chartInfo.title.toLowerCase()}</p>
          </div>
        {/if}
      </Card>
    {/each}

    {#if selectedCharts.length === 0}
      <Card>
        <div class="text-center py-16">
          <div class="text-6xl opacity-50 mb-6">📈</div>
          <h3 class="text-xl font-semibold text-gray-700 mb-3">No Charts Selected</h3>
          <p class="text-gray-600">Select charts from the options above to view visualizations</p>
        </div>
      </Card>
    {/if}
  </div>
</div>
