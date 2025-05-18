/**
 * Switch Tooltip Component
 * 
 * A tooltip component for displaying additional information.
 */

(function(global) {
    'use strict';
    
    // Define the Tooltip component
    const Tooltip = {
        /**
         * Create a new Tooltip component
         * @param {Object} props - Tooltip properties
         * @returns {Object} - Tooltip component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                id: `tooltip-${Date.now()}`,
                content: '',
                position: 'top', // top, right, bottom, left
                trigger: 'hover', // hover, click, focus
                delay: 300,
                arrow: true,
                maxWidth: 200,
                theme: 'dark', // dark, light
                interactive: false,
                appendTo: 'parent', // parent, body
                zIndex: 9999,
                offset: 8,
                animation: true,
                duration: 200,
                hideOnClick: true,
                onShow: null,
                onHide: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Tooltip',
                props: mergedProps,
                state: {
                    visible: false,
                    target: null,
                    tooltipElement: null,
                    showTimeout: null,
                    hideTimeout: null
                },
                render: function(props, state) {
                    // Return an empty string since the tooltip will be created dynamically
                    return '';
                },
                mounted: function() {
                    // Create the tooltip element
                    this.createTooltipElement();
                    
                    // Find the target element
                    const targetSelector = `[data-tooltip="${this.props.id}"]`;
                    const target = document.querySelector(targetSelector);
                    
                    if (target) {
                        this.state.target = target;
                        
                        // Add event listeners based on trigger
                        this.addEventListeners();
                    }
                },
                unmounted: function() {
                    // Remove event listeners
                    this.removeEventListeners();
                    
                    // Remove tooltip element
                    if (this.state.tooltipElement && this.state.tooltipElement.parentNode) {
                        this.state.tooltipElement.parentNode.removeChild(this.state.tooltipElement);
                    }
                    
                    // Clear timeouts
                    if (this.state.showTimeout) {
                        clearTimeout(this.state.showTimeout);
                    }
                    
                    if (this.state.hideTimeout) {
                        clearTimeout(this.state.hideTimeout);
                    }
                },
                createTooltipElement: function() {
                    // Create tooltip element
                    const tooltipElement = document.createElement('div');
                    tooltipElement.className = `switch-tooltip switch-tooltip-${this.props.theme}`;
                    tooltipElement.id = this.props.id;
                    tooltipElement.style.zIndex = this.props.zIndex;
                    tooltipElement.style.maxWidth = `${this.props.maxWidth}px`;
                    tooltipElement.style.opacity = '0';
                    tooltipElement.style.visibility = 'hidden';
                    tooltipElement.style.position = 'absolute';
                    tooltipElement.style.transition = this.props.animation ? `opacity ${this.props.duration}ms, visibility ${this.props.duration}ms` : 'none';
                    
                    // Create tooltip content
                    const tooltipContent = document.createElement('div');
                    tooltipContent.className = 'switch-tooltip-content';
                    tooltipContent.innerHTML = this.props.content;
                    tooltipElement.appendChild(tooltipContent);
                    
                    // Create tooltip arrow
                    if (this.props.arrow) {
                        const tooltipArrow = document.createElement('div');
                        tooltipArrow.className = 'switch-tooltip-arrow';
                        tooltipElement.appendChild(tooltipArrow);
                    }
                    
                    // Add event listeners if interactive
                    if (this.props.interactive) {
                        tooltipElement.addEventListener('mouseenter', () => {
                            this.clearHideTimeout();
                        });
                        
                        tooltipElement.addEventListener('mouseleave', () => {
                            this.hide();
                        });
                    }
                    
                    // Append to document body or parent
                    if (this.props.appendTo === 'body') {
                        document.body.appendChild(tooltipElement);
                    }
                    
                    // Store tooltip element
                    this.state.tooltipElement = tooltipElement;
                },
                addEventListeners: function() {
                    if (!this.state.target) return;
                    
                    const target = this.state.target;
                    
                    if (this.props.trigger === 'hover') {
                        target.addEventListener('mouseenter', this.handleMouseEnter.bind(this));
                        target.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
                    } else if (this.props.trigger === 'click') {
                        target.addEventListener('click', this.handleClick.bind(this));
                        
                        if (this.props.hideOnClick) {
                            document.addEventListener('click', this.handleDocumentClick.bind(this));
                        }
                    } else if (this.props.trigger === 'focus') {
                        target.addEventListener('focus', this.handleFocus.bind(this));
                        target.addEventListener('blur', this.handleBlur.bind(this));
                    }
                },
                removeEventListeners: function() {
                    if (!this.state.target) return;
                    
                    const target = this.state.target;
                    
                    if (this.props.trigger === 'hover') {
                        target.removeEventListener('mouseenter', this.handleMouseEnter.bind(this));
                        target.removeEventListener('mouseleave', this.handleMouseLeave.bind(this));
                    } else if (this.props.trigger === 'click') {
                        target.removeEventListener('click', this.handleClick.bind(this));
                        
                        if (this.props.hideOnClick) {
                            document.removeEventListener('click', this.handleDocumentClick.bind(this));
                        }
                    } else if (this.props.trigger === 'focus') {
                        target.removeEventListener('focus', this.handleFocus.bind(this));
                        target.removeEventListener('blur', this.handleBlur.bind(this));
                    }
                },
                handleMouseEnter: function() {
                    this.clearHideTimeout();
                    this.show();
                },
                handleMouseLeave: function() {
                    this.hide();
                },
                handleClick: function(event) {
                    event.stopPropagation();
                    
                    if (this.state.visible) {
                        this.hide();
                    } else {
                        this.show();
                    }
                },
                handleDocumentClick: function(event) {
                    if (this.state.visible && !this.state.tooltipElement.contains(event.target) && !this.state.target.contains(event.target)) {
                        this.hide();
                    }
                },
                handleFocus: function() {
                    this.show();
                },
                handleBlur: function() {
                    this.hide();
                },
                show: function() {
                    if (this.state.showTimeout) {
                        clearTimeout(this.state.showTimeout);
                    }
                    
                    this.state.showTimeout = setTimeout(() => {
                        if (!this.state.tooltipElement || !this.state.target) return;
                        
                        // Append to parent if not already appended
                        if (this.props.appendTo === 'parent' && !this.state.tooltipElement.parentNode) {
                            this.state.target.parentNode.appendChild(this.state.tooltipElement);
                        }
                        
                        // Position the tooltip
                        this.position();
                        
                        // Show the tooltip
                        this.state.tooltipElement.style.opacity = '1';
                        this.state.tooltipElement.style.visibility = 'visible';
                        
                        // Update state
                        this.state.visible = true;
                        
                        // Call onShow callback
                        if (typeof this.props.onShow === 'function') {
                            this.props.onShow();
                        }
                    }, this.props.delay);
                },
                hide: function() {
                    this.clearShowTimeout();
                    
                    this.state.hideTimeout = setTimeout(() => {
                        if (!this.state.tooltipElement) return;
                        
                        // Hide the tooltip
                        this.state.tooltipElement.style.opacity = '0';
                        this.state.tooltipElement.style.visibility = 'hidden';
                        
                        // Update state
                        this.state.visible = false;
                        
                        // Call onHide callback
                        if (typeof this.props.onHide === 'function') {
                            this.props.onHide();
                        }
                    }, this.props.delay);
                },
                clearShowTimeout: function() {
                    if (this.state.showTimeout) {
                        clearTimeout(this.state.showTimeout);
                        this.state.showTimeout = null;
                    }
                },
                clearHideTimeout: function() {
                    if (this.state.hideTimeout) {
                        clearTimeout(this.state.hideTimeout);
                        this.state.hideTimeout = null;
                    }
                },
                position: function() {
                    if (!this.state.tooltipElement || !this.state.target) return;
                    
                    const tooltipElement = this.state.tooltipElement;
                    const target = this.state.target;
                    const position = this.props.position;
                    const arrow = tooltipElement.querySelector('.switch-tooltip-arrow');
                    
                    // Get target and tooltip dimensions
                    const targetRect = target.getBoundingClientRect();
                    const tooltipRect = tooltipElement.getBoundingClientRect();
                    
                    // Calculate position
                    let top, left;
                    
                    switch (position) {
                        case 'top':
                            top = targetRect.top - tooltipRect.height - this.props.offset;
                            left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                            break;
                        case 'right':
                            top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                            left = targetRect.right + this.props.offset;
                            break;
                        case 'bottom':
                            top = targetRect.bottom + this.props.offset;
                            left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
                            break;
                        case 'left':
                            top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
                            left = targetRect.left - tooltipRect.width - this.props.offset;
                            break;
                    }
                    
                    // Apply position
                    tooltipElement.style.top = `${top}px`;
                    tooltipElement.style.left = `${left}px`;
                    
                    // Position arrow
                    if (arrow) {
                        arrow.className = `switch-tooltip-arrow switch-tooltip-arrow-${position}`;
                    }
                }
            });
        }
    };
    
    // Register the Tooltip component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Tooltip = Tooltip;
    
})(typeof window !== 'undefined' ? window : this);
