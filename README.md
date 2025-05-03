# Mono Language Interpreter

<p align="center">
  <img src="assets/mono_logo.png" alt="Mono Logo" width="200" height="200">
</p>

A simple interpreter for the Mono programming language with support for reactive programming, static typing, and generics.

## Features

### Basic Mono
- Component-based programming model
- Support for variables and methods
- Basic control structures (for loops)
- Method calls with parameters
- Print statements

### Reactive Mono
- Component-based architecture
- State management
- Reactive updates
- Component communication

### Type System
- Static typing with type inference
- Support for primitive types (int, float, string, bool)
- Type annotations for variables, parameters, and return types
- Support for generics to create reusable component logic

### Component Lifecycle
- Explicit lifecycle hooks for component management
- Constructor for initialization
- Mount/unmount hooks for setup and cleanup
- Update hooks for handling state changes
- Error handling hooks for recovery

### Arithmetic Operations
- Support for complex arithmetic operations
- Multiplication, division, modulo, and power operations
- Method return values for calculations
- Chained operations and expressions

### Collections and Boolean Operations
- Arrays with indexing and iteration
- Dictionaries with key-value pairs
- Boolean operations (==, !=, >, <, >=, <=, &&, ||)
- Control structures (if/else, for loops, while loops)
- Line comments using //

### Component Elements
- Primitive Elements: Built-in elements like div, span, button, etc.
- Composite Elements: Custom elements composed of other components
- Element Hierarchy: Parent-child relationships with event bubbling/capturing
- Slots: Placeholders for dynamic content injection

### Inter-Component Communication
- Events: Custom events with pub/sub mechanisms (e.g., component.emit("click", data))
- Services: Global state management (e.g., Redux-like stores)
- Context API: Pass data through the component tree without explicit props

### Frames (Hierarchical Component Containers)
- Frame Lifecycle: Inherits component lifecycle hooks but adds frameWillLoad and frameDidUnload
- Frame-Scoped State: Shared state accessible only to components within the frame
- Isolation: Frames run in isolated memory/thread pools to prevent interference

### Kits (Pre-Baked Component Suites)
- Kit Definition: Define collections of components, tools, and utilities
- Kit Versioning: Semantic versioning for backward compatibility
- Kit Registry: Central repository for discovering kits
- Kit Tools: CLI generators, linters, or debuggers bundled with kits

### Package Manager
- Scoped Packages: Public/private registries with namespace support
- Dependency Graph Analysis: Audit package relationships and flag conflicts
- Security Scanning: Automatically detect vulnerabilities in dependencies
- License Compliance: Enforce licensing rules (e.g., block GPL dependencies)

### Layout System
- Declarative Layouts: Define component arrangements using JSON/DSL or code
- Responsive Design: Adapt components to screen sizes or environments
- Constraint-Based Layouts: Use rules like "center vertically" or "fill 80% width"
- Z-Ordering: Manage overlapping components (e.g., modals, popovers)

### Runtime Environment
- Scheduler: Manage component threads and prioritize tasks
- Garbage Collection: Automatically clean up unmounted components
- Hot Reloading: Update components at runtime without restarting
- Resource Management: Monitor and control memory and CPU usage

## Supported Components

- **Counter**: A simple counter with increment and decrement methods
- **Calculator**: A calculator with add, subtract, multiply, and divide methods

## Usage

### Basic Mono

```bash
./mono <script.mono>
```

Example:
```bash
./mono templates/start.mono
```

### Reactive Mono

```bash
./mono <script.mono>
```

The interpreter automatically detects reactive features. You can also use the -r flag:

```bash
./mono -r templates/reactive_app.mono
```

### Type Checking

```bash
./mono -t <script.mono>
```

Example:
```bash
./mono -t templates/typed_counter.mono
```

You can also use the --verbose flag to see detailed type information:
```bash
./mono -t --verbose templates/typed_counter.mono
```

### Component Lifecycle

```bash
./mono -l <script.mono>
```

Example:
```bash
./mono -l templates/lifecycle_demo.mono
```

This enables support for component lifecycle hooks:
- `constructor()`: Initialization when component is created
- `onMount()`: Called when component is added to the layout
- `onUpdate(prevState, prevProps)`: Called after state or props change
- `onUnmount()`: Called when component is removed
- `onError()`: Called when an error occurs in the component

### Arithmetic Operations

```bash
./mono -a <script.mono>
```

Example:
```bash
./mono -a templates/arithmetic_demo.mono
```

This enables support for complex arithmetic operations:
- Multiplication: `a * b`
- Division: `a / b`
- Modulo: `a % b`
- Power: `a ** b`
- Method return values: `return a + b;`
- Chained operations: `calc.add(calc.multiply(3, 4), calc.divide(10, 2))`

### Collections and Boolean Operations

```bash
./mono -c <script.mono>
```

Example:
```bash
./mono -c templates/collections_demo.mono
```

