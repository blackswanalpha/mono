/**
 * Switch DOM Utilities
 * 
 * Enhanced DOM manipulation utilities for the Switch framework.
 * This module provides robust DOM operations with error handling,
 * performance optimizations, and cross-browser compatibility.
 */

(function(global) {
    'use strict';

    // DOM manipulation utilities
    const SwitchDOM = {
        /**
         * Create a DOM element with attributes and children
         * @param {string} tagName - The tag name of the element
         * @param {Object} attributes - Attributes to set on the element
         * @param {Array|string} children - Child elements or text content
         * @returns {HTMLElement} The created element
         */
        createElement: function(tagName, attributes = {}, children = []) {
            try {
                // Create the element
                const element = document.createElement(tagName);
                
                // Set attributes
                Object.entries(attributes).forEach(([key, value]) => {
                    if (key === 'className') {
                        element.className = value;
                    } else if (key === 'style' && typeof value === 'object') {
                        Object.entries(value).forEach(([prop, val]) => {
                            element.style[prop] = val;
                        });
                    } else if (key.startsWith('data-')) {
                        element.setAttribute(key, value);
                    } else if (key.startsWith('on') && typeof value === 'function') {
                        const eventName = key.substring(2).toLowerCase();
                        element.addEventListener(eventName, value);
                    } else {
                        element.setAttribute(key, value);
                    }
                });
                
                // Add children
                if (Array.isArray(children)) {
                    children.forEach(child => {
                        if (child instanceof HTMLElement) {
                            element.appendChild(child);
                        } else if (child !== null && child !== undefined) {
                            element.appendChild(document.createTextNode(String(child)));
                        }
                    });
                } else if (children !== null && children !== undefined) {
                    element.textContent = String(children);
                }
                
                return element;
            } catch (error) {
                console.error('Error creating element:', error);
                return document.createElement('div');
            }
        },
        
        /**
         * Query selector with error handling
         * @param {string} selector - CSS selector
         * @param {HTMLElement} context - Context element (default: document)
         * @returns {HTMLElement|null} The selected element or null
         */
        querySelector: function(selector, context = document) {
            try {
                return context.querySelector(selector);
            } catch (error) {
                console.error(`Error querying selector "${selector}":`, error);
                return null;
            }
        },
        
        /**
         * Query selector all with error handling
         * @param {string} selector - CSS selector
         * @param {HTMLElement} context - Context element (default: document)
         * @returns {Array<HTMLElement>} Array of selected elements
         */
        querySelectorAll: function(selector, context = document) {
            try {
                return Array.from(context.querySelectorAll(selector));
            } catch (error) {
                console.error(`Error querying selector "${selector}":`, error);
                return [];
            }
        },
        
        /**
         * Add event listener with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} eventName - Event name
         * @param {Function} handler - Event handler
         * @param {Object} options - Event options
         */
        addEventListener: function(element, eventName, handler, options = {}) {
            if (!element || !eventName || typeof handler !== 'function') {
                console.error('Invalid parameters for addEventListener');
                return;
            }
            
            try {
                element.addEventListener(eventName, handler, options);
            } catch (error) {
                console.error(`Error adding event listener "${eventName}":`, error);
            }
        },
        
        /**
         * Remove event listener with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} eventName - Event name
         * @param {Function} handler - Event handler
         * @param {Object} options - Event options
         */
        removeEventListener: function(element, eventName, handler, options = {}) {
            if (!element || !eventName || typeof handler !== 'function') {
                console.error('Invalid parameters for removeEventListener');
                return;
            }
            
            try {
                element.removeEventListener(eventName, handler, options);
            } catch (error) {
                console.error(`Error removing event listener "${eventName}":`, error);
            }
        },
        
        /**
         * Set HTML content with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} html - HTML content
         */
        setHTML: function(element, html) {
            if (!element) {
                console.error('Invalid element for setHTML');
                return;
            }
            
            try {
                element.innerHTML = html;
            } catch (error) {
                console.error('Error setting HTML:', error);
                // Fallback to text content
                try {
                    element.textContent = html;
                } catch (e) {
                    console.error('Error setting text content:', e);
                }
            }
        },
        
        /**
         * Add class to element with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class name to add
         */
        addClass: function(element, className) {
            if (!element || !className) {
                console.error('Invalid parameters for addClass');
                return;
            }
            
            try {
                element.classList.add(className);
            } catch (error) {
                console.error(`Error adding class "${className}":`, error);
            }
        },
        
        /**
         * Remove class from element with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class name to remove
         */
        removeClass: function(element, className) {
            if (!element || !className) {
                console.error('Invalid parameters for removeClass');
                return;
            }
            
            try {
                element.classList.remove(className);
            } catch (error) {
                console.error(`Error removing class "${className}":`, error);
            }
        },
        
        /**
         * Toggle class on element with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class name to toggle
         * @param {boolean} force - Force add or remove
         */
        toggleClass: function(element, className, force) {
            if (!element || !className) {
                console.error('Invalid parameters for toggleClass');
                return;
            }
            
            try {
                if (force !== undefined) {
                    element.classList.toggle(className, force);
                } else {
                    element.classList.toggle(className);
                }
            } catch (error) {
                console.error(`Error toggling class "${className}":`, error);
            }
        },
        
        /**
         * Check if element has class with error handling
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class name to check
         * @returns {boolean} True if element has class
         */
        hasClass: function(element, className) {
            if (!element || !className) {
                console.error('Invalid parameters for hasClass');
                return false;
            }
            
            try {
                return element.classList.contains(className);
            } catch (error) {
                console.error(`Error checking class "${className}":`, error);
                return false;
            }
        }
    };
    
    // Export the SwitchDOM object
    global.SwitchDOM = SwitchDOM;
    
})(typeof window !== 'undefined' ? window : this);
