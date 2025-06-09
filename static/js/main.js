// UniversityPYQ Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeTooltips();
    initializeAnimations();
    initializeFormValidation();
    initializeSearchFilters();
    initializeThemeToggle();
    initializeBackToTop();
    
    console.log('UniversityPYQ initialized successfully');
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize scroll animations
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe cards and sections for animation
    document.querySelectorAll('.card, .hero-section, .stats-section').forEach(el => {
        observer.observe(el);
    });
}

// Enhanced form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        }, false);
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Search filters functionality
function initializeSearchFilters() {
    const searchForm = document.querySelector('form[method="GET"]');
    if (!searchForm) return;
    
    const searchInput = searchForm.querySelector('input[name="search"]');
    const filterSelects = searchForm.querySelectorAll('select');
    
    // Auto-submit on filter change (with debounce for search input)
    let searchTimeout;
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 3 || this.value.length === 0) {
                    searchForm.submit();
                }
            }, 500);
        });
    }
    
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            searchForm.submit();
        });
    });
    
    // Clear filters functionality
    const clearButton = document.getElementById('clear-filters');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (searchInput) searchInput.value = '';
            filterSelects.forEach(select => select.selectedIndex = 0);
            searchForm.submit();
        });
    }
}

// Theme toggle functionality
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        
        // Update icon
        const icon = this.querySelector('i');
        if (next === 'dark') {
            icon.classList.replace('fa-moon', 'fa-sun');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
        }
    });
}

// Back to top button
function initializeBackToTop() {
    // Create back to top button
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTop.className = 'btn btn-primary btn-floating back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: none;
        z-index: 1000;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(backToTop);
    
    // Show/hide on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'flex';
            backToTop.style.alignItems = 'center';
            backToTop.style.justifyContent = 'center';
        } else {
            backToTop.style.display = 'none';
        }
    });
    
    // Smooth scroll to top
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Toast notification system
function showToast(message, type = 'success', duration = 5000) {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const toastId = 'toast-' + Date.now();
    toast.id = toastId;
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration,
        autohide: true
    });
    
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
    
    return toast;
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Loading states
function showLoading(button) {
    if (!button) return;
    
    const originalText = button.innerHTML;
    const originalWidth = button.offsetWidth;
    
    button.dataset.originalText = originalText;
    button.style.width = originalWidth + 'px';
    button.innerHTML = '<span class="loading"></span>';
    button.disabled = true;
    
    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
        button.style.width = '';
        delete button.dataset.originalText;
    };
}

// File upload preview
function previewFile(input, previewContainer) {
    if (!input.files || !input.files[0]) return;
    
    const file = input.files[0];
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const preview = document.createElement('div');
        preview.className = 'file-preview mt-2 p-3 border rounded';
        
        if (file.type.startsWith('image/')) {
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px;">
                <p class="mt-2 mb-0"><strong>${file.name}</strong></p>
                <small class="text-muted">${formatFileSize(file.size)}</small>
            `;
        } else {
            preview.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-file-alt fa-2x text-primary me-3"></i>
                    <div>
                        <p class="mb-0"><strong>${file.name}</strong></p>
                        <small class="text-muted">${formatFileSize(file.size)}</small>
                    </div>
                </div>
            `;
        }
        
        if (previewContainer) {
            previewContainer.innerHTML = '';
            previewContainer.appendChild(preview);
        }
    };
    
    reader.readAsDataURL(file);
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success', 2000);
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        showToast('Failed to copy to clipboard', 'error');
    } finally {
        document.body.removeChild(textArea);
    }
}

// Download tracking
function trackDownload(paperId, paperTitle) {
    // Send analytics event if needed
    if (typeof gtag !== 'undefined') {
        gtag('event', 'download', {
            'event_category': 'Paper',
            'event_label': paperTitle,
            'value': paperId
        });
    }
    
    console.log(`Download tracked: ${paperTitle} (ID: ${paperId})`);
}

// Search suggestions
function initializeSearchSuggestions() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    let suggestionsContainer;
    
    searchInput.addEventListener('input', debounce(function() {
        const query = this.value.trim();
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        // Here you could fetch suggestions from an API
        // For now, we'll use localStorage to store recent searches
        const recentSearches = getRecentSearches();
        const suggestions = recentSearches.filter(search => 
            search.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5);
        
        showSuggestions(suggestions);
    }, 300));
    
    searchInput.addEventListener('blur', function() {
        setTimeout(hideSuggestions, 150); // Delay to allow click on suggestions
    });
    
    function showSuggestions(suggestions) {
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.className = 'search-suggestions position-absolute bg-white border rounded shadow-sm';
            suggestionsContainer.style.cssText = `
                top: 100%;
                left: 0;
                right: 0;
                z-index: 1000;
                max-height: 200px;
                overflow-y: auto;
            `;
            searchInput.parentNode.style.position = 'relative';
            searchInput.parentNode.appendChild(suggestionsContainer);
        }
        
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }
        
        suggestionsContainer.innerHTML = suggestions.map(suggestion => `
            <div class="suggestion-item p-2 border-bottom cursor-pointer" style="cursor: pointer;">
                <i class="fas fa-search text-muted me-2"></i>${suggestion}
            </div>
        `).join('');
        
        suggestionsContainer.style.display = 'block';
        
        // Add click listeners
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                const text = this.textContent.trim();
                searchInput.value = text;
                hideSuggestions();
                searchInput.form.submit();
            });
        });
    }
    
    function hideSuggestions() {
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    }
    
    // Save search when form is submitted
    searchInput.form.addEventListener('submit', function() {
        const query = searchInput.value.trim();
        if (query) {
            saveRecentSearch(query);
        }
    });
}

function getRecentSearches() {
    const searches = localStorage.getItem('recentSearches');
    return searches ? JSON.parse(searches) : [];
}

function saveRecentSearch(query) {
    let searches = getRecentSearches();
    searches = searches.filter(search => search !== query); // Remove duplicates
    searches.unshift(query); // Add to beginning
    searches = searches.slice(0, 10); // Keep only last 10
    localStorage.setItem('recentSearches', JSON.stringify(searches));
}

// Initialize additional features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSearchSuggestions();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add loading states to form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                showLoading(submitButton);
            }
        });
    });
});

// Export functions for global use
window.UniversityPYQ = {
    showToast,
    showLoading,
    copyToClipboard,
    trackDownload,
    formatFileSize,
    previewFile
};
