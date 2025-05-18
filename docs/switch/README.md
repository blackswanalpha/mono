# Switch Framework Documentation

Switch is a modern frontend framework for the Mono language. It provides a component-based architecture, state management, server-side rendering, and more.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Components](#components)
3. [State Management](#state-management)
4. [Server-Side Rendering](#server-side-rendering)
5. [UI Kit](#ui-kit)
6. [Deployment](#deployment)
7. [API Reference](#api-reference)

## Getting Started

### Installation

Switch is included with the Mono language. To use it, you need to have Mono installed:

```bash
# Clone the Mono repository
git clone https://github.com/blackswanalpha/mono.git

# Navigate to the Mono directory
cd mono

# Run a Switch application
./bin/mono-switch examples/switch_ui_kit_demo.mono
```

### Creating a Simple Application

Here's a simple "Hello World" application using Switch:

```mono
component Main {
    function start() {
        print "Starting Hello World app...";
        
        // Configure routes
        http.get("/", "handleRoot");
        
        // Start the server
        http.start();
    }
    
    function handleRoot(req, res) {
        print "Handling request to /";
        
        // Create a Hello component
        var hello = new Hello({ name: "World" });
        
        // Render the app
        var html = switch.render("Hello World", ["/app.js"], ["/app.css"]);
        
        // Send the response
        res.html(html);
    }
}

component Hello {
    function render() {
        return `
            <div class="hello">
                <h1>Hello, ${this.props.name}!</h1>
                <p>Welcome to Switch!</p>
            </div>
        `;
    }
}
```

Run the application:

```bash
./bin/mono-switch hello.mono
```

Then open your browser to `http://localhost:8000` to see the application.

## Components

Components are the building blocks of Switch applications. They encapsulate state and behavior, and can be composed to create complex UIs.

### Creating Components

To create a component, use the `component` keyword:

```mono
component Button {
    function render() {
        return `
            <button class="button ${this.props.type || 'default'}"
                    onclick="handleClick()">
                ${this.props.text || 'Button'}
            </button>
        `;
    }
    
    function handleClick() {
        print "Button clicked!";
        
        // Call the onClick handler if provided
        if (this.props.onClick) {
            this.props.onClick();
        }
    }
}
```

### Component Lifecycle

Components have the following lifecycle methods:

- `init()`: Called when the component is created
- `render()`: Called when the component needs to be rendered
- `update()`: Called when the component's props or state change
- `destroy()`: Called when the component is removed from the DOM

### Props

Props are immutable data passed to a component from its parent:

```mono
// Create a button with props
var button = new Button({
    text: "Click Me",
    type: "primary",
    onClick: function() {
        print "Button was clicked!";
    }
});
```

### State

State is mutable data managed by the component:

```mono
component Counter {
    state {
        count: number = 0
    }
    
    function increment() {
        this.state.count += 1;
    }
    
    function render() {
        return `
            <div class="counter">
                <p>Count: ${this.state.count}</p>
                <button onclick="increment()">Increment</button>
            </div>
        `;
    }
}
```

## State Management

Switch provides a centralized state management system similar to Redux or Vuex.

### Creating a Store

```mono
// Create a store
var store = switch.createStore({
    state: {
        count: 0,
        todos: []
    },
    getters: {
        completedTodos: function(state) {
            return state.todos.filter(function(todo) {
                return todo.completed;
            });
        }
    },
    mutations: {
        INCREMENT: function(state) {
            state.count += 1;
        },
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
```

### Using the Store in Components

```mono
component TodoList {
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
            return `<li>${todo.text}</li>`;
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

## Server-Side Rendering

Switch supports server-side rendering (SSR) for improved performance and SEO.

### Creating SSR Components

```mono
component SSRTodoList {
    function render(renderer) {
        // Fetch data on the server
        var todos = this.fetchTodos();
        
        // Render the component
        var todoItems = todos.map(function(todo) {
            return `<li>${todo.text}</li>`;
        }).join("");
        
        return `
            <div class="todo-list">
                <h2>Todo List</h2>
                <ul>${todoItems}</ul>
                <button onclick="addNewTodo()">Add Todo</button>
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
}
```

### Using SSR in an Application

```mono
component Main {
    function start() {
        print "Starting SSR app...";
        
        // Configure routes
        http.get("/", "handleRoot");
        
        // Start the server
        http.start();
    }
    
    function handleRoot(req, res) {
        print "Handling request to /";
        
        // Create an SSR component
        var todoList = ssr.createComponent(SSRTodoList);
        
        // Render the component
        var html = ssr.renderToString(todoList);
        
        // Send the response
        res.html(html);
    }
}
```

## UI Kit

Switch comes with a comprehensive UI kit that provides ready-to-use components.

### Using UI Kit Components

```mono
component App {
    function render() {
        // Create a button component
        var button = SwitchComponents.Button.create({
            text: "Click Me",
            type: "primary",
            onClick: function() {
                console.log("Button clicked");
            }
        });
        
        // Create a card component
        var card = SwitchComponents.Card.create({
            title: "Card Title",
            content: "This is a card component from the Switch UI Kit."
        });
        
        return `
            <div class="app">
                <h1>UI Kit Demo</h1>
                ${button.render()}
                ${card.render()}
            </div>
        `;
    }
}
```

## Deployment

Switch applications can be deployed to various platforms, including Vercel.

### Deploying to Vercel

```bash
# Deploy to Vercel
./bin/mono-switch-deploy my-app
```

## API Reference

For detailed API documentation, see the [API Reference](api-reference.md).

### Switch Component API

- `switch.component(name, props)`: Create a new component
- `switch.render(title, scripts, styles)`: Render a component to HTML
- `switch.clientEvent(event, handler)`: Register a client-side event handler

### Switch Store API

- `switch.createStore(options)`: Create a new store
- `store.state`: Access the store state
- `store.getters`: Access the store getters
- `store.commit(type, payload)`: Commit a mutation
- `store.dispatch(type, payload)`: Dispatch an action
- `store.subscribe(handler)`: Subscribe to store changes
- `store.watch(getter, callback)`: Watch for changes to a getter

### SSR API

- `ssr.createComponent(componentClass, props)`: Create an SSR component
- `ssr.renderToString(component)`: Render a component to an HTML string
- `ssr.renderToStaticMarkup(component)`: Render a component to static HTML
