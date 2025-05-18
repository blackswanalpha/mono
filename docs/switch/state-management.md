# Switch State Management

The Switch framework provides a robust state management system similar to Redux or Vuex. It allows you to manage application state in a centralized store, making it easier to share state between components and maintain a predictable state flow.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Creating a Store](#creating-a-store)
4. [State](#state)
5. [Getters](#getters)
6. [Mutations](#mutations)
7. [Actions](#actions)
8. [Modules](#modules)
9. [Using the Store in Components](#using-the-store-in-components)
10. [Plugins](#plugins)
11. [Server-Side State Management](#server-side-state-management)
12. [Best Practices](#best-practices)

## Introduction

State management is a critical aspect of modern web applications. As applications grow in complexity, managing state across components becomes challenging. The Switch state management system provides a solution by centralizing state and enforcing a strict pattern for state mutations.

## Core Concepts

The Switch state management system is based on the following core concepts:

- **State**: The single source of truth for your application
- **Getters**: Computed properties derived from the state
- **Mutations**: Synchronous functions that modify the state
- **Actions**: Asynchronous functions that commit mutations
- **Modules**: Namespaced sections of the store for organizing state
- **Plugins**: Extensions that add functionality to the store

## Creating a Store

To create a store, use the `switch.createStore` function:

```mono
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

## State

The state is the single source of truth for your application. It's a plain object that contains all the data your application needs:

```mono
var store = switch.createStore({
    state: {
        count: 0,
        user: {
            name: "John Doe",
            email: "john@example.com"
        },
        todos: []
    }
});
```

To access the state, use the `state` property of the store:

```mono
var count = store.state.count;
var userName = store.state.user.name;
```

## Getters

Getters are computed properties derived from the state. They allow you to compute derived state without modifying the original state:

```mono
var store = switch.createStore({
    state: {
        todos: [
            { id: 1, text: "Learn Mono", completed: true },
            { id: 2, text: "Learn Switch", completed: false }
        ]
    },
    getters: {
        completedTodos: function(state) {
            return state.todos.filter(function(todo) {
                return todo.completed;
            });
        },
        incompleteTodos: function(state) {
            return state.todos.filter(function(todo) {
                return !todo.completed;
            });
        },
        todoCount: function(state) {
            return state.todos.length;
        }
    }
});
```

To access getters, use the `getters` property of the store:

```mono
var completedTodos = store.getters.completedTodos;
var todoCount = store.getters.todoCount;
```

## Mutations

Mutations are synchronous functions that modify the state. They are the only way to change the state in a Switch store:

```mono
var store = switch.createStore({
    state: {
        count: 0
    },
    mutations: {
        INCREMENT: function(state) {
            state.count += 1;
        },
        DECREMENT: function(state) {
            state.count -= 1;
        },
        SET_COUNT: function(state, count) {
            state.count = count;
        }
    }
});
```

To commit a mutation, use the `commit` method of the store:

```mono
store.commit('INCREMENT');
store.commit('SET_COUNT', 10);
```

## Actions

Actions are asynchronous functions that commit mutations. They are used for operations that may include asynchronous API calls:

```mono
var store = switch.createStore({
    state: {
        user: null,
        loading: false,
        error: null
    },
    mutations: {
        SET_LOADING: function(state, loading) {
            state.loading = loading;
        },
        SET_USER: function(state, user) {
            state.user = user;
        },
        SET_ERROR: function(state, error) {
            state.error = error;
        }
    },
    actions: {
        fetchUser: function(context, userId) {
            // Set loading state
            context.commit('SET_LOADING', true);
            
            // Make API call
            api.getUser(userId)
                .then(function(user) {
                    // Set user data
                    context.commit('SET_USER', user);
                    context.commit('SET_ERROR', null);
                })
                .catch(function(error) {
                    // Set error
                    context.commit('SET_ERROR', error);
                    context.commit('SET_USER', null);
                })
                .finally(function() {
                    // Clear loading state
                    context.commit('SET_LOADING', false);
                });
        }
    }
});
```

To dispatch an action, use the `dispatch` method of the store:

```mono
store.dispatch('fetchUser', 123);
```

## Modules

Modules allow you to organize your store into namespaced sections:

```mono
var store = switch.createStore({
    modules: {
        user: {
            state: {
                name: "John Doe",
                email: "john@example.com"
            },
            getters: {
                fullName: function(state) {
                    return state.name;
                }
            },
            mutations: {
                SET_NAME: function(state, name) {
                    state.name = name;
                }
            },
            actions: {
                updateName: function(context, name) {
                    context.commit('SET_NAME', name);
                }
            }
        },
        todos: {
            state: {
                items: []
            },
            mutations: {
                ADD_TODO: function(state, todo) {
                    state.items.push(todo);
                }
            }
        }
    }
});
```

To access module state, getters, mutations, and actions, use the module namespace:

```mono
// Access state
var userName = store.state.user.name;
var todos = store.state.todos.items;

// Access getters
var fullName = store.getters['user/fullName'];

// Commit mutations
store.commit('user/SET_NAME', "Jane Doe");
store.commit('todos/ADD_TODO', { id: 1, text: "Learn Mono", completed: false });

// Dispatch actions
store.dispatch('user/updateName', "Jane Doe");
```

## Using the Store in Components

To use the store in a component, use the `use_store`, `map_state`, and `map_actions` methods:

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
            addTodo: "addTodo",
            toggleTodo: "toggleTodo"
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

## Plugins

Plugins add functionality to the store. The Switch framework includes a localStorage plugin for persisting state:

```mono
var localStoragePlugin = switch.createLocalStoragePlugin({
    key: 'my-app-state',
    paths: ['user', 'todos']
});

var store = switch.createStore({
    state: {
        user: null,
        todos: [],
        settings: {}
    },
    plugins: [localStoragePlugin]
});
```

## Server-Side State Management

The Switch framework supports server-side state management. The store can be created on the server and hydrated on the client:

```mono
// Server-side
var store = create_store({
    state: {
        user: {
            name: "John Doe",
            email: "john@example.com"
        }
    }
});

// Render with SSR
var html = ssr.renderToString(component, { store: store });

// Client-side
// The store state is automatically hydrated from the server
```

## Best Practices

- Use the store for shared state only
- Keep component-specific state in the component
- Use mutations for synchronous state changes
- Use actions for asynchronous operations
- Use modules to organize your store
- Use getters for computed state
- Use plugins for cross-cutting concerns
- Use namespaced modules for large applications
