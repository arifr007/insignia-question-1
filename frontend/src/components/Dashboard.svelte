<script>
  import { onMount } from 'svelte';
  import api from '../services/api.js';
  import Card from './ui/Card.svelte';
  import DashboardCard from './ui/DashboardCard.svelte';
  import LoadingSpinner from './ui/LoadingSpinner.svelte';
  import Alert from './ui/Alert.svelte';

  let edaData = null;
  let loading = true;
  let error = null;

  // Helper function to transform object into array of [key, value] pairs
  function objectToArray(obj) {
    return obj ? Object.entries(obj) : [];
  }

  function formatCurrency(amount) {
    // Use compact notation only for amounts >= 1 million
    const useCompact = Math.abs(amount) >= 1000000;

    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      notation: useCompact ? 'compact' : 'standard',
      maximumFractionDigits: 0
    }).format(amount);
  }

  function formatNumber(num) {
    // Use compact notation only for numbers >= 1 million
    const useCompact = Math.abs(num) >= 1000000;

    return new Intl.NumberFormat('id-ID', {
      notation: useCompact ? 'compact' : 'standard',
      maximumFractionDigits: useCompact ? 1 : 0
    }).format(num);
  }

  function formatCurrencyFull(amount) {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0
    }).format(amount);
  }

  onMount(async () => {
    try {
      edaData = await api.getEDASummary();
    } catch (err) {
      error = err.response?.data?.error || 'Failed to load dashboard data';
    } finally {
      loading = false;
    }
  });
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <h1 class="text-3xl lg:text-4xl font-bold text-primary text-center mb-8">📊 Finance Dashboard</h1>

  {#if loading}
    <div class="flex justify-center py-12">
      <LoadingSpinner size="large" />
    </div>
  {:else if error}
    <Alert type="error" {error} />
  {:else if edaData}
    <!-- Summary Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <Card class="text-center">
        <h3 class="text-sm font-medium text-gray-600 mb-2">Total Records</h3>
        <div
          class="text-xl lg:text-2xl font-bold text-accent break-words"
          title={new Intl.NumberFormat('id-ID').format(edaData.total_rows)}
        >
          {formatNumber(edaData.total_rows)}
        </div>
      </Card>

      <Card class="text-center">
        <h3 class="text-sm font-medium text-gray-600 mb-2">Total Amount</h3>
        <div
          class="text-xl lg:text-2xl font-bold text-accent break-words"
          title={formatCurrencyFull(edaData.financial_summary?.total_amount || 0)}
        >
          {formatCurrency(edaData.financial_summary?.total_amount || 0)}
        </div>
      </Card>

      <Card class="text-center">
        <h3 class="text-sm font-medium text-gray-600 mb-2">Average Amount</h3>
        <div
          class="text-xl lg:text-2xl font-bold text-accent break-words"
          title={formatCurrencyFull(edaData.financial_summary?.average_amount || 0)}
        >
          {formatCurrency(edaData.financial_summary?.average_amount || 0)}
        </div>
      </Card>

      <Card class="text-center">
        <h3 class="text-sm font-medium text-gray-600 mb-2">Median Amount</h3>
        <div
          class="text-xl lg:text-2xl font-bold text-accent break-words"
          title={formatCurrencyFull(edaData.financial_summary?.median_amount || 0)}
        >
          {formatCurrency(edaData.financial_summary?.median_amount || 0)}
        </div>
      </Card>
    </div>

    <!-- Organizational Breakdown -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-primary mb-6">📋 Organizational Breakdown</h2>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {#if edaData.organizational_breakdown?.top_directorates}
          <DashboardCard
            title="Top Directorates"
            items={objectToArray(edaData.organizational_breakdown.top_directorates)}
            formatValue={formatCurrency}
          />
        {/if}

        {#if edaData.organizational_breakdown?.top_functional_areas}
          <DashboardCard
            title="Top Functional Areas"
            items={objectToArray(edaData.organizational_breakdown.top_functional_areas)}
            formatValue={formatCurrency}
          />
        {/if}

        {#if edaData.organizational_breakdown?.top_cost_centers}
          <DashboardCard
            title="Top Cost Centers"
            items={objectToArray(edaData.organizational_breakdown.top_cost_centers)}
            formatValue={formatCurrency}
          />
        {/if}

        {#if edaData.organizational_breakdown?.top_profit_centers}
          <DashboardCard
            title="Top Profit Centers"
            items={objectToArray(edaData.organizational_breakdown.top_profit_centers)}
            formatValue={formatCurrency}
          />
        {/if}
      </div>
    </div>

    <!-- General Ledger Analysis -->
    {#if edaData.general_ledger_account_analysis?.top_general_ledger_accounts}
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-primary mb-6">📊 General Ledger Analysis</h2>
        <DashboardCard
          title="Top General Ledger Accounts"
          items={objectToArray(edaData.general_ledger_account_analysis.top_general_ledger_accounts)}
          formatValue={formatCurrency}
        />
      </div>
    {/if}

    <!-- Supplier Analysis -->
    {#if edaData.supplier_analysis?.top_suppliers}
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-primary mb-6">🏢 Supplier Analysis</h2>
        <DashboardCard
          title="Top Suppliers (Total: {edaData.supplier_analysis.supplier_count})"
          items={objectToArray(edaData.supplier_analysis.top_suppliers)}
          formatValue={formatCurrency}
          formatKey={key => `Supplier ${key}`}
        />
      </div>
    {/if}

    <!-- Monthly Trends -->
    {#if edaData.temporal_analysis?.recent_months}
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-primary mb-6">📈 Recent Monthly Trends</h2>
        <DashboardCard
          title="Monthly Trends"
          items={objectToArray(edaData.temporal_analysis.recent_months)}
          formatValue={formatCurrency}
        />
      </div>
    {/if}

    <!-- Transaction Analysis -->
    {#if edaData.transaction_analysis}
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-primary mb-6">💳 Transaction Analysis</h2>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {#if edaData.transaction_analysis.debit_credit_split}
            <DashboardCard
              title="Debit/Credit Split"
              items={objectToArray(edaData.transaction_analysis.debit_credit_split)}
              formatValue={formatCurrency}
              formatKey={type => (type === 'H' ? 'Debit (H)' : 'Credit (S)')}
            />
          {/if}

          {#if edaData.transaction_analysis.top_transaction_types}
            <DashboardCard
              title="Top Transaction Types"
              items={objectToArray(edaData.transaction_analysis.top_transaction_types).slice(0, 5)}
              formatValue={formatCurrency}
              formatKey={type => type || 'Unknown'}
            />
          {/if}
        </div>
      </div>
    {/if}

    <!-- Data Quality -->
    {#if edaData.data_quality}
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-primary mb-6">⚠️ Data Quality</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {#if edaData.data_quality.data_completeness}
            <DashboardCard
              title="Data Completeness"
              items={[
                ['Total Amount Records', edaData.data_quality.data_completeness.amount_records],
                [
                  'Negative Amount Records',
                  edaData.data_quality.data_completeness.negative_amount_records
                ],
                ['Zero Amount Records', edaData.data_quality.data_completeness.zero_amount_records]
              ]}
              formatValue={(value, key) => {
                if (key === 'Total Amount Records') return formatNumber(value);
                return formatNumber(value);
              }}
              valueColor={(key, value) => {
                if (key === 'Total Amount Records') return 'text-gray-900';
                return value > 0 ? 'text-yellow-600' : 'text-green-600';
              }}
            />
          {/if}

          {#if edaData.data_quality.unique_counts}
            <DashboardCard
              title="Unique Values Count"
              items={objectToArray(edaData.data_quality.unique_counts)}
              formatValue={formatNumber}
              valueColor="text-blue-600"
              maxHeight={true}
              itemClass="p-2"
            />
          {/if}

          {#if edaData.data_quality.missing_values}
            <DashboardCard
              title="Missing Values Summary"
              items={objectToArray(edaData.data_quality.missing_values)}
              formatValue={formatNumber}
              valueColor={(key, value) => (value > 0 ? 'text-yellow-600' : 'text-green-600')}
              maxHeight={true}
              itemClass="p-2"
            >
              {#if Object.values(edaData.data_quality.missing_values).every(count => count === 0)}
                <div class="text-center text-green-600 font-medium py-4 text-sm">
                  ✅ No missing values detected
                </div>
              {/if}
            </DashboardCard>
          {/if}
        </div>
      </div>
    {/if}
  {/if}
</div>
