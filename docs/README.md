# Mono Documentation

Welcome to the Mono documentation! This guide will help you learn how to use Mono to build reactive, component-based applications.

## Table of Contents

- [Getting Started](#getting-started)
- [Tutorials](#tutorials)
- [Case Studies](#case-studies)
- [API Reference](#api-reference)
- [Examples](#examples)

## Getting Started

Mono is a component-based language for building reactive applications. It features:

- **Component-Based Architecture**: Build applications using reusable components
- **Reactive Programming**: Components automatically update when their state changes
- **Type System**: Static typing with type inference and generics
- **Concurrency**: Built-in support for parallel execution and thread management
- **Layouts**: Declarative layout system for arranging components
- **Kits**: Pre-baked component suites for rapid development
- **Runtime Environment**: Advanced scheduling, garbage collection, and hot reloading

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mono.git
cd mono

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x bin/*
```

### Hello World

Create a file named `hello.mono`:

```mono
component HelloWorld {
    state {
        message: string = "Hello, World!"
    }
    
    function render(): string {
        return "<div>" + this.state.message + "</div>";
    }
}

component Main {
    function start(): void {
        var hello = new HelloWorld();
        print hello.render();
    }
}
```

Run it with:

```bash
./bin/mono hello.mono
```

## Tutorials

- [Building a TODO App](tutorials/todo-app.md) - Learn how to build a complete TODO application with Mono
- [Parallel Components](tutorials/parallel-components.md) - Learn how to use Mono's concurrency features
- [Creating Custom Layouts](tutorials/custom-layouts.md) - Learn how to create custom layouts for your components
- [Building a Kit](tutorials/building-kit.md) - Learn how to create a reusable kit of components

## Case Studies

- [Thread Management Best Practices](case-studies/thread-management.md) - Learn best practices for managing threads in Mono
- [Layout System Best Practices](case-studies/layout-system.md) - Learn best practices for using Mono's layout system
- [Performance Optimization](case-studies/performance-optimization.md) - Learn how to optimize the performance of your Mono applications

## API Reference

- [Component Lifecycle](api/component-lifecycle.md) - Detailed documentation of component lifecycle hooks
- [Concurrency API](api/concurrency.md) - Detailed documentation of Mono's concurrency features
- [Layout API](api/layout.md) - Detailed documentation of Mono's layout system
- [Kit API](api/kit.md) - Detailed documentation of Mono's kit system
- [Runtime Environment API](api/runtime.md) - Detailed documentation of Mono's runtime environment

## Examples

- [Counter](examples/counter.md) - A simple counter component
- [Calculator](examples/calculator.md) - A calculator application
- [TODO List](examples/todo-list.md) - A TODO list application
- [Chat Application](examples/chat.md) - A real-time chat application
- [Dashboard](examples/dashboard.md) - A data visualization dashboard
