# Switch UI Kit Documentation

The Switch UI Kit is a comprehensive collection of UI components for the Switch framework. It provides a set of ready-to-use components that follow modern design principles and are fully customizable.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Components](#components)
   - [Button](#button)
   - [Card](#card)
   - [Modal](#modal)
   - [Tabs](#tabs)
   - [Alert](#alert)
   - [Dropdown](#dropdown)
   - [Table](#table)
   - [Form](#form)
   - [Tooltip](#tooltip)
   - [Accordion](#accordion)
   - [Pagination](#pagination)
   - [Progress](#progress)
   - [Spinner](#spinner)
   - [Badge](#badge)
   - [Avatar](#avatar)
   - [DatePicker](#datepicker)
   - [Slider](#slider)
   - [Carousel](#carousel)
4. [Customization](#customization)
5. [Best Practices](#best-practices)

## Installation

The Switch UI Kit is included with the Switch framework. To use it, you need to have Mono and Switch installed:

```bash
# Clone the Mono repository
git clone https://github.com/blackswanalpha/mono.git

# Navigate to the Mono directory
cd mono

# Run a Switch application with the UI Kit
./bin/mono-switch --kits examples/switch_ui_kit_demo.mono
```

## Basic Usage

To use the UI Kit in your Switch application, you need to include the kit's loader script:

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

## Components

### Button

The Button component provides a customizable button element.

#### Usage

```mono
var button = SwitchComponents.Button.create({
    text: "Click Me",
    type: "primary",
    size: "medium",
    disabled: false,
    outline: false,
    block: false,
    rounded: false,
    icon: null,
    iconPosition: "left",
    onClick: function() {
        console.log("Button clicked");
    }
});

// Render the button
button.render();
```

#### Options

- `text`: The button text
- `type`: The button type (`primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`)
- `size`: The button size (`small`/`sm`, `medium`/`md`, `large`/`lg`)
- `disabled`: Whether the button is disabled
- `outline`: Whether to use an outline style
- `block`: Whether the button should be a block-level element
- `rounded`: Whether to use rounded corners
- `icon`: HTML content for an icon
- `iconPosition`: The icon position (`left` or `right`)
- `onClick`: Click event handler
- `attributes`: Additional HTML attributes

### Card

The Card component provides a flexible container with header, body, and footer sections.

#### Usage

```mono
var card = SwitchComponents.Card.create({
    title: "Card Title",
    content: "This is the card content.",
    footer: "Card Footer",
    image: "https://example.com/image.jpg",
    imagePosition: "top",
    shadow: true,
    border: true,
    rounded: true
});

// Render the card
card.render();
```

#### Options

- `title`: The card title
- `content`: The card content (HTML or plain text)
- `footer`: The card footer (HTML or plain text)
- `image`: URL to an image
- `imagePosition`: The image position (`top` or `bottom`)
- `shadow`: Whether to add a shadow
- `border`: Whether to add a border
- `rounded`: Whether to use rounded corners
- `attributes`: Additional HTML attributes

### DatePicker

The DatePicker component provides a date selection interface.

#### Usage

```mono
var datePicker = SwitchComponents.DatePicker.create({
    value: new Date(),
    min: "2023-01-01",
    max: "2023-12-31",
    format: "yyyy-mm-dd",
    placeholder: "Select a date",
    onChange: function(date) {
        console.log("Selected date:", date);
    }
});

// Render the date picker
datePicker.render();
```

#### Options

- `value`: The selected date
- `min`: The minimum selectable date
- `max`: The maximum selectable date
- `format`: The date format
- `placeholder`: The input placeholder
- `disabled`: Whether the date picker is disabled
- `readonly`: Whether the input is readonly
- `required`: Whether the input is required
- `name`: The input name
- `id`: The component ID
- `onChange`: Change event handler
- `attributes`: Additional HTML attributes

### Slider

The Slider component provides a range input with customizable appearance and behavior.

#### Usage

```mono
var slider = SwitchComponents.Slider.create({
    min: 0,
    max: 100,
    value: 50,
    step: 1,
    showValue: true,
    showLabels: true,
    showTicks: false,
    tickInterval: 10,
    vertical: false,
    height: "200px",
    onChange: function(value) {
        console.log("Slider value:", value);
    }
});

// Render the slider
slider.render();
```

#### Options

- `min`: The minimum value
- `max`: The maximum value
- `value`: The current value
- `step`: The step size
- `disabled`: Whether the slider is disabled
- `showValue`: Whether to show the current value
- `showLabels`: Whether to show min/max labels
- `showTicks`: Whether to show tick marks
- `tickInterval`: The interval between tick marks
- `vertical`: Whether to use a vertical orientation
- `height`: The height when vertical
- `onChange`: Change event handler
- `onInput`: Input event handler
- `attributes`: Additional HTML attributes

### Carousel

The Carousel component provides a slideshow for cycling through elements.

#### Usage

```mono
var carousel = SwitchComponents.Carousel.create({
    items: [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
    ],
    autoplay: true,
    autoplayInterval: 5000,
    showControls: true,
    showIndicators: true,
    showCaptions: true,
    infinite: true,
    animation: "slide",
    animationDuration: 500,
    responsive: true,
    aspectRatio: "16:9",
    onChange: function(index) {
        console.log("Carousel slide:", index);
    }
});

// Render the carousel
carousel.render();
```

#### Options

- `items`: Array of items (strings for image URLs or objects with `image`, `caption`, and `content` properties)
- `autoplay`: Whether to automatically cycle through items
- `autoplayInterval`: The interval between slides in milliseconds
- `showControls`: Whether to show navigation controls
- `showIndicators`: Whether to show slide indicators
- `showCaptions`: Whether to show captions
- `infinite`: Whether to loop infinitely
- `animation`: The animation type (`slide` or `fade`)
- `animationDuration`: The animation duration in milliseconds
- `responsive`: Whether to use responsive sizing
- `aspectRatio`: The aspect ratio for responsive sizing
- `onChange`: Change event handler
- `attributes`: Additional HTML attributes

## Customization

You can customize the appearance of the UI Kit components by overriding the CSS variables:

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

## Best Practices

- Use the appropriate component for each UI element
- Maintain consistent styling across your application
- Use the component options to customize behavior rather than modifying the component directly
- Combine components to create more complex UI elements
- Use the kit's CSS variables for theming rather than overriding component styles directly
