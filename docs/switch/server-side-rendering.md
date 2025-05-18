# Server-Side Rendering in Switch

Server-Side Rendering (SSR) is a technique for rendering web pages on the server instead of in the browser. The Switch framework provides built-in support for SSR, allowing you to create applications that load faster and are more SEO-friendly.

## Table of Contents

1. [Introduction](#introduction)
2. [Benefits of SSR](#benefits-of-ssr)
3. [How SSR Works in Switch](#how-ssr-works-in-switch)
4. [Creating SSR Components](#creating-ssr-components)
5. [SSR with State Management](#ssr-with-state-management)
6. [SSR Context](#ssr-context)
7. [Hydration](#hydration)
8. [Partial Hydration](#partial-hydration)
9. [SSR Middleware](#ssr-middleware)
10. [Performance Optimization](#performance-optimization)
11. [Best Practices](#best-practices)

## Introduction

Server-Side Rendering (SSR) is the process of rendering a client-side application on the server and sending the fully rendered HTML to the client. This approach combines the benefits of traditional server rendering (faster initial load, better SEO) with the benefits of client-side rendering (rich interactivity, client-side navigation).

## Benefits of SSR

- **Faster Initial Load**: Users see the content sooner because the HTML is already rendered
- **Better SEO**: Search engines can index the content more easily
- **Improved Performance on Low-End Devices**: Less JavaScript needs to be parsed and executed on the client
- **Better User Experience**: Users see content immediately, reducing perceived load time
- **Social Media Sharing**: Better preview cards when sharing links on social media

## How SSR Works in Switch

The Switch framework uses a hybrid approach to SSR:

1. The server renders the initial HTML for the page
2. The client "hydrates" the HTML with JavaScript to make it interactive
3. Subsequent navigation and updates happen on the client

This approach gives you the best of both worlds: fast initial load times and rich interactivity.

## Creating SSR Components

To create an SSR component, use the `SSRComponent` class:

```mono
component TodoListSSR {
    function render(renderer) {
        // Fetch data on the server
        var todos = this.fetchTodos();
        
        // Set the data for client-side hydration
        this.set_state({
            todos: todos
        });
        
        // Render the component
        var todoItems = todos.map(function(todo) {
            return `<li class="${todo.completed ? 'completed' : ''}">${todo.text}</li>`;
        }).join("");
        
        return `
            <div class="todo-list">
                <h2>Todo List</h2>
                <ul>${todoItems}</ul>
                <button onclick="addTodo()">Add Todo</button>
            </div>
        `;
    }
    
    function fetchTodos() {
        // This runs on the server
        return [
            { id: 1, text: "Learn Mono", completed: true },
            { id: 2, text: "Learn Switch", completed: false }
        ];
    }
    
    function addTodo() {
        // This runs on the client
        var todos = this.state.todos;
        todos.push({
            id: Date.now(),
            text: "New Todo",
            completed: false
        });
        this.set_state({ todos: todos });
    }
}
```

To render an SSR component, use the `ssr.createComponent` and `ssr.renderToString` functions:

```mono
function handleRoot(req, res) {
    // Create an SSR component
    var todoList = ssr.createComponent(TodoListSSR);
    
    // Render the component to HTML
    var html = ssr.renderToString(todoList);
    
    // Send the response
    res.html(html);
}
```

## SSR with State Management

You can use the Switch state management system with SSR. The store is created on the server, and its state is serialized and sent to the client for hydration:

```mono
// Create a store
var store = switch.createStore({
    state: {
        todos: [
            { id: 1, text: "Learn Mono", completed: true },
            { id: 2, text: "Learn Switch", completed: false }
        ]
    },
    mutations: {
        ADD_TODO: function(state, todo) {
            state.todos.push(todo);
        }
    },
    actions: {
        addTodo: function(context, text) {
            var todo = {
                id: Date.now(),
                text: text,
                completed: false
            };
            context.commit('ADD_TODO', todo);
        }
    }
});

// Create an SSR component that uses the store
var todoList = ssr.createComponent(TodoListSSR, null, store);

// Render the component to HTML
var html = ssr.renderToString(todoList);
```

On the client, the store is automatically hydrated with the server state:

```mono
component TodoListSSR {
    function init() {
        // Use the store
        this.use_store(store);
        
        // Map state to props
        this.map_state({
            todos: "todos"
        });
        
        // Map actions to methods
        this.map_actions({
            addTodo: "addTodo"
        });
    }
    
    function render() {
        var todoItems = this.props.todos.map(function(todo) {
            return `<li class="${todo.completed ? 'completed' : ''}">${todo.text}</li>`;
        }).join("");
        
        return `
            <div class="todo-list">
                <h2>Todo List</h2>
                <ul>${todoItems}</ul>
                <button onclick="addNewTodo()">Add Todo</button>
            </div>
        `;
    }
    
    function addNewTodo() {
        this.addTodo("New Todo");
    }
}
```

## SSR Context

The SSR context allows you to share data between components during server-side rendering:

```mono
// Create an SSR renderer with context
var renderer = new SSRRenderer();
renderer.set_ssr_context({
    user: {
        name: "John Doe",
        role: "Admin"
    },
    theme: "light"
});

// Use the context in a component
component Header {
    function render(renderer) {
        // Get the context
        var context = this.get_ssr_context();
        var user = context.user;
        
        return `
            <header>
                <h1>Welcome, ${user.name}</h1>
                <p>Role: ${user.role}</p>
            </header>
        `;
    }
}
```

## Hydration

Hydration is the process of attaching event listeners and state to the server-rendered HTML on the client. The Switch framework handles hydration automatically:

```mono
// Server-side
var html = ssr.renderToString(component);

// Client-side
// The component is automatically hydrated
```

The hydration process:

1. The server renders the component to HTML
2. The HTML is sent to the client
3. The client loads the JavaScript
4. The JavaScript "hydrates" the HTML by attaching event listeners and state
5. The component becomes interactive

## Partial Hydration

Partial hydration allows you to hydrate only specific parts of the page, reducing the amount of JavaScript that needs to be executed:

```mono
// Server-side
var html = ssr.renderToString(component, { hydrate: ["header", "footer"] });

// Client-side
// Only the header and footer components are hydrated
```

## SSR Middleware

The Switch framework provides middleware for handling SSR requests:

```mono
// Create an SSR middleware
var ssrMiddleware = new SSRMiddleware();

// Register components
ssrMiddleware.register_component(new Header());
ssrMiddleware.register_component(new Footer());
ssrMiddleware.register_component(new TodoList());

// Use the middleware
http.use(ssrMiddleware.handle);

// Handle requests
http.get("/", function(req, res) {
    // Render a component
    var html = ssrMiddleware.render_page("TodoList");
    res.html(html);
});
```

## Performance Optimization

To optimize SSR performance:

- **Caching**: Cache rendered HTML for static or rarely changing pages
- **Streaming**: Stream the HTML to the client as it's generated
- **Code Splitting**: Split your JavaScript into smaller chunks
- **Lazy Loading**: Load components only when they're needed
- **Prefetching**: Prefetch resources that will be needed soon

Example of caching:

```mono
var cache = {};

function handleRoot(req, res) {
    // Check if the page is in the cache
    if (cache[req.path]) {
        res.html(cache[req.path]);
        return;
    }
    
    // Render the page
    var html = ssr.renderToString(component);
    
    // Cache the page
    cache[req.path] = html;
    
    // Send the response
    res.html(html);
}
```

## Best Practices

- **Keep Components Simple**: Complex components are harder to render on the server
- **Avoid Browser-Specific APIs**: Use feature detection and conditional execution
- **Handle Async Data**: Fetch data before rendering or use placeholders
- **Optimize for First Contentful Paint**: Prioritize rendering above-the-fold content
- **Use Code Splitting**: Split your JavaScript into smaller chunks
- **Implement Progressive Enhancement**: Ensure the application works without JavaScript
- **Test Both Server and Client Rendering**: Ensure consistency between environments
- **Monitor Performance**: Track server rendering time and client hydration time
