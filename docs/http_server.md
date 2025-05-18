# Mono HTTP Server

The Mono HTTP Server is a simple web server implementation for the Mono language. It provides a way to create web applications and APIs using Mono components.

## Features

- **HTTP Server**: A simple HTTP server for handling web requests
- **Request Handling**: Parse and handle HTTP requests
- **Response Building**: Build and send HTTP responses
- **Routing**: Route requests to appropriate handlers

## Usage

To run a Mono HTTP server, use the `mono-http` command:

```bash
./bin/mono-http <script.mono>
```

For example:

```bash
./bin/mono-http examples/web_server.mono
./bin/mono-http examples/rest_api.mono
./bin/mono-http examples/static_server.mono
```

## Creating a Web Server

Here's a simple example of a web server in Mono:

```mono
component WebServer {
    state {
        port: number = 8000;
        host: string = "localhost";
    }
    
    function constructor(port: number, host: string) {
        if (port) {
            this.port = port;
        }
        if (host) {
            this.host = host;
        }
    }
    
    function start() {
        print "Starting web server on " + this.host + ":" + this.port;
        
        // Configure routes
        http.get("/", "handleRoot");
        http.get("/hello", "handleHello");
        http.get("/users/:id", "handleUser");
        http.post("/api/data", "handleData");
        
        // Start the server
        http.start();
        
        print "Server is running. Press Ctrl+C to stop.";
    }
    
    function handleRoot(req, res) {
        print "Handling request to /";
        res.html("<html><body><h1>Welcome to Mono Web Server</h1><p>A simple HTTP server written in Mono</p></body></html>");
    }
    
    function handleHello(req, res) {
        print "Handling request to /hello";
        
        // Get the name from query parameters
        var name = req.query.name ? req.query.name[0] : "World";
        
        res.html("<html><body><h1>Hello, " + name + "!</h1><p>Welcome to Mono Web Server</p></body></html>");
    }
    
    function handleUser(req, res) {
        print "Handling request to /users/:id";
        
        // Get the user ID from route parameters
        var userId = req.params.id;
        
        // Simulate a database lookup
        var user = {
            id: userId,
            name: "User " + userId,
            email: "user" + userId + "@example.com"
        };
        
        res.json(user);
    }
}

component Main {
    function start() {
        print "=== Mono Web Server Example ===";
        
        // Create a web server on port 8000
        var server = new WebServer(8000, "localhost");
        
        // Start the server
        server.start();
    }
}
```

## HTTP API

### Server Methods

- `http.start()`: Start the HTTP server
- `http.stop()`: Stop the HTTP server
- `http.get(path, handlerMethod)`: Register a GET route
- `http.post(path, handlerMethod)`: Register a POST route
- `http.put(path, handlerMethod)`: Register a PUT route
- `http.delete(path, handlerMethod)`: Register a DELETE route

### Request Object

The request object is passed to handler methods and contains information about the HTTP request:

- `req.method`: The HTTP method (GET, POST, etc.)
- `req.path`: The request path
- `req.headers`: The request headers
- `req.body`: The request body
- `req.params`: Route parameters (e.g., `:id` in `/users/:id`)
- `req.query`: Query parameters (e.g., `?name=John`)

### Response Object

The response object is passed to handler methods and provides methods for sending HTTP responses:

- `res.status(code)`: Set the status code
- `res.header(name, value)`: Set a header
- `res.text(content)`: Send a text response
- `res.html(content)`: Send an HTML response
- `res.json(data)`: Send a JSON response

## Examples

### Simple Web Server

See `examples/web_server.mono` for a simple web server example.

### RESTful API Server

See `examples/rest_api.mono` for a RESTful API server example.

### Static File Server

See `examples/static_server.mono` for a static file server example.
