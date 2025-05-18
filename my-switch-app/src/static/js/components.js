/**
 * Switch Components - UI Components for the Switch Framework
 * 
 * This module provides reusable UI components for the Switch framework.
 */

(function(global) {
    'use strict';

    // Check if Switch is available
    if (!global.Switch) {
        console.error('Switch framework not found. Make sure to include switch.js before components.js.');
        return;
    }

    // Create the SwitchComponents namespace
    const SwitchComponents = {};

    /**
     * Button Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Button = function(props = {}) {
        const defaults = {
            text: 'Button',
            type: 'primary',
            size: 'medium',
            disabled: false,
            onClick: null
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Button',
            props: mergedProps,
            events: {
                click: function(e) {
                    if (!this.props.disabled && typeof this.props.onClick === 'function') {
                        this.props.onClick(e);
                    }
                }
            },
            render: function() {
                const { text, type, size, disabled } = this.props;
                const classes = [
                    'switch-btn',
                    `switch-btn-${type}`,
                    `switch-btn-${size}`,
                    disabled ? 'switch-btn-disabled' : ''
                ].filter(Boolean).join(' ');

                return `
                    <button class="${classes}" ${disabled ? 'disabled' : ''} data-event="click">
                        ${text}
                    </button>
                `;
            }
        });
    };

    /**
     * Card Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Card = function(props = {}) {
        const defaults = {
            title: '',
            content: '',
            footer: '',
            shadow: true
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Card',
            props: mergedProps,
            render: function() {
                const { title, content, footer, shadow } = this.props;
                const classes = [
                    'switch-card',
                    shadow ? 'switch-card-shadow' : ''
                ].filter(Boolean).join(' ');

                return `
                    <div class="${classes}">
                        ${title ? `<div class="switch-card-header"><h3 class="switch-card-title">${title}</h3></div>` : ''}
                        <div class="switch-card-body">${content}</div>
                        ${footer ? `<div class="switch-card-footer">${footer}</div>` : ''}
                    </div>
                `;
            }
        });
    };

    /**
     * Form Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Form = function(props = {}) {
        const defaults = {
            action: '',
            method: 'post',
            onSubmit: null
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Form',
            props: mergedProps,
            events: {
                submit: function(e) {
                    e.preventDefault();
                    if (typeof this.props.onSubmit === 'function') {
                        // Get form data
                        const formData = new FormData(e.target);
                        const data = {};
                        for (const [key, value] of formData.entries()) {
                            data[key] = value;
                        }
                        this.props.onSubmit(data, e);
                    }
                }
            },
            render: function() {
                const { action, method } = this.props;
                return `
                    <form action="${action}" method="${method}" data-event="submit">
                        <div data-child-container></div>
                    </form>
                `;
            }
        });
    };

    /**
     * Input Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Input = function(props = {}) {
        const defaults = {
            type: 'text',
            name: '',
            label: '',
            value: '',
            placeholder: '',
            required: false,
            disabled: false,
            onChange: null
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Input',
            props: mergedProps,
            events: {
                input: function(e) {
                    if (typeof this.props.onChange === 'function') {
                        this.props.onChange(e.target.value, e);
                    }
                }
            },
            render: function() {
                const { type, name, label, value, placeholder, required, disabled } = this.props;
                const id = `input-${name}-${Date.now()}`;
                return `
                    <div class="switch-form-group">
                        ${label ? `<label class="switch-form-label" for="${id}">${label}</label>` : ''}
                        <input
                            type="${type}"
                            id="${id}"
                            name="${name}"
                            value="${value}"
                            placeholder="${placeholder}"
                            class="switch-form-control"
                            ${required ? 'required' : ''}
                            ${disabled ? 'disabled' : ''}
                            data-event="input"
                        />
                    </div>
                `;
            }
        });
    };

    /**
     * Select Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Select = function(props = {}) {
        const defaults = {
            name: '',
            label: '',
            value: '',
            options: [],
            required: false,
            disabled: false,
            onChange: null
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Select',
            props: mergedProps,
            events: {
                change: function(e) {
                    if (typeof this.props.onChange === 'function') {
                        this.props.onChange(e.target.value, e);
                    }
                }
            },
            render: function() {
                const { name, label, value, options, required, disabled } = this.props;
                const id = `select-${name}-${Date.now()}`;
                
                // Generate options HTML
                const optionsHtml = options.map(option => {
                    if (typeof option === 'object') {
                        return `<option value="${option.value}" ${option.value === value ? 'selected' : ''}>${option.label}</option>`;
                    } else {
                        return `<option value="${option}" ${option === value ? 'selected' : ''}>${option}</option>`;
                    }
                }).join('');
                
                return `
                    <div class="switch-form-group">
                        ${label ? `<label class="switch-form-label" for="${id}">${label}</label>` : ''}
                        <select
                            id="${id}"
                            name="${name}"
                            class="switch-form-control"
                            ${required ? 'required' : ''}
                            ${disabled ? 'disabled' : ''}
                            data-event="change"
                        >
                            ${optionsHtml}
                        </select>
                    </div>
                `;
            }
        });
    };

    /**
     * Checkbox Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Checkbox = function(props = {}) {
        const defaults = {
            name: '',
            label: '',
            checked: false,
            disabled: false,
            onChange: null
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Checkbox',
            props: mergedProps,
            events: {
                change: function(e) {
                    if (typeof this.props.onChange === 'function') {
                        this.props.onChange(e.target.checked, e);
                    }
                }
            },
            render: function() {
                const { name, label, checked, disabled } = this.props;
                const id = `checkbox-${name}-${Date.now()}`;
                return `
                    <div class="switch-form-check">
                        <input
                            type="checkbox"
                            id="${id}"
                            name="${name}"
                            class="switch-form-check-input"
                            ${checked ? 'checked' : ''}
                            ${disabled ? 'disabled' : ''}
                            data-event="change"
                        />
                        ${label ? `<label class="switch-form-check-label" for="${id}">${label}</label>` : ''}
                    </div>
                `;
            }
        });
    };

    /**
     * Alert Component
     * @param {Object} props - Component properties
     * @returns {Object} - Component definition
     */
    SwitchComponents.Alert = function(props = {}) {
        const defaults = {
            type: 'info',
            message: '',
            dismissible: false,
            onDismiss: null
        };

        // Merge props with defaults
        const mergedProps = { ...defaults, ...props };

        // Create the component
        return Switch.createComponent({
            name: 'Alert',
            props: mergedProps,
            state: {
                visible: true
            },
            events: {
                dismiss: function() {
                    this.state.visible = false;
                    if (typeof this.props.onDismiss === 'function') {
                        this.props.onDismiss();
                    }
                    this.update({ visible: false });
                }
            },
            render: function() {
                if (!this.state.visible) {
                    return '';
                }
                
                const { type, message, dismissible } = this.props;
                return `
                    <div class="switch-alert switch-alert-${type}">
                        ${message}
                        ${dismissible ? `<button type="button" class="switch-alert-close" data-event="dismiss">&times;</button>` : ''}
                    </div>
                `;
            }
        });
    };

    // Export the components
    global.SwitchComponents = SwitchComponents;

})(typeof window !== 'undefined' ? window : this);
