/**
 * Switch Form Component
 * 
 * A form component for the Switch framework.
 */

(function(global) {
    'use strict';
    
    // Define the Form component
    const Form = {
        /**
         * Create a new Form component
         * @param {Object} props - Form properties
         * @returns {Object} - Form component
         */
        create: function(props = {}) {
            // Default properties
            const defaultProps = {
                fields: [],
                values: {},
                onSubmit: null,
                onChange: null,
                submitText: 'Submit'
            };
            
            // Merge default properties with provided properties
            const mergedProps = Object.assign({}, defaultProps, props);
            
            // Create the component
            return Switch.createComponent({
                name: 'Form',
                props: mergedProps,
                state: {
                    values: mergedProps.values || {},
                    errors: {}
                },
                render: function(props, state) {
                    // Build the form HTML
                    let html = `<form class="switch-form" data-event="submit">`;
                    
                    // Add fields
                    props.fields.forEach(field => {
                        html += this.renderField(field, state.values[field.name], state.errors[field.name]);
                    });
                    
                    // Add submit button
                    html += `
                        <div class="switch-form-group">
                            <button type="submit" class="switch-button switch-button-primary">
                                ${props.submitText}
                            </button>
                        </div>
                    `;
                    
                    html += '</form>';
                    
                    return html;
                },
                renderField: function(field, value, error) {
                    // Default value
                    value = value !== undefined ? value : '';
                    
                    // Field wrapper
                    let html = `<div class="switch-form-group">`;
                    
                    // Add label if provided
                    if (field.label) {
                        html += `<label for="${field.name}" class="switch-form-label">${field.label}</label>`;
                    }
                    
                    // Render different field types
                    switch (field.type) {
                        case 'textarea':
                            html += `
                                <textarea class="switch-form-control ${error ? 'switch-form-error' : ''}"
                                    id="${field.name}" name="${field.name}" placeholder="${field.placeholder || ''}"
                                    data-event="change" ${field.required ? 'required' : ''}>
                                    ${value}
                                </textarea>
                            `;
                            break;
                        case 'select':
                            html += `
                                <select class="switch-form-control ${error ? 'switch-form-error' : ''}"
                                    id="${field.name}" name="${field.name}"
                                    data-event="change" ${field.required ? 'required' : ''}>
                            `;
                            
                            // Add options
                            if (field.options) {
                                field.options.forEach(option => {
                                    const selected = option.value === value ? 'selected' : '';
                                    html += `<option value="${option.value}" ${selected}>${option.label}</option>`;
                                });
                            }
                            
                            html += '</select>';
                            break;
                        case 'checkbox':
                            html += `
                                <div class="switch-form-check">
                                    <input type="checkbox" class="switch-form-check-input"
                                        id="${field.name}" name="${field.name}"
                                        ${value ? 'checked' : ''} data-event="change">
                                    <label class="switch-form-check-label" for="${field.name}">
                                        ${field.checkboxLabel || field.label}
                                    </label>
                                </div>
                            `;
                            break;
                        case 'radio':
                            if (field.options) {
                                field.options.forEach(option => {
                                    const checked = option.value === value ? 'checked' : '';
                                    html += `
                                        <div class="switch-form-check">
                                            <input type="radio" class="switch-form-check-input"
                                                id="${field.name}_${option.value}" name="${field.name}" value="${option.value}"
                                                ${checked} data-event="change">
                                            <label class="switch-form-check-label" for="${field.name}_${option.value}">
                                                ${option.label}
                                            </label>
                                        </div>
                                    `;
                                });
                            }
                            break;
                        default:
                            // Default to text input
                            html += `
                                <input type="${field.type || 'text'}" class="switch-form-control ${error ? 'switch-form-error' : ''}"
                                    id="${field.name}" name="${field.name}" value="${value}"
                                    placeholder="${field.placeholder || ''}" data-event="change"
                                    ${field.required ? 'required' : ''}>
                            `;
                    }
                    
                    // Add error message if any
                    if (error) {
                        html += `<div class="switch-form-error-message">${error}</div>`;
                    }
                    
                    html += '</div>';
                    
                    return html;
                },
                events: {
                    change: function(event) {
                        const name = event.target.name;
                        let value;
                        
                        // Get the appropriate value based on the field type
                        if (event.target.type === 'checkbox') {
                            value = event.target.checked;
                        } else {
                            value = event.target.value;
                        }
                        
                        // Update the state
                        const newValues = Object.assign({}, this.state.values);
                        newValues[name] = value;
                        
                        this.update({ values: newValues });
                        
                        // Call the onChange handler if provided
                        if (typeof this.props.onChange === 'function') {
                            this.props.onChange(name, value, newValues);
                        }
                    },
                    submit: function(event) {
                        event.preventDefault();
                        
                        // Validate the form
                        const errors = this.validate();
                        
                        // Update the state with errors
                        this.update({ errors });
                        
                        // If there are no errors, call the onSubmit handler
                        if (Object.keys(errors).length === 0 && typeof this.props.onSubmit === 'function') {
                            this.props.onSubmit(this.state.values);
                        }
                    }
                },
                validate: function() {
                    const errors = {};
                    
                    // Validate each field
                    this.props.fields.forEach(field => {
                        const value = this.state.values[field.name];
                        
                        // Check required fields
                        if (field.required && (value === undefined || value === '' || value === null)) {
                            errors[field.name] = `${field.label || field.name} is required`;
                        }
                        
                        // Check custom validation
                        if (field.validate && typeof field.validate === 'function') {
                            const error = field.validate(value);
                            if (error) {
                                errors[field.name] = error;
                            }
                        }
                    });
                    
                    return errors;
                }
            });
        }
    };
    
    // Register the Form component
    if (!global.SwitchComponents) {
        global.SwitchComponents = {};
    }
    
    global.SwitchComponents.Form = Form;
    
})(typeof window !== 'undefined' ? window : this);
