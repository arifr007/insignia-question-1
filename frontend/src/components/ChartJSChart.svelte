<script>
  import { onMount, onDestroy } from 'svelte';
  import LoadingSpinner from './ui/LoadingSpinner.svelte';

  export let data = null;
  export let type = 'line';
  export let options = null;

  let chartElement;
  let chartInstance;
  let Chart;
  let chartLoading = true;
  let chartError = false;

  onMount(async () => {
    try {
      const chartModule = await import('chart.js/auto');
      Chart = chartModule.default;

      if (type === 'line' || type === 'bar') {
        await import('chartjs-adapter-date-fns');
      }

      chartLoading = false;

      if (data && chartElement) {
        createChart();
      }
    } catch (error) {
      console.error('Failed to load Chart.js:', error);
      chartError = true;
      chartLoading = false;
    }
  });

  onDestroy(() => {
    if (chartInstance) {
      chartInstance.destroy();
    }
  });

  $: if (data && chartElement && Chart && !chartLoading) {
    updateChart();
  }

  function createChart() {
    if (!data || !chartElement || !Chart) return;

    if (chartInstance) {
      chartInstance.destroy();
    }

    try {
      console.log('Creating chart with data:', data);
      const chartData = convertPlotlyToChartJS(data);
      console.log('Converted chart data:', chartData);

      const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#ffffff'
            }
          }
        },
        scales: getScalesConfig(),
        ...(options || {})
      };

      chartInstance = new Chart(chartElement, {
        type: type,
        data: chartData,
        options: chartOptions
      });
    } catch (error) {
      console.error('Error creating chart:', error);
      chartError = true;
    }
  }

  function updateChart() {
    if (!chartInstance) {
      createChart();
      return;
    }

    try {
      const chartData = convertPlotlyToChartJS(data);
      chartInstance.data = chartData;
      chartInstance.update();
    } catch (error) {
      console.error('Error updating chart:', error);
      createChart();
    }
  }

  function convertPlotlyToChartJS(plotlyData) {
    console.log('Converting Plotly data:', plotlyData, 'Chart type:', type);

    // Handle different data structures
    if (!plotlyData) {
      console.warn('No plotly data provided');
      return { datasets: [] };
    }

    // If it's already Chart.js format
    if (plotlyData.datasets) {
      console.log('Data is already in Chart.js format');
      return plotlyData;
    }

    // Handle API response structure: { status: "success", data: { chart_data: ..., raw_data: ..., summary: ... } }
    if (plotlyData.status === 'success' && plotlyData.data) {
      console.log('Found API response structure, extracting data...');
      return convertPlotlyToChartJS(plotlyData.data);
    }

    // Handle nested chart_data structure
    if (plotlyData.chart_data) {
      console.log('Found nested chart_data, recursing...');
      // If we have raw_data available and chart_data has encoded values, use raw_data instead
      if (
        plotlyData.raw_data &&
        plotlyData.chart_data.data &&
        plotlyData.chart_data.data[0] &&
        ((plotlyData.chart_data.data[0].y && plotlyData.chart_data.data[0].y.bdata) ||
          (plotlyData.chart_data.data[0].values && plotlyData.chart_data.data[0].values.bdata) ||
          (plotlyData.chart_data.data[0].z && plotlyData.chart_data.data[0].z.bdata))
      ) {
        console.log('Detected encoded values, using raw_data instead');
        return convertRawDataToChartJS(plotlyData.raw_data, plotlyData.chart_type);
      }
      return convertPlotlyToChartJS(plotlyData.chart_data);
    }

    // Handle Plotly format with data array
    if (plotlyData.data && Array.isArray(plotlyData.data)) {
      console.log('Found plotly data array with', plotlyData.data.length, 'traces');
      return convertPlotlyTraces(plotlyData.data);
    }

    // Handle direct array of traces
    if (Array.isArray(plotlyData)) {
      console.log('Data is direct array of traces with', plotlyData.length, 'traces');
      return convertPlotlyTraces(plotlyData);
    }

    // Handle single trace
    if (plotlyData.x || plotlyData.y || plotlyData.values) {
      console.log('Data is single trace, wrapping in array');
      return convertPlotlyTraces([plotlyData]);
    }

    // Fallback
    console.warn('Unknown data format:', plotlyData);
    return { datasets: [] };
  }

  function convertRawDataToChartJS(rawData, chartType) {
    console.log('Converting raw data:', rawData, 'for chart type:', chartType);

    if (!rawData) {
      console.warn('No valid raw data provided');
      return { datasets: [] };
    }

    const colors = [
      'rgba(59, 130, 246, 0.8)', // blue
      'rgba(16, 185, 129, 0.8)', // green
      'rgba(245, 158, 11, 0.8)', // yellow
      'rgba(239, 68, 68, 0.8)', // red
      'rgba(139, 92, 246, 0.8)', // purple
      'rgba(236, 72, 153, 0.8)', // pink
      'rgba(34, 197, 94, 0.8)', // emerald
      'rgba(251, 146, 60, 0.8)', // orange
      'rgba(168, 85, 247, 0.8)', // violet
      'rgba(14, 165, 233, 0.8)', // sky
      'rgba(132, 204, 22, 0.8)', // lime
      'rgba(244, 63, 94, 0.8)' // rose
    ];

    // Handle different raw data structures based on chart type
    if (chartType === 'line_chart' || type === 'line') {
      // For trend charts: rawData = [{ month_year: "2023-09", amount: 125481449636.86 }, ...]
      if (!Array.isArray(rawData) || rawData.length === 0) {
        console.warn('No valid array data for line chart');
        return { datasets: [] };
      }

      const labels = rawData.map(item => item.month_year || item.x || item.label);
      const values = rawData.map(item => item.amount || item.y || item.value);

      return {
        labels: labels,
        datasets: [
          {
            label: 'Monthly Expenses',
            data: values,
            backgroundColor: colors[0],
            borderColor: colors[0].replace('0.8', '1'),
            borderWidth: 2,
            fill: false,
            tension: 0.1
          }
        ]
      };
    } else if (chartType === 'pie_chart' || type === 'pie') {
      // For pie charts: rawData = [{ functional_area_name: "Area", amount: 1000, percentage: 10.5 }, ...]
      if (!Array.isArray(rawData) || rawData.length === 0) {
        console.warn('No valid array data for pie chart');
        return { datasets: [] };
      }

      const labels = rawData.map(item => item.functional_area_name || item.name || item.label);
      const values = rawData.map(item => item.amount || item.value);

      return {
        labels: labels,
        datasets: [
          {
            label: 'Distribution',
            data: values,
            backgroundColor: colors.slice(0, values.length),
            borderColor: colors.slice(0, values.length).map(color => color.replace('0.8', '1')),
            borderWidth: 1
          }
        ]
      };
    } else if (chartType === 'bar_chart' || chartType === 'heatmap' || type === 'bar') {
      // Handle different heatmap/bar chart structures
      if (rawData.values && rawData.x_labels && rawData.y_labels) {
        // Heatmap structure: { values: [[val1, val2], ...], x_labels: [...], y_labels: [...] }
        console.log('Processing heatmap raw data structure');

        // For Chart.js, we'll represent the heatmap as a bar chart showing totals for each cost center
        const labels = rawData.y_labels;
        const values = rawData.values.map(row => row.reduce((sum, val) => sum + val, 0)); // Sum values for each cost center

        return {
          labels: labels,
          datasets: [
            {
              label: 'Total Amount',
              data: values,
              backgroundColor: colors[0],
              borderColor: colors[0].replace('0.8', '1'),
              borderWidth: 1
            }
          ]
        };
      } else if (Array.isArray(rawData)) {
        // Array structure for bar charts: [{ cost_center_name: "CC1", amount: 1000 }, ...]
        let labels, values;

        if (rawData[0] && rawData[0].cost_center_name) {
          labels = rawData.map(item => item.cost_center_name || item.name);
          values = rawData.map(item => item.amount || item.value);
        } else {
          // Generic bar data
          labels = rawData.map((item, index) => item.label || item.name || `Item ${index + 1}`);
          values = rawData.map(item => item.amount || item.value || item.y);
        }

        return {
          labels: labels,
          datasets: [
            {
              label: 'Values',
              data: values,
              backgroundColor: colors[0],
              borderColor: colors[0].replace('0.8', '1'),
              borderWidth: 1
            }
          ]
        };
      }
    }

    // Fallback
    console.warn('Unknown raw data format for chart type:', chartType);
    return { datasets: [] };
  }

  function convertPlotlyTraces(traces) {
    console.log('Converting traces:', traces, 'for chart type:', type);

    if (!traces || !Array.isArray(traces) || traces.length === 0) {
      console.warn('No valid traces provided');
      return { datasets: [] };
    }

    const colors = [
      'rgba(59, 130, 246, 0.8)', // blue
      'rgba(16, 185, 129, 0.8)', // green
      'rgba(245, 158, 11, 0.8)', // yellow
      'rgba(239, 68, 68, 0.8)', // red
      'rgba(139, 92, 246, 0.8)', // purple
      'rgba(236, 72, 153, 0.8)', // pink
      'rgba(34, 197, 94, 0.8)', // emerald
      'rgba(251, 146, 60, 0.8)' // orange
    ];

    const borderColors = colors.map(color => color.replace('0.8', '1'));

    const datasets = traces.map((trace, index) => {
      console.log(`Processing trace ${index}:`, trace);
      const colorIndex = index % colors.length;

      // Handle pie/doughnut charts - look for labels and values
      if (
        (trace.labels && trace.values) ||
        trace.type === 'pie' ||
        type === 'pie' ||
        type === 'doughnut'
      ) {
        console.log('Creating pie chart dataset');

        // Check if values are encoded
        if (trace.values && typeof trace.values === 'object' && trace.values.bdata) {
          console.warn('Pie chart values are encoded, cannot decode. Returning empty dataset.');
          return {
            label: trace.name || `Dataset ${index + 1}`,
            data: [],
            backgroundColor: [],
            borderColor: [],
            borderWidth: 1
          };
        }

        const values = trace.values || trace.y || [];
        const _labels = trace.labels || trace.x || [];

        return {
          label: trace.name || `Dataset ${index + 1}`,
          data: values,
          backgroundColor: colors.slice(0, values.length),
          borderColor: borderColors.slice(0, values.length),
          borderWidth: 1
        };
      }

      // Handle scatter plots
      if (trace.mode === 'markers' || trace.type === 'scatter' || type === 'scatter') {
        console.log('Creating scatter plot dataset');
        const chartData = [];
        if (trace.x && trace.y && Array.isArray(trace.x) && Array.isArray(trace.y)) {
          for (let i = 0; i < Math.min(trace.x.length, trace.y.length); i++) {
            chartData.push({
              x: trace.x[i],
              y: trace.y[i]
            });
          }
        }
        console.log(`Scatter dataset ${index} created with ${chartData.length} points`);

        // Use specific colors for anomaly detection
        let backgroundColor, borderColor;
        if (trace.name && trace.name.includes('Anomalies')) {
          backgroundColor = 'rgba(239, 68, 68, 0.8)'; // red for anomalies
          borderColor = 'rgba(239, 68, 68, 1)';
        } else if (trace.name && trace.name.includes('Normal')) {
          backgroundColor = 'rgba(59, 130, 246, 0.8)'; // blue for normal
          borderColor = 'rgba(59, 130, 246, 1)';
        } else {
          backgroundColor = colors[colorIndex];
          borderColor = borderColors[colorIndex];
        }

        return {
          label: trace.name || `Dataset ${index + 1}`,
          data: chartData,
          backgroundColor: backgroundColor,
          borderColor: borderColor,
          borderWidth: 2,
          pointRadius: trace.name && trace.name.includes('Anomalies') ? 6 : 4,
          pointStyle: trace.name && trace.name.includes('Anomalies') ? 'cross' : 'circle'
        };
      }

      // Handle line/bar charts
      console.log('Creating line/bar chart dataset');
      let chartData = [];

      if (trace.x && trace.y) {
        // Check if y values are encoded (binary data)
        if (trace.y && typeof trace.y === 'object' && trace.y.bdata) {
          console.warn(
            'Y values are encoded, cannot decode binary data. Chart may not display correctly.'
          );
          chartData = []; // Empty data as we can't decode
        } else if (type === 'line') {
          // For line charts, create x-y point objects
          chartData = trace.x.map((x, i) => ({
            x: x,
            y: trace.y[i]
          }));
        } else {
          // For bar charts, just use y values
          chartData = trace.y;
        }
      } else if (trace.y && !trace.y.bdata) {
        chartData = trace.y;
      } else if (trace.z) {
        // Handle heatmap data (flatten z matrix)
        chartData = Array.isArray(trace.z[0]) ? trace.z.flat() : trace.z;
      }

      return {
        label: trace.name || `Dataset ${index + 1}`,
        data: chartData,
        backgroundColor: colors[colorIndex],
        borderColor: borderColors[colorIndex],
        borderWidth: 2,
        fill: type === 'line' ? false : true,
        tension: type === 'line' ? 0.1 : 0
      };
    });

    // Handle labels for categorical data or x-axis
    let labels = [];
    const firstTrace = traces[0];

    if (type === 'pie' || type === 'doughnut') {
      // For pie charts, use labels from the trace
      labels = firstTrace?.labels || [];
    } else if (firstTrace?.x) {
      // For other charts, use x values as labels
      labels = firstTrace.x;
    } else if (type === 'bar' && firstTrace?.y) {
      // Generate numeric labels for bar charts if no x labels
      labels = firstTrace.y.map((_, i) => `Item ${i + 1}`);
    }

    console.log('Final chart data:', { labels, datasets });

    return {
      labels: labels,
      datasets: datasets
    };
  }

  function getScalesConfig() {
    if (type === 'pie' || type === 'doughnut') {
      return {};
    }

    const baseConfig = {
      x: {
        type: type === 'scatter' ? 'category' : 'linear',
        ticks: {
          color: '#ffffff'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      y: {
        type: 'linear',
        ticks: {
          color: '#ffffff'
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    };

    return baseConfig;
  }
</script>

<div class="w-full min-h-96 bg-white/5 border border-white/10 rounded-xl p-4">
  {#if chartLoading}
    <div class="flex items-center justify-center h-96">
      <LoadingSpinner size="lg" />
      <span class="ml-3 text-gray-300">Loading chart engine...</span>
    </div>
  {:else if chartError}
    <div class="flex items-center justify-center h-96 text-red-400">
      <div class="text-center">
        <div class="text-4xl mb-2">❌</div>
        <p>Failed to load chart engine</p>
        <p class="text-sm mt-2">Check console for details</p>
      </div>
    </div>
  {:else if data}
    <canvas bind:this={chartElement} class="w-full h-96"></canvas>
  {:else}
    <div class="flex items-center justify-center h-96 text-gray-400 italic">
      No chart data available
    </div>
  {/if}
</div>
