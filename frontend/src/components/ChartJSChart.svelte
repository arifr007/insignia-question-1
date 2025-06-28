<script>
  import { onMount, onDestroy } from 'svelte';
  import LoadingSpinner from './ui/LoadingSpinner.svelte';

  export let data = null;
  export let type = 'line';
  export let options = null;

  // Function to decode binary data from Plotly format
  function decodeBdata(bdataStr, dtype = 'f8') {
    try {
      // Decode base64 string to binary
      const binaryString = atob(bdataStr);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Convert bytes to numbers based on dtype
      const buffer = bytes.buffer;
      let values = [];

      if (dtype === 'f8') { // 64-bit float (double)
        const floatArray = new Float64Array(buffer);
        values = Array.from(floatArray);
      } else if (dtype === 'f4') { // 32-bit float
        const floatArray = new Float32Array(buffer);
        values = Array.from(floatArray);
      } else if (dtype === 'i8') { // 64-bit int
        const intArray = new BigInt64Array(buffer);
        values = Array.from(intArray, x => Number(x));
      } else if (dtype === 'i4') { // 32-bit int
        const intArray = new Int32Array(buffer);
        values = Array.from(intArray);
      } else {
        // Default to 64-bit float
        const floatArray = new Float64Array(buffer);
        values = Array.from(floatArray);
      }

      return values;
    } catch (error) {
      console.error('Error decoding bdata:', error);
      return [];
    }
  }

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
      console.log('Chart type:', type);
      const chartData = convertPlotlyToChartJS(data);
      console.log('Converted chart data:', chartData);

      if (!chartData.datasets || chartData.datasets.length === 0) {
        console.error('No datasets found in converted data, creating fallback');
        
        // Create a fallback chart with placeholder data to show something
        const fallbackData = {
          labels: ['No Data'],
          datasets: [{
            label: 'No Data Available',
            data: [0],
            backgroundColor: 'rgba(239, 68, 68, 0.5)',
            borderColor: 'rgba(239, 68, 68, 1)',
            borderWidth: 1
          }]
        };
        
        chartInstance = new Chart(chartElement, {
          type: type === 'scatter' ? 'bar' : type, // Use bar for scatter fallback
          data: fallbackData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: { color: '#ffffff' }
              },
              title: {
                display: true,
                text: 'Chart data could not be loaded',
                color: '#ffffff'
              }
            },
            scales: type === 'pie' ? {} : {
              x: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255, 255, 255, 0.1)' }},
              y: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255, 255, 255, 0.1)' }}
            }
          }
        });
        return;
      }

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
    console.log('=== convertPlotlyToChartJS START ===');
    console.log('Input data:', plotlyData);
    console.log('Chart type:', type);

    // Handle different data structures
    if (!plotlyData) {
      console.warn('No plotly data provided');
      return { datasets: [] };
    }

    // If it's already Chart.js format
    if (plotlyData.datasets) {
      console.log('✓ Data is already in Chart.js format');
      return plotlyData;
    }

    // Handle API response structure: { status: "success", data: { chart_data: ..., raw_data: ..., summary: ... } }
    if (plotlyData.status === 'success' && plotlyData.data) {
      console.log('✓ Found API response structure, extracting data...');
      return convertPlotlyToChartJS(plotlyData.data);
    }

    // Handle nested chart_data structure
    if (plotlyData.chart_data) {
      console.log('✓ Found nested chart_data, recursing...');
      
      // Check for double nested chart_data (trend charts)
      if (plotlyData.chart_data.chart_data) {
        console.log('✓ Found double nested chart_data structure');
        
        // Always prefer raw_data if available for trend charts
        if (plotlyData.raw_data && plotlyData.chart_type) {
          console.log('✓ Using raw_data for trend chart with chart_type:', plotlyData.chart_type);
          return convertRawDataToChartJS(plotlyData.raw_data, plotlyData.chart_type);
        }
        
        // If we have raw_data available and chart_data has encoded values, use raw_data instead
        if (
          plotlyData.raw_data &&
          plotlyData.chart_data.chart_data.data &&
          plotlyData.chart_data.chart_data.data[0] &&
          ((plotlyData.chart_data.chart_data.data[0].y && plotlyData.chart_data.chart_data.data[0].y.bdata) ||
            (plotlyData.chart_data.chart_data.data[0].values && plotlyData.chart_data.chart_data.data[0].values.bdata) ||
            (plotlyData.chart_data.chart_data.data[0].z && plotlyData.chart_data.chart_data.data[0].z.bdata))
        ) {
          console.log('✓ Detected encoded values in double nested structure, using raw_data instead');
          return convertRawDataToChartJS(plotlyData.raw_data, plotlyData.chart_type);
        }
        
        console.log('→ Processing double nested chart_data');
        return convertPlotlyToChartJS(plotlyData.chart_data.chart_data);
      }
      
      // Always prefer raw_data if available and chart_type is present
      if (plotlyData.raw_data && plotlyData.chart_type) {
        console.log('✓ Using raw_data with chart_type:', plotlyData.chart_type);
        return convertRawDataToChartJS(plotlyData.raw_data, plotlyData.chart_type);
      }
      
      // If we have raw_data available and chart_data has encoded values, use raw_data instead
      if (
        plotlyData.raw_data &&
        plotlyData.chart_data.data &&
        plotlyData.chart_data.data[0] &&
        ((plotlyData.chart_data.data[0].y && plotlyData.chart_data.data[0].y.bdata) ||
          (plotlyData.chart_data.data[0].values && plotlyData.chart_data.data[0].values.bdata) ||
          (plotlyData.chart_data.data[0].z && plotlyData.chart_data.data[0].z.bdata))
      ) {
        console.log('✓ Detected encoded values, using raw_data instead');
        return convertRawDataToChartJS(plotlyData.raw_data, plotlyData.chart_type);
      }
      console.log('→ Processing single nested chart_data');
      return convertPlotlyToChartJS(plotlyData.chart_data);
    }

    // Handle special case: heatmap data without chart_data.data array
    if (plotlyData.chart_type === 'heatmap' && plotlyData.raw_data && 
        plotlyData.raw_data.values && plotlyData.raw_data.x_labels && plotlyData.raw_data.y_labels) {
      console.log('✓ Found heatmap data without plotly traces, using raw_data');
      return convertRawDataToChartJS(plotlyData.raw_data, plotlyData.chart_type);
    }

    // Handle Plotly format with data array
    if (plotlyData.data && Array.isArray(plotlyData.data)) {
      console.log('✓ Found plotly data array with', plotlyData.data.length, 'traces');
      return convertPlotlyTraces(plotlyData.data);
    }

    // Handle direct array of traces
    if (Array.isArray(plotlyData)) {
      console.log('✓ Data is direct array of traces with', plotlyData.length, 'traces');
      return convertPlotlyTraces(plotlyData);
    }

    // Handle single trace
    if (plotlyData.x || plotlyData.y || plotlyData.values) {
      console.log('✓ Data is single trace, wrapping in array');
      return convertPlotlyTraces([plotlyData]);
    }

    // Fallback
    console.warn('❌ Unknown data format:', plotlyData);
    console.log('=== convertPlotlyToChartJS END (FALLBACK) ===');
    return { datasets: [] };
  }

  function convertRawDataToChartJS(rawData, chartType) {
    console.log('=== convertRawDataToChartJS START ===');
    console.log('Raw data:', rawData);
    console.log('Chart type:', chartType);
    console.log('Component type prop:', type);

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
      console.log('✓ Processing line chart with raw data');
      // For trend charts: rawData = [{ month_year: "2023-09", amount: 125481449636.86 }, ...]
      if (!Array.isArray(rawData) || rawData.length === 0) {
        console.warn('No valid array data for line chart');
        return { datasets: [] };
      }

      const labels = rawData.map(item => item.month_year || item.x || item.label);
      const values = rawData.map(item => item.amount || item.y || item.value);
      
      console.log('Line chart labels:', labels);
      console.log('Line chart values:', values);

      const result = {
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
      
      console.log('✓ Line chart result:', result);
      console.log('=== convertRawDataToChartJS END (LINE) ===');
      return result;
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
      console.log('✓ Processing bar/heatmap chart with raw data');
      // Handle different heatmap/bar chart structures
      if (rawData.values && rawData.x_labels && rawData.y_labels) {
        console.log('✓ Processing heatmap raw data structure with matrix values');
        console.log('Values matrix:', rawData.values);
        console.log('X labels (months):', rawData.x_labels);
        console.log('Y labels (cost centers):', rawData.y_labels);

        // Create a more detailed bar chart representation of the heatmap
        // We'll create a dataset for each functional area (x_labels)
        const datasets = [];
        const numFunctionalAreas = rawData.x_labels.length;
        const numCostCenters = rawData.y_labels.length;

        // Validate data structure
        if (!Array.isArray(rawData.values) || rawData.values.length !== numCostCenters) {
          console.warn('Heatmap values array length does not match y_labels length');
          return { datasets: [] };
        }

        // For each functional area, create a dataset
        for (let functionalAreaIndex = 0; functionalAreaIndex < numFunctionalAreas; functionalAreaIndex++) {
          const functionalAreaData = [];
          
          // Extract values for this functional area across all cost centers
          for (let costCenterIndex = 0; costCenterIndex < numCostCenters; costCenterIndex++) {
            const rowValues = rawData.values[costCenterIndex];
            const value = Array.isArray(rowValues) && rowValues[functionalAreaIndex] ? rowValues[functionalAreaIndex] : 0;
            functionalAreaData.push(value);
          }

          datasets.push({
            label: rawData.x_labels[functionalAreaIndex],
            data: functionalAreaData,
            backgroundColor: colors[functionalAreaIndex % colors.length],
            borderColor: colors[functionalAreaIndex % colors.length].replace('0.8', '1'),
            borderWidth: 1
          });
        }

        const result = {
          labels: rawData.y_labels, // Cost centers as x-axis labels
          datasets: datasets
        };
        
        console.log('✓ Heatmap chart result:', result);
        console.log('=== convertRawDataToChartJS END (HEATMAP) ===');
        return result;
      } else if (rawData.cost_centers && rawData.functional_areas && rawData.amounts) {
        // Alternative heatmap structure: { cost_centers: [...], functional_areas: [...], amounts: [...] }
        console.log('Processing alternative heatmap structure');
        
        // Group by functional area and cost center
        const functionalAreaGroups = {};
        
        for (let i = 0; i < rawData.cost_centers.length; i++) {
          const costCenter = rawData.cost_centers[i];
          const functionalArea = rawData.functional_areas[i];
          const amount = rawData.amounts[i] || 0;
          
          if (!functionalAreaGroups[functionalArea]) {
            functionalAreaGroups[functionalArea] = {};
          }
          functionalAreaGroups[functionalArea][costCenter] = amount;
        }
        
        // Get unique cost centers for labels
        const allCostCenters = [...new Set(rawData.cost_centers)];
        const datasets = [];
        
        // Create dataset for each functional area
        Object.keys(functionalAreaGroups).forEach((functionalArea, index) => {
          const data = allCostCenters.map(costCenter => 
            functionalAreaGroups[functionalArea][costCenter] || 0
          );
          
          datasets.push({
            label: functionalArea,
            data: data,
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length].replace('0.8', '1'),
            borderWidth: 1
          });
        });

        return {
          labels: allCostCenters,
          datasets: datasets
        };
      } else if (Array.isArray(rawData)) {
        // Array structure for bar charts: [{ cost_center_name: "CC1", amount: 1000 }, ...]
        let labels, values;

        if (rawData[0] && rawData[0].cost_center_name) {
          labels = rawData.map(item => item.cost_center_name || item.name);
          values = rawData.map(item => item.amount || item.value);
        } else if (rawData[0] && rawData[0].functional_area_name) {
          labels = rawData.map(item => item.functional_area_name || item.name);
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
    } else if (chartType === 'scatter_plot' || type === 'scatter') {
      // Handle scatter plot raw data 
      if (Array.isArray(rawData) && rawData.length > 0) {
        const chartData = rawData.map(item => ({
          x: item.month_year || item.x || item.label,
          y: item.amount || item.y || item.value
        }));
        
        return {
          datasets: [
            {
              label: 'Data Points',
              data: chartData,
              backgroundColor: colors[0],
              borderColor: colors[0].replace('0.8', '1'),
              borderWidth: 2,
              pointRadius: 4
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

        let values = [];
        
        // Check if values are encoded
        if (trace.values && typeof trace.values === 'object' && trace.values.bdata) {
          console.log('Decoding binary values for pie chart:', trace.values);
          values = decodeBdata(trace.values.bdata, trace.values.dtype || 'f8');
        } else {
          values = trace.values || trace.y || [];
        }

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
      if (trace.mode === 'markers' || (trace.type === 'scatter' && type === 'scatter')) {
        console.log('Creating scatter plot dataset');
        let y = trace.y;
        if (y && typeof y === 'object' && y.bdata) {
          y = decodeBdata(y.bdata, y.dtype || 'f8');
        }
        const chartData = [];
        if (trace.x && y && Array.isArray(trace.x) && Array.isArray(y)) {
          for (let i = 0; i < Math.min(trace.x.length, y.length); i++) {
            chartData.push({
              x: trace.x[i],
              y: y[i]
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
      let y = trace.y;
      if (y && typeof y === 'object' && y.bdata) {
        console.log('Decoding binary y data for line/bar chart:', y);
        y = decodeBdata(y.bdata, y.dtype || 'f8');
        console.log('Decoded y values:', y);
      }
      let chartData = [];
      if (trace.x && y) {
        if (type === 'line' || (trace.mode && trace.mode.includes('lines'))) {
          // For line charts, create x-y point objects
          chartData = trace.x.map((x, i) => ({
            x: x,
            y: y[i]
          }));
          console.log('Created line chart data with', chartData.length, 'points');
        } else {
          // For bar charts, just use y values
          chartData = y;
          console.log('Created bar chart data with', chartData.length, 'values');
        }
      } else if (y) {
        chartData = y;
        console.log('Using y values directly with', chartData.length, 'values');
      } else if (trace.z) {
        // Handle heatmap data (special case for z matrix)
        let z = trace.z;
        if (z && typeof z === 'object' && z.bdata) {
          console.log('Decoding binary z data for heatmap:', z);
          z = decodeBdata(z.bdata, z.dtype || 'f8');
          console.log('Decoded z values:', z);
        }
        if (Array.isArray(z) && Array.isArray(z[0])) {
          // 2D array for heatmap - convert to grouped bar chart
          const numRows = z.length;
          const numCols = z[0].length;
          console.log(`Processing 2D heatmap data: ${numRows}x${numCols}`);
          // Use x and y labels if available, otherwise generate them
          const xLabels = trace.x || Array.from({length: numCols}, (_, i) => `Col ${i + 1}`);
          const yLabels = trace.y || Array.from({length: numRows}, (_, i) => `Row ${i + 1}`);
          // Create datasets for each column (functional area)
          const heatmapDatasets = [];
          for (let col = 0; col < numCols; col++) {
            const columnData = [];
            for (let row = 0; row < numRows; row++) {
              columnData.push(z[row][col] || 0);
            }
            heatmapDatasets.push({
              label: xLabels[col] || `Series ${col + 1}`,
              data: columnData,
              backgroundColor: colors[col % colors.length],
              borderColor: borderColors[col % colors.length],
              borderWidth: 1
            });
          }
          return {
            labels: yLabels,
            datasets: heatmapDatasets
          };
        } else {
          console.log('Using 1D z data as single dataset');
          chartData = Array.isArray(z) ? z : [z];
        }
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
        type: type === 'line' ? 'category' : (type === 'scatter' ? 'category' : 'category'),
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
          color: '#ffffff',
          callback: function(value) {
            // Format large numbers nicely
            if (Math.abs(value) >= 1000000000) {
              return (value / 1000000000).toFixed(1) + 'B';
            } else if (Math.abs(value) >= 1000000) {
              return (value / 1000000).toFixed(1) + 'M';
            } else if (Math.abs(value) >= 1000) {
              return (value / 1000).toFixed(1) + 'K';
            }
            return value;
          }
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
