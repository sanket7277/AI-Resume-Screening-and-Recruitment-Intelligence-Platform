/*
   RecruitIQ - Dashboard Charts & Metrics
   Chart.js wrapper functions and animated counters for KPI cards.
*/

// Theme-aware color palettes
function getChartColors() {
    var isDark = document.body.getAttribute('data-theme') !== 'light';
    return {
        primary: '#4f46e5',
        secondary: '#7c3aed',
        accent: '#06b6d4',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        text: isDark ? '#e2e8f0' : '#1e293b',
        grid: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
        palette: ['#4f46e5', '#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#0ea5e9']
    };
}

// Set Chart.js global defaults
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

var activeCharts = {};

function createBarChart(canvasId, labels, data, customOpts) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    var colors = getChartColors();
    
    if (activeCharts[canvasId]) activeCharts[canvasId].destroy();
    
    activeCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: (customOpts && customOpts.label) || 'Count',
                data: data,
                backgroundColor: colors.palette.slice(0, data.length),
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: colors.text }, grid: { display: false } },
                y: { ticks: { color: colors.text }, grid: { color: colors.grid } }
            }
        }
    });
    return activeCharts[canvasId];
}

function createPieChart(canvasId, labels, data, customOpts) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    var colors = getChartColors();
    
    if (activeCharts[canvasId]) activeCharts[canvasId].destroy();
    
    activeCharts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.palette.slice(0, data.length),
                borderWidth: 0
            }]
        },
        options: {
            plugins: {
                legend: { position: 'bottom', labels: { color: colors.text, padding: 15 } }
            }
        }
    });
    return activeCharts[canvasId];
}

function createDoughnutChart(canvasId, labels, data, customOpts) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    var colors = getChartColors();
    
    if (activeCharts[canvasId]) activeCharts[canvasId].destroy();
    
    activeCharts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.palette.slice(0, data.length),
                borderWidth: 0,
                cutout: '65%'
            }]
        },
        options: {
            plugins: {
                legend: { position: 'bottom', labels: { color: colors.text, padding: 15 } }
            }
        }
    });
    return activeCharts[canvasId];
}

function createLineChart(canvasId, labels, datasets, customOpts) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    var colors = getChartColors();
    
    if (activeCharts[canvasId]) activeCharts[canvasId].destroy();
    
    var formattedDatasets = datasets.map(function(ds, idx) {
        return {
            label: ds.label || 'Series ' + (idx + 1),
            data: ds.data,
            borderColor: colors.palette[idx % colors.palette.length],
            backgroundColor: colors.palette[idx % colors.palette.length] + '20',
            fill: true,
            tension: 0.4,
            pointRadius: 3
        };
    });
    
    activeCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: formattedDatasets },
        options: {
            plugins: { legend: { labels: { color: colors.text } } },
            scales: {
                x: { ticks: { color: colors.text }, grid: { display: false } },
                y: { ticks: { color: colors.text }, grid: { color: colors.grid } }
            }
        }
    });
    return activeCharts[canvasId];
}

function createRadarChart(canvasId, labels, data, customOpts) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    var colors = getChartColors();
    
    if (activeCharts[canvasId]) activeCharts[canvasId].destroy();
    
    activeCharts[canvasId] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: (customOpts && customOpts.label) || 'Score',
                data: data,
                backgroundColor: colors.primary + '30',
                borderColor: colors.primary,
                pointBackgroundColor: colors.primary,
                borderWidth: 2
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: { color: colors.grid },
                    grid: { color: colors.grid },
                    pointLabels: { color: colors.text },
                    ticks: { color: colors.text, backdropColor: 'transparent' }
                }
            },
            plugins: { legend: { labels: { color: colors.text } } }
        }
    });
    return activeCharts[canvasId];
}

/* Animated counter for stat cards */
function animateCounter(elementId, targetValue, duration) {
    duration = duration || 1500;
    var element = document.getElementById(elementId);
    if (!element) return;
    
    var start = 0;
    var startTime = null;
    
    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        var current = Math.floor(eased * targetValue);
        element.textContent = formatNumber(current);
        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.textContent = formatNumber(targetValue);
        }
    }
    requestAnimationFrame(step);
}

function updateAllChartThemes(theme) {
    Object.keys(activeCharts).forEach(function(key) {
        if (activeCharts[key]) {
            activeCharts[key].destroy();
        }
    });
    // Charts will be recreated when dashboard reloads or re-renders
}
