/*
   RecruitIQ - Live Search Module
   Debounced candidate search with result highlighting and filters.
*/

document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.getElementById('candidate-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            performSearch(searchInput.value);
        }, 300));
    }
});

function performSearch(query) {
    if (!query || query.length < 2) {
        var resultsEl = document.getElementById('search-results');
        if (resultsEl) resultsEl.innerHTML = '<p class="text-muted">Type at least 2 characters to search.</p>';
        return;
    }
    
    ajaxRequest('/api/v1/search?q=' + encodeURIComponent(query), 'GET', null, function(err, response) {
        if (err || !response || !response.data) {
            showToast('Search failed. Please try again.', 'danger');
            return;
        }
        renderSearchResults(response.data, query);
    });
}

function renderSearchResults(results, query) {
    var container = document.getElementById('search-results');
    if (!container) return;
    
    if (results.length === 0) {
        container.innerHTML = '<div class="text-center py-4"><i class="bi bi-search text-muted" style="font-size:2rem"></i><p class="mt-2 text-muted">No candidates found matching "' + query + '"</p></div>';
        return;
    }
    
    var html = '<div class="list-group">';
    results.forEach(function(item) {
        var name = highlightText(item.name || 'Unknown', query);
        var skills = (item.skills || []).slice(0, 5).join(', ');
        html += '<a href="/resume/view/' + item.id + '" class="list-group-item list-group-item-action glass-card mb-2">' +
            '<div class="d-flex justify-content-between align-items-center">' +
            '<div><h6 class="mb-1">' + name + '</h6>' +
            '<small class="text-muted">' + highlightText(skills, query) + '</small></div>' +
            '<span class="badge bg-primary">' + (item.ats_score || 'N/A') + '</span></div></a>';
    });
    html += '</div>';
    container.innerHTML = html;
}

function highlightText(text, query) {
    if (!text || !query) return text || '';
    var regex = new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function clearSearch() {
    var input = document.getElementById('candidate-search');
    if (input) input.value = '';
    var results = document.getElementById('search-results');
    if (results) results.innerHTML = '';
}

function toggleFilterPanel() {
    var panel = document.getElementById('filter-panel');
    if (panel) panel.classList.toggle('d-none');
}
