# Building a TODO App with Switch

This tutorial will guide you through building a simple TODO application using the Switch framework. You'll learn how to create components, manage state, handle events, and use server-side rendering.

## Prerequisites

- Mono installed
- Basic knowledge of Mono syntax
- Basic understanding of HTML, CSS, and JavaScript

## Step 1: Create the Project Structure

Create a new directory for your project:

```bash
mkdir todo-app
cd todo-app
```

Create the following files:

- `todo-app.mono`: The main application file
- `static/styles.css`: CSS styles for the application
- `static/app.js`: Client-side JavaScript

## Step 2: Create the Main Component

Edit `todo-app.mono` and add the following code:

```mono
//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// TODO App

component Main {
    function start() {
        print "Starting TODO App...";
        
        // Create the store
        var store = switch.createStore({
            state: {
                todos: []
            },
            mutations: {
                ADD_TODO: function(state, todo) {
                    state.todos.push(todo);
                },
                TOGGLE_TODO: function(state, id) {
                    for (var i = 0; i < state.todos.length; i++) {
                        if (state.todos[i].id === id) {
                            state.todos[i].completed = !state.todos[i].completed;
                            break;
                        }
                    }
                },
                REMOVE_TODO: function(state, id) {
                    state.todos = state.todos.filter(function(todo) {
                        return todo.id !== id;
                    });
                }
            },
            actions: {
                addTodo: function(context, text) {
                    if (!text.trim()) {
                        return;
                    }
                    
                    var todo = {
                        id: Date.now(),
                        text: text,
                        completed: false
                    };
                    
                    context.commit('ADD_TODO', todo);
                },
                toggleTodo: function(context, id) {
                    context.commit('TOGGLE_TODO', id);
                },
                removeTodo: function(context, id) {
                    context.commit('REMOVE_TODO', id);
                }
            }
        });
        
        // Configure routes
        http.get("/", "handleRoot");
        http.get("/styles.css", "handleStyles");
        http.get("/app.js", "handleAppJs");
        
        // Start the server
        http.start();
    }
    
    function handleRoot(req, res) {
        print "Handling request to /";
        
        // Create the TodoApp component
        var todoApp = new TodoApp();
        
        // Render the app
        var html = switch.render("TODO App", ["/app.js"], ["/styles.css"]);
        
        // Send the response
        res.html(html);
    }
    
    function handleStyles(req, res) {
        print "Handling request to /styles.css";
        
        // Read the CSS file
        var css = file.read("static/styles.css");
        
        // Send the response
        res.header("Content-Type", "text/css");
        res.text(css);
    }
    
    function handleAppJs(req, res) {
        print "Handling request to /app.js";
        
        // Read the JavaScript file
        var js = file.read("static/app.js");
        
        // Send the response
        res.header("Content-Type", "application/javascript");
        res.text(js);
    }
}

component TodoApp {
    state {
        newTodo: string = "",
        filter: string = "all"
    }
    
    function init() {
        // Use the store
        this.use_store(store);
        
        // Map state to props
        this.map_state({
            todos: "todos"
        });
        
        // Map actions to methods
        this.map_actions({
            addTodo: "addTodo",
            toggleTodo: "toggleTodo",
            removeTodo: "removeTodo"
        });
    }
    
    function render() {
        // Register client-side event handlers
        switch.clientEvent("submit", "handleSubmit");
        switch.clientEvent("click", "handleClick");
        switch.clientEvent("change", "handleChange");
        
        // Filter todos
        var filteredTodos = this.getFilteredTodos();
        
        // Render the todo items
        var todoItems = filteredTodos.map(function(todo) {
            return `
                <li class="todo-item ${todo.completed ? 'completed' : ''}">
                    <input type="checkbox" 
                           class="todo-checkbox" 
                           data-id="${todo.id}" 
                           ${todo.completed ? 'checked' : ''}>
                    <span class="todo-text">${todo.text}</span>
                    <button class="todo-delete" data-id="${todo.id}">×</button>
                </li>
            `;
        }).join("");
        
        // Return the HTML
        return `
            <div class="todo-app">
                <h1>TODO App</h1>
                
                <form class="todo-form">
                    <input type="text" 
                           class="todo-input" 
                           placeholder="What needs to be done?" 
                           value="${this.state.newTodo}">
                    <button type="submit" class="todo-add">Add</button>
                </form>
                
                <ul class="todo-list">
                    ${todoItems}
                </ul>
                
                <div class="todo-filters">
                    <button class="todo-filter ${this.state.filter === 'all' ? 'active' : ''}" 
                            data-filter="all">All</button>
                    <button class="todo-filter ${this.state.filter === 'active' ? 'active' : ''}" 
                            data-filter="active">Active</button>
                    <button class="todo-filter ${this.state.filter === 'completed' ? 'active' : ''}" 
                            data-filter="completed">Completed</button>
                </div>
            </div>
        `;
    }
    
    function getFilteredTodos() {
        if (this.state.filter === "active") {
            return this.props.todos.filter(function(todo) {
                return !todo.completed;
            });
        } else if (this.state.filter === "completed") {
            return this.props.todos.filter(function(todo) {
                return todo.completed;
            });
        } else {
            return this.props.todos;
        }
    }
    
    function handleSubmit(event) {
        event.preventDefault();
        
        // Add the new todo
        this.addTodo(this.state.newTodo);
        
        // Clear the input
        this.state.newTodo = "";
    }
    
    function handleClick(event) {
        // Check if this is a todo checkbox
        if (event.target.classList.contains("todo-checkbox")) {
            var id = parseInt(event.target.dataset.id);
            this.toggleTodo(id);
        }
        
        // Check if this is a todo delete button
        if (event.target.classList.contains("todo-delete")) {
            var id = parseInt(event.target.dataset.id);
            this.removeTodo(id);
        }
        
        // Check if this is a filter button
        if (event.target.classList.contains("todo-filter")) {
            this.state.filter = event.target.dataset.filter;
        }
    }
    
    function handleChange(event) {
        // Check if this is the todo input
        if (event.target.classList.contains("todo-input")) {
            this.state.newTodo = event.target.value;
        }
    }
}
```

