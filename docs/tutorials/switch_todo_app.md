# Building a Todo App with the Switch Framework

In this tutorial, we'll build a simple Todo application using the Switch framework for Mono. This will demonstrate the key features of the framework, including components, state management, event handling, and server integration.

## Prerequisites

- Mono language installed
- Basic knowledge of HTML, CSS, and JavaScript
- Familiarity with the Mono language

## Step 1: Create the Project Structure

First, let's create a new file for our Todo application:

```bash
touch examples/switch_todo.mono
```

## Step 2: Define the TodoItem Component

The TodoItem component represents a single item in our todo list. It has a text property and a completed property.

```mono
component TodoItem {
    state {
        id: string = "",
        text: string = "",
        completed: boolean = false
    }
    
    function constructor(id: string, text: string, completed: boolean = false) {
        this.state.id = id;
        this.state.text = text;
        this.state.completed = completed;
    }
    
    function toggle() {
        this.state.completed = !this.state.completed;
    }
    
    function render() {
        // Use the Switch framework to render the component
        switch.clientEvent("click", "handleToggle");
        
        // Create a Switch component
        var todoItem = switch.component("TodoItem", {
            id: this.state.id,
            text: this.state.text,
            completed: this.state.completed
        });
        
        // Return the HTML
        return `
            <li class="switch-list-item" data-id="${this.state.id}">
                <div class="switch-form-check">
                    <input class="switch-form-check-input" type="checkbox" id="todo-${this.state.id}" 
                           ${this.state.completed ? "checked" : ""} data-event="click" data-action="toggle">
                    <label class="switch-form-check-label ${this.state.completed ? "switch-text-muted" : ""}" for="todo-${this.state.id}">
                        ${this.state.text}
                    </label>
                </div>
            </li>
        `;
    }
    
    function handleToggle(event) {
        if (event.target.dataset.action === "toggle") {
            this.toggle();
        }
    }
}
```

## Step 3: Define the TodoList Component

The TodoList component manages a list of TodoItem components and provides methods for adding and removing items.

```mono
component TodoList {
    state {
        items: any[] = []
    }
    
    function constructor() {
        // Initialize with some sample items
        this.state.items = [
            new TodoItem("1", "Learn Mono", true),
            new TodoItem("2", "Build a Switch app", false),
            new TodoItem("3", "Share with the community", false)
        ];
    }
    
    function addItem(text: string) {
        var id = Date.now().toString();
        var item = new TodoItem(id, text);
        this.state.items.push(item);
    }
    
    function removeItem(id: string) {
        this.state.items = this.state.items.filter(function(item) {
            return item.state.id !== id;
        });
    }
    
    function render() {
        // Use the Switch framework to render the component
        switch.clientEvent("submit", "handleAddItem");
        switch.clientEvent("click", "handleRemoveItem");
        
        // Create a Switch component
        var todoList = switch.component("TodoList", {
            items: this.state.items.map(function(item) {
                return {
                    id: item.state.id,
                    text: item.state.text,
                    completed: item.state.completed
                };
            })
        });
        
        // Generate the items HTML
        var itemsHtml = "";
        for (var i = 0; i < this.state.items.length; i++) {
            itemsHtml += this.state.items[i].render();
        }
        
        // Return the HTML
        return `
            <div class="switch-card">
                <div class="switch-card-header">
                    <h2>Todo List</h2>
                </div>
                <div class="switch-card-body">
                    <form class="switch-form switch-mb-3" data-event="submit" data-action="add">
                        <div class="switch-form-group">
                            <input type="text" class="switch-form-control" id="new-todo" placeholder="Add a new todo">
                        </div>
                        <button type="submit" class="switch-button switch-button-primary">Add</button>
                    </form>
                    <ul class="switch-list">
                        ${itemsHtml}
                    </ul>
                </div>
            </div>
        `;
    }
    
    function handleAddItem(event) {
        if (event.target.dataset.action === "add") {
            event.preventDefault();
            var input = document.getElementById("new-todo");
            var text = input.value.trim();
            if (text) {
                this.addItem(text);
                input.value = "";
            }
        }
    }
    
    function handleRemoveItem(event) {
        if (event.target.dataset.action === "remove") {
            var id = event.target.dataset.id;
            this.removeItem(id);
        }
    }
}
```

