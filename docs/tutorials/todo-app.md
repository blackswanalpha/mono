# Building a TODO App with Parallel Components

This tutorial will guide you through building a complete TODO application using Mono's component system and concurrency features. You'll learn how to:

1. Create reusable components
2. Manage application state
3. Use parallel components for background tasks
4. Implement a responsive user interface

## Prerequisites

- Basic understanding of Mono syntax
- Mono installed on your system
- Understanding of component-based architecture

## Project Structure

We'll create the following files:

- `todo-app.mono` - The main application file
- `components/todo-item.mono` - The TODO item component
- `components/todo-list.mono` - The TODO list component
- `components/todo-form.mono` - The form for adding new TODOs
- `components/todo-filter.mono` - The filter for filtering TODOs
- `components/todo-stats.mono` - The statistics component (runs in parallel)

## Step 1: Create the TODO Item Component

First, let's create the TODO item component. This component will represent a single TODO item in our list.

Create a file named `components/todo-item.mono`:

```mono
component TodoItem {
    state {
        id: int = 0,
        text: string = "",
        completed: boolean = false,
        createdAt: any = Date.now()
    }
    
    function constructor(id: int, text: string): void {
        this.state.id = id;
        this.state.text = text;
    }
    
    function toggle(): void {
        this.state.completed = !this.state.completed;
    }
    
    function setText(text: string): void {
        this.state.text = text;
    }
    
    function render(): string {
        var completedClass = this.state.completed ? "completed" : "";
        
        return "<li class=\"todo-item " + completedClass + "\">" +
               "  <input type=\"checkbox\" " + (this.state.completed ? "checked" : "") + " onclick=\"this.toggle()\" />" +
               "  <span class=\"todo-text\">" + this.state.text + "</span>" +
               "  <button class=\"delete-btn\" onclick=\"this.delete()\">Delete</button>" +
               "</li>";
    }
    
    function delete(): void {
        // This will be implemented by the parent component
    }
}
```

## Step 2: Create the TODO List Component

Next, let's create the TODO list component. This component will manage a list of TODO items.

Create a file named `components/todo-list.mono`:

```mono
component TodoList {
    state {
        items: any[] = [],
        filter: string = "all" // all, active, completed
    }
    
    function addItem(text: string): void {
        var id = this.state.items.length > 0 ? this.state.items[this.state.items.length - 1].id + 1 : 1;
        var item = new TodoItem(id, text);
        
        // Set up the delete method
        item.delete = function() {
            this.removeItem(id);
        }.bind(this);
        
        this.state.items.push(item);
    }
    
    function removeItem(id: int): void {
        this.state.items = this.state.items.filter(function(item) {
            return item.state.id !== id;
        });
    }
    
    function toggleItem(id: int): void {
        for (var i = 0; i < this.state.items.length; i++) {
            if (this.state.items[i].state.id === id) {
                this.state.items[i].toggle();
                break;
            }
        }
    }
    
    function clearCompleted(): void {
        this.state.items = this.state.items.filter(function(item) {
            return !item.state.completed;
        });
    }
    
    function setFilter(filter: string): void {
        this.state.filter = filter;
    }
    
    function getFilteredItems(): any[] {
        if (this.state.filter === "active") {
            return this.state.items.filter(function(item) {
                return !item.state.completed;
            });
        } else if (this.state.filter === "completed") {
            return this.state.items.filter(function(item) {
                return item.state.completed;
            });
        } else {
            return this.state.items;
        }
    }
    
    function render(): string {
        var items = this.getFilteredItems();
        var itemsHtml = "";
        
        for (var i = 0; i < items.length; i++) {
            itemsHtml += items[i].render();
        }
        
        return "<ul class=\"todo-list\">" + itemsHtml + "</ul>";
    }
}
```

## Step 3: Create the TODO Form Component

Now, let's create the form component for adding new TODOs.

Create a file named `components/todo-form.mono`:

