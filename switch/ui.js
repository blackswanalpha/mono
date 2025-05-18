/**
 * Switch UI Components
 * 
 * Enhanced UI components for the Switch framework.
 * This module provides improved UI components with better accessibility and usability.
 */

(function(global) {
    'use strict';

    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before ui.js.');
        return;
    }

    // UI components
    const SwitchUI = {
        /**
         * Create a modal dialog
         * @param {Object} options - Modal options
         * @returns {Object} - Modal object
         */
        createModal: function(options = {}) {
            const id = options.id || `switch-modal-${Date.now()}`;
            const title = options.title || 'Modal';
            const content = options.content || '';
            const size = options.size || 'medium'; // small, medium, large
            const closable = options.closable !== false;
            
            // Create the modal element
            const modalElement = global.SwitchDOM ? 
                SwitchDOM.createElement('div', {
                    id,
                    className: `switch-modal ${size}`,
                    'aria-modal': 'true',
                    role: 'dialog',
                    tabindex: '-1'
                }) : 
                document.createElement('div');
                
            if (!global.SwitchDOM) {
                modalElement.id = id;
                modalElement.className = `switch-modal ${size}`;
                modalElement.setAttribute('aria-modal', 'true');
                modalElement.setAttribute('role', 'dialog');
                modalElement.setAttribute('tabindex', '-1');
            }
            
            // Create the modal HTML
            const modalHTML = `
                <div class="switch-modal-backdrop"></div>
                <div class="switch-modal-dialog">
                    <div class="switch-modal-content">
                        <div class="switch-modal-header">
                            <h5 class="switch-modal-title">${title}</h5>
                            ${closable ? '<button type="button" class="switch-modal-close" aria-label="Close">&times;</button>' : ''}
                        </div>
                        <div class="switch-modal-body">
                            ${content}
                        </div>
                        <div class="switch-modal-footer">
                            <button type="button" class="switch-btn switch-btn-secondary" data-dismiss="modal">Close</button>
                            <button type="button" class="switch-btn switch-btn-primary">Save changes</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Set the modal HTML
            if (global.SwitchDOM) {
                SwitchDOM.setHTML(modalElement, modalHTML);
            } else {
                modalElement.innerHTML = modalHTML;
            }
            
            // Add the modal to the document
            document.body.appendChild(modalElement);
            
            // Create the modal object
            const modal = {
                id,
                element: modalElement,
                
                /**
                 * Show the modal
                 */
                show: function() {
                    if (global.SwitchDOM) {
                        SwitchDOM.addClass(modalElement, 'show');
                        SwitchDOM.addClass(document.body, 'switch-modal-open');
                    } else {
                        modalElement.classList.add('show');
                        document.body.classList.add('switch-modal-open');
                    }
                    
                    // Focus the modal
                    modalElement.focus();
                    
                    // Dispatch show event
                    modalElement.dispatchEvent(new CustomEvent('switch:modal-show'));
                },
                
                /**
                 * Hide the modal
                 */
                hide: function() {
                    if (global.SwitchDOM) {
                        SwitchDOM.removeClass(modalElement, 'show');
                        SwitchDOM.removeClass(document.body, 'switch-modal-open');
                    } else {
                        modalElement.classList.remove('show');
                        document.body.classList.remove('switch-modal-open');
                    }
                    
                    // Dispatch hide event
                    modalElement.dispatchEvent(new CustomEvent('switch:modal-hide'));
                },
                
                /**
                 * Destroy the modal
                 */
                destroy: function() {
                    // Remove event listeners
                    
                    // Remove the modal from the document
                    document.body.removeChild(modalElement);
                    
                    // Dispatch destroy event
                    document.dispatchEvent(new CustomEvent('switch:modal-destroy', {
                        detail: { id }
                    }));
                }
            };
            
            // Add event listeners
            const closeButton = modalElement.querySelector('.switch-modal-close');
            if (closeButton) {
                if (global.SwitchDOM) {
                    SwitchDOM.addEventListener(closeButton, 'click', () => modal.hide());
                } else {
                    closeButton.addEventListener('click', () => modal.hide());
                }
            }
            
            const dismissButtons = modalElement.querySelectorAll('[data-dismiss="modal"]');
            dismissButtons.forEach(button => {
                if (global.SwitchDOM) {
                    SwitchDOM.addEventListener(button, 'click', () => modal.hide());
                } else {
                    button.addEventListener('click', () => modal.hide());
                }
            });
            
            // Close when clicking on backdrop
            const backdrop = modalElement.querySelector('.switch-modal-backdrop');
            if (backdrop && closable) {
                if (global.SwitchDOM) {
                    SwitchDOM.addEventListener(backdrop, 'click', () => modal.hide());
                } else {
                    backdrop.addEventListener('click', () => modal.hide());
                }
            }
            
            // Close when pressing Escape
            if (closable) {
                if (global.SwitchDOM) {
                    SwitchDOM.addEventListener(modalElement, 'keydown', (e) => {
                        if (e.key === 'Escape') modal.hide();
                    });
                } else {
                    modalElement.addEventListener('keydown', (e) => {
                        if (e.key === 'Escape') modal.hide();
                    });
                }
            }
            
            return modal;
        },
        
        /**
         * Create a toast notification
         * @param {Object} options - Toast options
         * @returns {Object} - Toast object
         */
        createToast: function(options = {}) {
            const id = options.id || `switch-toast-${Date.now()}`;
            const title = options.title || 'Notification';
            const message = options.message || '';
            const type = options.type || 'info'; // info, success, warning, error
            const duration = options.duration || 3000; // ms
            const position = options.position || 'top-right'; // top-right, top-left, bottom-right, bottom-left
            
            // Create toast container if it doesn't exist
            let container = document.querySelector(`.switch-toast-container.${position}`);
            if (!container) {
                container = global.SwitchDOM ? 
                    SwitchDOM.createElement('div', {
                        className: `switch-toast-container ${position}`
                    }) : 
                    document.createElement('div');
                    
                if (!global.SwitchDOM) {
                    container.className = `switch-toast-container ${position}`;
                }
                
                document.body.appendChild(container);
            }
            
            // Create the toast element
            const toastElement = global.SwitchDOM ? 
                SwitchDOM.createElement('div', {
                    id,
                    className: `switch-toast ${type}`,
                    role: 'alert',
                    'aria-live': 'assertive'
                }) : 
                document.createElement('div');
                
            if (!global.SwitchDOM) {
                toastElement.id = id;
                toastElement.className = `switch-toast ${type}`;
                toastElement.setAttribute('role', 'alert');
                toastElement.setAttribute('aria-live', 'assertive');
            }
            
            // Create the toast HTML
            const toastHTML = `
                <div class="switch-toast-header">
                    <strong class="switch-toast-title">${title}</strong>
                    <button type="button" class="switch-toast-close" aria-label="Close">&times;</button>
                </div>
                <div class="switch-toast-body">
                    ${message}
                </div>
            `;
            
            // Set the toast HTML
            if (global.SwitchDOM) {
                SwitchDOM.setHTML(toastElement, toastHTML);
            } else {
                toastElement.innerHTML = toastHTML;
            }
            
            // Add the toast to the container
            container.appendChild(toastElement);
            
            // Create the toast object
            const toast = {
                id,
                element: toastElement,
                
                /**
                 * Show the toast
                 */
                show: function() {
                    if (global.SwitchDOM) {
                        SwitchDOM.addClass(toastElement, 'show');
                    } else {
                        toastElement.classList.add('show');
                    }
                    
                    // Auto-hide after duration
                    if (duration > 0) {
                        setTimeout(() => this.hide(), duration);
                    }
                    
                    // Dispatch show event
                    toastElement.dispatchEvent(new CustomEvent('switch:toast-show'));
                },
                
                /**
                 * Hide the toast
                 */
                hide: function() {
                    if (global.SwitchDOM) {
                        SwitchDOM.addClass(toastElement, 'hiding');
                    } else {
                        toastElement.classList.add('hiding');
                    }
                    
                    // Remove after animation
                    setTimeout(() => this.destroy(), 300);
                    
                    // Dispatch hide event
                    toastElement.dispatchEvent(new CustomEvent('switch:toast-hide'));
                },
                
                /**
                 * Destroy the toast
                 */
                destroy: function() {
                    // Remove the toast from the container
                    container.removeChild(toastElement);
                    
                    // Remove the container if it's empty
                    if (container.children.length === 0) {
                        document.body.removeChild(container);
                    }
                    
                    // Dispatch destroy event
                    document.dispatchEvent(new CustomEvent('switch:toast-destroy', {
                        detail: { id }
                    }));
                }
            };
            
            // Add event listeners
            const closeButton = toastElement.querySelector('.switch-toast-close');
            if (closeButton) {
                if (global.SwitchDOM) {
                    SwitchDOM.addEventListener(closeButton, 'click', () => toast.hide());
                } else {
                    closeButton.addEventListener('click', () => toast.hide());
                }
            }
            
            // Show the toast
            setTimeout(() => toast.show(), 100);
            
            return toast;
        }
    };
    
    // Export the SwitchUI object
    global.SwitchUI = SwitchUI;
    
})(typeof window !== 'undefined' ? window : this);
