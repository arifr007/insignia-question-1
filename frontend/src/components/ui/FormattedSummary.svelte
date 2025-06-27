<script>
  export let data = null;
  export let type = 'general'; // Options: 'general', 'eda', 'anomaly', 'trend'

  // Helper function for formatting currencies
  function formatCurrency(value) {
    if (value === null || value === undefined) return 'N/A';

    // Use compact notation only for amounts >= 1 million
    const useCompact = Math.abs(value) >= 1000000;

    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0,
      notation: useCompact ? 'compact' : 'standard'
    }).format(value);
  }

  // Helper function for formatting percentages
  function formatPercent(value) {
    if (value === null || value === undefined) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  }

  // Helper function to format numbers
  function formatNumber(value) {
    if (value === null || value === undefined) return 'N/A';

    // Use compact notation only for numbers >= 1 million
    const useCompact = Math.abs(value) >= 1000000;

    return new Intl.NumberFormat('id-ID', {
      maximumFractionDigits: useCompact ? 2 : 0,
      notation: useCompact ? 'compact' : 'standard'
    }).format(value);
  }

  // Helper function to format dates
  function formatDate(dateStr) {
    if (!dateStr) return 'N/A';

    try {
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }).format(date);
    } catch (_e) {
      return dateStr;
    }
  }

  // Format keys to be more readable
  function formatKey(key) {
    return key
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  // Helper function to determine if a value should be formatted as currency
  function isCurrencyField(key) {
    const currencyFields = [
      'amount',
      'total',
      'budget',
      'expense',
      'cost',
      'price',
      'value',
      'revenue',
      'balance',
      'avg_amount',
      'median_amount',
      'min_amount',
      'max_amount'
    ];
    return currencyFields.some(field => key.toLowerCase().includes(field));
  }

  // Helper function to determine if a value should be formatted as percentage
  function isPercentField(key) {
    const percentFields = [
      'percentage',
      'ratio',
      'rate',
      'proportion',
      'change',
      'growth',
      'increase',
      'decrease'
    ];
    return percentFields.some(field => key.toLowerCase().includes(field));
  }

  // Helper function to determine if a value should be formatted as date
  function isDateField(key) {
    const dateFields = ['date', 'time', 'timestamp', 'created_at', 'updated_at', 'year'];
    return dateFields.some(field => key.toLowerCase().includes(field));
  }
</script>

{#if data}
  {#if type === 'eda'}
    <div class="bg-white/5 border border-white/20 rounded-lg p-4 mb-4">
      <h3 class="text-lg font-semibold text-white mb-3">Data Analysis Summary</h3>

      {#if data.record_count !== undefined}
        <div class="mb-2">
          <span class="text-white/70">Total Records:</span>
          <span class="text-white font-medium">{formatNumber(data.record_count)}</span>
        </div>
      {/if}

      {#if data.time_period}
        <div class="mb-2">
          <span class="text-white/70">Time Period:</span>
          <span class="text-white font-medium">{data.time_period}</span>
        </div>
      {/if}

      {#if data.missing_values}
        <div class="mb-2">
          <h4 class="text-white/80 font-medium mt-3 mb-1">Missing Values:</h4>
          <div class="grid grid-cols-2 gap-x-4 gap-y-1">
            {#each Object.entries(data.missing_values) as [key, value]}
              <div class="text-sm">
                <span class="text-white/60">{formatKey(key)}:</span>
                <span class="text-white">{formatNumber(value)}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if data.unique_counts}
        <div class="mb-2">
          <h4 class="text-white/80 font-medium mt-3 mb-1">Unique Values:</h4>
          <div class="grid grid-cols-2 gap-x-4 gap-y-1">
            {#each Object.entries(data.unique_counts) as [key, value]}
              <div class="text-sm">
                <span class="text-white/60">{formatKey(key)}:</span>
                <span class="text-white">{formatNumber(value)}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if data.numeric_summary}
        <div class="mt-4">
          <h4 class="text-white/80 font-medium mb-2">Numeric Summary:</h4>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-white/10">
                  <th class="text-left p-2 border border-white/20">Metric</th>
                  {#each Object.keys(data.numeric_summary) as field}
                    <th class="text-left p-2 border border-white/20">{formatKey(field)}</th>
                  {/each}
                </tr>
              </thead>
              <tbody>
                {#each ['min', 'max', 'mean', 'median'] as metric}
                  <tr class="border-b border-white/10">
                    <td class="p-2 border border-white/20 font-medium">{formatKey(metric)}</td>
                    {#each Object.entries(data.numeric_summary) as [field, values]}
                      <td class="p-2 border border-white/20">
                        {isCurrencyField(field)
                          ? formatCurrency(values[metric])
                          : isPercentField(field)
                            ? formatPercent(values[metric])
                            : formatNumber(values[metric])}
                      </td>
                    {/each}
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  {:else if type === 'anomaly'}
    <div class="bg-white/5 border border-white/20 rounded-lg p-4 mb-4">
      <h3 class="text-lg font-semibold text-white mb-3">Anomaly Detection Results</h3>

      {#if data.anomaly_count !== undefined}
        <div class="mb-2">
          <span class="text-white/70">Anomalies Detected:</span>
          <span class="text-white font-medium">{data.anomaly_count}</span>
          {#if data.total_records && data.anomaly_count}
            <span class="text-white/60 text-sm ml-2">
              ({formatPercent(data.anomaly_count / data.total_records)} of total)
            </span>
          {/if}
        </div>
      {/if}

      {#if data.threshold !== undefined}
        <div class="mb-2">
          <span class="text-white/70">Detection Threshold:</span>
          <span class="text-white font-medium">{data.threshold}</span>
          <span class="text-white/60 text-sm ml-2">(standard deviations)</span>
        </div>
      {/if}

      {#if data.anomalies && data.anomalies.length > 0}
        <div class="mt-4">
          <h4 class="text-white/80 font-medium mb-2">Top Anomalies:</h4>
          <div class="overflow-x-auto max-h-60">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-white/10">
                  {#each Object.keys(data.anomalies[0]) as field}
                    <th class="text-left p-2 border border-white/20">{formatKey(field)}</th>
                  {/each}
                </tr>
              </thead>
              <tbody>
                {#each data.anomalies.slice(0, 10) as anomaly}
                  <tr class="border-b border-white/10">
                    {#each Object.entries(anomaly) as [field, value]}
                      <td class="p-2 border border-white/20">
                        {isCurrencyField(field)
                          ? formatCurrency(value)
                          : isDateField(field)
                            ? formatDate(value)
                            : isPercentField(field)
                              ? formatPercent(value)
                              : typeof value === 'number'
                                ? formatNumber(value)
                                : value}
                      </td>
                    {/each}
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          {#if data.anomalies.length > 10}
            <div class="text-white/60 text-sm mt-1 italic">
              Showing 10 of {data.anomalies.length} anomalies
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {:else if type === 'trend'}
    <div class="bg-white/5 border border-white/20 rounded-lg p-4 mb-4">
      <h3 class="text-lg font-semibold text-white mb-3">Trend Analysis</h3>

      {#if data.trend_direction}
        <div class="mb-3">
          <span class="text-white/70">Overall Trend:</span>
          <span
            class="font-medium
            {data.trend_direction === 'increasing'
              ? 'text-red-400'
              : data.trend_direction === 'decreasing'
                ? 'text-green-400'
                : 'text-white'}"
          >
            {formatKey(data.trend_direction)}
            {#if data.trend_direction === 'increasing'}↑{:else if data.trend_direction === 'decreasing'}↓{/if}
          </span>
        </div>
      {/if}

      {#if data.trend_rate !== undefined}
        <div class="mb-3">
          <span class="text-white/70">Rate of Change:</span>
          <span class="font-medium text-white">
            {formatPercent(data.trend_rate)}
            {#if data.trend_period}
              <span class="text-white/60 text-sm ml-1">per {data.trend_period}</span>
            {/if}
          </span>
        </div>
      {/if}

      {#if data.average_value !== undefined}
        <div class="mb-3">
          <span class="text-white/70">Average Value:</span>
          <span class="font-medium text-white">
            {isCurrencyField('average_value')
              ? formatCurrency(data.average_value)
              : formatNumber(data.average_value)}
          </span>
        </div>
      {/if}

      {#if data.highest_point && data.highest_point.value !== undefined}
        <div class="mb-3">
          <span class="text-white/70">Peak Value:</span>
          <span class="font-medium text-white">
            {isCurrencyField('value')
              ? formatCurrency(data.highest_point.value)
              : formatNumber(data.highest_point.value)}
          </span>
          {#if data.highest_point.period}
            <span class="text-white/60 text-sm ml-2">({data.highest_point.period})</span>
          {/if}
        </div>
      {/if}

      {#if data.lowest_point && data.lowest_point.value !== undefined}
        <div class="mb-3">
          <span class="text-white/70">Lowest Value:</span>
          <span class="font-medium text-white">
            {isCurrencyField('value')
              ? formatCurrency(data.lowest_point.value)
              : formatNumber(data.lowest_point.value)}
          </span>
          {#if data.lowest_point.period}
            <span class="text-white/60 text-sm ml-2">({data.lowest_point.period})</span>
          {/if}
        </div>
      {/if}
    </div>
  {:else}
    <div class="bg-white/5 border border-white/20 rounded-lg p-4 mb-4">
      <h3 class="text-lg font-semibold text-white mb-3">Summary</h3>
      <div class="grid grid-cols-1 gap-2">
        {#each Object.entries(data) as [key, value]}
          {#if typeof value !== 'object' || value === null}
            <div>
              <span class="text-white/70">{formatKey(key)}:</span>
              <span class="text-white">
                {isCurrencyField(key)
                  ? formatCurrency(value)
                  : isDateField(key)
                    ? formatDate(value)
                    : isPercentField(key)
                      ? formatPercent(value)
                      : typeof value === 'number'
                        ? formatNumber(value)
                        : typeof value === 'boolean'
                          ? value
                            ? 'Yes'
                            : 'No'
                          : value === null || value === undefined
                            ? 'N/A'
                            : value}
              </span>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  {/if}
{:else}
  <div class="bg-white/5 border border-white/20 rounded-lg p-4 mb-4 text-white/60 italic">
    No summary data available
  </div>
{/if}
