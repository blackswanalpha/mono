# Component Lifecycle API Reference

This document provides a detailed reference for Mono's component lifecycle hooks. These hooks allow you to run code at specific points in a component's lifecycle, such as when it's created, mounted, updated, or unmounted.

## Overview

Mono components go through several phases during their lifecycle:

1. **Creation**: The component is instantiated
2. **Mounting**: The component is added to the DOM or parent component
3. **Updating**: The component's state or props change
4. **Unmounting**: The component is removed from the DOM or parent component

Each phase has corresponding lifecycle hooks that you can implement in your components.

## Lifecycle Hooks

### constructor()

The `constructor` method is called when a component is created.

**Syntax:**
```mono
function constructor(): void {
    // Initialization code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to initialize the component's state and bind methods.
- This is the first method called in the component lifecycle.
- You can accept parameters in the constructor to initialize the component with specific values.

**Example:**
```mono
component Counter {
    state {
        count: int = 0,
        increment: int = 1
    }
    
    function constructor(initialCount: int = 0, increment: int = 1): void {
        this.state.count = initialCount;
        this.state.increment = increment;
        
        // Bind methods
        this.increment = this.increment.bind(this);
    }
    
    function increment(): void {
        this.state.count += this.state.increment;
    }
}
```

**Best Practices:**
- Keep constructors simple and focused on initialization.
- Don't perform side effects (like API calls) in the constructor.
- Initialize all state variables in the constructor or in the state declaration.

### onMount()

The `onMount` method is called when a component is mounted (added to the DOM or parent component).

**Syntax:**
```mono
function onMount(): void {
    // Mounting code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to perform side effects like fetching data or setting up subscriptions.
- This method is called after the component is mounted and its initial render is complete.
- This is a good place to interact with the DOM or external APIs.

**Example:**
```mono
component DataFetcher {
    state {
        data: any = null,
        isLoading: boolean = true,
        error: string = null
    }
    
    function onMount(): void {
        // Fetch data when the component is mounted
        this.fetchData();
    }
    
    function fetchData(): void {
        // Simulate API call
        setTimeout(function() {
            try {
                // Simulate successful response
                this.state.data = { id: 1, name: "Example" };
                this.state.isLoading = false;
            } catch (error) {
                this.state.error = error.message;
                this.state.isLoading = false;
            }
        }.bind(this), 1000);
    }
    
    function render(): string {
        if (this.state.isLoading) {
            return "<div>Loading...</div>";
        }
        
        if (this.state.error) {
            return "<div>Error: " + this.state.error + "</div>";
        }
        
        return "<div>Data: " + JSON.stringify(this.state.data) + "</div>";
    }
}
```

**Best Practices:**
- Use `onMount` for side effects that should happen once when the component is mounted.
- Clean up any resources created in `onMount` in the `onUnmount` method.
- Don't rely on DOM elements being available before `onMount` is called.

### onUpdate(prevState)

The `onUpdate` method is called when a component's state or props change.

**Syntax:**
```mono
function onUpdate(prevState: any): void {
    // Update code
}
```

**Parameters:**
- `prevState`: An object containing the component's previous state

**Returns:**
- `void`

**Description:**
- Use this hook to respond to state or prop changes.
- This method is called after the component's state or props have changed and the component has re-rendered.
- You can compare the current state with the previous state to perform conditional side effects.

**Example:**
```mono
component SearchBox {
    state {
        query: string = "",
        results: any[] = []
    }
    
    function onUpdate(prevState: any): void {
        // Check if the query has changed
        if (prevState.query !== this.state.query) {
            // Perform search when the query changes
            this.performSearch();
        }
    }
    
    function setQuery(query: string): void {
        this.state.query = query;
    }
    
    function performSearch(): void {
        // Simulate API call
        setTimeout(function() {
            this.state.results = [
                { id: 1, title: "Result 1 for " + this.state.query },
                { id: 2, title: "Result 2 for " + this.state.query }
            ];
        }.bind(this), 500);
    }
    
    function render(): string {
        var resultsHtml = "";
        
        for (var i = 0; i < this.state.results.length; i++) {
            resultsHtml += "<li>" + this.state.results[i].title + "</li>";
        }
        
        return "<div class=\"search-box\">" +
               "  <input type=\"text\" value=\"" + this.state.query + "\" " +
               "         oninput=\"this.setQuery(event.target.value)\" />" +
               "  <ul class=\"results\">" + resultsHtml + "</ul>" +
               "</div>";
    }
}
```

**Best Practices:**
- Compare the current state with the previous state to avoid unnecessary side effects.
- Don't update the state in `onUpdate` without a condition, as it will cause an infinite loop.
- Use `onUpdate` for side effects that should happen when specific state or props change.

### onUnmount()

The `onUnmount` method is called when a component is unmounted (removed from the DOM or parent component).

**Syntax:**
```mono
function onUnmount(): void {
    // Cleanup code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to clean up resources created during the component's lifecycle.
- This method is called before the component is removed from the DOM or parent component.
- This is a good place to cancel network requests, clear timers, or remove event listeners.

**Example:**
```mono
component Timer {
    state {
        count: int = 0,
        intervalId: any = null
    }
    
    function onMount(): void {
        // Start the timer when the component is mounted
        this.state.intervalId = setInterval(function() {
            this.state.count++;
        }.bind(this), 1000);
    }
    
    function onUnmount(): void {
        // Clear the interval when the component is unmounted
        if (this.state.intervalId !== null) {
            clearInterval(this.state.intervalId);
        }
    }
    
    function render(): string {
        return "<div>Count: " + this.state.count + "</div>";
    }
}
```

**Best Practices:**
- Always clean up resources created during the component's lifecycle.
- Cancel any ongoing network requests to prevent memory leaks.
- Clear any timers or intervals to prevent them from running after the component is unmounted.
- Remove any event listeners added during the component's lifecycle.

### onError(error)

The `onError` method is called when an error occurs in the component.

**Syntax:**
```mono
function onError(error: any): void {
    // Error handling code
}
```

**Parameters:**
- `error`: The error that occurred

**Returns:**
- `void`

**Description:**
- Use this hook to handle errors that occur in the component.
- This method is called when an error occurs during rendering, in a lifecycle method, or in an event handler.
- You can use this to log errors, display error messages, or recover from errors.

**Example:**
```mono
component ErrorBoundary {
    state {
        hasError: boolean = false,
        errorMessage: string = null
    }
    
    function onError(error: any): void {
        // Update state to indicate an error occurred
        this.state.hasError = true;
        this.state.errorMessage = error.message;
        
        // Log the error
        console.error("Error in component:", error);
    }
    
    function render(): string {
        if (this.state.hasError) {
            return "<div class=\"error-boundary\">" +
                   "  <h2>Something went wrong</h2>" +
                   "  <p>" + this.state.errorMessage + "</p>" +
                   "</div>";
        }
        
        // Render children normally
        return this.renderChildren();
    }
    
    function renderChildren(): string {
        // In a real implementation, this would render the component's children
        return "<div>Child content</div>";
    }
}
```

**Best Practices:**
- Use error boundaries to catch and handle errors in components.
- Log errors for debugging purposes.
- Provide user-friendly error messages.
- Try to recover from errors when possible.

## Frame Lifecycle Hooks

In addition to the standard component lifecycle hooks, Mono also provides lifecycle hooks for frames. Frames are a higher-level abstraction that can contain multiple components.

### frameWillLoad()

The `frameWillLoad` method is called before a frame is loaded.

**Syntax:**
```mono
function frameWillLoad(): void {
    // Pre-loading code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to prepare for frame loading.
- This method is called before the frame and its components are loaded.
- This is a good place to initialize frame-specific resources.

**Example:**
```mono
component AppFrame {
    function frameWillLoad(): void {
        print "Frame will load";
        
        // Initialize frame-specific resources
        this.initializeFrameResources();
    }
    
    function initializeFrameResources(): void {
        // Initialize resources
    }
}
```

### frameDidLoad()

The `frameDidLoad` method is called after a frame is loaded.

**Syntax:**
```mono
function frameDidLoad(): void {
    // Post-loading code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to perform actions after the frame is loaded.
- This method is called after the frame and its components are loaded.
- This is a good place to start frame-specific operations.

**Example:**
```mono
component AppFrame {
    function frameDidLoad(): void {
        print "Frame did load";
        
        // Start frame-specific operations
        this.startFrameOperations();
    }
    
    function startFrameOperations(): void {
        // Start operations
    }
}
```

### frameWillUnload()

The `frameWillUnload` method is called before a frame is unloaded.

**Syntax:**
```mono
function frameWillUnload(): void {
    // Pre-unloading code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to prepare for frame unloading.
- This method is called before the frame and its components are unloaded.
- This is a good place to save frame state or perform cleanup.

**Example:**
```mono
component AppFrame {
    function frameWillUnload(): void {
        print "Frame will unload";
        
        // Save frame state
        this.saveFrameState();
    }
    
    function saveFrameState(): void {
        // Save state
    }
}
```

### frameDidUnload()

The `frameDidUnload` method is called after a frame is unloaded.

**Syntax:**
```mono
function frameDidUnload(): void {
    // Post-unloading code
}
```

**Parameters:**
- None

**Returns:**
- `void`

**Description:**
- Use this hook to perform actions after the frame is unloaded.
- This method is called after the frame and its components are unloaded.
- This is a good place to clean up frame-specific resources.

**Example:**
```mono
component AppFrame {
    function frameDidUnload(): void {
        print "Frame did unload";
        
        // Clean up frame-specific resources
        this.cleanupFrameResources();
    }
    
    function cleanupFrameResources(): void {
        // Clean up resources
    }
}
```

## Lifecycle Flow

Here's the typical flow of lifecycle hooks for a component:

1. `constructor()` - Component is created
2. `render()` - Initial render
3. `onMount()` - Component is mounted
4. `render()` - Re-render when state or props change
5. `onUpdate(prevState)` - Component is updated
6. `onUnmount()` - Component is unmounted

For frames, the lifecycle flow is:

1. `frameWillLoad()` - Before frame is loaded
2. `constructor()` for each component - Components are created
3. `render()` for each component - Initial render
4. `onMount()` for each component - Components are mounted
5. `frameDidLoad()` - After frame is loaded
6. `frameWillUnload()` - Before frame is unloaded
7. `onUnmount()` for each component - Components are unmounted
8. `frameDidUnload()` - After frame is unloaded

## Best Practices

### Do's

- **Do** use `constructor()` for initialization.
- **Do** use `onMount()` for side effects like data fetching.
- **Do** use `onUpdate()` to respond to state or prop changes.
- **Do** use `onUnmount()` to clean up resources.
- **Do** use `onError()` to handle errors.
- **Do** keep lifecycle methods focused on a single responsibility.
- **Do** clean up resources created in one lifecycle method in the corresponding cleanup method.

### Don'ts

- **Don't** perform side effects in the constructor.
- **Don't** update state in `onUpdate()` without a condition.
- **Don't** forget to clean up resources in `onUnmount()`.
- **Don't** rely on DOM elements being available before `onMount()` is called.
- **Don't** use lifecycle methods for logic that doesn't depend on the component's lifecycle.

## Examples

### Complete Component Lifecycle Example

```mono
component LifecycleDemo {
    state {
        count: int = 0,
        intervalId: any = null,
        data: any = null,
        isLoading: boolean = true,
        error: string = null
    }
    
    function constructor(initialCount: int = 0): void {
        print "Constructor called";
        this.state.count = initialCount;
    }
    
    function onMount(): void {
        print "onMount called";
        
        // Start a timer
        this.state.intervalId = setInterval(function() {
            this.state.count++;
        }.bind(this), 1000);
        
        // Fetch data
        this.fetchData();
    }
    
    function onUpdate(prevState: any): void {
        print "onUpdate called";
        print "Previous count: " + prevState.count;
        print "Current count: " + this.state.count;
        
        // Check if data has changed
        if (prevState.data !== this.state.data) {
            print "Data has changed";
        }
    }
    
    function onUnmount(): void {
        print "onUnmount called";
        
        // Clear the interval
        if (this.state.intervalId !== null) {
            clearInterval(this.state.intervalId);
        }
    }
    
    function onError(error: any): void {
        print "onError called";
        print "Error: " + error.message;
        
        this.state.error = error.message;
    }
    
    function fetchData(): void {
        // Simulate API call
        setTimeout(function() {
            try {
                // Simulate successful response
                this.state.data = { id: 1, name: "Example" };
                this.state.isLoading = false;
            } catch (error) {
                this.onError(error);
                this.state.isLoading = false;
            }
        }.bind(this), 1000);
    }
    
    function render(): string {
        print "Render called";
        
        if (this.state.isLoading) {
            return "<div>Loading...</div>";
        }
        
        if (this.state.error) {
            return "<div>Error: " + this.state.error + "</div>";
        }
        
        return "<div>" +
               "  <p>Count: " + this.state.count + "</p>" +
               "  <p>Data: " + JSON.stringify(this.state.data) + "</p>" +
               "</div>";
    }
}
```

### Frame Lifecycle Example

```mono
component AppFrame {
    state {
        components: any[] = [],
        frameState: any = {}
    }
    
    function frameWillLoad(): void {
        print "frameWillLoad called";
        
        // Initialize frame resources
        this.initializeFrameResources();
    }
    
    function frameDidLoad(): void {
        print "frameDidLoad called";
        
        // Start frame operations
        this.startFrameOperations();
    }
    
    function frameWillUnload(): void {
        print "frameWillUnload called";
        
        // Save frame state
        this.saveFrameState();
    }
    
    function frameDidUnload(): void {
        print "frameDidUnload called";
        
        // Clean up frame resources
        this.cleanupFrameResources();
    }
    
    function initializeFrameResources(): void {
        print "Initializing frame resources";
        
        // Initialize resources
    }
    
    function startFrameOperations(): void {
        print "Starting frame operations";
        
        // Create components
        this.createComponents();
    }
    
    function saveFrameState(): void {
        print "Saving frame state";
        
        // Save state
        this.frameState = {
            componentCount: this.components.length,
            timestamp: Date.now()
        };
    }
    
    function cleanupFrameResources(): void {
        print "Cleaning up frame resources";
        
        // Clean up resources
        this.components = [];
    }
    
    function createComponents(): void {
        print "Creating components";
        
        // Create components
        this.components.push(new LifecycleDemo(0));
        this.components.push(new LifecycleDemo(10));
    }
    
    function render(): string {
        print "Rendering frame";
        
        var componentsHtml = "";
        
        for (var i = 0; i < this.components.length; i++) {
            componentsHtml += this.components[i].render();
        }
        
        return "<div class=\"frame\">" + componentsHtml + "</div>";
    }
}
```

## Conclusion

Mono's component lifecycle hooks provide a powerful way to manage the lifecycle of your components. By understanding and using these hooks effectively, you can build robust and efficient applications.

Remember to follow the best practices outlined in this document, and refer to the examples when implementing lifecycle hooks in your own components.
