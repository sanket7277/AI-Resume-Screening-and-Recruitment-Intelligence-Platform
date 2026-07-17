/*
   RecruitIQ - Analytics Plotly Integration
   Plotly chart creation helpers with dark-mode awareness.
*/

function getPlotlyLayout(title) {
    var isDark = document.body.getAttribute('data-theme') !== 'light';
    return {
        title: { text: title, font: { family: 'Inter', color: isDark ? '#e2e8f0' : '#1e293b' } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Inter', color: isDark ? '#94a3b8' : '#475569' },
        margin: { t: 50, r: 20, b: 50, l: 50 },
        xaxis: { gridcolor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' },
        yaxis: { gridcolor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }
    };
}

function createPlotlyBar(divId, xData, yData, title) {
    var trace = { x: xData, y: yData, type: 'bar', marker: { color: '#4f46e5', line: { width: 0 } } };
    Plotly.newPlot(divId, [trace], getPlotlyLayout(title), { responsive: true, displayModeBar: false });
}

function createPlotlyPie(divId, labels, values, title) {
    var colors = ['#4f46e5', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#0ea5e9'];
    var trace = { labels: labels, values: values, type: 'pie', marker: { colors: colors }, hole: 0.4, textinfo: 'label+percent' };
    Plotly.newPlot(divId, [trace], getPlotlyLayout(title), { responsive: true, displayModeBar: false });
}

function createPlotlyHeatmap(divId, zData, xLabels, yLabels, title) {
    var trace = { z: zData, x: xLabels, y: yLabels, type: 'heatmap', colorscale: 'Viridis' };
    Plotly.newPlot(divId, [trace], getPlotlyLayout(title), { responsive: true, displayModeBar: false });
}

function createPlotlyScatter(divId, xData, yData, textLabels, title) {
    var trace = {
        x: xData, y: yData, text: textLabels, mode: 'markers',
        marker: { size: 10, color: '#4f46e5', opacity: 0.7 }
    };
    Plotly.newPlot(divId, [trace], getPlotlyLayout(title), { responsive: true, displayModeBar: false });
}
