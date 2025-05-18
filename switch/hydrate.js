/**
 * Switch Hydration - Client-side hydration for server-side rendered components
 * 
 * This script hydrates server-side rendered components on the client.
 */

(function(global) {
    'use strict';
    
    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before hydrate.js.');
        return;
    }
    
    // Add hydration functionality to Switch
    global.Switch.hydrate = function(component, container) {
        // If no container is provided, use the root element
        const targetContainer = container || document.getElementById('switch-root');
        if (!targetContainer) {
            console.error('Target container not found for hydration.');
            return;
        }
        
        // Find the hydration element
        const hydrationElement = document.getElementById(component.hydration_id);
        if (!hydrationElement) {
            console.error(`Hydration element not found: ${component.hydration_id}`);
            return;
        }
        
        // Store the component
        global.Switch.components[component.id] = component;
        
        // Attach event handlers
        global.Switch.attachEvents(component, hydrationElement);
        
        // Hydrate children
        global.Switch.hydrateChildren(component, hydrationElement);
        
        console.log(`Hydrated component: ${component.name} (${component.id})`);
        
        return component;
    };
    
    // Add method to hydrate children
    global.Switch.hydrateChildren = function(component, container) {
        // Find child containers
        const childContainers = container.querySelectorAll('[data-child-container]');
        
        // Hydrate each child
        component.children.forEach((child, index) => {
            // Get the child component
            const childComponent = global.Switch.components[child.id] || this.createComponent(child);
            
            // Get the container for this child
            const childContainer = childContainers[index] || container.querySelector('.switch-component-content');
            
            // Hydrate the child
            this.hydrate(childComponent, childContainer);
        });
    };
    
    // Initialize hydration when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Check if we're in SSR mode
        if (global.SWITCH_SSR && global.SWITCH_INITIAL_DATA) {
            console.log('Hydrating server-side rendered components...');
            
            // Hydrate the root component
            global.Switch.hydrate(global.SWITCH_INITIAL_DATA);
            
            console.log('Hydration complete.');
        }
    });
    
})(typeof window !== 'undefined' ? window : this);
