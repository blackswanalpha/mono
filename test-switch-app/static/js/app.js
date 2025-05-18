/**
 * Test Switch App - Application Script
 */

(function() {
    'use strict';

    // Initialize the application when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Test Switch App initialized');
        
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
})();
