/**
 * Mono Hydration
 * 
 * This module provides hydration capabilities for Mono components and frames.
 * Hydration is the process of attaching event listeners and state to server-rendered HTML.
 */

(function(global) {
    'use strict';

    /**
     * Mono Hydration
     */
    const MonoHydration = {
        /**
         * Initialize the hydration system
         */
        init: function() {
            console.log('Initializing Mono Hydration system...');
        },
        
        /**
         * Hydrate a component
         * @param {Object} component - Component object
         * @param {HTMLElement} container - Container element
         * @returns {Object} - Hydrated component
         */
        hydrateComponent: function(component, container) {
            console.log(`Hydrating component: ${component.name}`);
            
            // Find the component element
            const componentElement = container.querySelector(`[data-component="${component.name}"]`) || container;
            
            // Attach event listeners
            this.attachEventListeners(component, componentElement);
            
            // Hydrate child components
            this.hydrateChildren(component, componentElement);
            
            // Mark as hydrated
            componentElement.setAttribute('data-hydrated', 'true');
            
            return component;
        },
        
        /**
         * Hydrate a frame
         * @param {Object} frame - Frame object
         * @param {HTMLElement} container - Container element
         * @returns {Object} - Hydrated frame
         */
        hydrateFrame: function(frame, container) {
            console.log(`Hydrating frame: ${frame.name}`);
            
            // Find the frame element
            const frameElement = container.querySelector(`[data-frame="${frame.name}"]`) || container;
            
            // Attach event listeners
            this.attachEventListeners(frame, frameElement);
            
            // Hydrate components in the frame
            frame.components.forEach(component => {
                this.hydrateComponent(component, frameElement);
            });
            
            // Hydrate child frames
            this.hydrateChildren(frame, frameElement);
            
            // Mark as hydrated
            frameElement.setAttribute('data-hydrated', 'true');
            
            return frame;
        },
        
        /**
         * Attach event listeners to an element
         * @param {Object} obj - Component or frame object
         * @param {HTMLElement} element - Element to attach listeners to
         */
        attachEventListeners: function(obj, element) {
            // Find all elements with data-event attribute
            const eventElements = element.querySelectorAll('[data-event]');
            
            // Attach event handlers
            eventElements.forEach(eventElement => {
                const eventName = eventElement.getAttribute('data-event');
                const actionName = eventElement.getAttribute('data-action');
                
                if (!eventName || !actionName) {
                    return;
                }
                
                // Remove any existing event listeners
                const newElement = eventElement.cloneNode(true);
                eventElement.parentNode.replaceChild(newElement, eventElement);
                
                // Add new event listener
                newElement.addEventListener(eventName, event => {
                    // Prevent default for links
                    if (newElement.tagName === 'A') {
                        event.preventDefault();
                    }
                    
                    // Call the method on the object
                    if (obj[actionName]) {
                        obj[actionName](event, newElement);
                    } else if (obj.callMethod) {
                        obj.callMethod(actionName, event, newElement);
                    }
                });
            });
        },
        
        /**
         * Hydrate child components or frames
         * @param {Object} parent - Parent object
         * @param {HTMLElement} container - Container element
         */
        hydrateChildren: function(parent, container) {
            // Find child containers
            const childContainers = container.querySelectorAll('[data-child-container], [data-frame-children]');
            
            if (childContainers.length === 0) {
                return;
            }
            
            // Hydrate each child
            if (parent.children) {
                parent.children.forEach((child, index) => {
                    // Get the container for this child
                    const childContainer = childContainers[index] || childContainers[0];
                    
                    // Hydrate the child based on its type
                    if (child.components) {
                        this.hydrateFrame(child, childContainer);
                    } else {
                        this.hydrateComponent(child, childContainer);
                    }
                });
            }
        },
        
        /**
         * Hydrate a server-rendered page
         * @param {HTMLElement} container - Container element
         * @param {Object} data - Initial data
         */
        hydratePage: function(container, data) {
            console.log('Hydrating page with data:', data);
            
            // Create components and frames from the data
            if (data.frames) {
                data.frames.forEach(frameData => {
                    // Create the frame
                    const frame = global.MonoFrames.createFrame(frameData, {
                        id: frameData.id,
                        state: frameData.state
                    });
                    
                    // Find the frame container
                    const frameContainer = container.querySelector(`[data-frame-id="${frameData.id}"]`) || container;
                    
                    // Hydrate the frame
                    this.hydrateFrame(frame, frameContainer);
                });
            }
            
            if (data.components) {
                data.components.forEach(componentData => {
                    // Create the component
                    const component = global.SwitchEnhanced.component.create(componentData);
                    
                    // Find the component container
                    const componentContainer = container.querySelector(`[data-component-id="${componentData.id}"]`) || container;
                    
                    // Hydrate the component
                    this.hydrateComponent(component, componentContainer);
                });
            }
            
            console.log('Page hydration complete');
        }
    };
    
    // Expose to global scope
    global.MonoHydration = MonoHydration;
    
    // Initialize when the DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        MonoHydration.init();
        
        // Check if we have initial data for hydration
        if (global.SWITCH_INITIAL_DATA && global.SWITCH_INITIAL_DATA.hydrate) {
            // Hydrate the page
            MonoHydration.hydratePage(
                document.getElementById('switch-root') || document.body,
                global.SWITCH_INITIAL_DATA
            );
        }
    });
    
})(window);
