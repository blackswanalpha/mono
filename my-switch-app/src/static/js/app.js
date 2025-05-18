// my-switch-app - Application JavaScript

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('my-switch-app loaded');
    
    // Initialize event listeners
    initializeEventListeners();
    
    // Initialize dark mode
    initializeDarkMode();
    
    // Initialize sidebar
    initializeSidebar();
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.dropdown')) {
            closeAllDropdowns();
        }
    });
});

// Initialize event listeners
function initializeEventListeners() {
    // Handle navigation
    document.addEventListener('click', function(event) {
        // Handle dark mode toggle
        if (event.target.dataset.action === 'toggle-dark-mode' || event.target.closest('[data-action="toggle-dark-mode"]')) {
            toggleDarkMode();
        }
        
        // Handle sidebar toggle
        if (event.target.dataset.action === 'toggle-sidebar' || event.target.closest('[data-action="toggle-sidebar"]')) {
            toggleSidebar();
        }
        
        // Handle dropdown toggle
        if (event.target.dataset.action === 'toggle-dropdown' || event.target.closest('[data-action="toggle-dropdown"]')) {
            const dropdown = event.target.closest('.dropdown');
            if (dropdown) {
                toggleDropdown(dropdown);
            }
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

// Initialize sidebar
function initializeSidebar() {
    // Check if sidebar is collapsed
    const isSidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    // Apply sidebar collapsed if enabled
    if (isSidebarCollapsed) {
        document.body.classList.add('sidebar-collapsed');
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

// Toggle sidebar
function toggleSidebar() {
    // Toggle sidebar collapsed class
    document.body.classList.toggle('sidebar-collapsed');
    
    // Save preference to localStorage
    const isSidebarCollapsed = document.body.classList.contains('sidebar-collapsed');
    localStorage.setItem('sidebarCollapsed', isSidebarCollapsed);
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

// Package management API
const packageAPI = {
    // Get all packages
    getPackages: function() {
        return fetch('/api/packages')
            .then(response => response.json());
    },
    
    // Get package by name
    getPackage: function(name) {
        return fetch(`/api/packages/${name}`)
            .then(response => response.json());
    },
    
    // Search packages
    searchPackages: function(query) {
        return fetch(`/api/packages/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json());
    },
    
    // Install package
    installPackage: function(name, version) {
        return fetch('/api/packages/install', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                version: version
            })
        })
        .then(response => response.json());
    },
    
    // Uninstall package
    uninstallPackage: function(name) {
        return fetch('/api/packages/uninstall', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name
            })
        })
        .then(response => response.json());
    }
};

// Kit management API
const kitAPI = {
    // Get all kits
    getKits: function() {
        return fetch('/api/kits')
            .then(response => response.json());
    },
    
    // Get kit by name
    getKit: function(name) {
        return fetch(`/api/kits/${name}`)
            .then(response => response.json());
    },
    
    // Search kits
    searchKits: function(query) {
        return fetch(`/api/kits/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json());
    },
    
    // Install kit
    installKit: function(name, version) {
        return fetch('/api/kits/install', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                version: version
            })
        })
        .then(response => response.json());
    },
    
    // Uninstall kit
    uninstallKit: function(name) {
        return fetch('/api/kits/uninstall', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name
            })
        })
        .then(response => response.json());
    }
};