```mono
component TodoForm {
    state {
        text: string = ""
    }
    
    function setText(text: string): void {
        this.state.text = text;
    }
    
    function submit(): void {
        if (this.state.text.trim() === "") {
            return;
        }
        
        // This will be implemented by the parent component
        this.addItem(this.state.text);
        this.state.text = "";
    }
    
    function render(): string {
        return "<form class=\"todo-form\" onsubmit=\"event.preventDefault(); this.submit();\">" +
               "  <input type=\"text\" value=\"" + this.state.text + "\" " +
               "         oninput=\"this.setText(event.target.value)\" " +
               "         placeholder=\"What needs to be done?\" />" +
               "  <button type=\"submit\">Add</button>" +
               "</form>";
    }
    
    function addItem(text: string): void {
        // This will be implemented by the parent component
    }
}
```

## Step 4: Create the TODO Filter Component

Let's create the filter component for filtering TODOs.

Create a file named `components/todo-filter.mono`:

```mono
component TodoFilter {
    state {
        filter: string = "all" // all, active, completed
    }
    
    function setFilter(filter: string): void {
        this.state.filter = filter;
        
        // This will be implemented by the parent component
        this.onFilterChange(filter);
    }
    
    function render(): string {
        return "<div class=\"todo-filter\">" +
               "  <button class=\"" + (this.state.filter === "all" ? "active" : "") + "\" " +
               "          onclick=\"this.setFilter('all')\">All</button>" +
               "  <button class=\"" + (this.state.filter === "active" ? "active" : "") + "\" " +
               "          onclick=\"this.setFilter('active')\">Active</button>" +
               "  <button class=\"" + (this.state.filter === "completed" ? "active" : "") + "\" " +
               "          onclick=\"this.setFilter('completed')\">Completed</button>" +
               "</div>";
    }
    
    function onFilterChange(filter: string): void {
        // This will be implemented by the parent component
    }
}
```

## Step 5: Create the TODO Stats Component (Parallel)

Now, let's create the statistics component that will run in parallel to calculate statistics about our TODOs.

Create a file named `components/todo-stats.mono`:

```mono
component TodoStats {
    state {
        total: int = 0,
        active: int = 0,
        completed: int = 0,
        averageCompletionTime: int = 0,
        isCalculating: boolean = false
    }
    
    function constructor(): void {
        // Create a channel for communication between threads
        this.channel = new Channel();
    }
    
    function updateStats(items: any[]): void {
        // If already calculating, don't start another calculation
        if (this.state.isCalculating) {
            return;
        }
        
        this.state.isCalculating = true;
        
        // Run the calculation in parallel
        parallel {
            this.calculateStats(items);
        }
    }
    
    function calculateStats(items: any[]): void {
        // Simulate a complex calculation
        sleep(100);
        
        var total = items.length;
        var completed = 0;
        var completionTimes = [];
        
        for (var i = 0; i < items.length; i++) {
            if (items[i].state.completed) {
                completed++;
                var completionTime = Date.now() - items[i].state.createdAt;
                completionTimes.push(completionTime);
            }
        }
        
        var active = total - completed;
        var averageCompletionTime = 0;
        
        if (completionTimes.length > 0) {
            var sum = 0;
            for (var i = 0; i < completionTimes.length; i++) {
                sum += completionTimes[i];
            }
            averageCompletionTime = Math.round(sum / completionTimes.length);
        }
        
        // Send the results back to the main thread
        this.channel.send({
            total: total,
            active: active,
            completed: completed,
            averageCompletionTime: averageCompletionTime
        });
        
        // Update the state in the main thread
        this.state.total = total;
        this.state.active = active;
        this.state.completed = completed;
        this.state.averageCompletionTime = averageCompletionTime;
        this.state.isCalculating = false;
    }
    
    function render(): string {
        var avgTimeStr = this.state.averageCompletionTime > 0 
            ? this.formatTime(this.state.averageCompletionTime) 
            : "N/A";
        
        return "<div class=\"todo-stats\">" +
               "  <div class=\"stat\">" +
               "    <span class=\"stat-label\">Total:</span>" +
               "    <span class=\"stat-value\">" + this.state.total + "</span>" +
               "  </div>" +
               "  <div class=\"stat\">" +
               "    <span class=\"stat-label\">Active:</span>" +
               "    <span class=\"stat-value\">" + this.state.active + "</span>" +
               "  </div>" +
               "  <div class=\"stat\">" +
               "    <span class=\"stat-label\">Completed:</span>" +
               "    <span class=\"stat-value\">" + this.state.completed + "</span>" +
               "  </div>" +
               "  <div class=\"stat\">" +
               "    <span class=\"stat-label\">Avg. Completion Time:</span>" +
               "    <span class=\"stat-value\">" + avgTimeStr + "</span>" +
               "  </div>" +
               "  " + (this.state.isCalculating ? "<div class=\"calculating\">Calculating...</div>" : "") +
               "</div>";
    }
    
    function formatTime(ms: int): string {
        if (ms < 1000) {
            return ms + "ms";
        } else if (ms < 60000) {
            return Math.round(ms / 1000) + "s";
        } else if (ms < 3600000) {
            return Math.round(ms / 60000) + "m";
        } else {
            return Math.round(ms / 3600000) + "h";
        }
    }
}
```

