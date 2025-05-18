/**
 * Switch Enhanced Hydration - Advanced client-side hydration for server-side rendered components
 * 
 * This script provides enhanced hydration capabilities for the Switch framework:
 * - Progressive hydration: Hydrate components in order of importance
 * - Selective hydration: Only hydrate specific components
 * - Lazy hydration: Hydrate components when they become visible or on interaction
 * - Streaming hydration: Hydrate components as they arrive from the server
 */

(function(global) {
    'use strict';
    
    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before enhanced-hydration.js.');
        return;
    }
    
    // Check if SwitchEnhanced is available
    if (!global.SwitchEnhanced) {
        global.SwitchEnhanced = {};
    }
    
    // Create the hydration module
    const EnhancedHydration = {
        /**
         * Initialize the enhanced hydration system
         */
        init: function() {
            console.log('Initializing Switch Enhanced Hydration...');
            
            // Store references to the original hydration methods
            this.originalHydrate = global.Switch.hydrate;
            
            // Override the original hydration methods
            global.Switch.hydrate = this.hydrateComponent.bind(this);
            
            // Initialize the intersection observer for visibility-based hydration
            this._initIntersectionObserver();
            
            // Initialize event listeners for interaction-based hydration
            this._initInteractionListeners();
            
            console.log('Switch Enhanced Hydration initialized.');
        },
        
        /**
         * Hydrate the root component and all its children
         * 
         * @param {HTMLElement} rootElement - The root element
         * @param {Object} initialData - The initial component data
         * @param {Object} config - Hydration configuration
         */
        hydrateRoot: function(rootElement, initialData, config) {
            console.log('Hydrating root with enhanced hydration:', initialData.name);
            
            // Store the configuration
            this.config = config || {
                enabled: true,
                selective: false,
                components: [],
                streaming: false
            };
            
            // Find all components that need to be hydrated
            const componentElements = rootElement.querySelectorAll('[data-ssr-component]');
            console.log(`Found ${componentElements.length} components to hydrate.`);
            
            // Create a map of components by ID
            this.components = {};
            componentElements.forEach(element => {
                const componentName = element.getAttribute('data-ssr-component');
                const componentId = element.id;
                const hydrationStrategy = element.getAttribute('data-hydration-strategy') || 'eager';
                const isCritical = element.hasAttribute('data-critical');
                
                this.components[componentId] = {
                    element,
                    name: componentName,
                    id: componentId,
                    hydrationStrategy,
                    isCritical,
                    hydrated: false
                };
            });
            
            // Hydrate components based on their strategy
            this._hydrateByStrategy();
        },
        
        /**
         * Hydrate a single component
         * 
         * @param {String|Object} component - Component ID or component object
         * @param {HTMLElement} container - Container element
         * @returns {Object} - Hydrated component
         */
        hydrateComponent: function(component, container) {
            // Get the component ID
            const componentId = typeof component === 'string' ? component : component.id;
            
            // Check if we should hydrate this component
            if (this.config && this.config.selective && !this.config.components.includes(componentId)) {
                console.log(`Skipping hydration for component ${componentId} (not in selective hydration list).`);
                return null;
            }
            
            // Find the component element
            const componentElement = container || document.getElementById(componentId);
            if (!componentElement) {
                console.error(`Component element not found: ${componentId}`);
                return null;
            }
            
            console.log(`Hydrating component: ${componentId}`);
            
            // Call the original hydration method
            const hydratedComponent = this.originalHydrate.call(global.Switch, component, container);
            
            // Mark the component as hydrated
            if (this.components && this.components[componentId]) {
                this.components[componentId].hydrated = true;
            }
            
            // Add the hydrated attribute
            componentElement.setAttribute('data-hydrated', 'true');
            
            return hydratedComponent;
        },
        
        /**
         * Hydrate components based on their strategy
         * 
         * @private
         */
        _hydrateByStrategy: function() {
            // First, hydrate critical components
            this._hydrateCriticalComponents();
            
            // Then, hydrate eager components
            this._hydrateEagerComponents();
            
            // Schedule lazy components for later hydration
            this._scheduleLazyComponents();
            
            // Set up visibility-based hydration
            this._setupVisibilityHydration();
            
            // Set up interaction-based hydration
            this._setupInteractionHydration();
        },
        
        /**
         * Hydrate critical components
         * 
         * @private
         */
        _hydrateCriticalComponents: function() {
            console.log('Hydrating critical components...');
            
            // Find all critical components
            const criticalComponents = Object.values(this.components).filter(component => 
                component.isCritical && !component.hydrated
            );
            
            // Hydrate them
            criticalComponents.forEach(component => {
                this.hydrateComponent(component.id, component.element);
            });
            
            console.log(`Hydrated ${criticalComponents.length} critical components.`);
        },
        
        /**
         * Hydrate eager components
         * 
         * @private
         */
        _hydrateEagerComponents: function() {
            console.log('Hydrating eager components...');
            
            // Find all eager components
            const eagerComponents = Object.values(this.components).filter(component => 
                component.hydrationStrategy === 'eager' && !component.hydrated
            );
            
            // Hydrate them
            eagerComponents.forEach(component => {
                this.hydrateComponent(component.id, component.element);
            });
            
            console.log(`Hydrated ${eagerComponents.length} eager components.`);
        },
        
        /**
         * Schedule lazy components for later hydration
         * 
         * @private
         */
        _scheduleLazyComponents: function() {
            console.log('Scheduling lazy components for hydration...');
            
            // Find all lazy components
            const lazyComponents = Object.values(this.components).filter(component => 
                component.hydrationStrategy === 'lazy' && !component.hydrated
            );
            
            // Schedule them for hydration after a delay
            if (lazyComponents.length > 0) {
                setTimeout(() => {
                    console.log('Hydrating lazy components...');
                    
                    lazyComponents.forEach(component => {
                        if (!component.hydrated) {
                            this.hydrateComponent(component.id, component.element);
                        }
                    });
                    
                    console.log(`Hydrated ${lazyComponents.length} lazy components.`);
                }, 1000); // 1 second delay
            }
        },
        
        /**
         * Set up visibility-based hydration
         * 
         * @private
         */
        _setupVisibilityHydration: function() {
            console.log('Setting up visibility-based hydration...');
            
            // Find all components that should be hydrated when visible
            const visibleComponents = Object.values(this.components).filter(component => 
                component.hydrationStrategy === 'visible' && !component.hydrated
            );
            
            // Observe them
            visibleComponents.forEach(component => {
                this.intersectionObserver.observe(component.element);
            });
            
            console.log(`Observing ${visibleComponents.length} components for visibility.`);
        },
        
        /**
         * Set up interaction-based hydration
         * 
         * @private
         */
        _setupInteractionHydration: function() {
            console.log('Setting up interaction-based hydration...');
            
            // Find all components that should be hydrated on interaction
            const interactiveComponents = Object.values(this.components).filter(component => 
                component.hydrationStrategy === 'interactive' && !component.hydrated
            );
            
            // Add event listeners to them
            interactiveComponents.forEach(component => {
                component.element.setAttribute('data-hydrate-on-interaction', 'true');
            });
            
            console.log(`Set up ${interactiveComponents.length} components for interaction-based hydration.`);
        },
        
        /**
         * Initialize the intersection observer for visibility-based hydration
         * 
         * @private
         */
        _initIntersectionObserver: function() {
            // Create the intersection observer
            this.intersectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        // Get the component element
                        const element = entry.target;
                        const componentId = element.id;
                        
                        // Hydrate the component
                        if (this.components[componentId] && !this.components[componentId].hydrated) {
                            console.log(`Component ${componentId} is now visible, hydrating...`);
                            this.hydrateComponent(componentId, element);
                        }
                        
                        // Stop observing this element
                        this.intersectionObserver.unobserve(element);
                    }
                });
            }, {
                root: null, // viewport
                rootMargin: '0px',
                threshold: 0.1 // 10% visible
            });
        },
        
        /**
         * Initialize event listeners for interaction-based hydration
         * 
         * @private
         */
        _initInteractionListeners: function() {
            // Listen for interactions on the document
            document.addEventListener('mouseover', this._handleInteraction.bind(this), { capture: true });
            document.addEventListener('focusin', this._handleInteraction.bind(this), { capture: true });
            document.addEventListener('touchstart', this._handleInteraction.bind(this), { capture: true });
            document.addEventListener('click', this._handleInteraction.bind(this), { capture: true });
        },
        
        /**
         * Handle interaction events for interaction-based hydration
         * 
         * @param {Event} event - The interaction event
         * @private
         */
        _handleInteraction: function(event) {
            // Find the closest component that needs to be hydrated
            let element = event.target;
            while (element && element !== document) {
                if (element.hasAttribute('data-hydrate-on-interaction')) {
                    const componentId = element.id;
                    
                    // Hydrate the component
                    if (this.components[componentId] && !this.components[componentId].hydrated) {
                        console.log(`User interacted with component ${componentId}, hydrating...`);
                        this.hydrateComponent(componentId, element);
                    }
                    
                    // Remove the attribute to prevent future hydration
                    element.removeAttribute('data-hydrate-on-interaction');
                    break;
                }
                
                element = element.parentElement;
            }
        }
    };
    
    // Expose to global scope
    global.SwitchEnhanced = global.SwitchEnhanced || {};
    global.SwitchEnhanced.hydration = EnhancedHydration;
    
    // Initialize when the DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        EnhancedHydration.init();
        
        // Check if we have initial data for hydration
        if (global.SWITCH_SSR && global.SWITCH_INITIAL_DATA && global.SWITCH_HYDRATION_CONFIG) {
            // Hydrate the root component
            EnhancedHydration.hydrateRoot(
                document.getElementById('switch-root'),
                global.SWITCH_INITIAL_DATA,
                global.SWITCH_HYDRATION_CONFIG
            );
        }
    });
    
})(typeof window !== 'undefined' ? window : this);
