// Dashboard Application JavaScript

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('{{APP_NAME}} Dashboard loaded');
    
    // Initialize charts if Chart.js is available
    if (window.Chart) {
        initializeCharts();
    }
    
    // Initialize event listeners
    initializeEventListeners();
});

// Initialize charts
function initializeCharts() {
    // Find all chart canvases
    const chartCanvases = document.querySelectorAll('canvas[data-chart-type]');
    
    // Initialize each chart
    chartCanvases.forEach(canvas => {
        const type = canvas.dataset.chartType;
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        const options = JSON.parse(canvas.dataset.chartOptions || '{}');
        
        // Create the chart
        const chart = new Chart(canvas, {
            type: type,
            data: data,
            options: options
        });
        
        // Store the chart instance
        canvas._chart = chart;
    });
}

// Initialize event listeners
function initializeEventListeners() {
    // Handle navigation
    document.addEventListener('click', function(event) {
        // Handle sidebar toggle
        if (event.target.dataset.action === 'toggle-sidebar' || event.target.closest('[data-action="toggle-sidebar"]')) {
            toggleSidebar();
        }
        
        // Handle dark mode toggle
        if (event.target.dataset.action === 'toggle-dark-mode' || event.target.closest('[data-action="toggle-dark-mode"]')) {
            toggleDarkMode();
        }
        
        // Handle dropdown toggle
        if (event.target.dataset.action === 'toggle-dropdown' || event.target.closest('[data-action="toggle-dropdown"]')) {
            const dropdown = event.target.closest('.dropdown');
            if (dropdown) {
                toggleDropdown(dropdown);
            }
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.dropdown')) {
            closeAllDropdowns();
        }
    });
}

// Toggle sidebar
function toggleSidebar() {
    const app = document.querySelector('.app');
    if (app) {
        app.classList.toggle('sidebar-collapsed');
        
        // Save preference to localStorage
        const isCollapsed = app.classList.contains('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
        
        // Resize charts if any
        resizeCharts();
    }
}

// Toggle dark mode
function toggleDarkMode() {
    const app = document.querySelector('.app');
    if (app) {
        app.classList.toggle('dark-mode');
        
        // Save preference to localStorage
        const isDarkMode = app.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        
        // Update charts if any
        updateChartsTheme();
    }
}

// Toggle dropdown
function toggleDropdown(dropdown) {
    // Close all other dropdowns
    const allDropdowns = document.querySelectorAll('.dropdown');
    allDropdowns.forEach(d => {
        if (d !== dropdown) {
            d.classList.remove('show');
            const menu = d.querySelector('.dropdown-menu');
            if (menu) {
                menu.classList.remove('show');
            }
        }
    });
    
    // Toggle this dropdown
    dropdown.classList.toggle('show');
    const menu = dropdown.querySelector('.dropdown-menu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// Close all dropdowns
function closeAllDropdowns() {
    const allDropdowns = document.querySelectorAll('.dropdown');
    allDropdowns.forEach(dropdown => {
        dropdown.classList.remove('show');
        const menu = dropdown.querySelector('.dropdown-menu');
        if (menu) {
            menu.classList.remove('show');
        }
    });
}

// Resize charts when sidebar is toggled
function resizeCharts() {
    if (window.Chart) {
        const chartCanvases = document.querySelectorAll('canvas[data-chart-type]');
        chartCanvases.forEach(canvas => {
            if (canvas._chart) {
                canvas._chart.resize();
            }
        });
    }
}

// Update charts theme when dark mode is toggled
function updateChartsTheme() {
    if (window.Chart) {
        const isDarkMode = document.querySelector('.app').classList.contains('dark-mode');
        const chartCanvases = document.querySelectorAll('canvas[data-chart-type]');
        
        chartCanvases.forEach(canvas => {
            if (canvas._chart) {
                // Update chart colors based on theme
                if (isDarkMode) {
                    // Set dark mode colors
                    canvas._chart.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
                    canvas._chart.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
                    canvas._chart.options.scales.x.ticks.color = 'rgba(255, 255, 255, 0.7)';
                    canvas._chart.options.scales.y.ticks.color = 'rgba(255, 255, 255, 0.7)';
                } else {
                    // Set light mode colors
                    canvas._chart.options.scales.x.grid.color = 'rgba(0, 0, 0, 0.1)';
                    canvas._chart.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';
                    canvas._chart.options.scales.x.ticks.color = 'rgba(0, 0, 0, 0.7)';
                    canvas._chart.options.scales.y.ticks.color = 'rgba(0, 0, 0, 0.7)';
                }
                
                // Update the chart
                canvas._chart.update();
            }
        });
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) {
        return 'Never';
    }
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format number
function formatNumber(number) {
    return number.toLocaleString();
}

// Format percentage
function formatPercentage(number) {
    return number.toFixed(2) + '%';
}

// Handle form submission
function handleFormSubmit(event, formId) {
    event.preventDefault();
    
    const form = document.getElementById(formId);
    if (!form) {
        return;
    }
    
    // Get form data
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
        
        // Simulate form submission
        setTimeout(() => {
            // Show success message
            const successAlert = document.createElement('div');
            successAlert.className = 'alert alert-success mt-3';
            successAlert.textContent = 'Form submitted successfully!';
            
            // Insert the alert after the form
            form.parentNode.insertBefore(successAlert, form.nextSibling);
            
            // Reset the button
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            
            // Remove the alert after 3 seconds
            setTimeout(() => {
                successAlert.remove();
            }, 3000);
        }, 1000);
    }
}

// API functions
const api = {
    // Get stats
    getStats: function() {
        return fetch('/api/stats')
            .then(response => response.json());
    },
    
    // Get chart data
    getChartData: function() {
        return fetch('/api/chart-data')
            .then(response => response.json());
    },
    
    // Get user profile
    getUserProfile: function() {
        return fetch('/api/user/profile')
            .then(response => response.json());
    },
    
    // Update user profile
    updateUserProfile: function(data) {
        return fetch('/api/user/profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json());
    },
    
    // Update user settings
    updateUserSettings: function(data) {
        return fetch('/api/user/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json());
    }
};
