/*
   RecruitIQ - Global JavaScript
   Handles theme toggling, flash messages, AJAX helpers, and shared utilities.
*/

document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initFlashMessages();
    initTooltips();
    initPageAnimations();
});

/* --- Theme Toggle (Dark / Light) --- */
function initTheme() {
    const saved = localStorage.getItem('recruitiq-theme') || 'dark';
    document.body.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
}

function toggleTheme() {
    const current = document.body.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', next);
    localStorage.setItem('recruitiq-theme', next);
    updateThemeIcon(next);

    // Notify chart modules to refresh palette if they exist
    if (typeof updateAllChartThemes === 'function') {
        updateAllChartThemes(next);
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
}

/* --- Flash Messages Auto-dismiss --- */
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        }, 5000);
    });
}

/* --- Bootstrap Tooltips --- */
function initTooltips() {
    var tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(function(el) {
        new bootstrap.Tooltip(el);
    });
}

/* --- Page Fade-In Animations --- */
function initPageAnimations() {
    var content = document.querySelector('.main-content');
    if (content) {
        content.classList.add('fade-in');
    }
}

/* --- Sidebar Toggle (mobile) --- */
function toggleSidebar() {
    var sidebar = document.getElementById('app-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

/* --- AJAX Helper with CSRF token --- */
function ajaxRequest(url, method, data, callback) {
    var csrfToken = document.querySelector('meta[name="csrf-token"]');
    var headers = { 'Content-Type': 'application/json' };
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken.getAttribute('content');
    }
    
    var options = { method: method, headers: headers };
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    fetch(url, options)
        .then(function(response) { return response.json(); })
        .then(function(result) { if (callback) callback(null, result); })
        .catch(function(err) { if (callback) callback(err, null); });
}

/* --- Utility Functions --- */
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    var units = ['B', 'KB', 'MB', 'GB'];
    var i = 0;
    while (bytes >= 1024 && i < units.length - 1) {
        bytes /= 1024;
        i++;
    }
    return bytes.toFixed(1) + ' ' + units[i];
}

function debounce(func, delay) {
    var timer;
    return function() {
        var context = this, args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function() { func.apply(context, args); }, delay);
    };
}

function showToast(message, type) {
    type = type || 'info';
    var container = document.querySelector('.alert-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'alert-container';
        document.body.appendChild(container);
    }
    
    var alert = document.createElement('div');
    alert.className = 'alert alert-' + type + ' alert-dismissible alert-custom fade show';
    alert.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    container.appendChild(alert);
    
    setTimeout(function() {
        alert.style.opacity = '0';
        setTimeout(function() { alert.remove(); }, 500);
    }, 4000);
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    });
}
