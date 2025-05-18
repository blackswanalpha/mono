/**
 * Switch Framework - A frontend framework for Mono
 * 
 * This is the core client-side JavaScript file for the Switch framework.
 * It provides:
 * 1. Component-based architecture
 * 2. Virtual DOM for efficient updates
 * 3. State management
 * 4. Event handling
 * 5. Routing
 * 6. Enhanced DOM manipulation
 */

(function(global) {
    'use strict';

    // Store components by ID
    const components = {};
    
    // Store component templates
    const templates = {};
    
    // Store routes
    const routes = [];
    
    // Current route
    let currentRoute = null;
    
    // Root element
    let rootElement = null;
    
    /**
     * Switch Framework
     */
    const Switch = {
        /**
         * Initialize the Switch framework
         * @param {Object} options - Configuration options
         */
        init: function(options = {}) {
            console.log('Initializing Switch framework...');
            
            // Set the root element
            rootElement = document.getElementById(options.rootElementId || 'switch-root');
            if (!rootElement) {
                console.error('Root element not found. Please add a div with id "switch-root" to your HTML.');
                return;
            }
            
            // Initialize routing
            this.router.init();
            
            // Render the initial component if provided
            if (global.SWITCH_INITIAL_DATA) {
                this.render(global.SWITCH_INITIAL_DATA);
            }
            
            console.log('Switch framework initialized.');
        },
        
        /**
         * Create a component
         * @param {Object} definition - Component definition
         * @returns {Object} - Component instance
         */
        createComponent: function(definition) {
            const id = definition.id || `switch-component-${Date.now()}`;
            
            // Create the component
            const component = {
                id: id,
                name: definition.name,
                props: definition.props || {},
                state: definition.state || {},
                events: definition.events || {},
                children: definition.children || [],
                render: definition.render || function() { return ''; },
                update: function(newState) {
                    // Update the state
                    Object.assign(this.state, newState);
                    
                    // Re-render the component
                    Switch.renderComponent(this);
                }
            };
            
            // Store the component
            components[id] = component;
            
            return component;
        },
        
        /**
         * Render a component
         * @param {Object} component - Component to render
         * @param {HTMLElement} container - Container element (optional)
         */
        renderComponent: function(component, container) {
            try {
                // Use the provided container or the root element
                const targetContainer = container || rootElement;
                
                if (!targetContainer) {
                    console.error('Target container not found for rendering component:', component.name);
                    return;
                }
                
                // Get the component template
                let template = templates[component.name];
                
                // If no template exists, create one
                if (!template) {
                    template = this.createTemplate(component);
                    templates[component.name] = template;
                }
                
                // Render the component
                const html = this.renderTemplate(template, component);
                
                // Update the DOM using SwitchDOM utilities
                if (global.SwitchDOM) {
                    SwitchDOM.setHTML(targetContainer, html);
                } else {
                    // Fallback to standard DOM API
                    targetContainer.innerHTML = html;
                }
                
                // Attach event handlers
                this.attachEvents(component, targetContainer);
                
                // Render children
                this.renderChildren(component, targetContainer);
                
                // Dispatch a component rendered event
                const event = new CustomEvent('switch:component-rendered', {
                    detail: { component: component }
                });
                document.dispatchEvent(event);
            } catch (error) {
                console.error('Error rendering component:', error);
            }
        },
        
        /**
         * Create a template for a component
         * @param {Object} component - Component
         * @returns {Function} - Template function
         */
        createTemplate: function(component) {
            // If the component has a render function, use it
            if (typeof component.render === 'function') {
                return component.render;
            }
            
            // Otherwise, create a default template
            return function(props, state) {
                return `<div class="switch-component ${component.name.toLowerCase()}" data-component-id="${component.id}">
                    <h2>${component.name}</h2>
                    <div class="switch-component-content"></div>
                </div>`;
            };
        },
        
        /**
         * Render a template
         * @param {Function} template - Template function
         * @param {Object} component - Component
         * @returns {string} - HTML string
         */
        renderTemplate: function(template, component) {
            return template(component.props, component.state);
        },
        
        /**
         * Attach event handlers to a component
         * @param {Object} component - Component
         * @param {HTMLElement} container - Container element
         */
        attachEvents: function(component, container) {
            try {
                if (!container) {
                    console.error('Container not found for attaching events to component:', component.name);
                    return;
                }
                
                // Attach event handlers
                for (const [event, handler] of Object.entries(component.events)) {
                    // Find elements with the event using SwitchDOM utilities
                    let elements = [];
                    
                    if (global.SwitchDOM) {
                        elements = SwitchDOM.querySelectorAll(`[data-event="${event}"]`, container);
                    } else {
                        // Fallback to standard DOM API
                        elements = Array.from(container.querySelectorAll(`[data-event="${event}"]`));
                    }
                    
                    // Attach the event handler
                    elements.forEach(element => {
                        const eventHandler = function(e) {
                            try {
                                // Call the handler
                                if (typeof handler === 'function') {
                                    handler.call(component, e);
                                } else if (typeof handler === 'string') {
                                    // If the handler is a string, it's a server-side handler
                                    Switch.callServerEvent(component.id, handler, {
                                        event: event,
                                        target: e.target.dataset,
                                        value: e.target.value
                                    });
                                }
                            } catch (error) {
                                console.error(`Error in event handler for ${event}:`, error);
                            }
                        };
                        
                        // Use SwitchDOM utilities if available
                        if (global.SwitchDOM) {
                            SwitchDOM.addEventListener(element, event, eventHandler);
                        } else {
                            // Fallback to standard DOM API
                            element.addEventListener(event, eventHandler);
                        }
                        
                        // Store the handler reference for potential cleanup
                        if (!element._switchEventHandlers) {
                            element._switchEventHandlers = {};
                        }
                        element._switchEventHandlers[event] = eventHandler;
                    });
                }
                
                // Also handle data-action attributes for common actions
                this.attachActionHandlers(component, container);
            } catch (error) {
                console.error('Error attaching events:', error);
            }
        },
        
        /**
         * Attach action handlers to elements with data-action attributes
         * @param {Object} component - Component
         * @param {HTMLElement} container - Container element
         */
        attachActionHandlers: function(component, container) {
            try {
                // Find elements with data-action attribute
                let elements = [];
                
                if (global.SwitchDOM) {
                    elements = SwitchDOM.querySelectorAll('[data-action]', container);
                } else {
                    elements = Array.from(container.querySelectorAll('[data-action]'));
                }
                
                // Attach click handlers for actions
                elements.forEach(element => {
                    const action = element.dataset.action;
                    
                    const actionHandler = function(e) {
                        try {
                            // Prevent default for links
                            if (element.tagName.toLowerCase() === 'a') {
                                e.preventDefault();
                            }
                            
                            // Handle common actions
                            switch (action) {
                                case 'navigate':
                                    const page = element.dataset.page;
                                    if (page) {
                                        // Update URL
                                        const url = page === 'home' ? '/' : `/${page}`;
                                        history.pushState({}, '', url);
                                        
                                        // Call component method if available
                                        if (component.setCurrentPage) {
                                            component.setCurrentPage(page);
                                        }
                                    }
                                    break;
                                    
                                case 'toggle-dropdown':
                                    const dropdown = element.closest('.dropdown');
                                    if (dropdown) {
                                        if (global.SwitchDOM) {
                                            SwitchDOM.toggleClass(dropdown, 'show');
                                            const menu = SwitchDOM.querySelector('.dropdown-menu', dropdown);
                                            if (menu) SwitchDOM.toggleClass(menu, 'show');
                                        } else {
                                            dropdown.classList.toggle('show');
                                            const menu = dropdown.querySelector('.dropdown-menu');
                                            if (menu) menu.classList.toggle('show');
                                        }
                                    }
                                    break;
                                    
                                default:
                                    // Call component method if it exists
                                    const methodName = action.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                                    if (component[methodName] && typeof component[methodName] === 'function') {
                                        component[methodName](e);
                                    }
                            }
                        } catch (error) {
                            console.error(`Error in action handler for ${action}:`, error);
                        }
                    };
                    
                    // Use SwitchDOM utilities if available
                    if (global.SwitchDOM) {
                        SwitchDOM.addEventListener(element, 'click', actionHandler);
                    } else {
                        element.addEventListener('click', actionHandler);
                    }
                    
                    // Store the handler reference
                    if (!element._switchActionHandler) {
                        element._switchActionHandler = actionHandler;
                    }
                });
            } catch (error) {
                console.error('Error attaching action handlers:', error);
            }
        },
        
        /**
         * Render children of a component
         * @param {Object} component - Component
         * @param {HTMLElement} container - Container element
         */
        renderChildren: function(component, container) {
            // Find child containers
            const childContainers = container.querySelectorAll('[data-child-container]');
            
            // Render each child
            component.children.forEach((child, index) => {
                // Get the child component
                const childComponent = components[child.id] || this.createComponent(child);
                
                // Get the container for this child
                const childContainer = childContainers[index] || container.querySelector('.switch-component-content');
                
                // Render the child
                this.renderComponent(childComponent, childContainer);
            });
        },
        
        /**
         * Call a server-side event handler
         * @param {string} componentId - Component ID
         * @param {string} handler - Handler name
         * @param {Object} data - Event data
         */
        callServerEvent: function(componentId, handler, data) {
            // Make an API request to the server
            fetch('/api/switch/event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    componentId: componentId,
                    handler: handler,
                    data: data
                })
            })
            .then(response => response.json())
            .then(result => {
                // If the result includes a state update, apply it
                if (result.state && components[componentId]) {
                    components[componentId].update(result.state);
                }
            })
            .catch(error => {
                console.error('Error calling server event:', error);
            });
        },
        
        /**
         * Render the initial component
         * @param {Object} data - Component data
         */
        render: function(data) {
            // Create the component
            const component = this.createComponent(data);
            
            // Render the component
            this.renderComponent(component);
        },
        
        /**
         * Router for client-side routing
         */
        router: {
            /**
             * Initialize the router
             */
            init: function() {
                // Handle navigation events
                window.addEventListener('popstate', this.handleNavigation.bind(this));
                
                // Handle initial navigation
                this.handleNavigation();
            },
            
            /**
             * Add a route
             * @param {string} path - Route path
             * @param {Function} handler - Route handler
             */
            addRoute: function(path, handler) {
                routes.push({ path, handler });
            },
            
            /**
             * Navigate to a path
             * @param {string} path - Path to navigate to
             * @param {Object} state - State to pass to the route
             */
            navigate: function(path, state = {}) {
                // Update the URL
                history.pushState(state, '', path);
                
                // Handle the navigation
                this.handleNavigation();
            },
            
            /**
             * Handle navigation events
             */
            handleNavigation: function() {
                // Get the current path
                const path = window.location.pathname;
                
                // Find a matching route
                const route = routes.find(route => {
                    // Convert route path to regex
                    const pattern = route.path.replace(/:\w+/g, '([^/]+)');
                    const regex = new RegExp(`^${pattern}$`);
                    
                    // Test the path
                    return regex.test(path);
                });
                
                // If a route was found, call its handler
                if (route) {
                    // Extract parameters
                    const params = {};
                    const paramNames = route.path.match(/:\w+/g) || [];
                    const paramValues = path.match(new RegExp(route.path.replace(/:\w+/g, '([^/]+)')));
                    
                    if (paramValues) {
                        paramNames.forEach((name, index) => {
                            params[name.substring(1)] = paramValues[index + 1];
                        });
                    }
                    
                    // Call the handler
                    route.handler(params);
                    
                    // Update the current route
                    currentRoute = route;
                }
            }
        }
    };
    
    // Export the Switch framework
    global.Switch = Switch;
    
    // Initialize the framework when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        Switch.init();
    });
    
})(typeof window !== 'undefined' ? window : this);
