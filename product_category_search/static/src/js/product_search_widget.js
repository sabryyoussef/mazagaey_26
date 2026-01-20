/** @odoo-module **/

/**
 * Product Search Widget
 * Helper functions for product categorization and search
 */

/**
 * Quick filter buttons for kanban view
 */
export function setupQuickFilters() {
    // Add click handlers for quick filter buttons
    document.addEventListener('DOMContentLoaded', function() {
        const filterButtons = document.querySelectorAll('.o_quick_filter_button');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Toggle active class
                this.classList.toggle('active');
                
                // Get filter type and value
                const filterType = this.dataset.filterType;
                const filterValue = this.dataset.filterValue;
                
                // Trigger Odoo search
                if (window.odoo && window.odoo.__DEBUG__) {
                    console.log('Quick filter:', filterType, filterValue);
                }
            });
        });
    });
}

// Initialize quick filters
setupQuickFilters();

/**
 * Service Type color helper
 */
export function getServiceTypeColor(serviceTypeName) {
    const colorMap = {
        'visa': '#2196f3',
        'accounting': '#9c27b0',
        'banking': '#4caf50',
        'business_setup': '#ff9800',
        'value_added': '#e91e63',
        'renewal': '#00bcd4',
        'liquidation': '#f44336',
        'administration': '#607d8b',
    };

    const key = serviceTypeName.toLowerCase().replace(/\s+/g, '_');
    return colorMap[key] || '#9e9e9e';
}

/**
 * Department color helper
 */
export function getDepartmentColor(departmentName) {
    const colorMap = {
        'accounts': '#0d47a1',
        'operations': '#1b5e20',
        'sales': '#bf360c',
        'admin': '#4a148c',
    };

    const key = departmentName.toLowerCase();
    return colorMap[key] || '#424242';
}

/**
 * Compliance level helper
 */
export function getComplianceLevel(hasCompliance, documentCount) {
    if (!hasCompliance) return 'none';
    if (documentCount >= 5) return 'high';
    if (documentCount >= 2) return 'medium';
    return 'low';
}

/**
 * Format price helper
 */
export function formatPrice(price, currency = 'AED') {
    return `${currency} ${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Export all helpers
export default {
    setupQuickFilters,
    getServiceTypeColor,
    getDepartmentColor,
    getComplianceLevel,
    formatPrice,
};
