/*
   RecruitIQ - ATS Matching Visualization
   Animated SVG gauge, skill comparison rendering, and ranking table helpers.
*/

function renderATSGauge(containerId, score) {
    var container = document.getElementById(containerId);
    if (!container) return;
    
    var radius = 50;
    var circumference = 2 * Math.PI * radius;
    var offset = circumference - (score / 100) * circumference;
    
    // Pick color based on score band
    var color = '#ef4444';
    if (score >= 75) color = '#10b981';
    else if (score >= 50) color = '#f59e0b';
    else if (score >= 30) color = '#f97316';
    
    container.innerHTML =
        '<div class="gauge-wrapper">' +
        '<svg class="gauge-svg" width="120" height="120">' +
        '<circle class="gauge-bg" cx="60" cy="60" r="' + radius + '"></circle>' +
        '<circle class="gauge-fill" cx="60" cy="60" r="' + radius + '" ' +
        'stroke="' + color + '" ' +
        'stroke-dasharray="' + circumference + '" ' +
        'stroke-dashoffset="' + circumference + '" ' +
        'style="transition: stroke-dashoffset 1s ease"></circle>' +
        '</svg>' +
        '<span class="gauge-text" style="color:' + color + '">' + Math.round(score) + '%</span>' +
        '</div>';
    
    // Animate after render
    setTimeout(function() {
        var fill = container.querySelector('.gauge-fill');
        if (fill) fill.style.strokeDashoffset = offset;
    }, 100);
}

function renderSkillComparison(containerId, matched, missing, extra) {
    var container = document.getElementById(containerId);
    if (!container) return;
    
    var html = '';
    
    if (matched && matched.length > 0) {
        html += '<div class="mb-3"><h6 class="text-success"><i class="bi bi-check-circle me-1"></i>Matched Skills</h6>';
        html += '<div class="skills-badge-container">';
        matched.forEach(function(s) { html += '<span class="skill-chip matched">' + s + '</span>'; });
        html += '</div></div>';
    }
    
    if (missing && missing.length > 0) {
        html += '<div class="mb-3"><h6 class="text-danger"><i class="bi bi-x-circle me-1"></i>Missing Skills</h6>';
        html += '<div class="skills-badge-container">';
        missing.forEach(function(s) { html += '<span class="skill-chip missing">' + s + '</span>'; });
        html += '</div></div>';
    }
    
    if (extra && extra.length > 0) {
        html += '<div class="mb-3"><h6 class="text-info"><i class="bi bi-plus-circle me-1"></i>Extra Skills</h6>';
        html += '<div class="skills-badge-container">';
        extra.forEach(function(s) { html += '<span class="skill-chip">' + s + '</span>'; });
        html += '</div></div>';
    }
    
    container.innerHTML = html;
}

function renderScoreBreakdown(canvasId, scores) {
    if (!scores) return;
    var labels = ['Skills', 'Experience', 'Education', 'Semantic', 'Keywords'];
    var data = [
        scores.skill_match_pct || 0,
        scores.experience_match || 0,
        scores.education_match || 0,
        (scores.semantic_similarity || 0) * 100,
        scores.keyword_coverage || 0
    ];
    createRadarChart(canvasId, labels, data, { label: 'Match Score' });
}

function sortRankingTable(columnIndex) {
    var table = document.getElementById('ranking-table');
    if (!table) return;
    
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort(function(a, b) {
        var aVal = a.cells[columnIndex].textContent.trim();
        var bVal = b.cells[columnIndex].textContent.trim();
        var aNum = parseFloat(aVal);
        var bNum = parseFloat(bVal);
        if (!isNaN(aNum) && !isNaN(bNum)) return bNum - aNum;
        return aVal.localeCompare(bVal);
    });
    
    rows.forEach(function(row) { tbody.appendChild(row); });
}
