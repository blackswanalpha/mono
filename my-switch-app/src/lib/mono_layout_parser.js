/**
 * Mono Layout Parser
 * 
 * This module parses Mono layout syntax and converts it to a layout object
 * that can be used by the Switch framework.
 */

(function(global) {
    'use strict';

    /**
     * Layout Parser
     */
    const MonoLayoutParser = {
        /**
         * Parse a layout definition
         * @param {string} content - Layout definition content
         * @returns {Object} - Layout object
         */
        parse: function(content) {
            // Extract layout name
            const nameMatch = content.match(/layout\s+([A-Za-z0-9_]+)/);
            if (!nameMatch) {
                throw new Error('Layout name not found');
            }

            const name = nameMatch[1];
            
            // Create the layout object
            const layout = {
                name: name,
                variables: {},
                root: {
                    width: '100%',
                    height: '100%',
                    elements: {}
                },
                mediaQueries: {}
            };
            
            // Parse variables
            this.parseVariables(content, layout);
            
            // Parse root element
            this.parseRoot(content, layout);
            
            // Parse media queries
            this.parseMediaQueries(content, layout);
            
            return layout;
        },
        
        /**
         * Parse variables section
         * @param {string} content - Layout definition content
         * @param {Object} layout - Layout object
         */
        parseVariables: function(content, layout) {
            const variablesMatch = content.match(/variables\s*{([^}]*)}/);
            if (!variablesMatch) {
                return;
            }
            
            const variablesContent = variablesMatch[1];
            const variableLines = variablesContent.split('\n');
            
            variableLines.forEach(line => {
                const trimmedLine = line.trim();
                if (!trimmedLine || trimmedLine.startsWith('//')) {
                    return;
                }
                
                const variableMatch = trimmedLine.match(/([A-Za-z0-9_]+)\s*:\s*([^;]+);?/);
                if (variableMatch) {
                    const name = variableMatch[1];
                    const value = variableMatch[2].trim();
                    layout.variables[name] = value;
                }
            });
        },
        
        /**
         * Parse root element
         * @param {string} content - Layout definition content
         * @param {Object} layout - Layout object
         */
        parseRoot: function(content, layout) {
            const rootMatch = content.match(/root\s*{([^}]*)}/);
            if (!rootMatch) {
                return;
            }
            
            const rootContent = rootMatch[1];
            
            // Parse root properties
            this.parseElementProperties(rootContent, layout.root);
            
            // Parse child elements
            this.parseElements(rootContent, layout.root);
        },
        
        /**
         * Parse element properties
         * @param {string} content - Element content
         * @param {Object} element - Element object
         */
        parseElementProperties: function(content, element) {
            const propertyLines = content.split('\n');
            
            propertyLines.forEach(line => {
                const trimmedLine = line.trim();
                if (!trimmedLine || trimmedLine.startsWith('//') || trimmedLine.startsWith('element')) {
                    return;
                }
                
                const propertyMatch = trimmedLine.match(/([A-Za-z0-9_-]+)\s*:\s*([^;]+);?/);
                if (propertyMatch) {
                    const name = propertyMatch[1];
                    const value = propertyMatch[2].trim();
                    
                    // Handle constraints separately
                    if (name === 'constraint') {
                        const constraintMatch = value.match(/([A-Za-z0-9_-]+)\s*:\s*([^;]+)/);
                        if (constraintMatch) {
                            const constraintName = constraintMatch[1];
                            const constraintValue = constraintMatch[2].trim();
                            
                            if (!element.constraints) {
                                element.constraints = {};
                            }
                            
                            element.constraints[constraintName] = constraintValue;
                        }
                    } else {
                        element[name] = value;
                    }
                }
            });
        },
        
        /**
         * Parse child elements
         * @param {string} content - Element content
         * @param {Object} parent - Parent element object
         */
        parseElements: function(content, parent) {
            const elementRegex = /element\s+([A-Za-z0-9_-]+)\s*{([^}]*)}/g;
            let match;
            
            while ((match = elementRegex.exec(content)) !== null) {
                const elementName = match[1];
                const elementContent = match[2];
                
                // Create the element
                const element = {
                    name: elementName,
                    constraints: {}
                };
                
                // Parse element properties
                this.parseElementProperties(elementContent, element);
                
                // Add to parent
                parent.elements[elementName] = element;
            }
        },
        
        /**
         * Parse media queries
         * @param {string} content - Layout definition content
         * @param {Object} layout - Layout object
         */
        parseMediaQueries: function(content, layout) {
            const mediaRegex = /media\s+([A-Za-z0-9_-]+)\s*\(([^)]*)\)\s*{([^}]*)}/g;
            let match;
            
            while ((match = mediaRegex.exec(content)) !== null) {
                const mediaName = match[1];
                const mediaCondition = match[2].trim();
                const mediaContent = match[3];
                
                // Create the media query
                const mediaQuery = {
                    name: mediaName,
                    condition: mediaCondition,
                    root: {
                        elements: {}
                    }
                };
                
                // Parse root properties
                this.parseElementProperties(mediaContent, mediaQuery.root);
                
                // Parse child elements
                this.parseElements(mediaContent, mediaQuery.root);
                
                // Add to layout
                layout.mediaQueries[mediaName] = mediaQuery;
            }
        },
        
        /**
         * Apply a layout to a DOM element
         * @param {Object} layout - Layout object
         * @param {HTMLElement} container - Container element
         * @param {Object} options - Options
         */
        applyLayout: function(layout, container, options = {}) {
            // Apply root styles
            Object.keys(layout.root).forEach(prop => {
                if (prop !== 'elements' && prop !== 'constraints') {
                    container.style[prop] = this.resolveVariable(layout.root[prop], layout.variables);
                }
            });
            
            // Apply constraints
            if (layout.root.constraints) {
                this.applyConstraints(layout.root.constraints, container, container.parentElement, layout.variables);
            }
            
            // Apply child elements
            Object.keys(layout.root.elements).forEach(elementName => {
                const elementDef = layout.root.elements[elementName];
                
                // Find or create the element
                let element = container.querySelector(`[data-layout-element="${elementName}"]`);
                if (!element) {
                    element = document.createElement('div');
                    element.setAttribute('data-layout-element', elementName);
                    container.appendChild(element);
                }
                
                // Apply styles
                Object.keys(elementDef).forEach(prop => {
                    if (prop !== 'name' && prop !== 'constraints') {
                        element.style[prop] = this.resolveVariable(elementDef[prop], layout.variables);
                    }
                });
                
                // Apply constraints
                if (elementDef.constraints) {
                    this.applyConstraints(elementDef.constraints, element, container, layout.variables);
                }
            });
            
            // Apply media queries
            this.applyMediaQueries(layout, container);
            
            // Add resize listener to reapply media queries
            if (!container._layoutResizeListener) {
                container._layoutResizeListener = () => {
                    this.applyMediaQueries(layout, container);
                };
                
                window.addEventListener('resize', container._layoutResizeListener);
            }
        },
        
        /**
         * Apply constraints to an element
         * @param {Object} constraints - Constraints object
         * @param {HTMLElement} element - Element to apply constraints to
         * @param {HTMLElement} container - Container element
         * @param {Object} variables - Variables object
         */
        applyConstraints: function(constraints, element, container, variables) {
            Object.keys(constraints).forEach(constraint => {
                const value = this.resolveVariable(constraints[constraint], variables);
                
                switch (constraint) {
                    case 'top':
                        element.style.top = value;
                        element.style.position = 'absolute';
                        break;
                    case 'left':
                        element.style.left = value;
                        element.style.position = 'absolute';
                        break;
                    case 'right':
                        element.style.right = value;
                        element.style.position = 'absolute';
                        break;
                    case 'bottom':
                        element.style.bottom = value;
                        element.style.position = 'absolute';
                        break;
                    case 'centerX':
                        element.style.left = '50%';
                        element.style.transform = element.style.transform 
                            ? element.style.transform + ' translateX(-50%)'
                            : 'translateX(-50%)';
                        element.style.position = 'absolute';
                        break;
                    case 'centerY':
                        element.style.top = '50%';
                        element.style.transform = element.style.transform 
                            ? element.style.transform + ' translateY(-50%)'
                            : 'translateY(-50%)';
                        element.style.position = 'absolute';
                        break;
                }
            });
        },
        
        /**
         * Apply media queries to a container
         * @param {Object} layout - Layout object
         * @param {HTMLElement} container - Container element
         */
        applyMediaQueries: function(layout, container) {
            // Check each media query
            Object.keys(layout.mediaQueries).forEach(mediaName => {
                const mediaQuery = layout.mediaQueries[mediaName];
                
                // Create a media query object
                const mq = window.matchMedia(`(${mediaQuery.condition})`);
                
                // Apply styles if the media query matches
                if (mq.matches) {
                    // Apply root styles
                    Object.keys(mediaQuery.root).forEach(prop => {
                        if (prop !== 'elements' && prop !== 'constraints') {
                            container.style[prop] = this.resolveVariable(mediaQuery.root[prop], layout.variables);
                        }
                    });
                    
                    // Apply constraints
                    if (mediaQuery.root.constraints) {
                        this.applyConstraints(mediaQuery.root.constraints, container, container.parentElement, layout.variables);
                    }
                    
                    // Apply child elements
                    Object.keys(mediaQuery.root.elements).forEach(elementName => {
                        const elementDef = mediaQuery.root.elements[elementName];
                        
                        // Find the element
                        const element = container.querySelector(`[data-layout-element="${elementName}"]`);
                        if (element) {
                            // Apply styles
                            Object.keys(elementDef).forEach(prop => {
                                if (prop !== 'name' && prop !== 'constraints') {
                                    element.style[prop] = this.resolveVariable(elementDef[prop], layout.variables);
                                }
                            });
                            
                            // Apply constraints
                            if (elementDef.constraints) {
                                this.applyConstraints(elementDef.constraints, element, container, layout.variables);
                            }
                        }
                    });
                }
            });
        },
        
        /**
         * Resolve a variable reference
         * @param {string} value - Value that may contain variable references
         * @param {Object} variables - Variables object
         * @returns {string} - Resolved value
         */
        resolveVariable: function(value, variables) {
            if (!value || typeof value !== 'string') {
                return value;
            }
            
            // Replace variable references
            return value.replace(/\$\{([A-Za-z0-9_]+)\}/g, (match, varName) => {
                return variables[varName] || match;
            });
        }
    };
    
    // Expose to global scope
    global.MonoLayoutParser = MonoLayoutParser;
    
})(window);
