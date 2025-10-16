// Main JavaScript file for Postasy

// Initialize Bootstrap components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Initialize poster card animations
    initializePosterCards();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize image preview functionality
    initializeImagePreviews();
});

// Poster card hover effects and interactions
function initializePosterCards() {
    const posterCards = document.querySelectorAll('.poster-card');
    
    posterCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
        });
        
        // Add click to view functionality
        const viewBtn = card.querySelector('a[href*="/poster/"]');
        if (viewBtn && !card.querySelector('.poster-overlay')) {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function(e) {
                if (e.target === this || e.target.classList.contains('poster-thumbnail')) {
                    window.location.href = viewBtn.href;
                }
            });
        }
    });
}

// Form enhancement functions
function initializeFormEnhancements() {
    // Character counters for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            addCharacterCounter(textarea, maxLength);
        }
    });
    
    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Focus first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            form.classList.add('was-validated');
        });
    });
    
    // File input enhancements
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.parentNode.querySelector('.form-label');
            if (fileName && label) {
                label.textContent = `${label.textContent.split(' (')[0]} (${fileName})`;
            }
        });
    });
}

// Add character counter to textarea
function addCharacterCounter(textarea, maxLength) {
    const counter = document.createElement('div');
    counter.className = 'character-counter text-muted small text-end mt-1';
    counter.innerHTML = `<span class="current">0</span>/${maxLength} characters`;
    
    textarea.parentNode.appendChild(counter);
    
    const currentSpan = counter.querySelector('.current');
    
    function updateCounter() {
        const currentLength = textarea.value.length;
        currentSpan.textContent = currentLength;
        
        if (currentLength > maxLength * 0.9) {
            counter.classList.add('text-warning');
            counter.classList.remove('text-muted');
        } else if (currentLength > maxLength) {
            counter.classList.add('text-danger');
            counter.classList.remove('text-warning', 'text-muted');
        } else {
            counter.classList.add('text-muted');
            counter.classList.remove('text-warning', 'text-danger');
        }
    }
    
    textarea.addEventListener('input', updateCounter);
    textarea.addEventListener('paste', () => setTimeout(updateCounter, 10));
    updateCounter(); // Initial count
}

// Image preview functionality
function initializeImagePreviews() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(input, e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Show image preview
function showImagePreview(input, src) {
    let preview = input.parentNode.querySelector('.image-preview');
    
    if (!preview) {
        preview = document.createElement('div');
        preview.className = 'image-preview mt-2';
        input.parentNode.appendChild(preview);
    }
    
    preview.innerHTML = `
        <img src="${src}" alt="Preview" class="img-thumbnail" style="max-height: 150px;">
        <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="removeImagePreview(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
}

// Remove image preview
function removeImagePreview(button) {
    const preview = button.parentNode;
    const input = preview.parentNode.querySelector('input[type="file"]');
    input.value = '';
    preview.remove();
}

// Utility functions
const Utils = {
    // Debounce function for search inputs
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Show loading state
    showLoading: function(element, text = 'Loading...') {
        const originalHTML = element.innerHTML;
        element.dataset.originalHTML = originalHTML;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
        element.disabled = true;
    },
    
    // Hide loading state
    hideLoading: function(element) {
        if (element.dataset.originalHTML) {
            element.innerHTML = element.dataset.originalHTML;
            delete element.dataset.originalHTML;
        }
        element.disabled = false;
    },
    
    // Show toast notification
    showToast: function(message, type = 'success', duration = 5000) {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const iconClass = type === 'success' ? 'fa-check-circle text-success' : 'fa-exclamation-circle text-danger';
        const title = type === 'success' ? 'Success' : 'Error';
        
        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas ${iconClass} me-2"></i>
                    <strong class="me-auto">${title}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', toastHTML);
        
        // Show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();
        
        // Remove from DOM after hiding
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard!');
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    },
    
    // Fallback copy method for older browsers
    fallbackCopyToClipboard: function(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                this.showToast('Copied to clipboard!');
            } else {
                this.showToast('Failed to copy text', 'error');
            }
        } catch (err) {
            this.showToast('Failed to copy text', 'error');
        }
        
        document.body.removeChild(textArea);
    }
};

// Search functionality for gallery pages
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const filterSelect = document.getElementById('filterSelect');
    const sortSelect = document.getElementById('sortSelect');
    
    if (searchInput || filterSelect || sortSelect) {
        const debouncedSearch = Utils.debounce(performSearch, 300);
        
        if (searchInput) searchInput.addEventListener('input', debouncedSearch);
        if (filterSelect) filterSelect.addEventListener('change', performSearch);
        if (sortSelect) sortSelect.addEventListener('change', performSearch);
    }
}

// Perform search and filtering
function performSearch() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const filterValue = document.getElementById('filterSelect')?.value || 'all';
    const sortValue = document.getElementById('sortSelect')?.value || 'newest';
    
    const items = document.querySelectorAll('.poster-item');
    let visibleItems = [];
    
    items.forEach(item => {
        const title = item.dataset.title || '';
        const isPublic = item.dataset.public === 'true';
        const date = new Date(item.dataset.date || 0);
        
        // Apply search filter
        const matchesSearch = title.includes(searchTerm);
        
        // Apply visibility filter
        let matchesFilter = true;
        if (filterValue === 'public') matchesFilter = isPublic;
        if (filterValue === 'private') matchesFilter = !isPublic;
        
        if (matchesSearch && matchesFilter) {
            visibleItems.push({ element: item, date: date, title: title });
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
    
    // Sort visible items
    visibleItems.sort((a, b) => {
        switch (sortValue) {
            case 'oldest':
                return a.date - b.date;
            case 'title':
                return a.title.localeCompare(b.title);
            case 'newest':
            default:
                return b.date - a.date;
        }
    });
    
    // Reorder DOM elements
    const container = document.getElementById('posterGrid');
    if (container) {
        visibleItems.forEach(item => {
            container.appendChild(item.element);
        });
    }
    
    // Show/hide empty state
    const emptyState = document.getElementById('emptyState');
    if (emptyState) {
        emptyState.style.display = visibleItems.length === 0 ? 'block' : 'none';
    }
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', initializeSearch);

// Poster generation form enhancements
document.addEventListener('DOMContentLoaded', function() {
    const posterForm = document.getElementById('posterForm');
    if (posterForm) {
        posterForm.addEventListener('submit', function(e) {
            const submitBtn = posterForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                Utils.showLoading(submitBtn, 'Generating...');
            }
        });
    }
});

// Export utilities for global use
window.PostasyUtils = Utils;
