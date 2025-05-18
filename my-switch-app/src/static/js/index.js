/**
 * Mono Display Engine - index.js
 *
 * This file serves as the main entry point for displaying Mono components in the browser.
 * It provides functionality to:
 * 1. Load and parse Mono components
 * 2. Render components to the DOM
 * 3. Handle component state updates
 * 4. Manage component lifecycle
 * 5. Handle events and routing
 */

(function(global) {
    'use strict';

    // MonoDisplay namespace
    const MonoDisplay = {
        // Configuration
        config: {
            rootElementId: 'switch-root',
            debug: true,
            autoRender: true,
            hmr: true
        },

        // State
        state: {
            components: {},
            currentComponent: null,
            isInitialized: false,
            pendingUpdates: []
        },

        /**
         * Initialize the Mono Display Engine
         * @param {Object} options - Configuration options
         */
        init: function(options = {}) {
            console.log('Initializing Mono Display Engine...');

            // Merge options with default config
            this.config = { ...this.config, ...options };

            // Set the root element
            const rootElement = document.getElementById(this.config.rootElementId) || document.getElementById('switch-root');
            if (!rootElement) {
                console.error('Root element not found. Please add a div with id "mono-root" or "switch-root" to your HTML.');
                return;
            }

            // Store the root element
            this.rootElement = rootElement;

            // Initialize the component loader
            this.initComponentLoader();

            // Initialize the router
            this.initRouter();

            // Initialize event handling
            this.initEventHandling();

            // Mark as initialized
            this.state.isInitialized = true;

            // Auto-render if configured
            if (this.config.autoRender && global.SWITCH_INITIAL_DATA) {
                this.renderInitialComponent(global.SWITCH_INITIAL_DATA);
            }

            console.log('Mono Display Engine initialized.');
        },

        /**
         * Initialize the component loader
         */
        initComponentLoader: function() {
            // Create a component loader
            this.componentLoader = {
                /**
                 * Load a component
                 * @param {string} name - Component name
                 * @param {Function} callback - Callback function
                 */
                load: function(name, callback) {
                    // Check if the component is already loaded
                    if (MonoDisplay.state.components[name]) {
                        callback(MonoDisplay.state.components[name]);
                        return;
                    }

                    // Load the component
                    fetch(`/src/pages/${name.toLowerCase()}.mono`)
                        .then(response => {
                            if (!response.ok) {
                                // Try fallback location
                                return fetch(`/src/components/${name.toLowerCase()}.mono`);
                            }
                            return response;
                        })
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Failed to load component: ${name}`);
                            }
                            return response.text();
                        })
                        .then(source => {
                            // Parse the component
                            const component = MonoDisplay.parseComponent(source, name);

                            // Store the component
                            MonoDisplay.state.components[name] = component;

                            // Call the callback
                            callback(component);
                        })
                        .catch(error => {
                            console.error(`Error loading component ${name}:`, error);
                            callback(null);
                        });
                },

                /**
                 * Load a Mono component directly
                 * @param {string} path - Path to the component
                 * @param {Function} callback - Callback function
                 */
                loadFromPath: function(path, callback) {
                    fetch(path)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Failed to load component from path: ${path}`);
                            }
                            return response.text();
                        })
                        .then(source => {
                            // Extract the component name from the path
                            const name = path.split('/').pop().replace('.mono', '');

                            // Parse the component
                            const component = MonoDisplay.parseComponent(source, name);

                            // Store the component
                            MonoDisplay.state.components[name] = component;

                            // Call the callback
                            callback(component);
                        })
                        .catch(error => {
                            console.error(`Error loading component from path ${path}:`, error);
                            callback(null);
                        });
                }
            };
        },

        /**
         * Parse a Mono component
         * @param {string} source - Component source code
         * @param {string} name - Component name
         * @returns {Object} - Parsed component
         */
        parseComponent: function(source, name) {
            console.log(`Parsing Mono component: ${name}`);

            try {
                // Log the source for debugging
                console.log(`Source content (first 100 chars): ${source.substring(0, 100)}...`);

                // Extract component definition - use a more robust approach
                // This regex looks for a component declaration that spans multiple lines
                const componentRegex = /component\s+(\w+)\s*{([\s\S]*?)(?=\n\s*\/\/\s*Export|\n\s*$)/;
                const componentMatch = source.match(componentRegex);

                if (!componentMatch) {
                    console.error(`Failed to parse component: ${name}`);
                    console.error(`Source content length: ${source.length}`);
                    // Try a simpler regex as fallback
                    const simpleRegex = /component\s+(\w+)/;
                    const simpleMatch = source.match(simpleRegex);

                    if (simpleMatch) {
                        console.log(`Found component name with simple regex: ${simpleMatch[1]}`);
                        // Create a basic component with the name
                        return {
                            name: simpleMatch[1],
                            source: source,
                            state: { title: simpleMatch[1] },
                            props: {},
                            render: function() {
                                return `
                                    <div class="mono-component ${simpleMatch[1].toLowerCase()}">
                                        <h2>${simpleMatch[1]}</h2>
                                        <p>Component source was loaded but could not be fully parsed.</p>
                                        <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 10px; border-radius: 5px;">${source.substring(0, 500)}...</pre>
                                    </div>
                                `;
                            }
                        };
                    }

                    return this.createFallbackComponent(name);
                }

                const componentName = componentMatch[1];
                const componentBody = componentMatch[2];

                console.log(`Found component: ${componentName}`);

                // Extract state
                const stateRegex = /state\s*{([\s\S]*?)}/;
                const stateMatch = componentBody.match(stateRegex);
                const stateObj = {};

                if (stateMatch) {
                    const stateBody = stateMatch[1];
                    console.log(`Found state section: ${stateBody.substring(0, 100)}...`);

                    // Extract string properties
                    const stringPropsRegex = /(\w+)\s*:\s*string\s*=\s*"([^"]*)"/g;
                    let stringMatch;
                    while ((stringMatch = stringPropsRegex.exec(stateBody)) !== null) {
                        stateObj[stringMatch[1]] = stringMatch[2];
                    }

                    // Extract array properties
                    const arrayRegex = /(\w+)\s*:\s*array\s*=\s*(\[[\s\S]*?\])/g;
                    let arrayMatch;
                    while ((arrayMatch = arrayRegex.exec(stateBody)) !== null) {
                        try {
                            console.log(`Attempting to parse array: ${arrayMatch[2]}`);

                            // Create a safer array parsing approach
                            // First, create a simple array with placeholder objects
                            const rawArray = arrayMatch[2];

                            // Count the number of objects in the array by counting opening braces
                            const objectCount = (rawArray.match(/{/g) || []).length;

                            // Create an array with that many empty objects
                            stateObj[arrayMatch[1]] = Array(objectCount).fill().map(() => ({}));

                            console.log(`Created array with ${objectCount} placeholder objects`);
                        } catch (e) {
                            console.error(`Error parsing array state property ${arrayMatch[1]}:`, e, "Original value:", arrayMatch[2]);
                            stateObj[arrayMatch[1]] = [];
                        }
                    }

                    // Extract number properties
                    const numberPropsRegex = /(\w+)\s*:\s*number\s*=\s*([0-9.]+)/g;
                    let numberMatch;
                    while ((numberMatch = numberPropsRegex.exec(stateBody)) !== null) {
                        stateObj[numberMatch[1]] = parseFloat(numberMatch[2]);
                    }

                    // Extract boolean properties
                    const boolPropsRegex = /(\w+)\s*:\s*boolean\s*=\s*(true|false)/g;
                    let boolMatch;
                    while ((boolMatch = boolPropsRegex.exec(stateBody)) !== null) {
                        stateObj[boolMatch[1]] = boolMatch[2] === 'true';
                    }

                    console.log(`Parsed state:`, stateObj);
                }

                // Extract all functions
                const functionsObj = {};
                const functionRegex = /function\s+(\w+)\s*\([^)]*\)\s*{([\s\S]*?)(?=\n\s*function|\n\s*}$)/g;
                let functionMatch;

                while ((functionMatch = functionRegex.exec(componentBody)) !== null) {
                    const funcName = functionMatch[1];
                    const funcBody = functionMatch[2];

                    console.log(`Found function: ${funcName}`);

                    // Store the function body for later use
                    functionsObj[funcName] = funcBody;
                }

                // Create the component object with all the extracted information
                const component = {
                    name: componentName,
                    source: source,
                    state: stateObj,
                    props: {},
                    functions: functionsObj,

                    // Add helper methods for rendering
                    renderFeatures: function() {
                        if (!this.state.features || !Array.isArray(this.state.features)) {
                            return '<div>No features found</div>';
                        }

                        let html = '';

                        for (let i = 0; i < this.state.features.length; i++) {
                            const feature = this.state.features[i];

                            html += `
                                <div class="col-md-4 mb-4">
                                    <div class="card h-100">
                                        <div class="card-body">
                                            <div class="d-flex align-items-center mb-3">
                                                <div class="feature-icon text-primary">
                                                    <i class="bi bi-${feature.icon}"></i>
                                                </div>
                                                <h4 class="mb-0 ms-3">${feature.title}</h4>
                                            </div>
                                            <p class="mb-0">${feature.description}</p>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }

                        return html;
                    },

                    // Main render function
                    render: function() {
                        console.log(`Rendering component ${this.name} with state:`, this.state);

                        // If we have a render function body, use it
                        if (this.functions.render) {
                            // Extract the template string from the render function
                            const templateRegex = /return\s+`([\s\S]*?)`\s*;/;
                            const templateMatch = this.functions.render.match(templateRegex);

                            if (templateMatch) {
                                const template = templateMatch[1];

                                // Replace template variables with actual values
                                const html = template.replace(/\${([^}]*)}/g, (match, expr) => {
                                    try {
                                        // Handle this.state references
                                        if (expr.startsWith('this.state.')) {
                                            const prop = expr.replace('this.state.', '');
                                            const value = this.state[prop];

                                            // Handle different types of values
                                            if (value === undefined) {
                                                return '';
                                            } else if (Array.isArray(value)) {
                                                // For arrays, return a simple representation
                                                return `Array(${value.length})`;
                                            } else if (typeof value === 'object' && value !== null) {
                                                // For objects, return a simple representation
                                                return 'Object';
                                            } else {
                                                return value;
                                            }
                                        }

                                        // Handle this.renderFeatures() call
                                        if (expr.trim() === 'this.renderFeatures()') {
                                            return this.renderFeatures();
                                        }

                                        // Handle other function calls
                                        if (expr.startsWith('this.') && expr.includes('(')) {
                                            const funcName = expr.substring(5, expr.indexOf('('));
                                            if (typeof this[funcName] === 'function') {
                                                return this[funcName]();
                                            }
                                        }

                                        console.warn(`Unhandled template expression: ${expr}`);
                                        return '';
                                    } catch (error) {
                                        console.error(`Error processing template variable: ${expr}`, error);
                                        return `[Error: ${error.message}]`;
                                    }
                                });

                                return html;
                            }
                        }

                        // Fallback rendering
                        return `
                            <div class="mono-component ${this.name.toLowerCase()}">
                                <h2>${this.state.title || this.name}</h2>
                                <p>Component rendered with basic information.</p>
                                <pre>${JSON.stringify(this.state, null, 2)}</pre>
                            </div>
                        `;
                    }
                };

                return component;

            } catch (error) {
                console.error(`Error parsing component ${name}:`, error);
                return this.createFallbackComponent(name);
            }
        },

        /**
         * Create a fallback component
         * @param {string} name - Component name
         * @returns {Object} - Fallback component
         */
        createFallbackComponent: function(name) {
            return {
                name: name,
                state: {},
                props: {},
                render: function() {
                    return `<div class="mono-component ${name.toLowerCase()}">
                        <h2>${name}</h2>
                        <p>Failed to parse component. This is a fallback rendering.</p>
                    </div>`;
                }
            };
        },

        /**
         * Initialize the router
         */
        initRouter: function() {
            // Create a router
            this.router = {
                routes: [],

                /**
                 * Add a route
                 * @param {string} path - Route path
                 * @param {Function} handler - Route handler
                 */
                addRoute: function(path, handler) {
                    this.routes.push({ path, handler });
                },

                /**
                 * Navigate to a path
                 * @param {string} path - Path to navigate to
                 */
                navigate: function(path) {
                    // Update the URL
                    history.pushState({}, '', path);

                    // Handle the navigation
                    this.handleNavigation();
                },

                /**
                 * Handle navigation
                 */
                handleNavigation: function() {
                    const path = window.location.pathname;

                    // Find a matching route
                    const route = this.routes.find(route => {
                        if (route.path === path) return true;
                        if (route.path === '*') return true;
                        return false;
                    });

                    // If a route was found, call its handler
                    if (route) {
                        route.handler(path);
                    }
                }
            };

            // Add a default route
            this.router.addRoute('*', (path) => {
                console.log(`Navigated to: ${path}`);

                // Extract the page name from the path
                const pageName = path === '/' ? 'home' : path.substring(1);

                // Update the current page if using Switch
                if (global.Switch && MonoDisplay.state.currentComponent) {
                    if (typeof MonoDisplay.state.currentComponent.setCurrentPage === 'function') {
                        MonoDisplay.state.currentComponent.setCurrentPage(pageName);
                    }
                }
            });

            // Handle popstate events
            window.addEventListener('popstate', () => {
                this.router.handleNavigation();
            });

            // Handle initial navigation
            this.router.handleNavigation();
        },

        /**
         * Initialize event handling
         */
        initEventHandling: function() {
            // Add a global click handler for navigation
            document.addEventListener('click', (event) => {
                // Check if this is a navigation link
                const link = event.target.closest('a[data-mono-nav]');
                if (link) {
                    // Prevent the default link behavior
                    event.preventDefault();

                    // Get the path
                    const path = link.getAttribute('href');

                    // Navigate to the path
                    this.router.navigate(path);
                }
            });
        },

        /**
         * Render the initial component
         * @param {Object} data - Component data
         */
        renderInitialComponent: function(data) {
            console.log('Rendering initial component:', data);

            // Create the component
            const component = this.createComponent(data);

            // Store the current component
            this.state.currentComponent = component;

            // Render the component
            this.renderComponent(component, this.rootElement);
        },

        /**
         * Create a component
         * @param {Object} data - Component data
         * @returns {Object} - Component object
         */
        createComponent: function(data) {
            // If Switch is available, use it to create the component
            if (global.Switch && typeof global.Switch.createComponent === 'function') {
                return global.Switch.createComponent(data);
            }

            // Otherwise, create a simple component
            return {
                id: `mono-component-${Date.now()}`,
                name: data.name,
                props: data.props || {},
                state: data.state || {},
                render: function() {
                    return `<div class="mono-component ${data.name.toLowerCase()}">
                        <h1>${data.name}</h1>
                        <pre>${JSON.stringify(this.props, null, 2)}</pre>
                    </div>`;
                }
            };
        },

        /**
         * Render a component
         * @param {Object} component - Component to render
         * @param {HTMLElement} container - Container element
         */
        renderComponent: function(component, container) {
            console.log('Rendering component:', component);

            // If Switch is available, use it to render the component
            if (global.Switch && typeof global.Switch.renderComponent === 'function') {
                global.Switch.renderComponent(component, container);
                return;
            }

            // Otherwise, render the component directly
            if (container && component.render) {
                container.innerHTML = component.render();
            }
        },

        /**
         * Update a component
         * @param {Object} component - Component to update
         * @param {Object} newState - New state
         */
        updateComponent: function(component, newState) {
            // Update the component state
            Object.assign(component.state, newState);

            // Re-render the component
            this.renderComponent(component, this.rootElement);
        },

        /**
         * Load and display a Mono component
         * @param {string} path - Path to the Mono component
         * @param {HTMLElement} container - Container element (optional)
         */
        loadAndDisplayComponent: function(path, container) {
            console.log(`Loading and displaying Mono component from path: ${path}`);

            // Show loading indicator
            const targetContainer = container || document.getElementById('mono-root');
            if (targetContainer) {
                targetContainer.innerHTML = '<div class="loading">Loading component...</div>';
                targetContainer.style.display = 'block';
            }

            // Add a small delay before fetching to ensure the server is ready
            setTimeout(() => {
                console.log(`Attempting to fetch: ${path}`);

                // Fetch the component source directly with retry logic
                const fetchWithRetry = (url, retries = 3, delay = 500) => {
                    return fetch(url)
                        .then(response => {
                            console.log(`Fetch response for ${url}:`, response);
                            if (!response.ok) {
                                throw new Error(`Failed to load component from path: ${url} (Status: ${response.status})`);
                            }
                            return response.text();
                        })
                        .catch(error => {
                            if (retries > 0) {
                                console.log(`Retrying fetch for ${url}, ${retries} retries left...`);
                                return new Promise(resolve => {
                                    setTimeout(() => resolve(fetchWithRetry(url, retries - 1, delay)), delay);
                                });
                            }
                            throw error;
                        });
                };

                fetchWithRetry(path)
                .then(source => {
                    console.log(`Successfully loaded component source from ${path}`);

                    // Process any template includes with @ symbol
                    source = this.processTemplateIncludes(source, path);

                    // Extract the component name from the path
                    const name = path.split('/').pop().replace('.mono', '');

                    // Parse the component
                    const component = this.parseComponent(source, name);

                    // Store the component
                    this.state.components[name] = component;
                    this.state.currentComponent = component;

                    // Render the component
                    if (targetContainer) {
                        console.log(`Rendering component to container:`, targetContainer);
                        targetContainer.innerHTML = component.render();

                        // Add event listeners if needed
                        this.addEventListeners(targetContainer, component);
                    } else {
                        console.error('No container found for rendering component');
                    }

                    console.log(`Successfully displayed component: ${component.name}`);
                })
                .catch(error => {
                    console.error(`Error loading component from ${path}:`, error);

                    if (targetContainer) {
                        targetContainer.innerHTML = `
                            <div class="error">
                                <h3>Error Loading Component</h3>
                                <p>${error.message}</p>
                                <p>Path: ${path}</p>
                            </div>
                        `;
                    }
                });
            }, 100); // Add a 100ms delay before fetching
        },

        /**
         * Add event listeners to a rendered component
         * @param {HTMLElement} container - Container element
         * @param {Object} component - Component object
         */
        addEventListeners: function(container, component) {
            // Find all elements with data-event attributes
            const elements = container.querySelectorAll('[data-event]');

            elements.forEach(element => {
                const eventType = element.dataset.event;
                const action = element.dataset.action;

                element.addEventListener(eventType, (event) => {
                    console.log(`Event triggered: ${eventType}, action: ${action}`);

                    // Prevent default for links
                    if (element.tagName.toLowerCase() === 'a') {
                        event.preventDefault();
                    }

                    // Handle the action if the component has a matching method
                    if (component[action] && typeof component[action] === 'function') {
                        component[action](event);

                        // Re-render the component after the action
                        container.innerHTML = component.render();

                        // Re-add event listeners
                        this.addEventListeners(container, component);
                    }
                });
            });
        },

        /**
         * Process template includes with @ symbol
         * @param {string} source - Source code
         * @param {string} currentPath - Current file path (for logging purposes)
         * @returns {string} - Processed source code
         */
        processTemplateIncludes: function(source, currentPath) {
            // Log the current path for debugging
            console.log(`Processing includes in file: ${currentPath}`);

            // Match {{ '@/path/to/file' }} pattern
            const includeRegex = /{{\s*['"]@\/([^'"]+)['"]\s*}}/g;

            // Replace all includes with the content of the referenced file
            return source.replace(includeRegex, (_, includePath) => {
                try {
                    // Resolve the path relative to the src directory
                    const fullPath = includePath.startsWith('src/') ? includePath : `src/${includePath}`;

                    // Synchronous fetch is not available in browser, so we'll use a placeholder
                    // In a real implementation, this would need to be handled asynchronously
                    console.log(`Including file: ${fullPath}`);

                    // Return a placeholder that will be processed when rendering
                    return `<!-- @include: ${fullPath} -->`;
                } catch (error) {
                    console.error(`Error including file ${includePath}:`, error);
                    return `<!-- Error including ${includePath}: ${error.message} -->`;
                }
            });
        },

        /**
         * Display a Mono file
         * @param {string} path - Path to the Mono file
         */
        displayMonoFile: function(path) {
            console.log(`Displaying Mono file: ${path}`);

            // Get the container
            const container = document.getElementById('mono-root');
            if (!container) {
                console.error('Mono root element not found');

                // Create a container if it doesn't exist
                const newContainer = document.createElement('div');
                newContainer.id = 'mono-root';
                newContainer.style.padding = '20px';
                newContainer.style.margin = '20px';
                newContainer.style.border = '1px solid #ccc';
                newContainer.style.borderRadius = '5px';
                newContainer.style.backgroundColor = '#f9f9f9';

                // Add it to the body
                document.body.appendChild(newContainer);

                // Load and display the component in the new container
                this.loadAndDisplayComponent(path, newContainer);
                return;
            }

            // Show the container
            container.style.display = 'block';

            // Add some styling to make it look better
            container.style.padding = '20px';
            container.style.margin = '20px';
            container.style.border = '1px solid #ccc';
            container.style.borderRadius = '5px';
            container.style.backgroundColor = '#f9f9f9';

            // Load and display the component
            this.loadAndDisplayComponent(path, container);

            // Scroll to the container
            container.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // Export the MonoDisplay object
    global.MonoDisplay = MonoDisplay;

    // Initialize when the DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        MonoDisplay.init();
    });

})(typeof window !== 'undefined' ? window : this);
