/**
 * Switch HMR - Hot Module Replacement
 * 
 * This script provides hot module replacement for the Switch framework.
 * It allows components to be updated without reloading the page.
 */

(function(global) {
    'use strict';
    
    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before hmr.js.');
        return;
    }
    
    // HMR configuration
    const config = {
        enabled: true,
        interval: 2000, // Poll interval in milliseconds
        debug: false
    };
    
    // HMR state
    const state = {
        components: {},
        polling: false,
        lastPoll: 0
    };
    
    // Add HMR functionality to Switch
    global.Switch.hmr = {
        /**
         * Initialize HMR
         * @param {Object} options - HMR options
         */
        init: function(options = {}) {
            // Merge options with config
            Object.assign(config, options);
            
            if (config.debug) {
                console.log('Switch HMR initialized');
            }
            
            // Start polling if enabled
            if (config.enabled) {
                this.startPolling();
            }
        },
        
        /**
         * Register a component for HMR
         * @param {Object} component - Component to register
         */
        register: function(component) {
            if (!component.id || !component.hmr_id) {
                return;
            }
            
            // Store the component
            state.components[component.id] = component;
            
            if (config.debug) {
                console.log(`Registered component for HMR: ${component.name} (${component.id})`);
            }
        },
        
        /**
         * Start polling for changes
         */
        startPolling: function() {
            if (state.polling) {
                return;
            }
            
            state.polling = true;
            
            // Poll immediately
            this.poll();
            
            // Set up interval
            setInterval(() => {
                this.poll();
            }, config.interval);
            
            if (config.debug) {
                console.log(`HMR polling started (interval: ${config.interval}ms)`);
            }
        },
        
        /**
         * Stop polling for changes
         */
        stopPolling: function() {
            state.polling = false;
            
            if (config.debug) {
                console.log('HMR polling stopped');
            }
        },
        
        /**
         * Poll for changes
         */
        poll: function() {
            if (!state.polling) {
                return;
            }
            
            // Get component IDs
            const componentIds = Object.keys(state.components);
            if (componentIds.length === 0) {
                return;
            }
            
            // Check if enough time has passed since the last poll
            const now = Date.now();
            if (now - state.lastPoll < config.interval) {
                return;
            }
            
            state.lastPoll = now;
            
            // Make API request
            fetch('/api/switch/hmr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    componentIds: componentIds
                })
            })
            .then(response => response.json())
            .then(result => {
                // Process updates
                if (result.updates && result.updates.length > 0) {
                    this.applyUpdates(result.updates);
                }
            })
            .catch(error => {
                console.error('HMR poll error:', error);
            });
        },
        
        /**
         * Apply updates to components
         * @param {Array} updates - Updates to apply
         */
        applyUpdates: function(updates) {
            if (updates.length === 0) {
                return;
            }
            
            if (config.debug) {
                console.log(`HMR: Applying ${updates.length} updates`);
            }
            
            // Process each update
            updates.forEach(update => {
                const component = state.components[update.id];
                if (!component) {
                    return;
                }
                
                // Update the component hash
                component.file_hash = update.hash;
                
                // Reload the component
                this.reloadComponent(component);
            });
        },
        
        /**
         * Reload a component
         * @param {Object} component - Component to reload
         */
        reloadComponent: function(component) {
            if (config.debug) {
                console.log(`HMR: Reloading component: ${component.name} (${component.id})`);
            }
            
            // Find the component element
            const element = document.getElementById(component.hmr_id);
            if (!element) {
                console.error(`HMR: Component element not found: ${component.hmr_id}`);
                return;
            }
            
            // Save the component state
            const state = component.state;
            
            // Fetch the updated component
            fetch('/api/switch/component', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    componentId: component.id,
                    props: component.props
                })
            })
            .then(response => response.json())
            .then(result => {
                // Update the component
                if (result.html) {
                    // Update the element
                    element.innerHTML = result.html;
                    
                    // Restore the component state
                    component.state = state;
                    
                    // Re-attach event handlers
                    global.Switch.attachEvents(component, element);
                    
                    if (config.debug) {
                        console.log(`HMR: Component reloaded: ${component.name} (${component.id})`);
                    }
                }
            })
            .catch(error => {
                console.error('HMR reload error:', error);
            });
        }
    };
    
    // Initialize HMR when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Check if HMR is enabled
        if (global.SWITCH_HMR) {
            global.Switch.hmr.init(global.SWITCH_HMR_CONFIG || {});
            
            // Register initial components
            if (global.SWITCH_INITIAL_DATA) {
                global.Switch.hmr.register(global.SWITCH_INITIAL_DATA);
            }
        }
    });
    
})(typeof window !== 'undefined' ? window : this);
