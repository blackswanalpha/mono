/**
 * Switch Alert Component
 * 
 * An alert component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Alert component
    const Alert = {
        /**
         * Create a new Alert component
         * @param {Object} props - Alert properties
         * @returns {Object} - Alert component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                id: `alert-${Date.now()}`,
                type: 'info', // primary, secondary, success, danger, warning, info, light, dark
                message: '',
                title: '',
                dismissible: true,
                icon: '',
                autoClose: false,
                autoCloseDelay: 5000,
                onClose: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Alert',
                props: mergedProps,
                state: {
                    visible: true,
                    timer: null
                },
                render: function(props, state) {
                    if (!state.visible) {
                        return '';
                    }
                    
                    // Determine alert classes
                    const alertClasses = ['switch-alert', `switch-alert-${props.type}`];
                    if (props.dismissible) alertClasses.push('switch-alert-dismissible');
                    
                    // Build the alert HTML
                    let html = `<div class="${alertClasses.join(' ')}" id="${props.id}" role="alert">`;
                    
                    // Add icon if provided
                    if (props.icon) {
                        html += `<span class="switch-alert-icon ${props.icon}"></span>`;
                    }
                    
                    // Add content
                    html += '<div class="switch-alert-content">';
                    
                    // Add title if provided
                    if (props.title) {
                        html += `<h4 class="switch-alert-title">${props.title}</h4>`;
                    }
                    
                    // Add message
                    html += `<div class="switch-alert-message">${props.message}</div>`;
                    
                    html += '</div>';
                    
                    // Add dismiss button if dismissible
                    if (props.dismissible) {
                        html += `
                            <button type="button" class="switch-alert-close" 
                                    data-event="click" data-action="close">
                                &times;
                            </button>
                        `;
                    }
                    
                    // Close the alert
                    html += '</div>';
                    
                    return html;
                },
                events: {
                    click: function(event) {
                        const action = event.target.dataset.action;
                        
                        if (action === 'close') {
                            this.close();
                        }
                    }
                },
                mounted: function() {
                    // Start auto-close timer if enabled
                    if (this.props.autoClose) {
                        this.startAutoCloseTimer();
                    }
                },
                startAutoCloseTimer: function() {
                    // Clear any existing timer
                    this.clearAutoCloseTimer();
                    
                    // Set a new timer
                    this.state.timer = setTimeout(() => {
                        this.close();
                    }, this.props.autoCloseDelay);
                },
                clearAutoCloseTimer: function() {
                    if (this.state.timer) {
                        clearTimeout(this.state.timer);
                        this.state.timer = null;
                    }
                },
                close: function() {
                    // Clear auto-close timer
                    this.clearAutoCloseTimer();
                    
                    // Update state
                    this.update({ visible: false });
                    
                    // Call onClose callback if provided
                    if (typeof this.props.onClose === 'function') {
                        this.props.onClose();
                    }
                },
                show: function() {
                    // Update state
                    this.update({ visible: true });
                    
                    // Start auto-close timer if enabled
                    if (this.props.autoClose) {
                        this.startAutoCloseTimer();
                    }
                }
            });
        },
        
        /**
         * Show a global alert
         * @param {Object} options - Alert options
         * @returns {Object} - Alert component
         */
        show: function(options = {}) {
            // Create alert container if it doesn't exist
            let container = document.getElementById('switch-alerts-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'switch-alerts-container';
                container.className = 'switch-alerts-container';
                document.body.appendChild(container);
            }
            
            // Create the alert
            const alert = this.create(options);
            
            // Render the alert
            const alertElement = document.createElement('div');
            alertElement.className = 'switch-alerts-item';
            container.appendChild(alertElement);
            
            // Render the alert in the container
            Switch.renderComponent(alert, alertElement);
            
            // Remove the alert element when closed
            const originalClose = alert.close;
            alert.close = function() {
                originalClose.call(alert);
                
                // Remove the element after animation
                setTimeout(() => {
                    if (alertElement.parentNode) {
                        alertElement.parentNode.removeChild(alertElement);
                    }
                }, 300);
            };
            
            return alert;
        }
    };
    
    // Helper methods for common alert types
    ['success', 'info', 'warning', 'danger'].forEach(type => {
        Alert[type] = function(message, options = {}) {
            return this.show(Object.assign({}, options, { type, message }));
        };
    });
    
    // Register the Alert component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Alert = Alert;
    
})(typeof window !== 'undefined' ? window : this);