This enables support for arrays, dictionaries, and boolean operations:
- Arrays: `var numbers = [1, 2, 3, 4, 5];`
- Array access: `numbers[0] = 10;`
- Dictionaries: `var person = {"name": "John", "age": 30};`
- Dictionary access: `person["name"] = "Jane";`
- Boolean operations: `if (a > b && c < d) { ... }`
- Control structures: `for (var i = 0; i < 10; i++) { ... }`
- Line comments: `// This is a comment`

### Component Elements

```bash
./bin/element-mono <script.mono>
```

Example:
```bash
./bin/element-mono templates/element_demo.mono
```

This enables support for component elements:
- Primitive Elements: `<div class="container">Content</div>`
- Composite Elements: `<Card title="My Card">Content</Card>`
- Element Hierarchy: `<div><span>Nested content</span></div>`
- Slots: `<Card><div slot="header">Header</div><div slot="content">Content</div></Card>`
- Event Handling: `<button onclick="this.handleClick()">Click me</button>`

### Inter-Component Communication

```bash
./bin/frame-mono <script.mono>
```

Example:
```bash
./bin/frame-mono templates/communication_demo.mono
```

This enables support for inter-component communication:
- Events: `this.emit("click", data)` and `this.on("click", callback)`
- Services: `this.registerService("name", initialState)` and `this.getService("name")`
- Context API: `this.provideContext("theme", value)` and `this.consumeContext("theme", callback)`

### Frames

```bash
./bin/frame-mono <script.mono>
```

Example:
```bash
./bin/frame-mono templates/frames_demo.mono
```

This enables support for frames:
- Creating Frames: `this.createFrame("frameName", "parentFrameName")`
- Frame Lifecycle: `frameWillLoad()`, `frameDidLoad()`, `frameWillUnload()`, `frameDidUnload()`
- Frame-Scoped State: `this.getFrameState("key")` and `this.setFrameState("key", value)`
- Frame Isolation: `this.runInFrame(function() { /* code */ })`

### Kits

```bash
./bin/mono-kit <command>
```

Commands:
- `create`: Create a new kit
- `list`: List all kits in the registry
- `search`: Search for kits by name or description
- `show`: Show details of a kit
- `import`: Import a kit from a definition file
- `demo`: Run the kits demo

Example:
```bash
./bin/mono-kit import templates/ui_kit.mono
./bin/mono-kit list
./bin/mono-kit demo
```

Kit definition syntax:
```mono
kit UIKit version 1.0.0 {
    description "A collection of UI components for Mono"

    collect {
        Button from "components/button.mono" as "A customizable button component"
        Card from "components/card.mono" as "A card component with header, body, and footer"
    }

    tools {
        generate "mono-tools generate-component $1 --template=ui" as "Generate a new UI component"
        lint "mono-tools lint $1 --config=ui" as "Lint a UI component"
    }

    depends {
        BaseKit version ^1.0.0
    }
}
```

### Layouts

```bash
./bin/mono-layout <command>
```

Commands:
- `parse`: Parse a layout definition file
- `render`: Render a layout to HTML or CSS
- `demo`: Run the layouts demo

Example:
```bash
./bin/mono-layout parse templates/app_layout.layout
./bin/mono-layout render templates/app_layout.layout -f css -o app_layout.css
./bin/mono-layout demo
```

Layout definition syntax:
```mono
layout AppLayout {
    // Define variables
    variables {
        headerHeight: 60px;
        sidebarWidth: 250px;
    }

    // Define the root element
    root {
        width: 100%;
        height: 100vh;

        // Header
        element header {
            width: 100%;
            height: 60px;
            z-index: 10;
            constraint top: 0;
            constraint left: 0;
        }

        // Content
        element content {
            width: calc(100% - 250px);
            height: calc(100vh - 60px - 40px);
            constraint top: 60px;
            constraint left: 250px;
        }
    }

    // Define responsive layouts
    media mobile (max-width: 480px) {
        root {
            element content {
                width: 100%;
                constraint left: 0;
            }
        }
    }
}
```

### Runtime Environment

```bash
./bin/mono-runtime <command>
```

Commands:
- `start`: Start the runtime environment
- `stop`: Stop the runtime environment
- `run`: Run a Mono script in the runtime environment
- `watch`: Watch a directory for changes
- `status`: Show the status of the runtime environment
- `demo`: Run the runtime environment demo

Example:
```bash
./bin/mono-runtime start -w 10 -g 60 -d templates/
./bin/mono-runtime run templates/counter_app.mono --watch
./bin/mono-runtime status
./bin/mono-runtime demo
```

Component lifecycle hooks:
```mono
component Counter {
    state {
        count: int = 0
    }

    // Lifecycle hooks
    function onMount(): void {
        print "Counter mounted";
    }

    function onUpdate(prevState: any): void {
        print "Counter updated from " + prevState.count + " to " + this.state.count;
    }

    function onUnmount(): void {
        print "Counter unmounted";
    }

    function increment(): void {
        this.state.count++;
    }
}
```

