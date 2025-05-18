/**
 * Switch UI Kit - Button Component
 * 
 * A customizable button component for the Switch UI Kit.
 */

(function(global) {
    'use strict';
    
    // Create the SwitchUIKit namespace if it doesn't exist
    global.SwitchUIKit = global.SwitchUIKit || {};
    
    // Create the Components namespace if it doesn't exist
    global.SwitchUIKit.Components = global.SwitchUIKit.Components || {};
    
    // Create the SwitchComponents namespace for easier access
    global.SwitchComponents = global.SwitchComponents || {};
    
    /**
     * Button Component
     */
    class Button {
        /**
         * Create a new Button
         * @param {Object} options - Button options
         * @returns {Button} - The button instance
         */
        constructor(options = {}) {
            // Default options
            this.options = Object.assign({
                text: 'Button',
                type: 'primary',
                size: 'medium',
                disabled: false,
                outline: false,
                block: false,
                rounded: false,
                icon: null,
                iconPosition: 'left',
                onClick: null,
                attributes: {}
            }, options);
            
            // Create the element
            this.element = this._createElement();
            
            return this;
        }
        
        /**
         * Create the button element
         * @returns {HTMLElement} - The button element
         * @private
         */
        _createElement() {
            // Create the button element
            const button = document.createElement('button');
            
            // Add classes
            button.classList.add('switch-button');
            button.classList.add(`switch-button-${this.options.type}`);
            
            // Add size class
            if (this.options.size === 'small' || this.options.size === 'sm') {
                button.classList.add('switch-button-sm');
            } else if (this.options.size === 'large' || this.options.size === 'lg') {
                button.classList.add('switch-button-lg');
            }
            
            // Add outline class
            if (this.options.outline) {
                button.classList.add('switch-button-outline');
            }
            
            // Add block class
            if (this.options.block) {
                button.classList.add('switch-button-block');
            }
            
            // Add rounded class
            if (this.options.rounded) {
                button.classList.add('switch-button-rounded');
            }
            
            // Set disabled attribute
            if (this.options.disabled) {
                button.disabled = true;
            }
            
            // Add custom attributes
            if (this.options.attributes) {
                for (const [key, value] of Object.entries(this.options.attributes)) {
                    button.setAttribute(key, value);
                }
            }
            
            // Add click event listener
            if (this.options.onClick && typeof this.options.onClick === 'function') {
                button.addEventListener('click', this.options.onClick);
            }
            
            // Add content
            if (this.options.icon) {
                // Create icon element
                const icon = document.createElement('span');
                icon.classList.add('switch-button-icon');
                icon.innerHTML = this.options.icon;
                
                // Add icon position class
                if (this.options.iconPosition === 'right') {
                    button.classList.add('switch-button-icon-right');
                    
                    // Add text
                    if (this.options.text) {
                        button.innerHTML = `<span class="switch-button-text">${this.options.text}</span>`;
                        button.appendChild(icon);
                    } else {
                        button.appendChild(icon);
                    }
                } else {
                    // Add icon and text
                    button.appendChild(icon);
                    
                    if (this.options.text) {
                        button.innerHTML += `<span class="switch-button-text">${this.options.text}</span>`;
                    }
                }
            } else {
                // Add text
                button.textContent = this.options.text;
            }
            
            return button;
        }
        
        /**
         * Render the button
         * @returns {string} - The button HTML
         */
        render() {
            return this.element.outerHTML;
        }
        
        /**
         * Get the button element
         * @returns {HTMLElement} - The button element
         */
        getElement() {
            return this.element;
        }
        
        /**
         * Set the button text
         * @param {string} text - The button text
         * @returns {Button} - The button instance
         */
        setText(text) {
            this.options.text = text;
            
            // Update the text
            if (this.options.icon) {
                // Find the text element
                const textElement = this.element.querySelector('.switch-button-text');
                if (textElement) {
                    textElement.textContent = text;
                }
            } else {
                this.element.textContent = text;
            }
            
            return this;
        }
        
        /**
         * Set the button type
         * @param {string} type - The button type
         * @returns {Button} - The button instance
         */
        setType(type) {
            // Remove the old type class
            this.element.classList.remove(`switch-button-${this.options.type}`);
            
            // Update the type
            this.options.type = type;
            
            // Add the new type class
            this.element.classList.add(`switch-button-${type}`);
            
            return this;
        }
        
        /**
         * Enable the button
         * @returns {Button} - The button instance
         */
        enable() {
            this.options.disabled = false;
            this.element.disabled = false;
            return this;
        }
        
        /**
         * Disable the button
         * @returns {Button} - The button instance
         */
        disable() {
            this.options.disabled = true;
            this.element.disabled = true;
            return this;
        }
    }
    
    // Factory function to create a new Button
    function createButton(options) {
        return new Button(options);
    }
    
    // Export the Button component
    global.SwitchUIKit.Components.Button = Button;
    global.SwitchUIKit.Components.createButton = createButton;
    
    // Export to SwitchComponents for easier access
    global.SwitchComponents.Button = Button;
    global.SwitchComponents.Button.create = createButton;
    
})(typeof window !== 'undefined' ? window : this);
