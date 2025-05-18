/**
 * Switch Modal Component
 * 
 * A modal dialog component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Modal component
    const Modal = {
        /**
         * Create a new Modal component
         * @param {Object} props - Modal properties
         * @returns {Object} - Modal component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                id: `modal-${Date.now()}`,
                title: '',
                content: '',
                footer: '',
                size: 'medium', // small, medium, large, fullscreen
                closeButton: true,
                backdrop: true,
                keyboard: true,
                centered: false,
                scrollable: false,
                onShow: null,
                onHide: null,
                onConfirm: null,
                confirmText: 'Confirm',
                cancelText: 'Cancel'
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Modal',
                props: mergedProps,
                state: {
                    visible: false
                },
                render: function(props, state) {
                    // Determine modal classes
                    const modalClasses = ['switch-modal'];
                    if (state.visible) modalClasses.push('switch-modal-visible');
                    
                    // Determine modal dialog classes
                    const dialogClasses = ['switch-modal-dialog'];
                    if (props.size === 'small') dialogClasses.push('switch-modal-sm');
                    if (props.size === 'large') dialogClasses.push('switch-modal-lg');
                    if (props.size === 'fullscreen') dialogClasses.push('switch-modal-fullscreen');
                    if (props.centered) dialogClasses.push('switch-modal-centered');
                    if (props.scrollable) dialogClasses.push('switch-modal-scrollable');
                    
                    // Build the modal HTML
                    let html = `
                        <div class="${modalClasses.join(' ')}" id="${props.id}" 
                             data-event="click" data-action="backdrop-click">
                            <div class="${dialogClasses.join(' ')}">
                                <div class="switch-modal-content">
                    `;
                    
                    // Add header if title is provided
                    if (props.title) {
                        html += `
                            <div class="switch-modal-header">
                                <h5 class="switch-modal-title">${props.title}</h5>
                                ${props.closeButton ? `
                                    <button type="button" class="switch-modal-close" 
                                            data-event="click" data-action="close">
                                        &times;
                                    </button>
                                ` : ''}
                            </div>
                        `;
                    }
                    
                    // Add body
                    html += `
                        <div class="switch-modal-body">
                            ${props.content}
                        </div>
                    `;
                    
                    // Add footer if provided or if confirm/cancel buttons are needed
                    if (props.footer || props.onConfirm) {
                        html += `
                            <div class="switch-modal-footer">
                                ${props.footer ? props.footer : ''}
                                ${props.onConfirm ? `
                                    <button type="button" class="switch-button switch-button-secondary" 
                                            data-event="click" data-action="cancel">
                                        ${props.cancelText}
                                    </button>
                                    <button type="button" class="switch-button switch-button-primary" 
                                            data-event="click" data-action="confirm">
                                        ${props.confirmText}
                                    </button>
                                ` : ''}
                            </div>
                        `;
                    }
                    
                    // Close the modal
                    html += `
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Add backdrop if enabled
                    if (props.backdrop) {
                        html += `
                            <div class="switch-modal-backdrop ${state.visible ? 'switch-modal-backdrop-visible' : ''}"></div>
                        `;
                    }
                    
                    return html;
                },
                events: {
                    click: function(event) {
                        const action = event.target.dataset.action;
                        
                        if (action === 'close' || action === 'cancel') {
                            this.hide();
                        } else if (action === 'confirm') {
                            if (typeof this.props.onConfirm === 'function') {
                                this.props.onConfirm();
                            }
                            this.hide();
                        } else if (action === 'backdrop-click' && event.target.classList.contains('switch-modal') && this.props.backdrop) {
                            this.hide();
                        }
                    }
                },
                show: function() {
                    // Update state
                    this.update({ visible: true });
                    
                    // Add body class to prevent scrolling
                    document.body.classList.add('switch-modal-open');
                    
                    // Add keyboard event listener if enabled
                    if (this.props.keyboard) {
                        document.addEventListener('keydown', this.handleKeyDown);
                    }
                    
                    // Call onShow callback if provided
                    if (typeof this.props.onShow === 'function') {
                        this.props.onShow();
                    }
                },
                hide: function() {
                    // Update state
                    this.update({ visible: false });
                    
                    // Remove body class
                    document.body.classList.remove('switch-modal-open');
                    
                    // Remove keyboard event listener
                    if (this.props.keyboard) {
                        document.removeEventListener('keydown', this.handleKeyDown);
                    }
                    
                    // Call onHide callback if provided
                    if (typeof this.props.onHide === 'function') {
                        this.props.onHide();
                    }
                },
                toggle: function() {
                    if (this.state.visible) {
                        this.hide();
                    } else {
                        this.show();
                    }
                },
                handleKeyDown: function(event) {
                    // Close modal on Escape key
                    if (event.key === 'Escape') {
                        this.hide();
                    }
                }
            });
        }
    };
    
    // Register the Modal component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Modal = Modal;
    
})(typeof window !== 'undefined' ? window : this);
