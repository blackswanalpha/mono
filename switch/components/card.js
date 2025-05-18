/**
 * Switch Card Component
 * 
 * A card component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Card component
    const Card = {
        /**
         * Create a new Card component
         * @param {Object} props - Card properties
         * @returns {Object} - Card component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                title: '',
                footer: '',
                content: '',
                color: '',
                shadow: true
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Card',
                props: mergedProps,
                render: function(props) {
                    // Determine card classes
                    const classes = ['switch-card'];
                    
                    if (props.color) {
                        classes.push(`switch-card-${props.color}`);
                    }
                    
                    if (props.shadow) {
                        classes.push('switch-card-shadow');
                    }
                    
                    // Build the card HTML
                    let html = `<div class="${classes.join(' ')}">`;
                    
                    // Add header if title is provided
                    if (props.title) {
                        html += `
                            <div class="switch-card-header">
                                <h3 class="switch-card-title">${props.title}</h3>
                            </div>
                        `;
                    }
                    
                    // Add body
                    html += `
                        <div class="switch-card-body">
                            ${props.content}
                        </div>
                    `;
                    
                    // Add footer if provided
                    if (props.footer) {
                        html += `
                            <div class="switch-card-footer">
                                ${props.footer}
                            </div>
                        `;
                    }
                    
                    html += '</div>';
                    
                    return html;
                }
            });
        }
    };
    
    // Register the Card component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Card = Card;
    
})(typeof window !== 'undefined' ? window : this);