## Step 3: Create the CSS Styles

Edit `static/styles.css` and add the following code:

```css
/* TODO App Styles */

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
    color: #333;
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
}

.todo-app {
    background-color: #fff;
    border-radius: 0.5rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
    padding: 2rem;
}

h1 {
    margin-top: 0;
    text-align: center;
}

.todo-form {
    display: flex;
    margin-bottom: 1.5rem;
}

.todo-input {
    flex: 1;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ddd;
    border-radius: 0.25rem 0 0 0.25rem;
}

.todo-add {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    background-color: #4299e1;
    color: white;
    border: none;
    border-radius: 0 0.25rem 0.25rem 0;
    cursor: pointer;
}

.todo-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem 0;
}

.todo-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid #eee;
}

.todo-item:last-child {
    border-bottom: none;
}

.todo-checkbox {
    margin-right: 0.75rem;
}

.todo-text {
    flex: 1;
}

.todo-item.completed .todo-text {
    text-decoration: line-through;
    color: #999;
}

.todo-delete {
    background-color: transparent;
    border: none;
    color: #e53e3e;
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0 0.5rem;
}

.todo-filters {
    display: flex;
    justify-content: center;
}

.todo-filter {
    background-color: transparent;
    border: 1px solid #ddd;
    border-radius: 0.25rem;
    padding: 0.25rem 0.75rem;
    margin: 0 0.25rem;
    cursor: pointer;
}

.todo-filter.active {
    background-color: #4299e1;
    color: white;
    border-color: #4299e1;
}
```

## Step 4: Create the Client-Side JavaScript

Edit `static/app.js` and add the following code:

```javascript
// TODO App Client-Side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('TODO App initialized');
});
```

## Step 5: Run the Application

Run the application using the `mono-switch` command:

```bash
mono-switch todo-app.mono
```

Open your browser to `http://localhost:8000` to see the application.

## Step 6: Add Server-Side Rendering (Optional)

To add server-side rendering, modify the `Main` component:

```mono
function handleRoot(req, res) {
    print "Handling request to /";
    
    // Create the TodoApp component with SSR
    var todoApp = ssr.createComponent(TodoApp);
    
    // Render the app
    var html = ssr.renderToString(todoApp);
    
    // Send the response
    res.html(html);
}
```

## Conclusion

Congratulations! You've built a simple TODO application using the Switch framework. You've learned how to:

- Create components
- Manage state using the store
- Handle events
- Style your application
- Use server-side rendering

For more advanced features, check out the [API Reference](../api-reference.md) and other tutorials.
