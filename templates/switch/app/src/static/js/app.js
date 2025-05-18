// {{APP_NAME}} - Application JavaScript

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('{{APP_NAME}} loaded');
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Initialize dark mode
    initializeDarkMode();
});

// Initialize event listeners
function initializeEventListeners() {
    // Handle navigation
    document.addEventListener('click', function(event) {
        // Handle dark mode toggle
        if (event.target.dataset.action === 'toggle-dark-mode' || event.target.closest('[data-action="toggle-dark-mode"]')) {
            toggleDarkMode();
        }
    });
}

// Initialize dark mode
function initializeDarkMode() {
    // Check if dark mode is enabled
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // Apply dark mode if enabled
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
}

// Toggle dark mode
function toggleDarkMode() {
    // Toggle dark mode class
    document.body.classList.toggle('dark-mode');
    
    // Save preference to localStorage
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// API functions
const api = {
    // Get data
    getData: function() {
        return fetch('/api/data')
            .then(response => response.json());
    },
    
    // Post data
    postData: function(data) {
        return fetch('/api/data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json());
    }
};
