/**
 * Switch Server-Side Rendering (SSR)
 * 
 * Enhanced server-side rendering support for the Switch framework.
 * This module provides improved hydration and state management for SSR.
 */

(function(global) {
    'use strict';

    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before ssr.js.');
        return;
    }

    // SSR utilities
    const SwitchSSR = {
        /**
         * Hydrate a server-rendered component
         * @param {Object} component - Component data
         * @param {HTMLElement} container - Container element (optional)
         * @returns {Object} - Hydrated component
         */
        hydrate: function(component, container) {
            console.log('Hydrating component:', component.name);
            
            // If no container is provided, use the root element
            const targetContainer = container || document.getElementById('switch-root');
            if (!targetContainer) {
                console.error('Target container not found for hydration.');
                return null;
            }
            
            // Create the component
            const hydratedComponent = Switch.createComponent(component);
            
            // Attach event handlers without re-rendering
            this.attachEvents(hydratedComponent, targetContainer);
            
            // Hydrate children
            this.hydrateChildren(hydratedComponent, targetContainer);
            
            // Dispatch a hydration event
            const event = new CustomEvent('switch:component-hydrated', {
                detail: { component: hydratedComponent }
            });
            document.dispatchEvent(event);
            
            return hydratedComponent;
        },
        
        /**
         * Attach event handlers to a hydrated component
         * @param {Object} component - Component
         * @param {HTMLElement} container - Container element
         */
        attachEvents: function(component, container) {
            try {
                // Use Switch's attachEvents method
                Switch.attachEvents(component, container);
                
                // Also attach action handlers
                if (Switch.attachActionHandlers) {
                    Switch.attachActionHandlers(component, container);
                }
            } catch (error) {
                console.error('Error attaching events during hydration:', error);
            }
        },
        
        /**
         * Hydrate children of a component
         * @param {Object} component - Component
         * @param {HTMLElement} container - Container element
         */
        hydrateChildren: function(component, container) {
            try {
                // Find child containers
                let childContainers = [];
                
                if (global.SwitchDOM) {
                    childContainers = SwitchDOM.querySelectorAll('[data-child-container]', container);
                } else {
                    childContainers = Array.from(container.querySelectorAll('[data-child-container]'));
                }
                
                // Hydrate each child
                component.children.forEach((child, index) => {
                    // Get the child component
                    const childComponent = Switch.createComponent(child);
                    
                    // Get the container for this child
                    const childContainer = childContainers[index] || 
                                          (global.SwitchDOM ? 
                                           SwitchDOM.querySelector('.switch-component-content', container) : 
                                           container.querySelector('.switch-component-content'));
                    
                    if (childContainer) {
                        // Hydrate the child
                        this.hydrate(childComponent, childContainer);
                    }
                });
            } catch (error) {
                console.error('Error hydrating children:', error);
            }
        },
        
        /**
         * Initialize SSR
         */
        init: function() {
            console.log('Initializing Switch SSR...');
            
            // Add hydration method to Switch
            Switch.hydrate = this.hydrate.bind(this);
            
            // Initialize when the DOM is ready
            document.addEventListener('DOMContentLoaded', function() {
                // Check if we're in SSR mode
                if (global.SWITCH_ENV && global.SWITCH_ENV.ssr && global.SWITCH_INITIAL_DATA) {
                    console.log('Hydrating server-side rendered components...');
                    
                    // Hydrate the root component
                    SwitchSSR.hydrate(global.SWITCH_INITIAL_DATA);
                    
                    console.log('Hydration complete.');
                }
            });
        }
    };
    
    // Initialize SSR
    SwitchSSR.init();
    
    // Export the SwitchSSR object
    global.SwitchSSR = SwitchSSR;
    
})(typeof window !== 'undefined' ? window : this);
