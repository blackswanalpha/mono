/**
 * Switch UI Kit Loader
 * 
 * This script loads all the components from the Switch UI Kit.
 */

(function(global) {
    'use strict';
    
    // Create the SwitchUIKit namespace
    global.SwitchUIKit = global.SwitchUIKit || {};
    
    // Define the loader
    const Loader = {
        /**
         * Load all components
         * @param {Object} options - Loader options
         * @returns {Promise} - Promise that resolves when all components are loaded
         */
        loadAll: function(options = {}) {
            return new Promise((resolve, reject) => {
                // Default options
                const defaultOptions = {
                    basePath: '/kits/SwitchUIKit/components',
                    components: [
                        'button',
                        'card',
                        'modal',
                        'tabs',
                        'alert',
                        'dropdown',
                        'table',
                        'form',
                        'tooltip',
                        'accordion',
                        'pagination',
                        'progress',
                        'spinner',
                        'badge',
                        'avatar'
                    ],
                    loadCSS: true,
                    cssPath: '/kits/SwitchUIKit/switch-ui-kit.css'
                };
                
                // Merge options
                const mergedOptions = Object.assign({}, defaultOptions, options);
                
                // Load CSS if enabled
                if (mergedOptions.loadCSS) {
                    this.loadCSS(mergedOptions.cssPath);
                }
                
                // Load components
                const promises = mergedOptions.components.map(component => {
                    return this.loadComponent(`${mergedOptions.basePath}/${component}.js`);
                });
                
                // Wait for all components to load
                Promise.all(promises)
                    .then(() => {
                        console.log('Switch UI Kit loaded successfully');
                        resolve();
                    })
                    .catch(error => {
                        console.error('Error loading Switch UI Kit:', error);
                        reject(error);
                    });
            });
        },
        
        /**
         * Load a single component
         * @param {string} path - Path to the component script
         * @returns {Promise} - Promise that resolves when the component is loaded
         */
        loadComponent: function(path) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = path;
                script.async = true;
                
                script.onload = () => {
                    resolve();
                };
                
                script.onerror = () => {
                    reject(new Error(`Failed to load component: ${path}`));
                };
                
                document.head.appendChild(script);
            });
        },
        
        /**
         * Load the CSS file
         * @param {string} path - Path to the CSS file
         */
        loadCSS: function(path) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = path;
            document.head.appendChild(link);
        }
    };
    
    // Export the loader
    global.SwitchUIKit.Loader = Loader;
    
    // Auto-load components when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Check if auto-load is enabled
        if (global.SWITCH_UI_KIT_AUTO_LOAD !== false) {
            Loader.loadAll();
        }
    });
    
})(typeof window !== 'undefined' ? window : this);
