/**
 * Mono Frames
 * 
 * This module implements the Mono frames system, which provides:
 * 1. Hierarchical component containers
 * 2. Frame lifecycle hooks
 * 3. Frame-scoped state
 * 4. Isolation between frames
 */

(function(global) {
    'use strict';

    // Store frames by ID
    const frames = {};
    
    // Frame registry
    const frameRegistry = {};
    
    /**
     * Mono Frames
     */
    const MonoFrames = {
        /**
         * Initialize the frames system
         */
        init: function() {
            console.log('Initializing Mono Frames system...');
            
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
         * Parse a frame definition
         * @param {string} content - Frame definition content
         * @returns {Object} - Frame definition object
         */
        parseFrame: function(content) {
            // Extract frame name
            const nameMatch = content.match(/frame\s+([A-Za-z0-9_]+)/);
            if (!nameMatch) {
                throw new Error('Frame name not found');
            }

            const name = nameMatch[1];
            
            // Create the frame definition
            const frameDef = {
                name: name,
                state: {},
                hooks: {},
                methods: {}
            };
            
            // Parse state
            this.parseState(content, frameDef);
            
            // Parse hooks
            this.parseHooks(content, frameDef);
            
            // Parse methods
            this.parseMethods(content, frameDef);
            
            return frameDef;
        },
        
        /**
         * Parse state section
         * @param {string} content - Frame definition content
         * @param {Object} frameDef - Frame definition object
         */
        parseState: function(content, frameDef) {
            const stateMatch = content.match(/state\s*{([^}]*)}/);
            if (!stateMatch) {
                return;
            }
            
            const stateContent = stateMatch[1];
            const stateLines = stateContent.split('\n');
            
            stateLines.forEach(line => {
                const trimmedLine = line.trim();
                if (!trimmedLine || trimmedLine.startsWith('//')) {
                    return;
                }
                
                const stateMatch = trimmedLine.match(/([A-Za-z0-9_]+)\s*:\s*([A-Za-z0-9_]+)\s*=\s*(.+?)(?:,|$)/);
                if (stateMatch) {
                    const name = stateMatch[1];
                    const type = stateMatch[2];
                    let value = stateMatch[3].trim();
                    
                    // Parse the value based on type
                    if (type === 'string') {
                        // Remove quotes
                        value = value.replace(/^["'](.*)["']$/, '$1');
                    } else if (type === 'number') {
                        value = parseFloat(value);
                    } else if (type === 'boolean') {
                        value = value === 'true';
                    } else if (type === 'object') {
                        try {
                            value = JSON.parse(value);
                        } catch (e) {
                            value = null;
                        }
                    } else if (type === 'array') {
                        try {
                            value = JSON.parse(value);
                        } catch (e) {
                            value = [];
                        }
                    }
                    
                    frameDef.state[name] = value;
                }
            });
        },
        
        /**
         * Parse lifecycle hooks
         * @param {string} content - Frame definition content
         * @param {Object} frameDef - Frame definition object
         */
        parseHooks: function(content, frameDef) {
            const hookNames = [
                'frameWillLoad',
                'frameDidLoad',
                'frameWillUnload',
                'frameDidUnload'
            ];
            
            hookNames.forEach(hookName => {
                const hookMatch = content.match(new RegExp(`function\\s+${hookName}\\s*\\([^)]*\\)\\s*{([^}]*)}`, 's'));
                if (hookMatch) {
                    frameDef.hooks[hookName] = hookMatch[1].trim();
                }
            });
        },
        
        /**
         * Parse methods
         * @param {string} content - Frame definition content
         * @param {Object} frameDef - Frame definition object
         */
        parseMethods: function(content, frameDef) {
            const methodRegex = /function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*{([^}]*)}/g;
            let match;
            
            while ((match = methodRegex.exec(content)) !== null) {
                const methodName = match[1];
                const methodParams = match[2].split(',').map(p => p.trim());
                const methodBody = match[3].trim();
                
                // Skip lifecycle hooks
                if (['frameWillLoad', 'frameDidLoad', 'frameWillUnload', 'frameDidUnload', 'render'].includes(methodName)) {
                    continue;
                }
                
                frameDef.methods[methodName] = {
                    params: methodParams,
                    body: methodBody
                };
            }
        },
        
        /**
         * Create a frame instance
         * @param {Object} frameDef - Frame definition object
         * @param {Object} options - Options
         * @returns {Object} - Frame instance
         */
        createFrame: function(frameDef, options = {}) {
            const id = options.id || `mono-frame-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            
            // Create the frame instance
            const frame = {
                id: id,
                name: frameDef.name,
                state: Object.assign({}, frameDef.state, options.state || {}),
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
                        if (component.render) {
                            component.render();
                        }
                    });
                },
                
                // Mount the frame
                mount: function(container) {
                    // Call frameWillLoad hook
                    this.callHook('frameWillLoad');
                    
                    // Render the frame
                    this.render(container);
                    
                    // Call frameDidLoad hook
                    this.callHook('frameDidLoad');
                },
                
                // Unmount the frame
                unmount: function() {
                    // Call frameWillUnload hook
                    this.callHook('frameWillUnload');
                    
                    // Unmount all components
                    this.components.forEach(component => {
                        if (component.unmount) {
                            component.unmount();
                        }
                    });
                    
                    // Unmount all child frames
                    this.children.forEach(child => {
                        child.unmount();
                    });
                    
                    // Call frameDidUnload hook
                    this.callHook('frameDidUnload');
                },
                
                // Call a hook
                callHook: function(hookName) {
                    if (frameDef.hooks[hookName]) {
                        try {
                            // Create a function from the hook body
                            const hookFn = new Function('this', frameDef.hooks[hookName]);
                            
                            // Call the hook with the frame as 'this'
                            hookFn.call(this);
                        } catch (error) {
                            console.error(`Error calling hook ${hookName}:`, error);
                        }
                    }
                },
                
                // Call a method
                callMethod: function(methodName, ...args) {
                    if (frameDef.methods[methodName]) {
                        try {
                            // Create a function from the method body
                            const methodFn = new Function(
                                ...frameDef.methods[methodName].params,
                                frameDef.methods[methodName].body
                            );
                            
                            // Call the method with the frame as 'this'
                            return methodFn.apply(this, args);
                        } catch (error) {
                            console.error(`Error calling method ${methodName}:`, error);
                        }
                    }
                },
                
                // Render the frame
                render: function(container) {
                    // Get the render method
                    const renderMatch = content.match(/function\s+render\s*\([^)]*\)\s*{([^}]*return\s+`([^`]*)`[^}]*)}/s);
                    if (!renderMatch) {
                        console.error('Render method not found');
                        return;
                    }
                    
                    const renderBody = renderMatch[1];
                    let template = renderMatch[2];
                    
                    // Process template variables
                    template = template.replace(/\${this\.state\.([A-Za-z0-9_]+)}/g, (match, propName) => {
                        if (propName in this.state) {
                            return this.state[propName];
                        }
                        return match; // Keep original if not found
                    });
                    
                    // Process ${this.children} placeholder
                    template = template.replace(/\${this\.children}/g, '<div data-frame-children></div>');
                    
                    // Set the container content
                    container.innerHTML = template;
                    
                    // Find the children container
                    const childrenContainer = container.querySelector('[data-frame-children]');
                    if (childrenContainer) {
                        // Render child frames
                        this.children.forEach(child => {
                            const childContainer = document.createElement('div');
                            childContainer.setAttribute('data-frame-id', child.id);
                            childrenContainer.appendChild(childContainer);
                            
                            child.render(childContainer);
                        });
                    }
                }
            };
            
            // Store the frame
            frames[id] = frame;
            
            return frame;
        }
    };
    
    // Expose to global scope
    global.MonoFrames = MonoFrames;
    
})(window);