### Documentation

```bash
./bin/mono-docs <command>
```

Commands:
- `serve`: Start the documentation server
- `generate`: Generate documentation from source code

Example:
```bash
./bin/mono-docs serve
./bin/mono-docs generate
```

The documentation server provides:
- Tutorials for learning Mono
- Case studies for best practices
- API reference for Mono features
- Examples of Mono applications

### Data Structures

```bash
./mono data <command>
```

Commands:
- `create`: Create a new data structure
- `list`: List all data structures
- `save`: Save a data structure to a file
- `load`: Load a data structure from a file
- `render`: Render a data structure to HTML or JSON
- `demo`: Run the data structures demo

Example:
```bash
./mono data create table MyTable --description "My sample table"
./mono data list
./mono data demo
```

Data structure types:
- `table`: For tabular data with sorting, pagination, and filtering
- `tree`: For hierarchical data with expand/collapse functionality
- `graph`: For network data with nodes and edges
- `list`: For linear data with selection and sorting
- `grid`: For matrix data with cell selection and editing

### Package Manager

```bash
./mono pkg <command>
```

or

```bash
./bin/mono-pkg <command>
```

Commands:
- `create`: Create a new package
- `list`: List all packages in the registry
- `search`: Search for packages by name or description
- `show`: Show details of a package
- `import`: Import a package from a definition file
- `install`: Install a package
- `audit`: Audit a package for security vulnerabilities
- `license`: Check license compliance for a package
- `demo`: Run the package manager demo

Example:
```bash
./mono pkg create MyPackage --version 1.0.0 --description "My awesome package"
./mono pkg import templates/ui_components.pkg
./mono pkg install UIComponents --dev
./mono pkg audit AuthModule --level critical
./mono pkg license DataStorage
./mono pkg deps --graph
./mono pkg demo
```

Package definition syntax:
```mono
package UIComponents version 1.0.0 {
    description "A collection of UI components for Mono applications"
    author "Mono Team"
    license "MIT"
    homepage "https://mono-lang.org/packages/ui-components"
    repository "https://github.com/mono-lang/ui-components"

    components {
        Button from "components/button.mono" as "A customizable button component"
        Card from "components/card.mono" as "A card component with header, body, and footer"
        Modal from "components/modal.mono" as "A modal dialog component"
    }

    dependencies {
        CoreUtils version ^1.0.0
        EventSystem version ~2.3.0
    }

    dev_dependencies {
        TestFramework version ^2.0.0
        DocGenerator version ^1.5.0
    }
}

## Basic Mono Examples

### Counter (start.mono)

```
component Counter {
    var count = 0;

    function increment() {
        this.count = this.count + 1;
    }
}

component Main {
    function start() {
        var counter = new Counter();
        for var i = 0; i < 5; i++ {
            counter.increment();
        }
        print counter.count;
    }
}
```

### Counter with Decrement (counter_test.mono)

```
component Counter {
    var count = 10;

    function increment() {
        this.count = this.count + 1;
    }

    function decrement() {
        this.count = this.count - 1;
    }
}

component Main {
    function start() {
        var counter = new Counter();
        counter.increment();
        counter.increment();
        counter.decrement();
        print counter.count;
    }
}
```

### Calculator (calculator.mono)

```
component Calculator {
    var result = 0;

    function add(value) {
        this.result = this.result + value;
    }

    function subtract(value) {
        this.result = this.result - value;
    }

    function multiply(value) {
        this.result = this.result * value;
    }

    function divide(value) {
        this.result = this.result / value;
    }
}

component Main {
    function start() {
        var calc = new Calculator();
        calc.add(10);
        calc.multiply(2);
        calc.subtract(5);
        calc.divide(3);
        print calc.result;
    }
}
```

## Typed Mono Examples

### Typed Counter

```mono
component Counter {
    state {
        count: int = 0,
        name: string = "Counter"
    }

    function increment(): void {
        this.state.count = this.state.count + 1;
    }

    function decrement(): void {
        this.state.count = this.state.count - 1;
    }

    function getValue(): int {
        return this.state.count;
    }

    function getName(): string {
        return this.state.name;
    }

    function render(): void {
        print this.state.name + ": " + this.state.count;
    }
}

component Main {
    function start(): void {
        var counter: Counter = new Counter();

        print "Initial state:";
        counter.render();

        counter.increment();
        counter.increment();
        print "After incrementing twice:";
        counter.render();

        counter.decrement();
        print "After decrementing once:";
        counter.render();

        var value: int = counter.getValue();
        var name: string = counter.getName();
        print "Counter " + name + " has value " + value;
    }
}
```

### Generic List

```mono
component List<T> {
    state {
        items: any[] = [],
        size: int = 0
    }

    function add(item: T): void {
        this.state.items[this.state.size] = item;
        this.state.size = this.state.size + 1;
    }

    function get(index: int): T {
        return this.state.items[index];
    }

    function getSize(): int {
        return this.state.size;
    }
}

