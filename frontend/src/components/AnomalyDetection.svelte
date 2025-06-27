<script>
  import { onMount } from 'svelte';
  import api from '../services/api.js';
  import ChartComponent from './ChartJSChart.svelte';
  import Card from './ui/Card.svelte';
  import Button from './ui/Button.svelte';
  import LoadingSpinner from './ui/LoadingSpinner.svelte';
  import Alert from './ui/Alert.svelte';

  let anomalies = null;
  let chartData = null;
  let loading = false;
  let error = null;
  let method = 'comprehensive';
  let threshold = 2.5;
  let contamination = 0.1;

  const methods = [
    { value: 'comprehensive', label: 'Comprehensive Analysis' },
    { value: 'statistical', label: 'Statistical (Z-Score)' },
    { value: 'ml', label: 'Machine Learning' },
    { value: 'trend', label: 'Trend Analysis' }
  ];

  onMount(() => {
    detectAnomalies();
  });

  async function detectAnomalies() {
    if (loading) return;

    try {
      loading = true;
      error = null;
      chartData = null;
      anomalies = null;

      const params = {};
      if (method === 'statistical') params.threshold = threshold;
      if (method === 'ml') params.contamination = contamination;
      if (method === 'trend') params.threshold_pct = 30.0; // Can make dynamic

      const response = await api.detectAnomalies(method, params);
      anomalies = response;
      await loadAnomalyChart(method === 'comprehensive' ? 'ml' : method);
    } catch (err) {
      error =
        err?.response?.data?.message ||
        err?.response?.data?.error ||
        err?.message ||
        'Failed to detect anomalies';
    } finally {
      loading = false;
    }
  }

  async function loadAnomalyChart(chartMethod) {
    try {
      const response = await api.getAnomalyScatterChart(chartMethod);
      if (response?.data?.chart_data) {
        chartData = response.data.chart_data;
      }
    } catch (_err) {
      console.warn('Chart loading failed');
    }
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount || 0);
  }
</script>

