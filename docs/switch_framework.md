# Switch Framework Documentation

The Switch framework is a robust frontend framework for the Mono language that enables developers to build interactive web applications. It integrates seamlessly with Mono's HTTP server to provide a complete solution for building modern web applications.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Components](#components)
4. [State Management](#state-management)
5. [Event Handling](#event-handling)
6. [Routing](#routing)
7. [Server Integration](#server-integration)
8. [Built-in Components](#built-in-components)
9. [API Reference](#api-reference)
10. [Examples](#examples)

## Introduction

Switch is a component-based frontend framework for Mono that allows you to build interactive web applications. It provides a seamless integration between the server-side Mono code and the client-side JavaScript code, enabling you to build modern web applications with ease.

Key features of the Switch framework include:

- **Component-based architecture**: Build UIs with reusable components
- **Client-side rendering**: Render components on the client for a responsive UI
- **State management**: Components have internal mutable state
- **Event handling**: Handle user interactions with event handlers
- **Routing**: Navigate between pages without full page reloads
- **Server integration**: Seamlessly integrate with Mono's HTTP server

## Getting Started

### Installation

The Switch framework is included with Mono. To use it, simply run your Mono application with the `mono-switch` command:

```bash
./bin/mono-switch examples/switch_app.mono
```

### Creating a Simple Application

Here's a simple "Hello World" application using the Switch framework:

```mono
component HelloWorld {
    state {
        message: string = "Hello, World!"
    }
    
    function render() {
        // Create a Switch component
        var hello = switch.component("HelloWorld", {
            message: this.state.message
        });
        
        // Return the HTML
        return `
            <div class="switch-card">
                <div class="switch-card-body">
                    <h1>${this.state.message}</h1>
                </div>
            </div>
        `;
    }
}

component Main {
    function start() {
        // Create the app
        var app = new HelloWorld();
        
        // Render the app
        var html = switch.render("Hello World");
        
        // Configure routes
        http.get("/", "handleRoot");
        
        // Start the server
        http.start();
    }
    
    function handleRoot(req, res) {
        // Create the app
        var app = new HelloWorld();
        
        // Render the app
        var html = switch.render("Hello World");
        
        // Send the response
        res.html(html);
    }
}
```

## Components

Components are the building blocks of a Switch application. Each component can have:

- **State**: Internal mutable data
- **Methods**: Functions that can update state or render output
- **Events**: Handlers for user interactions

### Component Structure

A typical Switch component has the following structure:

```mono
component MyComponent {
    state {
        // Component state
        count: number = 0
    }
    
    function constructor() {
        // Initialize the component
    }
    
    function someMethod() {
        // Component method
    }
    
    function render() {
        // Render the component
        return `
            <div>
                <!-- Component HTML -->
            </div>
        `;
    }
}
```

### Component Lifecycle

Switch components have a simple lifecycle:

1. **Constructor**: Initialize the component
2. **Render**: Render the component to HTML
3. **Event Handlers**: Handle user interactions
4. **Update**: Update the component state and re-render

## State Management

Each Switch component can have its own state, which is a collection of properties that can be updated. When the state changes, the component is automatically re-rendered.

### Defining State

State is defined in the `state` block of a component:

```mono
component Counter {
    state {
        count: number = 0
    }
}
```

### Updating State

State can be updated using component methods:

```mono
function increment() {
    this.state.count += 1;
}
```

## Event Handling

Switch provides a simple way to handle user interactions through events.

### Client-Side Events

Client-side events are handled in the browser:

```mono
function render() {
    // Register a client-side event handler
    switch.clientEvent("click", "handleClick");
    
    // Return the HTML
    return `
        <button data-event="click" data-action="increment">Increment</button>
    `;
}

function handleClick(event) {
    if (event.target.dataset.action === "increment") {
        this.increment();
    }
}
```

### Server-Side Events

Server-side events are handled on the server:

```mono
function render() {
    // Register a server-side event handler
    switch.serverEvent("saveData", "handleSaveData");
    
    // Return the HTML
    return `
        <button data-event="click" data-action="save">Save</button>
    `;
}

function handleClick(event) {
    if (event.target.dataset.action === "save") {
        // Call the server-side event handler
        Switch.callServerEvent(this.id, "saveData", { data: this.state.data });
    }
}

function handleSaveData(data) {
    // This method will be called on the server-side
    print "Saving data: " + JSON.stringify(data);
    return {
        success: true,
        message: "Data saved successfully"
    };
}
```

## Routing

Switch provides a client-side router for navigating between pages without full page reloads.

### Defining Routes

Routes are defined on the client-side:

```javascript
// Initialize the Switch router
Switch.router.addRoute('/', function() {
    console.log('Home route');
});

Switch.router.addRoute('/about', function() {
    console.log('About route');
});
```

### Navigating Between Routes

You can navigate between routes using the `navigate` method:

```javascript
// Navigate to the about page
Switch.router.navigate('/about');
```

## Server Integration

Switch integrates seamlessly with Mono's HTTP server.

### Rendering Components

Components are rendered on the server and sent to the client:

```mono
function handleRoot(req, res) {
    // Create the app
    var app = new MyApp();
    
    // Render the app
    var html = switch.render("My App");
    
    // Send the response
    res.html(html);
}
```

### Handling API Requests

API requests are handled on the server:

```mono
function handleEvent(req, res) {
    // Get the request body
    var data = JSON.parse(req.body);
    
    // Handle the event
    var result = handleServerEvent(data);
    
    // Send the response
    res.json(result);
}
```

## Built-in Components

Switch comes with several built-in components:

### Button

A customizable button component:

```javascript
// Create a button
const button = SwitchComponents.Button.create({
    text: 'Click Me',
    type: 'primary',
    size: 'medium',
    onClick: function() {
        console.log('Button clicked');
    }
});
```

### Card

A card component for displaying content:

```javascript
// Create a card
const card = SwitchComponents.Card.create({
    title: 'Card Title',
    content: 'Card content goes here',
    footer: 'Card footer'
});
```

### Form

A form component for collecting user input:

```javascript
// Create a form
const form = SwitchComponents.Form.create({
    fields: [
        {
            name: 'name',
            label: 'Name',
            type: 'text',
            required: true
        },
        {
            name: 'email',
            label: 'Email',
            type: 'email',
            required: true
        }
    ],
    onSubmit: function(values) {
        console.log('Form submitted', values);
    }
});
```

## API Reference

### Server-Side API

- **switch.render(title, scripts, styles)**: Render a component to HTML
- **switch.clientEvent(event, handler)**: Register a client-side event handler
- **switch.serverEvent(event, handler)**: Register a server-side event handler
- **switch.component(name, props)**: Create a Switch component

### Client-Side API

- **Switch.init(options)**: Initialize the Switch framework
- **Switch.createComponent(definition)**: Create a component
- **Switch.renderComponent(component, container)**: Render a component
- **Switch.callServerEvent(componentId, handler, data)**: Call a server-side event handler
- **Switch.router.addRoute(path, handler)**: Add a route
- **Switch.router.navigate(path, state)**: Navigate to a path

## Examples

The Switch framework comes with several examples:

- **switch_app.mono**: A simple application with a counter and a todo list
- **switch_dashboard.mono**: A more complex dashboard application with multiple pages

To run an example:

```bash
./bin/mono-switch examples/switch_app.mono
```
