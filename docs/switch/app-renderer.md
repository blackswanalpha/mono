# Switch Application Renderer

The Switch Application Renderer is a powerful tool for building and rendering Switch web applications. It provides a streamlined way to create, develop, and deploy web applications using the Switch framework.

## Features

- **Application Management**: Manage your Switch application with a dedicated application object
- **Component Rendering**: Render Switch components with ease
- **Asset Management**: Manage scripts, styles, and static assets
- **Server-Side Rendering**: Render components on the server for faster initial load
- **Hot Module Replacement**: Update components without reloading the page
- **Static File Serving**: Serve static files from a dedicated directory
- **Build Process**: Build your application for production deployment

## Getting Started

### Creating a New Application

To create a new Switch application, use the `mono-switch-create` command:

```bash
mono-switch-create my-app
```

This will create a new application in the `my-app` directory with the following structure:

```
my-app/
├── main.mono       # Entry point for the application
├── static/         # Static assets
│   ├── css/        # CSS files
│   │   └── app.css # Application styles
│   ├── js/         # JavaScript files
│   │   └── app.js  # Application scripts
│   └── img/        # Images
└── README.md       # Application documentation
```

### Running the Application

To run the application in development mode, use the `mono-switch` command:

```bash
cd my-app
mono-switch main.mono
```

This will start a development server on port 8000. You can access the application at [http://localhost:8000](http://localhost:8000).

### Building for Production

To build the application for production, use the `mono-switch-build` command:

```bash
mono-switch-build main.mono --output build
```

This will create a production-ready build in the `build` directory.

## Application Structure

A typical Switch application consists of the following components:

### Main Component

The `Main` component is the entry point for the application. It sets up the HTTP server and handles requests:

```mono
component Main {
    function start() {
        // Create the app
        var app = new App();
        
        // Configure routes
        http.get("/", "handleRoot");
        
        // Start the server
        http.start();
    }
    
    function handleRoot(req, res) {
        // Create the app
        var app = new App();
        
        // Render the app
        var html = switch.render("My App", ["/static/js/app.js"], ["/static/css/app.css"]);
        
        // Send the response
        res.html(html);
    }
}
```

### App Component

The `App` component is the root component for the application. It manages the application state and renders the UI:

```mono
component App {
    state {
        title: string = "My App",
        count: number = 0
    }
    
    function render() {
        // Register client-side event handlers
        switch.clientEvent("click", "handleClick");
        
        // Create the component
        var app = switch.component("App", {
            title: this.state.title,
            count: this.state.count
        });
        
        // Return the HTML
        return `
            <div class="app">
                <h1>${this.state.title}</h1>
                <p>Count: ${this.state.count}</p>
                <button data-event="click" data-action="increment">Increment</button>
            </div>
        `;
    }
    
    function handleClick(event) {
        if (event.target.dataset.action === "increment") {
            this.state.count++;
        }
    }
}
```

## Advanced Features

### Server-Side Rendering

To enable server-side rendering, use the `--ssr` flag when running the application:

```bash
mono-switch --ssr main.mono
```

This will render the components on the server and hydrate them on the client.

### Hot Module Replacement

To enable hot module replacement, use the `--hmr` flag when running the application:

```bash
mono-switch --hmr main.mono
```

This will update components without reloading the page when you make changes to the source code.

### Static File Serving

The application renderer automatically serves static files from the `static` directory. You can access them at `/static/path/to/file`.

### Custom Scripts and Styles

You can add custom scripts and styles to your application by passing them to the `switch.render` method:

```mono
var html = switch.render(
    "My App",
    [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
        "/static/js/app.js"
    ],
    [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
        "/static/css/app.css"
    ]
);
```

## API Reference

### SwitchApp

The `SwitchApp` class represents a Switch application.

#### Constructor

```python
SwitchApp(name: str = "Switch App", root_component: Optional[SwitchComponent] = None, use_ssr: bool = False, use_hmr: bool = False, debug: bool = False)
```

#### Methods

- `set_root_component(component: SwitchComponent) -> None`: Set the root component for the application
- `add_script(script: str) -> None`: Add a script to the application
- `add_style(style: str) -> None`: Add a style to the application
- `set_store(store: Store) -> None`: Set the global store for the application
- `set_static_dir(directory: str) -> None`: Set the directory for static assets
- `set_build_dir(directory: str) -> None`: Set the directory for build output
- `add_route(path: str, handler: Callable) -> None`: Add a route to the application
- `render() -> str`: Render the application to HTML
- `configure_http_server(http_server) -> None`: Configure the HTTP server for the application
- `build(output_dir: str) -> None`: Build the application for production

### Global Functions

- `get_switch_app() -> SwitchApp`: Get the global Switch application instance
- `set_switch_app(app: SwitchApp) -> None`: Set the global Switch application instance

## Examples

Check out the examples in the `examples` directory:

- `switch_app_renderer.mono`: A simple application that demonstrates the application renderer
- `switch_app.mono`: A more complex application with a counter and a todo list
- `switch_dashboard.mono`: A dashboard application with multiple pages

## License

The Switch Application Renderer is licensed under the MIT License.