component Main {
    function start(): void {
        // Create a list of strings
        var stringList: List<string> = new List<string>();
        stringList.add("Hello");
        stringList.add("World");

        // Create a list of numbers
        var numberList: List<int> = new List<int>();
        numberList.add(1);
        numberList.add(2);
        numberList.add(3);

        print "String list size: " + stringList.getSize();
        print "Number list size: " + numberList.getSize();
    }
}
```

## Component Lifecycle Examples

### Lifecycle Component

```mono
component Timer {
    state {
        count: 0,
        isRunning: false
    }

    // Lifecycle hooks
    constructor() {
        print "Timer: constructor called";
        this.state.count = 0;
        this.state.isRunning = false;
    }

    onMount() {
        print "Timer: onMount called";
        print "Timer: Starting timer...";
        this.start();
    }

    onUpdate(prevState, prevProps) {
        print "Timer: onUpdate called";
        print "Timer: Previous count: " + prevState.count;
        print "Timer: Current count: " + this.state.count;

        if (prevState.isRunning != this.state.isRunning) {
            if (this.state.isRunning) {
                print "Timer: Timer started";
            } else {
                print "Timer: Timer stopped";
            }
        }
    }

    onUnmount() {
        print "Timer: onUnmount called";
        print "Timer: Cleaning up resources...";
        this.stop();
    }

    onError() {
        print "Timer: onError called";
        print "Timer: Recovering from error...";
        this.state.count = 0;
        this.state.isRunning = false;
    }

    // Regular methods
    function start() {
        this.state.isRunning = true;
    }

    function stop() {
        this.state.isRunning = false;
    }

    function increment() {
        this.state.count = this.state.count + 1;
    }
}
```

## Reactive Mono Examples

### Basic Counter

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

component Main {
    function start() {
        var counter = new Counter();

        counter.render();
        counter.increment();
        counter.render();
        counter.increment();
        counter.render();
    }
}
```

## Component Elements Examples

### Todo List with Elements

```mono
// Component with Element Hierarchy
component TodoItem {
    state {
        text: string = "",
        completed: boolean = false
    }

    function setText(newText: string): void {
        this.state.text = newText;
    }

    function toggleCompleted(): void {
        this.state.completed = !this.state.completed;
    }

    function render(): string {
        var checkboxState = this.state.completed ? "checked" : "";
        return "<div class=\"todo-item\">" +
               "  <input type=\"checkbox\" " + checkboxState + " onclick=\"this.toggleCompleted()\" />" +
               "  <span class=\"" + (this.state.completed ? "completed" : "") + "\">" + this.state.text + "</span>" +
               "</div>";
    }
}

// Component with Slots
component TodoList {
    state {
        title: string = "Todo List"
    }

    function setTitle(newTitle: string): void {
        this.state.title = newTitle;
    }

    function render(): string {
        return "<div class=\"todo-list\">" +
               "  <h2>" + this.state.title + "</h2>" +
               "  <div class=\"todo-items\">" +
               "    <slot name=\"items\"></slot>" +
               "  </div>" +
               "  <div class=\"todo-actions\">" +
               "    <slot name=\"actions\"></slot>" +
               "  </div>" +
               "</div>";
    }
}

component Main {
    function start(): void {
        var todoList = new TodoList();
        todoList.setTitle("My Tasks");

        var item1 = new TodoItem();
        item1.setText("Learn Mono Elements");

        var item2 = new TodoItem();
        item2.setText("Build a Mono app");

        print "=== Todo List Demo ===\n";
        print todoList.render();
        print "\n";
        print item1.render();
        print item2.render();

        // Toggle completion
        item1.toggleCompleted();
        print "\n=== After completing a task ===\n";
        print item1.render();
    }
}
```

### Todo App

```mono
component TodoItem {
    state {
        text: "",
        completed: 0
    }

    function setText(newText) {
        this.state.text = newText;
    }

    function toggleCompleted() {
        this.state.completed = this.state.completed + 1;
    }

    function render() {
        print "Todo: " + this.state.text;
    }
}

component TodoList {
    state {
        itemCount: 0
    }

    function addItem() {
        this.state.itemCount = this.state.itemCount + 1;
    }

    function render() {
        print "Items: " + this.state.itemCount;
    }
}

component Main {
    function start() {
        var todoList = new TodoList();
        var item1 = new TodoItem();
        var item2 = new TodoItem();

        print "--- Todo App ---";

        print "--- Initial Todo List ---";
        todoList.render();

        print "--- Adding Items ---";
        item1.setText("Buy groceries");
        todoList.addItem();
        item1.render();
        todoList.render();

        item2.setText("Clean house");
        todoList.addItem();
        item2.render();
        todoList.render();

        print "--- Completing an Item ---";
        item1.toggleCompleted();
        item1.render();
    }
}
```

## Inter-Component Communication Examples

### Event-based Communication

