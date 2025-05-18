/**
 * Switch Introduction - Application Script
 */

(function() {
    'use strict';

    // Initialize the application when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Switch Introduction initialized');
        
        // Initialize the Switch framework if available
        if (window.Switch && typeof window.Switch.init === 'function') {
            window.Switch.init({
                rootElementId: 'switch-root'
            });
        }
    });
    
    // Create a simple Switch object if it doesn't exist
    if (!window.Switch) {
        window.Switch = {
            createComponent: function(data) {
                console.log('Creating component:', data);
                return {
                    id: 'app-' + Date.now(),
                    name: data.name,
                    props: data.props || {},
                    state: {},
                    render: function() {
                        return '<div class="app"><h1>' + this.props.title + '</h1><p>Welcome to Switch!</p></div>';
                    }
                };
            },
            renderComponent: function(component, container) {
                console.log('Rendering component:', component);
                if (container) {
                    container.innerHTML = '<div class="app"><h1>' + component.props.title + '</h1><p>Welcome to Switch!</p></div>';
                }
            },
            init: function() {
                console.log('Switch framework initialized');
            }
        };
    }
    
    // Add event listeners for navigation
    document.addEventListener('click', function(event) {
        // Check if this is a navigation link
        if (event.target.dataset.page) {
            // Prevent the default link behavior
            event.preventDefault();
            
            // Get the page
            var page = event.target.dataset.page;
            
            // Update the URL
            if (page === "home") {
                history.pushState({}, "", "/");
            } else {
                history.pushState({}, "", "/" + page);
            }
            
            // Reload the page
            window.location.reload();
        }
    });
    
    // Add event listeners for counter
    document.addEventListener('click', function(event) {
        // Check if this is a counter button
        if (event.target.dataset.action === "increment" || event.target.dataset.action === "decrement") {
            // Get the counter value element
            var counterValue = document.querySelector('.counter-value');
            if (counterValue) {
                // Get the current value
                var value = parseInt(counterValue.textContent, 10);
                
                // Update the value
                if (event.target.dataset.action === "increment") {
                    value += 1;
                } else {
                    value -= 1;
                }
                
                // Update the display
                counterValue.textContent = value;
            }
        }
    });
})();
