# Switch UI Kit

A collection of UI components for the Switch framework.

## Overview

The Switch UI Kit provides a set of reusable UI components for building web applications with the Switch framework. It includes components for common UI patterns such as buttons, cards, modals, tabs, and more.

## Components

The kit includes the following components:

- **Button**: A customizable button component
- **Card**: A card component with header, body, and footer
- **Modal**: A modal dialog component
- **Tabs**: A tabbed interface component
- **Alert**: An alert component for notifications
- **Dropdown**: A dropdown menu component
- **Table**: A table component with sorting, filtering, and pagination
- **Form**: A form component with validation
- **Tooltip**: A tooltip component for displaying additional information
- **Accordion**: An accordion component for collapsible content
- **Pagination**: A pagination component for navigating through pages
- **Progress**: A progress bar component
- **Spinner**: A loading spinner component
- **Badge**: A badge component for displaying counts or status
- **Avatar**: An avatar component for displaying user images

## Usage

To use the Switch UI Kit in your Switch application, you need to include the kit's loader script in your HTML:

```html
<script src="/kits/SwitchUIKit/loader.js"></script>
```

Alternatively, you can enable kit integration in the Switch interpreter:

```python
interpreter = SwitchInterpreter(use_kits=True)
```

Then, you can use the components in your Mono code:

```mono
component MyComponent {
    function render() {
        // Create a button component
        var button = SwitchComponents.Button.create({
            text: "Click Me",
            type: "primary",
            size: "medium",
            onClick: function() {
                console.log("Button clicked");
            }
        });
        
        // Return the HTML
        return `
            <div class="my-component">
                <h1>My Component</h1>
                ${button.render()}
            </div>
        `;
    }
}
```

## Customization

You can customize the appearance of the components by overriding the CSS variables:

```css
:root {
  --switch-primary-color: #3b82f6;
  --switch-secondary-color: #6b7280;
  --switch-success-color: #10b981;
  --switch-danger-color: #ef4444;
  --switch-warning-color: #f59e0b;
  --switch-info-color: #3b82f6;
  --switch-light-color: #f3f4f6;
  --switch-dark-color: #1f2937;
  --switch-white-color: #ffffff;
  --switch-black-color: #000000;
  
  --switch-border-radius: 0.25rem;
  --switch-border-color: #e5e7eb;
  --switch-box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  
  --switch-font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --switch-font-size: 1rem;
  --switch-line-height: 1.5;
  
  --switch-transition-duration: 0.2s;
  --switch-transition-timing: ease-in-out;
}
```

## License

This kit is licensed under the MIT License.