```mono
// Button component that emits events
component Button {
    state {
        text: string = "Click me",
        disabled: boolean = false
    }

    function setText(newText: string): void {
        this.state.text = newText;
    }

    function click(): void {
        // Emit a click event
        this.emit("click", this.state.text);
    }

    function render(): string {
        return "<button onclick=\"this.click()\">" + this.state.text + "</button>";
    }
}

// Counter component that listens for events
component Counter {
    state {
        count: int = 0,
        lastButtonClicked: string = "None"
    }

    function onMount(): void {
        // Listen for click events from any Button component
        this.on("click", function(data) {
            this.state.count = this.state.count + 1;
            this.state.lastButtonClicked = data;
        });
    }

    function onUnmount(): void {
        // Stop listening for click events
        this.off("click");
    }

    function render(): string {
        return "<div class=\"counter\">" +
               "  <h3>Button Click Counter</h3>" +
               "  <p>Count: " + this.state.count + "</p>" +
               "  <p>Last Button: " + this.state.lastButtonClicked + "</p>" +
               "</div>";
    }
}

component Main {
    function start(): void {
        var button1 = new Button();
        var button2 = new Button();
        var counter = new Counter();

        button1.setText("Increment");
        button2.setText("Add 5");

        print "=== Event-based Communication Demo ===\n";
        print button1.render();
        print button2.render();
        print counter.render();

        // Simulate button clicks
        button1.click();
        print "\nAfter button1 click:\n";
        print counter.render();

        button2.click();
        print "\nAfter button2 click:\n";
        print counter.render();
    }
}
```

## Frame Examples

### Frame-Scoped State

```mono
// Frame-aware component
component FrameComponent {
    state {
        name: string = "Default Component"
    }

    function frameWillLoad(): void {
        print this.state.name + ": frameWillLoad called";
    }

    function frameDidLoad(): void {
        print this.state.name + ": frameDidLoad called";
    }

    function setName(name: string): void {
        this.state.name = name;
    }

    function incrementFrameState(): void {
        // Update frame-scoped state
        var currentValue = this.getFrameState("counter", 0);
        this.setFrameState("counter", currentValue + 1);
        print this.state.name + ": Incremented frame counter to " + (currentValue + 1);
    }

    function render(): string {
        var counter = this.getFrameState("counter", 0);
        return "<div>" +
               "  <h3>" + this.state.name + "</h3>" +
               "  <p>Frame Counter: " + counter + "</p>" +
               "  <button onclick=\"this.incrementFrameState()\">Increment</button>" +
               "</div>";
    }
}

component Main {
    function start(): void {
        // Create frames
        this.createFrame("mainFrame");
        this.createFrame("childFrame", "mainFrame");

        // Create components in frames
        var component1 = new FrameComponent();
        component1.setName("Main Frame Component");
        this.addComponentToFrame("mainFrame", "component1", component1);

        var component2 = new FrameComponent();
        component2.setName("Child Frame Component");
        this.addComponentToFrame("childFrame", "component2", component2);

        // Load the frames
        this.loadFrame("mainFrame");

        // Demonstrate frame-scoped state
        print "\n=== Frame-Scoped State Demo ===\n";
        print component1.render();
        print component2.render();

        component1.incrementFrameState();
        print "\nAfter incrementing in main frame:\n";
        print component1.render();
        print component2.render();

        component2.incrementFrameState();
        print "\nAfter incrementing in child frame:\n";
        print component1.render();
        print component2.render();
    }
}
```

## Kit Examples

### Kit Definition

```mono
// Define a UI Kit
kit UIKit version 1.0.0 {
    description "A collection of UI components for Mono"

    collect {
        Button from "components/button.mono" as "A customizable button component"
        Card from "components/card.mono" as "A card component with header, body, and footer"
        Modal from "components/modal.mono" as "A modal dialog component"
    }

    tools {
        generate "mono-tools generate-component $1 --template=ui" as "Generate a new UI component"
        lint "mono-tools lint $1 --config=ui" as "Lint a UI component"
    }
}

// Define a Data Visualization Kit that depends on UIKit
kit DataVizKit version 0.2.0 {
    description "Data visualization components for Mono"

    collect {
        BarChart from "components/bar_chart.mono" as "A bar chart component"
        LineChart from "components/line_chart.mono" as "A line chart component"
        PieChart from "components/pie_chart.mono" as "A pie chart component"
    }

    tools {
        generate "mono-tools generate-chart $1" as "Generate a new chart component"
        convert "mono-tools convert-data $1 $2" as "Convert data to a format usable by charts"
    }

    depends {
        UIKit version ^1.0.0
    }
}
```

### Using Components from Kits

```mono
component Main {
    function start(): void {
        // Create components from UIKit
        var button = new Button();
        button.setText("Click Me");
        button.setType("primary");
        print "Button: " + button.render();

        // Create components from DataVizKit
        var barChart = new BarChart();
        barChart.setTitle("Monthly Sales");
        barChart.setData([
            { label: "Jan", value: 120 },
            { label: "Feb", value: 150 },
            { label: "Mar", value: 180 }
        ]);
        print "Bar Chart: " + barChart.render();
    }
}
```