<div class="max-w-7xl mx-auto space-y-8">
  <div class="text-center">
    <h1 class="text-4xl font-bold text-white mb-4">🔍 Anomaly Detection</h1>
    <p class="text-gray-300 text-lg">Detect unusual patterns and outliers in expense data</p>
  </div>

  <Card>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div>
        <label for="detection-method" class="block text-sm font-medium text-white mb-2"
          >Detection Method:</label
        >
        <select
          id="detection-method"
          bind:value={method}
          on:change={detectAnomalies}
          class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        >
          {#each methods as methodOption}
            <option value={methodOption.value} class="bg-slate-800 text-white">
              {methodOption.label}
            </option>
          {/each}
        </select>
      </div>

      {#if method === 'statistical'}
        <div>
          <label for="zscore-threshold" class="block text-sm font-medium text-white mb-2"
            >Z-Score Threshold:</label
          >
          <input
            id="zscore-threshold"
            type="number"
            bind:value={threshold}
            step="0.1"
            min="1"
            max="5"
            on:change={detectAnomalies}
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
      {/if}

      {#if method === 'ml'}
        <div>
          <label for="contamination-rate" class="block text-sm font-medium text-white mb-2"
            >Contamination Rate:</label
          >
          <input
            id="contamination-rate"
            type="number"
            bind:value={contamination}
            step="0.01"
            min="0.01"
            max="0.5"
            on:change={detectAnomalies}
            class="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
      {/if}

      <div class="flex items-end">
        <Button variant="primary" on:click={detectAnomalies} disabled={loading}>
          {loading ? 'Detecting...' : 'Refresh Analysis'}
        </Button>
      </div>
    </div>
  </Card>

  <Alert message={error} type="error" />

  {#if loading}
    <Card>
      <div class="text-center py-12">
        <LoadingSpinner size="lg" />
        <p class="text-gray-300 mt-4">Analyzing data for anomalies...</p>
      </div>
    </Card>
  {:else if anomalies}
    {#if method === 'comprehensive'}
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <Card>
          <h3 class="text-xl font-bold text-white mb-4">📊 Summary</h3>
          <div class="space-y-4">
            <div class="grid grid-cols-3 gap-4 text-center">
              <div class="p-3 bg-red-500/20 rounded-lg">
                <div class="text-2xl font-bold text-red-400">
                  {anomalies.data?.summary?.total_statistical_anomalies || 0}
                </div>
                <div class="text-xs text-gray-300">Statistical</div>
              </div>
              <div class="p-3 bg-blue-500/20 rounded-lg">
                <div class="text-2xl font-bold text-blue-400">
                  {anomalies.data?.summary?.total_ml_anomalies || 0}
                </div>
                <div class="text-xs text-gray-300">ML</div>
              </div>
              <div class="p-3 bg-yellow-500/20 rounded-lg">
                <div class="text-2xl font-bold text-yellow-400">
                  {anomalies.data?.summary?.total_trend_anomalies || 0}
                </div>
                <div class="text-xs text-gray-300">Trend</div>
              </div>
            </div>

            {#if anomalies.data?.summary?.recommendations}
              <div class="space-y-2">
                <h4 class="font-semibold text-white">Recommendations:</h4>
                <ul class="text-sm text-gray-300 space-y-1">
                  {#each anomalies.data.summary.recommendations as rec}
                    <li class="flex items-start space-x-2">
                      <span class="text-blue-400">•</span>
                      <span>{rec}</span>
                    </li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        </Card>

        <div class="xl:col-span-2 space-y-6">
          {#if anomalies.data?.statistical_anomalies?.anomalies?.length > 0}
            <Card>
              <h3 class="text-lg font-bold text-white mb-4">📈 Statistical Anomalies</h3>
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 max-h-80 overflow-y-auto">
                {#each anomalies.data.statistical_anomalies.anomalies.slice(0, 6) as anomaly}
                  <div class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <div class="flex justify-between items-start mb-2">
                      <span class="text-sm font-medium text-red-400">ID: {anomaly.id}</span>
                      {#if anomaly.z_score}<span class="text-xs bg-red-500/20 px-2 py-1 rounded"
                          >Z: {anomaly.z_score.toFixed(2)}</span
                        >{/if}
                    </div>
                    <div class="space-y-1 text-sm">
                      <div class="font-bold text-white">{formatCurrency(anomaly.amount || 0)}</div>
                      <div class="text-gray-300">{anomaly.cost_center_name || 'N/A'}</div>
                      <div class="text-gray-400 text-xs">
                        {anomaly.functional_area_name || 'N/A'}
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </Card>
          {/if}

          {#if anomalies.data?.ml_anomalies?.anomalies?.length > 0}
            <Card>
              <h3 class="text-lg font-bold text-white mb-4">🤖 ML Anomalies</h3>
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 max-h-80 overflow-y-auto">
                {#each anomalies.data.ml_anomalies.anomalies.slice(0, 6) as anomaly}
                  <div class="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div class="flex justify-between items-start mb-2">
                      <span class="text-sm font-medium text-blue-400">ID: {anomaly.id}</span>
                      {#if anomaly.anomaly_score}<span
                          class="text-xs bg-blue-500/20 px-2 py-1 rounded"
                          >{anomaly.anomaly_score.toFixed(3)}</span
                        >{/if}
                    </div>
                    <div class="space-y-1 text-sm">
                      <div class="font-bold text-white">{formatCurrency(anomaly.amount || 0)}</div>
                      <div class="text-gray-300">{anomaly.cost_center_name || 'N/A'}</div>
                      <div class="text-gray-400 text-xs">
                        {anomaly.functional_area_name || 'N/A'}
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </Card>
          {/if}

          {#if anomalies.data?.trend_anomalies?.anomalies?.length > 0}
            <Card>
              <h3 class="text-lg font-bold text-white mb-4">📅 Trend Anomalies</h3>
              <div class="space-y-3 max-h-80 overflow-y-auto">
                {#each anomalies.data.trend_anomalies.anomalies as anomaly}
                  <div class="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                    <div class="flex justify-between items-center">
                      <div>
                        <div class="font-bold text-yellow-400">{anomaly.month_year}</div>
                        <div class="text-sm text-gray-300">{anomaly.deviation_type}</div>
                      </div>
                      <div class="text-right">
                        <div class="font-bold text-white">
                          {formatCurrency(anomaly.total_amount || 0)}
                        </div>
                        <div class="text-sm text-gray-400">
                          {anomaly.mom_change_percent?.toFixed(1) || 'N/A'}%
                        </div>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </Card>
          {/if}
        </div>
      </div>
    {:else}
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card>
          <h2 class="text-2xl font-bold text-white mb-6">📊 Anomaly Results</h2>

          {#if anomalies.data?.anomalies?.length > 0}
            <div class="space-y-4">
              <div class="text-center p-4 bg-white/5 rounded-lg">
                <div class="text-3xl font-bold text-red-400">
                  {anomalies.data.anomaly_count || anomalies.data.anomalies.length}
                </div>
                <div class="text-sm text-gray-300">Anomalies Found</div>
              </div>

              <div class="space-y-3 max-h-96 overflow-y-auto">
                {#each anomalies.data.anomalies.slice(0, 10) as anomaly}
                  <div class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <div class="flex justify-between items-start">
                      <div>
                        <div class="font-medium text-white">
                          {anomaly.supplier_name || 'Unknown Supplier'}
                        </div>
                        <div class="text-sm text-gray-300">
                          {anomaly.functional_area ||
                            anomaly.functional_area_name ||
                            'Unknown Area'}
                        </div>
                        <div class="text-xs text-gray-400 mt-1">
                          {anomaly.date ? new Date(anomaly.date).toLocaleDateString() : 'N/A'}
                        </div>
                      </div>
                      <div class="text-right">
                        <div class="font-bold text-red-400">{formatCurrency(anomaly.amount)}</div>
                        {#if anomaly.z_score}
                          <div class="text-xs text-gray-400">Z: {anomaly.z_score.toFixed(2)}</div>
                        {:else if anomaly.anomaly_score}
                          <div class="text-xs text-gray-400">
                            Score: {anomaly.anomaly_score.toFixed(3)}
                          </div>
                        {/if}
                      </div>
                    </div>
                    {#if anomaly.reason}
                      <div
                        class="mt-2 text-sm text-gray-300 bg-white/5 p-2 rounded border-l-2 border-red-500"
                      >
                        {anomaly.reason}
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          {:else}
            <div class="text-center py-8">
              <div class="text-4xl mb-4">✅</div>
              <p class="text-gray-300">No anomalies detected in the current dataset.</p>
            </div>
          {/if}
        </Card>

        {#if chartData}
          <Card>
            <h2 class="text-2xl font-bold text-white mb-6">📈 Visualization</h2>
            <ChartComponent data={chartData} type="scatter" />
          </Card>
        {/if}
      </div>
    {/if}

    {#if chartData && method === 'comprehensive'}
      <Card>
        <h2 class="text-2xl font-bold text-white mb-6">📈 Comprehensive Visualization</h2>
        <ChartComponent data={chartData} type="scatter" />
      </Card>
    {/if}
  {:else}
    <Card>
      <div class="text-center py-12">
        <div class="text-6xl mb-4">🔍</div>
        <h3 class="text-xl font-bold text-white mb-2">Ready to Analyze</h3>
        <p class="text-gray-300">
          Click "Refresh Analysis" to detect anomalies in your expense data.
        </p>
      </div>
    </Card>
  {/if}
</div>
