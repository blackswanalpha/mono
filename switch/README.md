# Switch Framework for Mono

Switch is a robust frontend framework for the Mono language that enables developers to build interactive web applications. It integrates seamlessly with Mono's HTTP server to provide a complete solution for building modern web applications.

## Features

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

### Creating a Component

Components are the building blocks of a Switch application. Each component can have:

- **State**: Internal mutable data
- **Methods**: Functions that can update state or render output
- **Events**: Handlers for user interactions

Here's a simple example of a Counter component:

```mono
component Counter {
    state {
        count: number = 0
    }
    
    function increment() {
        this.state.count += 1;
    }
    
    function decrement() {
        this.state.count -= 1;
    }
    
    function render() {
        // Use the Switch framework to render the component
        switch.clientEvent("click", "handleIncrement");
        switch.clientEvent("click", "handleDecrement");
        
        // Create a Switch component
        var counter = switch.component("Counter", {
            count: this.state.count
        });
        
        // Return the HTML
        return `
            <div class="switch-card">
                <div class="switch-card-header">
                    <h2>Counter</h2>
                </div>
                <div class="switch-card-body">
                    <p class="switch-text-center">Count: ${this.state.count}</p>
                    <div class="switch-text-center">
                        <button class="switch-button switch-button-primary" data-event="click" data-action="increment">Increment</button>
                        <button class="switch-button switch-button-danger" data-event="click" data-action="decrement">Decrement</button>
                    </div>
                </div>
            </div>
        `;
    }
    
    function handleIncrement(event) {
        if (event.target.dataset.action === "increment") {
            this.increment();
        }
    }
    
    function handleDecrement(event) {
        if (event.target.dataset.action === "decrement") {
            this.decrement();
        }
    }
}
```

### Rendering a Component

To render a component, use the `switch.render` method:

```mono
function start() {
    // Create the app
    var app = new MyApp();
    
    // Render the app
    var html = switch.render("My App", ["/app.js"], ["/app.css"]);
    
    // Configure routes
    http.get("/", "handleRoot");
    
    // Start the server
    http.start();
}

function handleRoot(req, res) {
    // Create the app
    var app = new MyApp();
    
    // Render the app
    var html = switch.render("My App", ["/app.js"], ["/app.css"]);
    
    // Send the response
    res.html(html);
}
```

### Client-Side Events

To handle client-side events, use the `switch.clientEvent` method:

```mono
function render() {
    // Register a client-side event handler
    switch.clientEvent("click", "handleClick");
    
    // Return the HTML
    return `
        <button data-event="click" data-action="doSomething">Click Me</button>
    `;
}

function handleClick(event) {
    if (event.target.dataset.action === "doSomething") {
        // Handle the event
    }
}
```

### Server-Side Events

To handle server-side events, use the `switch.serverEvent` method:

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

## Examples

The Switch framework comes with several examples:

- **switch_app.mono**: A simple application with a counter and a todo list
- **switch_dashboard.mono**: A more complex dashboard application with multiple pages

To run an example:

```bash
./bin/mono-switch examples/switch_app.mono
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

## License

The Switch framework is licensed under the MIT License.