## Layout Examples

### Declarative Layout Definition

```mono
// Define a layout using the layout DSL
layout AppLayout {
    // Define variables
    variables {
        headerHeight: 60px;
        sidebarWidth: 250px;
        footerHeight: 40px;
    }

    // Define the root element
    root {
        width: 100%;
        height: 100vh;

        // Header
        element header {
            width: 100%;
            height: 60px;
            z-index: 10;
            constraint top: 0;
            constraint left: 0;
        }

        // Sidebar
        element sidebar {
            width: 250px;
            height: calc(100vh - 60px - 40px);
            z-index: 5;
            constraint top: 60px;
            constraint left: 0;
        }

        // Content
        element content {
            width: calc(100% - 250px);
            height: calc(100vh - 60px - 40px);
            constraint top: 60px;
            constraint left: 250px;
        }

        // Footer
        element footer {
            width: 100%;
            height: 40px;
            z-index: 10;
            constraint bottom: 0;
            constraint left: 0;
        }
    }

    // Define responsive layouts
    media tablet (max-width: 768px) {
        root {
            // Sidebar becomes hidden
            element sidebar {
                width: 0;
            }

            // Content takes full width
            element content {
                width: 100%;
                constraint left: 0;
            }
        }
    }

    media mobile (max-width: 480px) {
        root {
            // Header adjustments
            element header {
                height: 50px;
            }

            // Content adjustments
            element content {
                height: calc(100vh - 50px - 40px);
                constraint top: 50px;
            }
        }
    }
}
```

### Using Layouts in Components

```mono
component App {
    state {
        layout: any = null,
        viewportWidth: int = 800,
        viewportHeight: int = 600
    }

    function constructor(): void {
        // Load the layout
        this.state.layout = this.loadLayout("AppLayout");
    }

    function loadLayout(name: string): any {
        // Load the layout from a file
        return parseLayout(name + ".layout");
    }

    function setViewport(width: int, height: int): void {
        this.state.viewportWidth = width;
        this.state.viewportHeight = height;

        // Recalculate layout
        this.calculateLayout();
    }

    function calculateLayout(): void {
        // Calculate layout for current viewport
        calculateLayout(this.state.layout, this.state.viewportWidth, this.state.viewportHeight);
    }

    function render(): string {
        // Render components according to layout
        return "<div class=\"app\">" +
               "  <header id=\"header\"></header>" +
               "  <aside id=\"sidebar\"></aside>" +
               "  <main id=\"content\"></main>" +
               "  <footer id=\"footer\"></footer>" +
               "</div>";
    }
}
```

## Runtime Environment Examples

### Task Scheduling

```mono
component TaskDemo {
    state {
        tasks: any[] = []
    }

    function addTask(priority: string): void {
        var task = {
            id: this.state.tasks.length + 1,
            priority: priority,
            status: "pending"
        };

        this.state.tasks.push(task);

        // Schedule the task with the runtime
        scheduleTask(
            function() { this.executeTask(task.id); },
            priority,
            this,
            "Execute-Task-" + task.id
        );
    }

    function executeTask(taskId: int): void {
        // Find and update the task
        for (var i = 0; i < this.state.tasks.length; i++) {
            if (this.state.tasks[i].id == taskId) {
                this.state.tasks[i].status = "completed";
                break;
            }
        }
    }
}
```

### Component Lifecycle and Garbage Collection

```mono
component GCDemo {
    state {
        components: any[] = []
    }

    function onMount(): void {
        // Register with the runtime environment
        registerComponent(this);
    }

    function createComponent(): void {
        var component = new DynamicComponent();
        this.state.components.push(component);

        // Mount the component
        mountComponent(component);
    }

    function unmountComponent(index: int): void {
        if (index >= 0 && index < this.state.components.length) {
            // Unmount the component
            unmountComponent(this.state.components[index]);

            // The garbage collector will clean it up
            this.state.components.splice(index, 1);
        }
    }
}

component DynamicComponent {
    function onMount(): void {
        print "DynamicComponent mounted";
    }

    function onUnmount(): void {
        print "DynamicComponent unmounted";
    }
}
```

### Hot Reloading

```mono
component HotReloadDemo {
    state {
        message: string = "Edit this file to see hot reloading in action!",
        reloadCount: int = 0
    }

    function onMount(): void {
        // Watch the current file for changes
        watchFile("templates/hot_reload_demo.mono");
    }

    function onUpdate(prevState: any): void {
        // This will be called when the component is hot reloaded
        this.state.reloadCount++;
        print "Component was hot reloaded!";
        print "Previous message: " + prevState.message;
        print "Current message: " + this.state.message;
    }

    function render(): string {
        return "<div>" +
               "  <h2>Hot Reload Demo</h2>" +
               "  <p>" + this.state.message + "</p>" +
               "  <p>Reload count: " + this.state.reloadCount + "</p>" +
               "</div>";
    }
}
```

