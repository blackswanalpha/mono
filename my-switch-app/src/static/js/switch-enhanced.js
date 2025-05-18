/**
 * Switch Enhanced - Extended functionality for the Switch framework
 *
 * This file adds support for:
 * 1. Parent-child relationships between components
 * 2. Frames for component organization
 * 3. Layouts for component arrangement
 * 4. Event bubbling through the component hierarchy
 */

(function(global) {
    'use strict';

    // Store components by ID
    const components = {};

    // Store frames by ID
    const frames = {};

    // Store layouts by ID
    const layouts = {};

    // Component registry
    const componentRegistry = {};

    // Frame registry
    const frameRegistry = {};

    // Layout registry
    const layoutRegistry = {};

    /**
     * Switch Enhanced Framework
     */
    const SwitchEnhanced = {
        /**
         * Initialize the enhanced Switch framework
         * @param {Object} options - Configuration options
         */
        init: function(options = {}) {
            console.log('Initializing Switch Enhanced framework...');

            // Set default options
            this.options = Object.assign({
                rootElementId: 'switch-root',
                debug: false,
                hmr: false,
                ssr: false
            }, options);

            // Set the root element
            this.rootElement = document.getElementById(this.options.rootElementId);
            if (!this.rootElement) {
                console.error('Root element not found. Please add a div with id "' + this.options.rootElementId + '" to your HTML.');
                return;
            }

            // Initialize the component system
            this.component.init();

            // Initialize the frame system
            this.frame.init();

            // Initialize the layout system
            this.layout.init();

            // Initialize the event system
            this.event.init();

            // Initialize HMR if enabled
            if (this.options.hmr) {
                this.hmr.init();
            }

            console.log('Switch Enhanced framework initialized.');

            // Render the initial component if provided
            if (global.SWITCH_INITIAL_DATA) {
                this.render(global.SWITCH_INITIAL_DATA);
            }
        },

        /**
         * Render a component
         * @param {Object} data - Component data
         * @param {HTMLElement} container - Container element (optional)
         */
        render: function(data, container) {
            // Use the provided container or the root element
            const targetContainer = container || this.rootElement;

            // Create the component
            const component = this.component.create(data);

            // Render the component
            this.component.render(component, targetContainer);

            return component;
        },

        /**
         * Component system
         */
        component: {
            /**
             * Initialize the component system
             */
            init: function() {
                console.log('Initializing component system...');

                // Load component registry
                this.loadRegistry();
            },

            /**
             * Load the component registry
             */
            loadRegistry: function() {
                // Fetch the component registry from the server
                fetch('/switch-api/components')
                    .then(response => response.json())
                    .then(data => {
                        // Store the component registry
                        data.forEach(component => {
                            componentRegistry[component.name] = component;
                        });

                        console.log('Component registry loaded:', Object.keys(componentRegistry).length, 'components');
                    })
                    .catch(error => {
                        console.error('Error loading component registry:', error);
                    });
            },

            /**
             * Create a component
             * @param {Object} data - Component data
             * @returns {Object} - Component instance
             */
            create: function(data) {
                const id = data.id || `switch-component-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

                // Create the component
                const component = {
                    id: id,
                    name: data.name,
                    props: data.props || {},
                    state: data.state || {},
                    children: data.children || [],
                    parent: null,
                    frame: null,
                    layout: null,
                    events: {},

                    // Add a child component
                    addChild: function(child) {
                        this.children.push(child);
                        child.parent = this;
                    },

                    // Remove a child component
                    removeChild: function(child) {
                        const index = this.children.indexOf(child);
                        if (index !== -1) {
                            this.children.splice(index, 1);
                            child.parent = null;
                        }
                    },

                    // Update the component state
                    setState: function(newState) {
                        // Update the state
                        Object.assign(this.state, newState);

                        // Re-render the component
                        SwitchEnhanced.component.render(this);
                    },

                    // Add an event listener
                    addEventListener: function(event, callback) {
                        if (!this.events[event]) {
                            this.events[event] = [];
                        }

                        this.events[event].push(callback);
                    },

                    // Remove an event listener
                    removeEventListener: function(event, callback) {
                        if (!this.events[event]) {
                            return;
                        }

                        const index = this.events[event].indexOf(callback);
                        if (index !== -1) {
                            this.events[event].splice(index, 1);
                        }
                    },

                    // Dispatch an event
                    dispatchEvent: function(event, data) {
                        // Call event listeners on this component
                        if (this.events[event]) {
                            this.events[event].forEach(callback => {
                                callback(data);
                            });
                        }

                        // Bubble the event up to the parent
                        if (this.parent) {
                            this.parent.dispatchEvent(event, data);
                        }
                    }
                };

                // Store the component
                components[id] = component;

                // Add children
                if (data.children && data.children.length) {
                    data.children.forEach(childData => {
                        const child = this.create(childData);
                        component.addChild(child);
                    });
                }

                return component;
            },

            /**
             * Render a component
             * @param {Object} component - Component to render
             * @param {HTMLElement} container - Container element
             */
            render: function(component, container) {
                try {
                    // Use the provided container or find the component's container
                    const targetContainer = container || document.getElementById(component.id);

                    if (!targetContainer) {
                        console.error('Target container not found for rendering component:', component.name);
                        return;
                    }

                    // Get the component template
                    this.getTemplate(component)
                        .then(template => {
                            // Render the component
                            const html = this.renderTemplate(template, component);

                            // Update the DOM
                            targetContainer.innerHTML = html;

                            // Add component ID to the container
                            targetContainer.setAttribute('data-component-id', component.id);

                            // Attach event handlers
                            this.attachEvents(component, targetContainer);

                            // Render children
                            this.renderChildren(component, targetContainer);

                            // Dispatch a component rendered event
                            const event = new CustomEvent('switch:component-rendered', {
                                detail: { component: component }
                            });
                            document.dispatchEvent(event);
                        })
                        .catch(error => {
                            console.error('Error rendering component:', error);
                        });
                } catch (error) {
                    console.error('Error rendering component:', error);
                }
            },

            /**
             * Get the component template
             * @param {Object} component - Component
             * @returns {Promise<string>} - Template HTML
             */
            getTemplate: function(component) {
                return new Promise((resolve, reject) => {
                    // Check if we have the component in the registry
                    if (componentRegistry[component.name]) {
                        // Fetch the component file
                        fetch(componentRegistry[component.name].path)
                            .then(response => response.text())
                            .then(content => {
                                // Extract the render function
                                const renderMatch = content.match(/function\s+render\s*\(\s*\)\s*{([\s\S]*?)return\s+`([\s\S]*?)`\s*;?\s*}/);

                                if (renderMatch && renderMatch[2]) {
                                    // Get the HTML template
                                    let html = renderMatch[2];

                                    // Process any template includes with @ symbol
                                    html = this.processTemplateIncludes(html);

                                    resolve(html);
                                } else {
                                    reject(new Error('Could not extract render function from component'));
                                }
                            })
                            .catch(error => {
                                reject(error);
                            });
                    } else {
                        // Use a default template
                        resolve(`<div class="switch-component switch-component-${component.name.toLowerCase()}">
                            <h2>${component.name}</h2>
                            <div class="switch-component-content" data-child-container></div>
                        </div>`);
                    }
                });
            },

            /**
             * Process template includes with @ symbol
             * @param {string} content - Template content
             * @returns {string} - Processed content
             */
            processTemplateIncludes: function(content) {
                // Match {{ '@/path/to/file' }} pattern
                const includeRegex = /{{\s*['"]@\/([^'"]+)['"]\s*}}/g;

                // Replace all includes with the actual content
                return content.replace(includeRegex, (_, includePath) => {
                    // Resolve the path relative to the src directory
                    const fullPath = includePath.startsWith('src/') ? includePath : `src/${includePath}`;
                    console.log(`Including file: ${fullPath}`);

                    try {
                        // Try to fetch the file synchronously
                        const xhr = new XMLHttpRequest();
                        xhr.open('GET', fullPath, false); // false makes it synchronous
                        xhr.send(null);

                        if (xhr.status === 200) {
                            return `<!-- @include: ${fullPath} -->\n${xhr.responseText}`;
                        } else {
                            console.error(`Failed to load include: ${fullPath}`);
                            return `<!-- Failed to include: ${fullPath} -->`;
                        }
                    } catch (error) {
                        console.error(`Error including file: ${fullPath}`, error);
                        return `<!-- Error including: ${fullPath} -->`;
                    }
                });
            },

            /**
             * Render a template with component data
             * @param {string} template - Template HTML
             * @param {Object} component - Component
             * @returns {string} - Rendered HTML
             */
            renderTemplate: function(template, component) {
                // Replace ${this.props.xxx} variables
                let html = template.replace(/\${this\.props\.([a-zA-Z0-9_]+)}/g, (match, propName) => {
                    if (propName in component.props) {
                        return component.props[propName];
                    }
                    return match; // Keep original if not found
                });

                // Replace ${this.state.xxx} variables
                html = html.replace(/\${this\.state\.([a-zA-Z0-9_]+)}/g, (match, stateName) => {
                    if (stateName in component.state) {
                        return component.state[stateName];
                    }
                    return match; // Keep original if not found
                });

                // Replace ${this.children} with a placeholder for child components
                html = html.replace(/\${this\.children}/g, '<div data-child-container></div>');

                return html;
            },

            /**
             * Attach event handlers to a component
             * @param {Object} component - Component
             * @param {HTMLElement} container - Container element
             */
            attachEvents: function(component, container) {
                // Find all elements with data-event attribute
                const eventElements = container.querySelectorAll('[data-event]');

                // Attach event handlers
                eventElements.forEach(element => {
                    const eventName = element.getAttribute('data-event');
                    const actionName = element.getAttribute('data-action');

                    // Remove any existing event listeners
                    const newElement = element.cloneNode(true);
                    element.parentNode.replaceChild(newElement, element);

                    // Add new event listener
                    newElement.addEventListener(eventName, event => {
                        // Prevent default for links
                        if (newElement.tagName === 'A') {
                            event.preventDefault();
                        }

                        // Dispatch the event to the component
                        component.dispatchEvent(actionName, {
                            event: event,
                            element: newElement,
                            component: component
                        });
                    });
                });
            },

            /**
             * Render children of a component
             * @param {Object} component - Component
             * @param {HTMLElement} container - Container element
             */
            renderChildren: function(component, container) {
                // Find child containers
                const childContainers = container.querySelectorAll('[data-child-container]');

                // If no child containers and no children, return
                if (childContainers.length === 0 && component.children.length === 0) {
                    return;
                }

                // If no child containers but we have children, create a container
                if (childContainers.length === 0 && component.children.length > 0) {
                    const childContainer = document.createElement('div');
                    childContainer.setAttribute('data-child-container', '');
                    container.appendChild(childContainer);

                    // Render all children in this container
                    component.children.forEach(child => {
                        this.render(child, childContainer);
                    });

                    return;
                }

                // Render each child in its own container
                component.children.forEach((child, index) => {
                    // Get the container for this child
                    const childContainer = childContainers[index] || childContainers[0];

                    // Render the child
                    this.render(child, childContainer);
                });
            }
        },

        /**
         * Frame system
         */
        frame: {
            /**
             * Initialize the frame system
             */
            init: function() {
                console.log('Initializing frame system...');

                // Load frame registry
                this.loadRegistry();
            },

            /**
             * Load the frame registry
             */
            loadRegistry: function() {
                // Fetch the frame registry from the server
                fetch('/switch-api/frames')
                    .then(response => response.json())
                    .then(data => {
                        // Store the frame registry
                        data.forEach(frame => {
                            frameRegistry[frame.name] = frame;
                        });

                        console.log('Frame registry loaded:', Object.keys(frameRegistry).length, 'frames');
                    })
                    .catch(error => {
                        console.error('Error loading frame registry:', error);
                    });
            },

            /**
             * Create a frame
             * @param {Object} data - Frame data
             * @returns {Object} - Frame instance
             */
            create: function(data) {
                const id = data.id || `switch-frame-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

                // Create the frame
                const frame = {
                    id: id,
                    name: data.name,
                    state: data.state || {},
                    components: [],
                    parent: null,
                    children: [],

                    // Add a component to the frame
                    addComponent: function(component) {
                        this.components.push(component);
                        component.frame = this;
                    },

                    // Remove a component from the frame
                    removeComponent: function(component) {
                        const index = this.components.indexOf(component);
                        if (index !== -1) {
                            this.components.splice(index, 1);
                            component.frame = null;
                        }
                    },

                    // Add a child frame
                    addChild: function(child) {
                        this.children.push(child);
                        child.parent = this;
                    },

                    // Remove a child frame
                    removeChild: function(child) {
                        const index = this.children.indexOf(child);
                        if (index !== -1) {
                            this.children.splice(index, 1);
                            child.parent = null;
                        }
                    },

                    // Update the frame state
                    setState: function(newState) {
                        // Update the state
                        Object.assign(this.state, newState);

                        // Update all components in the frame
                        this.components.forEach(component => {
                            SwitchEnhanced.component.render(component);
                        });
                    }
                };

                // Store the frame
                frames[id] = frame;

                return frame;
            }
        },

        /**
         * Layout system
         */
        layout: {
            /**
             * Initialize the layout system
             */
            init: function() {
                console.log('Initializing layout system...');

                // Load layout registry
                this.loadRegistry();
            },

            /**
             * Load the layout registry
             */
            loadRegistry: function() {
                // Fetch the layout registry from the server
                fetch('/switch-api/layouts')
                    .then(response => response.json())
                    .then(data => {
                        // Store the layout registry
                        data.forEach(layout => {
                            layoutRegistry[layout.name] = layout;
                        });

                        console.log('Layout registry loaded:', Object.keys(layoutRegistry).length, 'layouts');
                    })
                    .catch(error => {
                        console.error('Error loading layout registry:', error);
                    });
            },

            /**
             * Create a layout
             * @param {Object} data - Layout data
             * @returns {Object} - Layout instance
             */
            create: function(data) {
                const id = data.id || `switch-layout-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

                // Create the layout
                const layout = {
                    id: id,
                    name: data.name,
                    components: [],

                    // Add a component to the layout
                    addComponent: function(component) {
                        this.components.push(component);
                        component.layout = this;
                    },

                    // Remove a component from the layout
                    removeComponent: function(component) {
                        const index = this.components.indexOf(component);
                        if (index !== -1) {
                            this.components.splice(index, 1);
                            component.layout = null;
                        }
                    },

                    // Apply the layout to a container
                    apply: function(container) {
                        // Apply layout styles to the container
                        container.classList.add(`switch-layout-${this.name.toLowerCase()}`);

                        // Apply layout to all components
                        this.components.forEach(component => {
                            const componentElement = document.getElementById(component.id);
                            if (componentElement) {
                                componentElement.classList.add(`switch-layout-item`);
                            }
                        });
                    }
                };

                // Store the layout
                layouts[id] = layout;

                return layout;
            }
        },

        /**
         * Event system
         */
        event: {
            /**
             * Initialize the event system
             */
            init: function() {
                console.log('Initializing event system...');

                // Set up global event listeners
                this.setupGlobalListeners();
            },

            /**
             * Set up global event listeners
             */
            setupGlobalListeners: function() {
                // Listen for component rendered events
                document.addEventListener('switch:component-rendered', event => {
                    console.log('Component rendered:', event.detail.component.name);
                });

                // Listen for navigation events
                document.addEventListener('click', event => {
                    // Check if this is a navigation link
                    const link = event.target.closest('a[data-nav="true"]');
                    if (link) {
                        // Prevent default link behavior
                        event.preventDefault();

                        // Get the href
                        const href = link.getAttribute('href');

                        // Navigate to the path
                        this.navigate(href);
                    }
                });
            },

            /**
             * Navigate to a path
             * @param {string} path - Path to navigate to
             */
            navigate: function(path) {
                console.log('Navigating to:', path);

                // Update URL
                if (path.startsWith('#')) {
                    window.location.hash = path.substring(1);
                } else if (path === '/') {
                    history.pushState({}, '', '/');
                    window.location.hash = '';
                } else {
                    window.location.hash = path;
                }

                // Dispatch a navigation event
                const event = new CustomEvent('switch:navigation', {
                    detail: { path: path }
                });
                document.dispatchEvent(event);
            }
        },

        /**
         * Hot Module Replacement (HMR) system
         */
        hmr: {
            /**
             * Initialize the HMR system
             */
            init: function() {
                console.log('Initializing HMR system...');

                // Set up polling for changes
                this.setupPolling();
            },

            /**
             * Set up polling for changes
             */
            setupPolling: function() {
                // Poll for changes every 2 seconds
                setInterval(() => {
                    this.checkForChanges();
                }, 2000);
            },

            /**
             * Check for changes
             */
            checkForChanges: function() {
                // Fetch changes from the server
                fetch('/switch-api/hmr')
                    .then(response => response.json())
                    .then(data => {
                        // Process changes
                        if (data.changes && data.changes.length > 0) {
                            console.log('Changes detected:', data.changes);

                            // Handle each change
                            data.changes.forEach(change => {
                                this.handleChange(change);
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error checking for changes:', error);
                    });
            },

            /**
             * Handle a change
             * @param {Object} change - Change object
             */
            handleChange: function(change) {
                console.log('Handling change:', change);

                // Handle different change types
                if (change.type === 'modified') {
                    // Reload the component
                    this.reloadComponent(change.path);
                } else if (change.type === 'added') {
                    // Add the component to the registry
                    this.addComponent(change.path);
                } else if (change.type === 'deleted') {
                    // Remove the component from the registry
                    this.removeComponent(change.path);
                }
            },

            /**
             * Reload a component
             * @param {string} path - Component path
             */
            reloadComponent: function(path) {
                console.log('Reloading component:', path);

                // Fetch the component
                fetch(path)
                    .then(response => response.text())
                    .then(content => {
                        // Extract the component name
                        const componentNameMatch = content.match(/component\s+([A-Za-z0-9_]+)/);
                        if (!componentNameMatch) return;

                        const componentName = componentNameMatch[1];

                        // Update the component in the registry
                        componentRegistry[componentName] = {
                            path: path,
                            name: componentName,
                            type: 'component'
                        };

                        // Find all instances of this component
                        const componentInstances = Object.values(components).filter(c => c.name === componentName);

                        // Re-render all instances
                        componentInstances.forEach(component => {
                            SwitchEnhanced.component.render(component);
                        });

                        console.log(`Reloaded component ${componentName} (${componentInstances.length} instances)`);
                    })
                    .catch(error => {
                        console.error('Error reloading component:', error);
                    });
            },

            /**
             * Add a component to the registry
             * @param {string} path - Component path
             */
            addComponent: function(path) {
                console.log('Adding component:', path);

                // Fetch the component
                fetch(path)
                    .then(response => response.text())
                    .then(content => {
                        // Extract the component name
                        const componentNameMatch = content.match(/component\s+([A-Za-z0-9_]+)/);
                        if (!componentNameMatch) return;

                        const componentName = componentNameMatch[1];

                        // Add the component to the registry
                        componentRegistry[componentName] = {
                            path: path,
                            name: componentName,
                            type: 'component'
                        };

                        console.log(`Added component ${componentName} to registry`);
                    })
                    .catch(error => {
                        console.error('Error adding component:', error);
                    });
            },

            /**
             * Remove a component from the registry
             * @param {string} path - Component path
             */
            removeComponent: function(path) {
                console.log('Removing component:', path);

                // Find the component in the registry
                const componentName = Object.keys(componentRegistry).find(name => componentRegistry[name].path === path);

                if (componentName) {
                    // Remove the component from the registry
                    delete componentRegistry[componentName];

                    console.log(`Removed component ${componentName} from registry`);
                }
            }
        }
    };

    // Expose the framework to the global scope
    global.SwitchEnhanced = SwitchEnhanced;

    // Initialize the framework when the DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize with options from global SWITCH_ENV
        SwitchEnhanced.init(global.SWITCH_ENV || {});
    });
})