## Step 6: Create the Main Application

Finally, let's create the main application that ties everything together.

Create a file named `todo-app.mono`:

```mono
// Import components
// Note: In a real application, you would import these components from files
// component TodoItem from "components/todo-item.mono";
// component TodoList from "components/todo-list.mono";
// component TodoForm from "components/todo-form.mono";
// component TodoFilter from "components/todo-filter.mono";
// component TodoStats from "components/todo-stats.mono";

component TodoApp {
    state {
        list: any = null,
        form: any = null,
        filter: any = null,
        stats: any = null
    }
    
    function constructor(): void {
        // Create components
        this.state.list = new TodoList();
        this.state.form = new TodoForm();
        this.state.filter = new TodoFilter();
        this.state.stats = new TodoStats();
        
        // Set up component relationships
        this.state.form.addItem = function(text) {
            this.state.list.addItem(text);
            this.updateStats();
        }.bind(this);
        
        this.state.filter.onFilterChange = function(filter) {
            this.state.list.setFilter(filter);
        }.bind(this);
    }
    
    function onMount(): void {
        // Add some initial items
        this.state.list.addItem("Learn Mono");
        this.state.list.addItem("Build a TODO app");
        this.state.list.addItem("Master parallel components");
        
        // Update stats
        this.updateStats();
    }
    
    function updateStats(): void {
        this.state.stats.updateStats(this.state.list.state.items);
    }
    
    function clearCompleted(): void {
        this.state.list.clearCompleted();
        this.updateStats();
    }
    
    function render(): string {
        return "<div class=\"todo-app\">" +
               "  <h1>TODO App</h1>" +
               "  " + this.state.form.render() +
               "  " + this.state.filter.render() +
               "  " + this.state.list.render() +
               "  <div class=\"todo-actions\">" +
               "    <button onclick=\"this.clearCompleted()\">Clear Completed</button>" +
               "  </div>" +
               "  " + this.state.stats.render() +
               "</div>";
    }
}

component Main {
    function start(): void {
        var app = new TodoApp();
        
        // Mount the app
        app.onMount();
        
        // Render the app
        print app.render();
    }
}
```

## Step 7: Run the Application

Now, let's run our TODO application:

```bash
./bin/mono todo-app.mono
```

You should see the HTML output of our TODO application. In a real-world scenario, you would integrate this with a web server or a UI framework to render the HTML in a browser.

## Understanding Parallel Components

In our TODO application, we used a parallel component (`TodoStats`) to calculate statistics about our TODOs. Let's understand how this works:

1. The `TodoStats` component uses the `parallel` keyword to run a function in a separate thread.
2. It uses a `Channel` for communication between threads.
3. The main thread can continue executing while the calculation is happening in the background.
4. When the calculation is complete, the results are sent back to the main thread via the channel.

This approach is useful for:

- Expensive calculations that would otherwise block the UI
- Background tasks like data fetching or processing
- Real-time updates that need to happen independently of the UI

## Conclusion

In this tutorial, you've learned how to:

1. Create reusable components for a TODO application
2. Manage application state across components
3. Use parallel components for background tasks
4. Implement a responsive user interface

You can extend this application by adding features like:

- Persistence (saving TODOs to localStorage or a server)
- Drag-and-drop reordering of TODOs
- Due dates and priorities for TODOs
- Categories or tags for TODOs

Happy coding with Mono!
