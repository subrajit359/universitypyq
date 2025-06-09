// Modern JavaScript for UniversityPYQ Application

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme();
        this.bindEvents();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateToggleIcon();
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
    }

    updateToggleIcon() {
        const toggleBtn = document.querySelector('.theme-toggle');
        if (toggleBtn) {
            toggleBtn.innerHTML = this.currentTheme === 'light' 
                ? '🌙' 
                : '☀️';
            toggleBtn.setAttribute('aria-label', 
                this.currentTheme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'
            );
        }
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('theme-toggle')) {
                this.toggleTheme();
            }
        });
    }
}

class MobileMenu {
    constructor() {
        this.isOpen = false;
        this.init();
    }

    init() {
        this.bindEvents();
    }

    toggle() {
        this.isOpen = !this.isOpen;
        const navCollapse = document.querySelector('.navbar-collapse');
        const toggler = document.querySelector('.navbar-toggler');
        
        if (navCollapse) {
            navCollapse.classList.toggle('show', this.isOpen);
        }
        
        if (toggler) {
            toggler.setAttribute('aria-expanded', this.isOpen.toString());
        }
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.navbar-toggler')) {
                this.toggle();
            }
            
            // Close menu when clicking outside
            if (this.isOpen && !e.target.closest('.navbar')) {
                this.isOpen = false;
                const navCollapse = document.querySelector('.navbar-collapse');
                if (navCollapse) {
                    navCollapse.classList.remove('show');
                }
            }
        });
    }
}

class FlashMessages {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.autoHideMessages();
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('alert-close')) {
                this.closeMessage(e.target.closest('.alert'));
            }
        });
    }

    closeMessage(messageElement) {
        if (messageElement) {
            messageElement.style.opacity = '0';
            messageElement.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                messageElement.remove();
            }, 300);
        }
    }

    autoHideMessages() {
        const messages = document.querySelectorAll('.alert');
        messages.forEach(message => {
            // Don't auto-hide error messages
            if (!message.classList.contains('alert-error')) {
                setTimeout(() => {
                    this.closeMessage(message);
                }, 5000);
            }
        });
    }

    show(message, type = 'info') {
        const container = this.getOrCreateContainer();
        const messageElement = this.createMessageElement(message, type);
        container.appendChild(messageElement);
        
        // Trigger animation
        setTimeout(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
        
        // Auto-hide if not error
        if (type !== 'error') {
            setTimeout(() => {
                this.closeMessage(messageElement);
            }, 5000);
        }
    }

    getOrCreateContainer() {
        let container = document.querySelector('.flash-messages');
        if (!container) {
            container = document.createElement('div');
            container.className = 'flash-messages';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    createMessageElement(message, type) {
        const element = document.createElement('div');
        element.className = `alert alert-${type}`;
        element.style.cssText = `
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
            margin-bottom: 10px;
        `;
        element.innerHTML = `
            ${message}
            <button type="button" class="alert-close" aria-label="Close">×</button>
        `;
        return element;
    }
}

class ModalManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            // Open modal
            if (e.target.hasAttribute('data-modal-target')) {
                const modalId = e.target.getAttribute('data-modal-target');
                this.openModal(modalId);
            }
            
            // Close modal
            if (e.target.classList.contains('modal-close') || 
                e.target.classList.contains('modal') ||
                e.target.hasAttribute('data-modal-close')) {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

class BookmarkManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('bookmark-btn')) {
                this.toggleBookmark(e.target);
            }
        });
    }

    async toggleBookmark(button) {
        const paperId = button.getAttribute('data-paper-id');
        if (!paperId) return;

        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = '...';

        try {
            const response = await fetch(`/bookmark/${paperId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok) {
                // Update button state
                if (data.status === 'added') {
                    button.textContent = '★ Bookmarked';
                    button.classList.add('bookmarked');
                } else {
                    button.textContent = '☆ Bookmark';
                    button.classList.remove('bookmarked');
                }
                
                // Show success message
                window.flashMessages.show(data.message, 'success');
            } else {
                throw new Error(data.error || 'Failed to toggle bookmark');
            }
        } catch (error) {
            console.error('Bookmark error:', error);
            window.flashMessages.show('Failed to update bookmark. Please try again.', 'error');
            button.textContent = originalText;
        } finally {
            button.disabled = false;
        }
    }
}

class SearchForm {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            const searchInput = searchForm.querySelector('input[name="search"]');
            const filterSelects = searchForm.querySelectorAll('select');

            // Auto-submit on filter change
            filterSelects.forEach(select => {
                select.addEventListener('change', () => {
                    searchForm.submit();
                });
            });

            // Submit on Enter key
            if (searchInput) {
                searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        searchForm.submit();
                    }
                });
            }
        }
    }
}

class FormValidation {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('needs-validation')) {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            }
        });

        // Real-time validation
        document.addEventListener('blur', (e) => {
            if (e.target.classList.contains('form-control')) {
                this.validateField(e.target);
            }
        }, true);
    }

    validateForm(form) {
        let isValid = true;
        const fields = form.querySelectorAll('.form-control[required]');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        // Required validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'This field is required.';
        }

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Please enter a valid email address.';
            }
        }

        // Password validation
        if (field.type === 'password' && value && value.length < 6) {
            isValid = false;
            message = 'Password must be at least 6 characters long.';
        }

        // Confirm password validation
        if (field.name === 'confirm_password') {
            const passwordField = field.form.querySelector('input[name="password"]');
            if (passwordField && value !== passwordField.value) {
                isValid = false;
                message = 'Passwords do not match.';
            }
        }

        this.showFieldValidation(field, isValid, message);
        return isValid;
    }

    showFieldValidation(field, isValid, message) {
        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        // Remove existing feedback
        const existingFeedback = formGroup.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Update field classes
        field.classList.toggle('is-valid', isValid);
        field.classList.toggle('is-invalid', !isValid);

        // Add feedback message
        if (!isValid && message) {
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            feedback.style.cssText = `
                display: block;
                color: hsl(var(--error-h), var(--error-s), var(--error-l));
                font-size: 0.875rem;
                margin-top: 0.25rem;
            `;
            formGroup.appendChild(feedback);
        }
    }
}

class LoadingManager {
    static setLoading(element, loading = true) {
        if (loading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }

    static showPageLoading() {
        // Create or show page loading overlay
        let overlay = document.getElementById('page-loading');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'page-loading';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p>Loading...</p>
                </div>
            `;
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    static hidePageLoading() {
        const overlay = document.getElementById('page-loading');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
}

// Utility functions
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
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    window.themeManager = new ThemeManager();
    window.mobileMenu = new MobileMenu();
    window.flashMessages = new FlashMessages();
    window.modalManager = new ModalManager();
    window.bookmarkManager = new BookmarkManager();
    window.searchForm = new SearchForm();
    window.formValidation = new FormValidation();
    
    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                LoadingManager.setLoading(submitBtn);
            }
        });
    });
    
    // Add loading states to navigation links
    document.querySelectorAll('a[href]:not([href^="#"]):not([href^="javascript:"]):not([target="_blank"])').forEach(link => {
        link.addEventListener('click', function() {
            LoadingManager.showPageLoading();
        });
    });
    
    // Hide loading on page load
    LoadingManager.hidePageLoading();
    
    console.log('UniversityPYQ application initialized successfully');
});