/**
 * Chart Utilities - Reusable chart creation functions
 */

class ChartUtils {
    /**
     * Create bar chart
     */
    static createBarChart(elementId, xData, yData, title, xLabel = '', yLabel = '') {
        const trace = {
            x: xData,
            y: yData,
            type: 'bar',
            marker: { color: '#ff6b35' }
        };

        const layout = {
            title: title,
            xaxis: { title: xLabel },
            yaxis: { title: yLabel },
            responsive: true,
            margin: { l: 50, r: 50, t: 50, b: 50 }
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    /**
     * Create line chart
     */
    static createLineChart(elementId, xData, yData, title, xLabel = '', yLabel = '') {
        const trace = {
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines+markers',
            marker: { color: '#ff6b35', size: 8 },
            line: { color: '#ff6b35', width: 2 }
        };

        const layout = {
            title: title,
            xaxis: { title: xLabel },
            yaxis: { title: yLabel },
            responsive: true,
            margin: { l: 50, r: 50, t: 50, b: 50 }
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    /**
     * Create pie chart
     */
    static createPieChart(elementId, labels, values, title) {
        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            marker: { colors: ['#ff6b35', '#ffc107', '#17a2b8', '#28a745', '#6c757d'] }
        };

        const layout = {
            title: title,
            responsive: true
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    /**
     * Create comparison bar chart (multiple series)
     */
    static createComparisonChart(elementId, categories, series, title, yLabel = '') {
        const traces = series.map((s, i) => ({
            x: categories,
            y: s.values,
            name: s.name,
            type: 'bar',
            marker: { color: ['#ff6b35', '#007bff', '#28a745', '#ffc107'][i % 4] }
        }));

        const layout = {
            title: title,
            yaxis: { title: yLabel },
            barmode: 'group',
            responsive: true
        };

        Plotly.newPlot(elementId, traces, layout);
    }

    /**
     * Create heatmap
     */
    static createHeatmap(elementId, x, y, z, title) {
        const trace = {
            x: x,
            y: y,
            z: z,
            type: 'heatmap',
            colorscale: 'Viridis'
        };

        const layout = {
            title: title,
            responsive: true
        };

        Plotly.newPlot(elementId, [trace], layout);
    }

    /**
     * Format number with comma separator
     */
    static formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    /**
     * Format percentage
     */
    static formatPercentage(value, decimals = 2) {
        return (value * 100).toFixed(decimals) + '%';
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartUtils;
}