## Data Structure Examples

### Table Component

```mono
component Table {
    state {
        data: any[] = [],
        columns: any[] = [],
        sortColumn: string = "",
        sortDirection: string = "asc",
        pageSize: int = 10,
        currentPage: int = 1
    }

    function setData(data: any[]): void {
        this.state.data = data;
    }

    function setColumns(columns: any[]): void {
        this.state.columns = columns;
    }

    function sort(column: string): void {
        if (this.state.sortColumn == column) {
            // Toggle sort direction
            this.state.sortDirection = this.state.sortDirection == "asc" ? "desc" : "asc";
        } else {
            // Set new sort column
            this.state.sortColumn = column;
            this.state.sortDirection = "asc";
        }

        // Sort the data
        this.sortData();
    }

    function sortData(): void {
        if (!this.state.sortColumn) {
            return;
        }

        this.state.data.sort((a, b) => {
            var aValue = a[this.state.sortColumn];
            var bValue = b[this.state.sortColumn];

            if (aValue < bValue) {
                return this.state.sortDirection == "asc" ? -1 : 1;
            } else if (aValue > bValue) {
                return this.state.sortDirection == "asc" ? 1 : -1;
            } else {
                return 0;
            }
        });
    }

    function setPage(page: int): void {
        this.state.currentPage = page;
    }

    function getPageCount(): int {
        return Math.ceil(this.state.data.length / this.state.pageSize);
    }

    function getCurrentPageData(): any[] {
        var startIndex = (this.state.currentPage - 1) * this.state.pageSize;
        var endIndex = startIndex + this.state.pageSize;
        return this.state.data.slice(startIndex, endIndex);
    }

    function render(): string {
        var headerHtml = "";
        var bodyHtml = "";
        var paginationHtml = "";

        // Generate header
        for (var i = 0; i < this.state.columns.length; i++) {
            var column = this.state.columns[i];
            var sortIndicator = "";

            if (this.state.sortColumn == column.key) {
                sortIndicator = this.state.sortDirection == "asc" ? " ▲" : " ▼";
            }

            headerHtml += "<th onclick=\"this.sort('" + column.key + "')\">" + column.label + sortIndicator + "</th>";
        }

        // Generate body
        var pageData = this.getCurrentPageData();
        for (var i = 0; i < pageData.length; i++) {
            var row = pageData[i];
            var rowHtml = "";

            for (var j = 0; j < this.state.columns.length; j++) {
                var column = this.state.columns[j];
                rowHtml += "<td>" + row[column.key] + "</td>";
            }

            bodyHtml += "<tr>" + rowHtml + "</tr>";
        }

        // Generate pagination
        var pageCount = this.getPageCount();
        for (var i = 1; i <= pageCount; i++) {
            var activeClass = i == this.state.currentPage ? "active" : "";
            paginationHtml += "<button class=\"page-button " + activeClass + "\" onclick=\"this.setPage(" + i + ")\">" + i + "</button>";
        }

        return "<div class=\"table-container\">" +
               "  <table class=\"data-table\">" +
               "    <thead>" +
               "      <tr>" + headerHtml + "</tr>" +
               "    </thead>" +
               "    <tbody>" + bodyHtml + "</tbody>" +
               "  </table>" +
               "  <div class=\"pagination\">" + paginationHtml + "</div>" +
               "</div>";
    }
}
```

### Using Data Structures

```mono
component Main {
    function start(): void {
        // Create a table
        var table = new Table();

        // Set columns
        table.setColumns([
            { key: "id", label: "ID" },
            { key: "name", label: "Name" },
            { key: "age", label: "Age" },
            { key: "city", label: "City" }
        ]);

        // Set data
        table.setData([
            { id: 1, name: "John Doe", age: 30, city: "New York" },
            { id: 2, name: "Jane Smith", age: 25, city: "London" },
            { id: 3, name: "Bob Johnson", age: 40, city: "Paris" },
            { id: 4, name: "Alice Brown", age: 35, city: "Berlin" },
            { id: 5, name: "Charlie Davis", age: 28, city: "Tokyo" }
        ]);

        // Sort by name
        table.sort("name");

        // Render the table
        print table.render();
    }
}
```

## Spark Editor

Spark is a simple code editor designed specifically for the Mono language. It provides a modern development environment with features tailored for Mono development.

### Features

- **Code Editor**: Edit Mono files with syntax highlighting
- **Terminal**: Run Mono commands and see output directly in the editor
- **Project Browser**: Navigate through your project files
- **Quick Actions**: Common actions like creating new files, saving, and running
- **AI Assistant**: Get help with Mono programming

### Usage

To run the Spark editor:

```bash
./spark.py
```

### Sections

1. **Project Browser** (Left Panel): Navigate through your project files
2. **Editor** (Center Panel, Top): Edit your Mono files with syntax highlighting
3. **Terminal** (Center Panel, Bottom): Run Mono commands and see output
4. **Quick Actions** (Left Panel, Bottom): Access common actions
5. **AI Assistant** (Right Panel): Get help with Mono programming

