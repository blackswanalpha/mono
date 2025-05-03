# Reactive Mono Language

A simple reactive programming language inspired by React's component model.

## Features

- **Component-based architecture**: Build UIs with reusable components
- **State management**: Components have internal mutable state
- **Reactive updates**: UI automatically updates when state changes
- **Component communication**: Components can pass data to each other

## Usage

```bash
./reactive-mono <script.mono>
```

Example:
```bash
./reactive-mono templates/reactive_app.mono
```

## Language Concepts

### Components

Components are the building blocks of a Mono application. Each component can have:

- **State**: Internal mutable data
- **Methods**: Functions that can update state or render output

```mono
component Counter {
    state {
        count: 0
    }
    
    function increment() {
        this.state.count = this.state.count + 1;
    }
    
    function render() {
        print "Count: " + this.state.count;
    }
}
```

### State

State is internal mutable data that belongs to a component. When state changes, the component can re-render to reflect the changes.

```mono
state {
    count: 0,
    lastUpdated: "Never"
}
```

### Methods

Methods are functions that belong to a component. They can:

- Update the component's state
- Render output
- Accept parameters

```mono
function increment() {
    this.state.count = this.state.count + 1;
}

function update(newValue) {
    this.state.value = newValue;
}
```

### Main Component

Every Mono application must have a `Main` component with a `start` method, which is the entry point of the application.

```mono
component Main {
    function start() {
        var counter = new Counter();
        counter.render();
        counter.increment();
        counter.render();
    }
}
```

## Example: Reactive Counter App

```mono
component Counter {
    state {
        count: 0,
        lastUpdated: "Never"
    }
    
    function increment() {
        this.state.count = this.state.count + 1;
        this.state.lastUpdated = "Now";
    }
    
    function render() {
        print "Count: " + this.state.count;
    }
}

component Display {
    state {
        value: 0,
        name: "Display"
    }
    
    function update(newValue) {
        this.state.value = newValue;
    }
    
    function render() {
        print "Display: " + this.state.value;
    }
}

component Main {
    function start() {
        var counter = new Counter();
        var display = new Display();
        
        print "--- Initial State ---";
        counter.render();
        display.render();
        
        print "--- After First Update ---";
        counter.increment();
        counter.render();
        display.update(counter.state.count);
        display.render();
        
        print "--- After Second Update ---";
        counter.increment();
        counter.render();
        display.update(counter.state.count);
        display.render();
    }
}
```

Output:
```
--- Initial State ---
Count: 0
Display: 0
--- After First Update ---
Count: 1
Display: 1
--- After Second Update ---
Count: 2
Display: 2
```

## Comparison with React

The Reactive Mono language is inspired by React's component model:

- **Components**: Both use a component-based architecture
- **State**: Both use state for internal mutable data
- **Props**: React uses props for immutable input from parent components (not yet implemented in Mono)
- **Reactive Programming**: Both automatically update components when state/props change

## Future Enhancements

- **Props**: Add support for immutable input from parent components
- **JSX-like syntax**: Add support for declarative UI templates
- **Virtual DOM**: Add support for efficient UI updates
- **Hooks**: Add support for stateful logic in functional components
- **Context**: Add support for passing data through the component tree without props
