/**
 * Switch Button Component
 * 
 * A customizable button component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Button component
    const Button = {
        /**
         * Create a new Button component
         * @param {Object} props - Button properties
         * @returns {Object} - Button component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                text: 'Button',
                type: 'primary',
                size: 'medium',
                disabled: false,
                onClick: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Button',
                props: mergedProps,
                render: function(props) {
                    // Determine button classes
                    const classes = [
                        'switch-button',
                        `switch-button-${props.type}`,
                        `switch-button-${props.size}`
                    ];
                    
                    // Add disabled attribute if needed
                    const disabled = props.disabled ? 'disabled' : '';
                    
                    // Return the HTML
                    return `
                        <button class="${classes.join(' ')}" ${disabled} data-event="click">
                            ${props.text}
                        </button>
                    `;
                },
                events: {
                    click: function(event) {
                        if (!this.props.disabled && typeof this.props.onClick === 'function') {
                            this.props.onClick(event);
                        }
                    }
                }
            });
        }
    };
    
    // Register the Button component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Button = Button;
    
})(typeof window !== 'undefined' ? window : this);