## Installation

### Local Installation

1. Clone this repository
2. Make the scripts executable:
   ```bash
   chmod +x bin/mono bin/reactive-mono spark.py
   ```
3. Run a Mono script:
   ```bash
   ./bin/mono templates/start.mono
   ./bin/reactive-mono templates/reactive_app.mono
   ```
4. Run the Spark editor:
   ```bash
   ./spark.py
   ```

### System-wide Installation

1. Clone this repository
2. Install the package:
   ```bash
   pip install -e .
   ```
3. Run a Mono script from anywhere:
   ```bash
   mono templates/start.mono
   reactive-mono templates/reactive_app.mono
   ```

### Adding to PATH (Optional)

If you don't want to install the package system-wide, you can add the bin directory to your PATH:

```bash
# Add the following line to your ~/.bashrc or ~/.zshrc file
export PATH="$PATH:/path/to/mono/bin"

# Then reload your shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

Then you can run Mono scripts from any directory:
```bash
mono start.mono
reactive-mono reactive_app.mono
```

## Project Structure

```
mono/
├── assets/         # Images and resources
│   ├── mono_logo.png  # Mono logo (PNG format)
│   └── mono_logo.svg  # Mono logo (SVG format)
├── bin/           # Executable scripts
│   ├── mono       # Main Mono interpreter
│   ├── reactive-mono  # Wrapper for backward compatibility
│   ├── element-mono   # Mono interpreter with element support
│   ├── frame-mono     # Mono interpreter with frame support
│   ├── mono-kit      # Mono kit manager
│   ├── mono-layout   # Mono layout manager
│   ├── mono-runtime  # Mono runtime environment
│   └── mono-docs     # Mono documentation server
├── spark/         # Spark editor for Mono
│   ├── __init__.py   # Package initialization
│   ├── main.py       # Main editor code
│   ├── run.py        # Run script for the editor
│   └── README.md     # Editor documentation
├── spark.py       # Launcher for Spark editor
├── components/     # Component source files
│   └── button.mono    # Button component
├── docs/           # Documentation
│   ├── README.md      # Documentation home
│   ├── api/           # API reference
│   ├── tutorials/     # Tutorials
│   ├── case-studies/  # Case studies
│   └── examples/      # Examples
├── kits/           # Kit registry
├── lib/           # Library code
│   ├── __init__.py    # Package initialization
│   ├── mono_core.py   # Basic Mono interpreter
│   ├── mono_lifecycle.py  # Component lifecycle hooks
│   ├── mono_reactive.py  # Reactive Mono interpreter
│   ├── mono_typed.py  # Typed Mono interpreter
│   ├── mono_types.py  # Type system implementation
│   ├── mono_utils.py  # Utility functions
│   ├── mono_elements.py  # Element support for Mono
│   ├── mono_element_interpreter.py  # Interpreter with element support
│   ├── mono_communication.py  # Inter-component communication
│   ├── mono_frames.py  # Frame support for Mono
│   ├── mono_frame_interpreter.py  # Interpreter with frame support
│   ├── mono_combined_interpreter.py  # Combined interpreter with all features
│   ├── mono_kits.py  # Kit system for Mono
│   ├── mono_layouts.py  # Layout system for Mono
│   └── mono_runtime.py  # Runtime environment for Mono
├── templates/     # Example Mono scripts
│   ├── app_layout.layout  # App layout definition
│   ├── basic_counter.mono  # Basic counter example
│   ├── basic_demo.mono     # Basic demo of core features
│   ├── calculator.mono     # Calculator example
│   ├── calculator_app.mono # Advanced calculator app
│   ├── communication_demo.mono # Inter-component communication demo
│   ├── counter_app.mono    # Counter application
│   ├── counter_test.mono   # Counter with decrement
│   ├── element_demo.mono   # Component elements demo
│   ├── frames_demo.mono    # Frames demo
│   ├── generic_list.mono   # Generic list example
│   ├── kits_demo.mono      # Kits demo
│   ├── layouts_demo.mono   # Layouts demo
│   ├── lifecycle_demo.mono # Component lifecycle demo
│   ├── reactive_app.mono   # Reactive counter with display
│   ├── runtime_demo.mono   # Runtime environment demo
│   ├── simple_calculator.mono # Simple calculator
│   ├── simple_reactive.mono  # Simple reactive counter
│   ├── simple_todo.mono    # Todo list application
│   ├── simple_todo_manager.mono # Simple todo manager
│   ├── start.mono          # Basic counter with loop
│   ├── todo_app.mono       # Complete TODO application
│   ├── todo_manager.mono   # Todo manager application
│   ├── typed_counter.mono  # Typed counter example
│   └── ui_kit.mono        # UI kit definition
├── README.md      # Documentation
├── README_REACTIVE.md # Reactive Mono documentation
└── setup.py       # Installation script
```
