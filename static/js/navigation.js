/**
 * ========================================
 * ACIDTECH NAVIGATION MANAGER
 * Bootstrap 5 Native - Professional System
 * ========================================
 */

class AcidTechNavigation {
    constructor() {
        this.init();
    }

    init() {
        this.highlightActiveNav();
        this.initMobileNavigation();
        this.initCurrencyFormatters();
        this.initDateFormatters();
    }

    /**
     * Highlight active navigation item based on current URL - Bootstrap 5 Native
     */
    highlightActiveNav() {
        const currentPath = window.location.pathname;
        
        // Remove active class from all nav links in both desktop and mobile sidebars
        document.querySelectorAll('#sidebarMenu .nav-link, #sidebarOffcanvas .nav-link').forEach(link => {
            link.classList.remove('active');
            link.classList.remove('bg-primary');
        });
        
        // Find and activate current page link
        const exactMatch = document.querySelector(`#sidebarMenu a[href="${currentPath}"], #sidebarOffcanvas a[href="${currentPath}"]`);
        if (exactMatch && exactMatch.classList.contains('nav-link')) {
            this.setActiveNavLink(exactMatch);
            return;
        }
        
        // Try pattern matching for account details and other dynamic routes
        this.activateNavByPattern(currentPath);
    }
    
    /**
     * Set active state for Bootstrap nav-link
     */
    setActiveNavLink(linkElement) {
        // Add active classes to both desktop and mobile versions
        const href = linkElement.getAttribute('href');
        
        // Find all matching links (desktop + mobile)
        document.querySelectorAll(`#sidebarMenu a[href="${href}"], #sidebarOffcanvas a[href="${href}"]`).forEach(link => {
            link.classList.add('active');
            link.classList.add('bg-primary');
        });
    }

    /**
     * Activate navigation based on URL patterns - Bootstrap 5
     */
    activateNavByPattern(currentPath) {
        const patterns = [
            { pattern: /^\/dashboard/, selector: '[data-page="dashboard"]' },
            { pattern: /^\/cash-flow\/enhanced-dashboard/, selector: '[data-page="enhanced"]' },
            { pattern: /^\/cash-flow\/account\/Revenue/, selector: '[data-page="revenue"]' },
            { pattern: /^\/cash-flow\/account\/Bill/, selector: '[data-page="billpay"]' },
            { pattern: /^\/cash-flow\/account\/Payroll/, selector: '[data-page="payroll"]' },
            { pattern: /^\/cash-flow\/account\/Capital/, selector: '[data-page="capital"]' },
            { pattern: /^\/cash-flow\/classification/, selector: '[data-page="classification"]' },
            { pattern: /^\/cash-flow/, selector: '[data-page="cash-flow"]' },
            { pattern: /^\/accounts-receivable/, selector: '[data-page="ar"]' },
            { pattern: /^\/accounts-payable/, selector: '[data-page="ap"]' },
            { pattern: /^\/purchase-orders/, selector: '[data-page="po"]' },
            { pattern: /^\/data-import/, selector: '[data-page="import"]' },
            { pattern: /^\/reports/, selector: '[data-page="reports"]' }
        ];

        for (const { pattern, selector } of patterns) {
            if (pattern.test(currentPath)) {
                // Find in both desktop and mobile sidebars
                const desktopNavLink = document.querySelector(`#sidebarMenu ${selector}`);
                const mobileNavLink = document.querySelector(`#sidebarOffcanvas ${selector}`);
                
                if (desktopNavLink) {
                    this.setActiveNavLink(desktopNavLink);
                    break;
                } else if (mobileNavLink) {
                    this.setActiveNavLink(mobileNavLink);
                    break;
                }
            }
        }
    }

    /**
     * Initialize mobile navigation functionality
     */
    initMobileNavigation() {
        // Mobile offcanvas auto-close after navigation
        const offcanvasElement = document.getElementById('mobileOffcanvas');
        if (offcanvasElement) {
            // Close offcanvas when clicking nav links
            offcanvasElement.addEventListener('click', (e) => {
                if (e.target.matches('a[data-bs-dismiss="offcanvas"]')) {
                    const offcanvas = bootstrap.Offcanvas.getInstance(offcanvasElement);
                    if (offcanvas) {
                        offcanvas.hide();
                    }
                }
            });
        }
    }

