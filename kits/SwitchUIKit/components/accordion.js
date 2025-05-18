/**
 * Switch Accordion Component
 * 
 * An accordion component for collapsible content.
 */

(function(global) {
    'use strict';
    
    // Define the Accordion component
    const Accordion = {
        /**
         * Create a new Accordion component
         * @param {Object} props - Accordion properties
         * @returns {Object} - Accordion component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                id: `accordion-${Date.now()}`,
                items: [],
                multiple: false,
                defaultActive: [],
                bordered: true,
                flush: false,
                animated: true,
                iconPosition: 'right', // right, left
                onToggle: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Accordion',
                props: mergedProps,
                state: {
                    activeItems: Array.isArray(mergedProps.defaultActive) ? [...mergedProps.defaultActive] : [mergedProps.defaultActive]
                },
                render: function(props, state) {
                    // Determine accordion classes
                    const accordionClasses = ['switch-accordion'];
                    if (props.bordered) accordionClasses.push('switch-accordion-bordered');
                    if (props.flush) accordionClasses.push('switch-accordion-flush');
                    
                    // Build the accordion HTML
                    let html = `<div class="${accordionClasses.join(' ')}" id="${props.id}">`;
                    
                    // Add items
                    props.items.forEach((item, index) => {
                        const isActive = state.activeItems.includes(index);
                        const itemClasses = ['switch-accordion-item'];
                        if (isActive) itemClasses.push('switch-accordion-active');
                        
                        html += `
                            <div class="${itemClasses.join(' ')}">
                                <div class="switch-accordion-header" data-event="click" data-action="toggle" data-index="${index}">
                                    ${props.iconPosition === 'left' ? 
                                        `<span class="switch-accordion-icon ${isActive ? 'switch-accordion-icon-active' : ''}"></span>` : ''}
                                    <h3 class="switch-accordion-title">${item.title}</h3>
                                    ${props.iconPosition === 'right' ? 
                                        `<span class="switch-accordion-icon ${isActive ? 'switch-accordion-icon-active' : ''}"></span>` : ''}
                                </div>
                                <div class="switch-accordion-content" style="${isActive ? '' : 'display: none;'}">
                                    <div class="switch-accordion-body">
                                        ${item.content}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    
                    // Close the accordion
                    html += '</div>';
                    
                    return html;
                },
                events: {
                    click: function(event) {
                        const action = event.target.dataset.action || event.target.parentElement.dataset.action;
                        
                        if (action === 'toggle') {
                            const index = parseInt(event.target.dataset.index || event.target.parentElement.dataset.index);
                            this.toggleItem(index);
                        }
                    }
                },
                toggleItem: function(index) {
                    // Check if the item is already active
                    const isActive = this.state.activeItems.includes(index);
                    let newActiveItems = [];
                    
                    if (isActive) {
                        // Remove the item from active items
                        newActiveItems = this.state.activeItems.filter(item => item !== index);
                    } else {
                        if (this.props.multiple) {
                            // Add the item to active items
                            newActiveItems = [...this.state.activeItems, index];
                        } else {
                            // Replace active items with the new item
                            newActiveItems = [index];
                        }
                    }
                    
                    // Update state
                    this.update({ activeItems: newActiveItems });
                    
                    // Call onToggle callback if provided
                    if (typeof this.props.onToggle === 'function') {
                        this.props.onToggle(index, !isActive, newActiveItems);
                    }
                },
                isItemActive: function(index) {
                    return this.state.activeItems.includes(index);
                },
                activateItem: function(index) {
                    if (!this.isItemActive(index)) {
                        this.toggleItem(index);
                    }
                },
                deactivateItem: function(index) {
                    if (this.isItemActive(index)) {
                        this.toggleItem(index);
                    }
                },
                activateAll: function() {
                    if (!this.props.multiple) return;
                    
                    const allIndices = this.props.items.map((_, index) => index);
                    this.update({ activeItems: allIndices });
                    
                    // Call onToggle callback if provided
                    if (typeof this.props.onToggle === 'function') {
                        this.props.onToggle(null, true, allIndices);
                    }
                },
                deactivateAll: function() {
                    this.update({ activeItems: [] });
                    
                    // Call onToggle callback if provided
                    if (typeof this.props.onToggle === 'function') {
                        this.props.onToggle(null, false, []);
                    }
                }
            });
        }
    };
    
    // Register the Accordion component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Accordion = Accordion;
    
})(typeof window !== 'undefined' ? window : this);
