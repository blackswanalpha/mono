/**
 * Switch Tabs Component
 * 
 * A tabbed interface component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Tabs component
    const Tabs = {
        /**
         * Create a new Tabs component
         * @param {Object} props - Tabs properties
         * @returns {Object} - Tabs component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                id: `tabs-${Date.now()}`,
                tabs: [],
                activeTab: 0,
                type: 'tabs', // tabs, pills, underline
                position: 'top', // top, left, right, bottom
                justified: false,
                fill: false,
                vertical: false,
                onTabChange: null
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Tabs',
                props: mergedProps,
                state: {
                    activeTab: mergedProps.activeTab
                },
                render: function(props, state) {
                    // Determine tabs container classes
                    const containerClasses = ['switch-tabs-container'];
                    if (props.vertical) containerClasses.push('switch-tabs-vertical');
                    if (props.position === 'left') containerClasses.push('switch-tabs-left');
                    if (props.position === 'right') containerClasses.push('switch-tabs-right');
                    if (props.position === 'bottom') containerClasses.push('switch-tabs-bottom');
                    
                    // Determine nav classes
                    const navClasses = ['switch-tabs-nav'];
                    if (props.type === 'pills') navClasses.push('switch-tabs-pills');
                    if (props.type === 'underline') navClasses.push('switch-tabs-underline');
                    if (props.justified) navClasses.push('switch-tabs-justified');
                    if (props.fill) navClasses.push('switch-tabs-fill');
                    
                    // Build the tabs HTML
                    let html = `<div class="${containerClasses.join(' ')}" id="${props.id}">`;
                    
                    // Render tabs navigation
                    html += `<ul class="${navClasses.join(' ')}">`;
                    props.tabs.forEach((tab, index) => {
                        const isActive = index === state.activeTab;
                        const tabClasses = ['switch-tabs-item'];
                        if (isActive) tabClasses.push('switch-tabs-active');
                        if (tab.disabled) tabClasses.push('switch-tabs-disabled');
                        
                        html += `
                            <li class="${tabClasses.join(' ')}">
                                <a class="switch-tabs-link" href="#${props.id}-tab-${index}" 
                                   data-event="click" data-action="tab-click" data-index="${index}"
                                   ${tab.disabled ? 'disabled' : ''}>
                                    ${tab.icon ? `<span class="switch-tabs-icon ${tab.icon}"></span>` : ''}
                                    ${tab.title}
                                </a>
                            </li>
                        `;
                    });
                    html += '</ul>';
                    
                    // Render tab content
                    html += '<div class="switch-tabs-content">';
                    props.tabs.forEach((tab, index) => {
                        const isActive = index === state.activeTab;
                        const paneClasses = ['switch-tabs-pane'];
                        if (isActive) paneClasses.push('switch-tabs-pane-active');
                        
                        html += `
                            <div class="${paneClasses.join(' ')}" id="${props.id}-tab-${index}">
                                ${tab.content}
                            </div>
                        `;
                    });
                    html += '</div>';
                    
                    // Close the container
                    html += '</div>';
                    
                    return html;
                },
                events: {
                    click: function(event) {
                        const action = event.target.dataset.action;
                        
                        if (action === 'tab-click') {
                            event.preventDefault();
                            const index = parseInt(event.target.dataset.index);
                            this.setActiveTab(index);
                        }
                    }
                },
                setActiveTab: function(index) {
                    // Check if the tab is disabled
                    if (this.props.tabs[index] && this.props.tabs[index].disabled) {
                        return;
                    }
                    
                    // Update state
                    this.update({ activeTab: index });
                    
                    // Call onTabChange callback if provided
                    if (typeof this.props.onTabChange === 'function') {
                        this.props.onTabChange(index, this.props.tabs[index]);
                    }
                },
                getActiveTab: function() {
                    return this.state.activeTab;
                },
                getActiveTabData: function() {
                    return this.props.tabs[this.state.activeTab];
                }
            });
        }
    };
    
    // Register the Tabs component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Tabs = Tabs;
    
})(typeof window !== 'undefined' ? window : this);