    /**
     * Format currency values consistently across the app
     */
    initCurrencyFormatters() {
        // Auto-format elements with data-format="currency"
        document.querySelectorAll('[data-format="currency"]').forEach(element => {
            const value = parseFloat(element.textContent || element.getAttribute('data-value') || 0);
            element.textContent = this.formatCurrency(value);
        });

        // Auto-format elements with currency class
        document.querySelectorAll('.currency').forEach(element => {
            const value = parseFloat(element.textContent || 0);
            if (!isNaN(value)) {
                element.textContent = this.formatCurrency(value);
            }
        });
    }

    /**
     * Format date values consistently
     */
    initDateFormatters() {
        document.querySelectorAll('[data-format="date"]').forEach(element => {
            const dateValue = element.textContent || element.getAttribute('data-value');
            if (dateValue && dateValue !== '--') {
                element.textContent = this.formatDate(dateValue);
            }
        });
    }

    /**
     * Professional currency formatter for Oil & Gas industry
     */
    formatCurrency(amount, options = {}) {
        const defaults = {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        };
        
        const config = { ...defaults, ...options };
        
        try {
            // Handle large numbers with appropriate scaling
            if (Math.abs(amount) >= 1000000) {
                return new Intl.NumberFormat('en-US', {
                    ...config,
                    notation: 'compact',
                    compactDisplay: 'short'
                }).format(amount);
            }
            
            return new Intl.NumberFormat('en-US', config).format(amount);
        } catch (error) {
            console.warn('Currency formatting error:', error);
            return `$${amount.toLocaleString()}`;
        }
    }

    /**
     * Professional date formatter
     */
    formatDate(dateInput, format = 'short') {
        try {
            const date = new Date(dateInput);
            
            if (isNaN(date.getTime())) {
                return dateInput; // Return original if invalid
            }

            const formats = {
                short: {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                },
                long: {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                },
                compact: {
                    year: '2-digit',
                    month: 'numeric',
                    day: 'numeric'
                }
            };

            return new Intl.DateTimeFormat('en-US', formats[format] || formats.short).format(date);
        } catch (error) {
            console.warn('Date formatting error:', error);
            return dateInput;
        }
    }

    /**
     * Format numbers with proper separators
     */
    formatNumber(number, decimals = 0) {
        try {
            return new Intl.NumberFormat('en-US', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }).format(number);
        } catch (error) {
            console.warn('Number formatting error:', error);
            return number.toString();
        }
    }

    /**
     * Format percentages
     */
    formatPercentage(value, decimals = 1) {
        try {
            return new Intl.NumberFormat('en-US', {
                style: 'percent',
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }).format(value / 100);
        } catch (error) {
            console.warn('Percentage formatting error:', error);
            return `${value}%`;
        }
    }

    /**
     * Update page title dynamically
     */
    updatePageTitle(title) {
        const titleElement = document.querySelector('.navbar-brand');
        if (titleElement) {
            titleElement.textContent = title;
        }
        
        document.title = `${title} - AcidTech Financial`;
    }

    /**
     * Show loading state for data-heavy operations
     */
    showLoadingState(element, message = 'Loading...') {
        if (element) {
            element.innerHTML = `
                <div class="d-flex align-items-center justify-content-center py-4">
                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="text-muted">${message}</span>
                </div>
            `;
        }
    }

    /**
     * Show error state
     */
    showErrorState(element, message = 'Error loading data') {
        if (element) {
            element.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${message}
                </div>
            `;
        }
    }

    /**
     * Refresh current page data (for dashboard updates)
     */
    refreshPageData() {
        // Trigger refresh event that individual pages can listen to
        window.dispatchEvent(new CustomEvent('acidtech:refresh-data'));
    }
}

// Initialize navigation when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.AcidTechNav = new AcidTechNavigation();
});

// Global utility functions for backward compatibility
window.AciTech = window.AciTech || {};
Object.assign(window.AciTech, {
    formatCurrency: (amount, options) => window.AcidTechNav?.formatCurrency(amount, options) || `$${amount}`,
    formatDate: (date, format) => window.AcidTechNav?.formatDate(date, format) || date,
    formatNumber: (number, decimals) => window.AcidTechNav?.formatNumber(number, decimals) || number,
    formatPercentage: (value, decimals) => window.AcidTechNav?.formatPercentage(value, decimals) || `${value}%`,
    showLoadingState: (element, message) => window.AcidTechNav?.showLoadingState(element, message),
    showErrorState: (element, message) => window.AcidTechNav?.showErrorState(element, message)
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AcidTechNavigation;
}