/*
   RecruitIQ - Resume Upload & Preview
   Drag-and-drop uploads, progress bars, and skills rendering.
*/

document.addEventListener('DOMContentLoaded', function() {
    initDropzone();
});

function initDropzone() {
    var dropzone = document.getElementById('resume-dropzone');
    var fileInput = document.getElementById('resume-file-input');
    if (!dropzone || !fileInput) return;
    
    // Click to browse
    dropzone.addEventListener('click', function() { fileInput.click(); });
    
    // Drag events
    dropzone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    dropzone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropzone.classList.remove('dragover');
    });
    dropzone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        var files = e.dataTransfer.files;
        if (files.length > 0) handleFile(files[0], fileInput);
    });
    
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) handleFile(fileInput.files[0], fileInput);
    });
}

function handleFile(file, fileInput) {
    var allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    var maxSize = 16 * 1024 * 1024; // 16MB
    
    if (allowed.indexOf(file.type) === -1 && !file.name.match(/\.(pdf|docx|txt)$/i)) {
        showToast('Invalid file type. Please upload PDF, DOCX, or TXT.', 'danger');
        return;
    }
    if (file.size > maxSize) {
        showToast('File exceeds 16MB limit.', 'danger');
        return;
    }
    
    // Show file info
    var infoEl = document.getElementById('file-info');
    if (infoEl) {
        var ext = file.name.split('.').pop().toUpperCase();
        infoEl.innerHTML = '<i class="bi bi-file-earmark-text me-2"></i>' +
            '<strong>' + file.name + '</strong> (' + formatFileSize(file.size) + ') ' +
            '<span class="badge bg-primary">' + ext + '</span>';
        infoEl.style.display = 'block';
    }
    
    // Show upload button
    var uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) uploadBtn.style.display = 'inline-block';
    
    simulateProgress();
}

function simulateProgress() {
    var bar = document.getElementById('upload-progress-bar');
    var container = document.getElementById('upload-progress');
    if (!bar || !container) return;
    
    container.style.display = 'block';
    var width = 0;
    var interval = setInterval(function() {
        width += Math.random() * 15;
        if (width >= 100) {
            width = 100;
            clearInterval(interval);
        }
        bar.style.width = width + '%';
        bar.setAttribute('aria-valuenow', Math.floor(width));
    }, 200);
}

function renderSkillTags(containerId, skills, type) {
    var container = document.getElementById(containerId);
    if (!container || !skills) return;
    
    container.innerHTML = '';
    skills.forEach(function(skill) {
        var chip = document.createElement('span');
        chip.className = 'skill-chip ' + (type || '');
        chip.textContent = skill;
        container.appendChild(chip);
    });
}

function confirmDeleteResume(resumeId) {
    confirmAction('Are you sure you want to delete this resume?', function() {
        window.location.href = '/resume/delete/' + resumeId;
    });
}