## Step 4: Define the TodoApp Component

The TodoApp component is the main component that brings everything together.

```mono
component TodoApp {
    state {
        todoList: any = null
    }
    
    function constructor() {
        this.state.todoList = new TodoList();
    }
    
    function render() {
        // Use the Switch framework to render the component
        var app = switch.component("TodoApp", {
            title: "Todo App"
        });
        
        // Return the HTML
        return `
            <div class="switch-container">
                <header class="switch-header switch-mb-4">
                    <h1 class="switch-text-center">Todo App</h1>
                </header>
                <main>
                    ${this.state.todoList.render()}
                </main>
                <footer class="switch-footer switch-mt-4 switch-text-center">
                    <p>Built with the Switch framework for Mono</p>
                </footer>
            </div>
        `;
    }
}
```

## Step 5: Define the Main Component

The Main component is the entry point for our application. It creates the TodoApp component and handles HTTP requests.

```mono
component Main {
    function start() {
        print "=== Todo App ===";
        
        // Create the app
        var app = new TodoApp();
        
        // Render the app
        var html = switch.render("Todo App", ["/todo.js"], ["/todo.css"]);
        
        // Configure routes
        http.get("/", "handleRoot");
        http.get("/todo.js", "handleTodoJs");
        http.get("/todo.css", "handleTodoCss");
        
        // Start the server
        http.start();
    }
    
    function handleRoot(req, res) {
        print "Handling request to /";
        
        // Create the app
        var app = new TodoApp();
        
        // Render the app
        var html = switch.render("Todo App", ["/todo.js"], ["/todo.css"]);
        
        // Send the response
        res.html(html);
    }
    
    function handleTodoJs(req, res) {
        print "Handling request to /todo.js";
        
        // Send the custom JavaScript
        res.header("Content-Type", "application/javascript");
        res.text(`
            // Custom JavaScript for the Todo app
            console.log('Todo app JavaScript loaded');
            
            // Add any custom JavaScript here
        `);
    }
    
    function handleTodoCss(req, res) {
        print "Handling request to /todo.css";
        
        // Send the custom CSS
        res.header("Content-Type", "text/css");
        res.text(`
            /* Custom CSS for the Todo app */
            body {
                background-color: #f8f9fa;
            }
            
            .switch-container {
                max-width: 800px;
                margin: 0 auto;
                padding: 1rem;
            }
            
            .switch-header {
                padding: 2rem 0;
            }
            
            .switch-footer {
                padding: 2rem 0;
                color: #6c757d;
            }
            
            .switch-text-muted {
                color: #6c757d;
                text-decoration: line-through;
            }
            
            /* Add any custom CSS here */
        `);
    }
}
```

## Step 6: Put It All Together

Now, let's put everything together in the `examples/switch_todo.mono` file:

```mono
//  __  __                   
// |  \/  | ___  _ __   ___  
// | |\/| |/ _ \| '_ \ / _ \ 
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/ 
//                           
// Switch Todo App - A simple todo application using the Switch framework

// TodoItem component
component TodoItem {
    // ... (copy from Step 2)
}

// TodoList component
component TodoList {
    // ... (copy from Step 3)
}

// TodoApp component
component TodoApp {
    // ... (copy from Step 4)
}

// Main component
component Main {
    // ... (copy from Step 5)
}
```

## Step 7: Run the Application

Now, let's run our Todo application:

```bash
./bin/mono-switch examples/switch_todo.mono
```

Open your browser and navigate to `http://localhost:8000` to see the Todo application in action.

## Conclusion

Congratulations! You've built a simple Todo application using the Switch framework for Mono. This demonstrates the key features of the framework, including:

- Component-based architecture
- State management
- Event handling
- Server integration

You can extend this application by adding features like:

- Saving todos to a database
- Adding categories or tags to todos
- Adding due dates to todos
- Adding user authentication

The Switch framework provides a solid foundation for building modern web applications with Mono.
