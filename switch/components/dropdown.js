/**
 * Switch Dropdown Component
 * 
 * A dropdown menu component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Dropdown component
    const Dropdown = {
        /**
         * Create a new Dropdown component
         * @param {Object} props - Dropdown properties
         * @returns {Object} - Dropdown component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                id: `dropdown-${Date.now()}`,
                text: 'Dropdown',
                items: [],
                direction: 'down', // down, up, left, right
                align: 'left', // left, right, center
                buttonType: 'primary', // primary, secondary, success, danger, warning, info, light, dark
                buttonSize: 'medium', // small, medium, large
                split: false,
                icon: '',
                disabled: false,
                onSelect: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Dropdown',
                props: mergedProps,
                state: {
                    open: false
                },
                render: function(props, state) {
                    // Determine dropdown classes
                    const dropdownClasses = ['switch-dropdown'];
                    if (state.open) dropdownClasses.push('switch-dropdown-open');
                    if (props.direction === 'up') dropdownClasses.push('switch-dropdown-up');
                    if (props.direction === 'left') dropdownClasses.push('switch-dropdown-left');
                    if (props.direction === 'right') dropdownClasses.push('switch-dropdown-right');
                    
                    // Determine button classes
                    const buttonClasses = [
                        'switch-button',
                        `switch-button-${props.buttonType}`,
                        `switch-button-${props.buttonSize}`
                    ];
                    if (props.disabled) buttonClasses.push('switch-button-disabled');
                    
                    // Determine menu classes
                    const menuClasses = ['switch-dropdown-menu'];
                    if (props.align === 'right') menuClasses.push('switch-dropdown-menu-right');
                    if (props.align === 'center') menuClasses.push('switch-dropdown-menu-center');
                    
                    // Build the dropdown HTML
                    let html = `<div class="${dropdownClasses.join(' ')}" id="${props.id}">`;
                    
                    // Add button
                    if (props.split) {
                        html += `
                            <div class="switch-button-group">
                                <button type="button" class="${buttonClasses.join(' ')}" 
                                        data-event="click" data-action="button-click"
                                        ${props.disabled ? 'disabled' : ''}>
                                    ${props.icon ? `<span class="switch-button-icon ${props.icon}"></span>` : ''}
                                    ${props.text}
                                </button>
                                <button type="button" class="${buttonClasses.join(' ')} switch-dropdown-toggle" 
                                        data-event="click" data-action="toggle"
                                        ${props.disabled ? 'disabled' : ''}>
                                    <span class="switch-dropdown-caret"></span>
                                </button>
                            </div>
                        `;
                    } else {
                        html += `
                            <button type="button" class="${buttonClasses.join(' ')} switch-dropdown-toggle" 
                                    data-event="click" data-action="toggle"
                                    ${props.disabled ? 'disabled' : ''}>
                                ${props.icon ? `<span class="switch-button-icon ${props.icon}"></span>` : ''}
                                ${props.text}
                                <span class="switch-dropdown-caret"></span>
                            </button>
                        `;
                    }
                    
                    // Add menu
                    html += `<div class="${menuClasses.join(' ')}">`;
                    
                    // Add items
                    props.items.forEach((item, index) => {
                        if (item.divider) {
                            html += '<div class="switch-dropdown-divider"></div>';
                        } else if (item.header) {
                            html += `<h6 class="switch-dropdown-header">${item.header}</h6>`;
                        } else {
                            const itemClasses = ['switch-dropdown-item'];
                            if (item.active) itemClasses.push('switch-dropdown-item-active');
                            if (item.disabled) itemClasses.push('switch-dropdown-item-disabled');
                            
                            html += `
                                <a class="${itemClasses.join(' ')}" href="${item.href || '#'}" 
                                   data-event="click" data-action="item-click" data-index="${index}"
                                   ${item.disabled ? 'disabled' : ''}>
                                    ${item.icon ? `<span class="switch-dropdown-item-icon ${item.icon}"></span>` : ''}
                                    ${item.text}
                                </a>
                            `;
                        }
                    });
                    
                    // Close the menu and dropdown
                    html += '</div></div>';
                    
                    return html;
                },
                events: {
                    click: function(event) {
                        const action = event.target.dataset.action;
                        
                        if (action === 'toggle') {
                            this.toggle();
                        } else if (action === 'button-click') {
                            // Handle split button click
                            if (typeof this.props.onSelect === 'function') {
                                this.props.onSelect(null, -1);
                            }
                        } else if (action === 'item-click') {
                            event.preventDefault();
                            const index = parseInt(event.target.dataset.index);
                            const item = this.props.items[index];
                            
                            if (!item.disabled) {
                                this.selectItem(item, index);
                            }
                        } else if (!event.target.closest('.switch-dropdown')) {
                            // Close dropdown when clicking outside
                            this.close();
                        }
                    }
                },
                mounted: function() {
                    // Add global click event listener to close dropdown when clicking outside
                    document.addEventListener('click', this.handleOutsideClick.bind(this));
                },
                unmounted: function() {
                    // Remove global click event listener
                    document.removeEventListener('click', this.handleOutsideClick.bind(this));
                },
                handleOutsideClick: function(event) {
                    if (this.state.open && !event.target.closest(`#${this.props.id}`)) {
                        this.close();
                    }
                },
                toggle: function() {
                    if (this.props.disabled) return;
                    
                    // Update state
                    this.update({ open: !this.state.open });
                },
                open: function() {
                    if (this.props.disabled || this.state.open) return;
                    
                    // Update state
                    this.update({ open: true });
                },
                close: function() {
                    if (!this.state.open) return;
                    
                    // Update state
                    this.update({ open: false });
                },
                selectItem: function(item, index) {
                    // Close the dropdown
                    this.close();
                    
                    // Call onSelect callback if provided
                    if (typeof this.props.onSelect === 'function') {
                        this.props.onSelect(item, index);
                    }
                }
            });
        }
    };
    
    // Register the Dropdown component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Dropdown = Dropdown;
    
})(typeof window !== 'undefined' ? window : this);
