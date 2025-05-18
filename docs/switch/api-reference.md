# Switch Framework API Reference

This document provides detailed information about the Switch framework API.

## Table of Contents

1. [Component API](#component-api)
2. [Store API](#store-api)
3. [SSR API](#ssr-api)
4. [UI Kit API](#ui-kit-api)
5. [Deployment API](#deployment-api)

## Component API

### SwitchComponent

The `SwitchComponent` class represents a Switch component.

#### Constructor

```python
SwitchComponent(name: str, props: Dict[str, Any] = None, children: List[SwitchComponent] = None, store: Store = None)
```

- `name`: The component name
- `props`: Optional props
- `children`: Optional child components
- `store`: Optional store for state management

#### Properties

- `id`: The component ID
- `name`: The component name
- `props`: The component props
- `state`: The component state
- `children`: The component's children
- `events`: The component's event handlers
- `store`: The component's store
- `store_namespace`: The component's store namespace
- `store_watchers`: The component's store watchers

#### Methods

##### add_child

```python
add_child(child: SwitchComponent) -> None
```

Add a child component.

##### set_prop

```python
set_prop(name: str, value: Any) -> None
```

Set a prop value.

##### set_state

```python
set_state(state: Dict[str, Any]) -> None
```

Set the component state.

##### add_event

```python
add_event(event: str, handler: str) -> None
```

Add an event handler.

##### use_store

```python
use_store(store: Store, namespace: str = None) -> None
```

Use a store for state management.

##### map_state

```python
map_state(mapping: Dict[str, str]) -> None
```

Map store state to component props.

##### map_actions

```python
map_actions(mapping: Dict[str, str]) -> None
```

Map store actions to component methods.

##### commit

```python
commit(mutation_type: str, payload: Any = None) -> None
```

Commit a mutation to the store.

##### dispatch

```python
dispatch(action_type: str, payload: Any = None) -> Any
```

Dispatch an action to the store.

##### to_dict

```python
to_dict() -> Dict[str, Any]
```

Convert the component to a dictionary for serialization.

##### to_json

```python
to_json() -> str
```

Convert the component to a JSON string.

### SwitchRenderer

The `SwitchRenderer` class renders Switch components to HTML.

#### Constructor

```python
SwitchRenderer(title: str = "Switch App", scripts: List[str] = None, styles: List[str] = None)
```

- `title`: The page title
- `scripts`: Optional scripts to include
- `styles`: Optional styles to include

#### Methods

##### render

```python
render(component: SwitchComponent) -> str
```

Render a Switch component to HTML.

## Store API

### Store

The `Store` class provides centralized state management.

#### Constructor

```python
Store(options: Dict[str, Any] = None)
```

- `options`: Store options

#### Properties

- `state`: The store state
- `getters`: The store getters
- `mutations`: The store mutations
- `actions`: The store actions
- `modules`: The store modules
- `subscribers`: The store subscribers

#### Methods

##### get_getter

```python
get_getter(name: str) -> Any
```

Get a getter.

##### commit

```python
commit(type: str, payload: Any = None) -> None
```

Commit a mutation.

##### dispatch

```python
dispatch(type: str, payload: Any = None) -> Any
```

Dispatch an action.

##### subscribe

```python
subscribe(fn: Callable) -> Callable
```

Subscribe to store mutations.

##### watch

```python
watch(getter: Union[str, Callable], cb: Callable, options: Dict[str, Any] = None) -> Callable
```

Watch a getter or state path for changes.

##### register_module

```python
register_module(name: str, module: Dict[str, Any]) -> None
```

Register a module.

##### unregister_module

```python
unregister_module(name: str) -> None
```

Unregister a module.

##### to_json

```python
to_json() -> str
```

Convert the store state to JSON.

### create_store

```python
create_store(options: Dict[str, Any] = None) -> Store
```

Create a new store.

### create_file_storage_plugin

```python
create_file_storage_plugin(options: Dict[str, Any] = None) -> Callable
```

Create a plugin that saves the state to a file.

## SSR API

### SSRComponent

The `SSRComponent` class represents a server-side rendered Switch component.

#### Constructor

```python
SSRComponent(name: str, props: Dict[str, Any] = None, children: List[SSRComponent] = None, store: Store = None)
```

- `name`: The component name
- `props`: Optional props
- `children`: Optional child components
- `store`: Optional store for state management

#### Properties

- `html`: The rendered HTML
- `hydration_id`: The hydration ID
- `ssr_data`: Data for server-side rendering
- `ssr_context`: The SSR context

#### Methods

##### render

```python
render(renderer: SSRRenderer) -> str
```

Render the component to HTML.

##### render_to_string

```python
render_to_string(renderer: SSRRenderer) -> str
```

Render the component to an HTML string.

##### set_ssr_data

```python
set_ssr_data(key: str, value: Any) -> None
```

Set data for server-side rendering.

##### get_ssr_data

```python
get_ssr_data(key: str, default: Any = None) -> Any
```

Get data for server-side rendering.

##### set_ssr_context

```python
set_ssr_context(context: Dict[str, Any]) -> None
```

Set the SSR context.

##### get_ssr_context

```python
get_ssr_context() -> Dict[str, Any]
```

Get the SSR context.

### SSRRenderer

The `SSRRenderer` class renders Switch components on the server.

#### Constructor

```python
SSRRenderer(title: str = "Switch App", scripts: List[str] = None, styles: List[str] = None, store: Store = None)
```

- `title`: The page title
- `scripts`: Optional scripts to include
- `styles`: Optional styles to include
- `store`: Optional store for state management

#### Methods

##### set_ssr_context

```python
set_ssr_context(context: Dict[str, Any]) -> None
```

Set the SSR context.

##### get_ssr_context

```python
get_ssr_context() -> Dict[str, Any]
```

Get the SSR context.

##### render

```python
render(component: SSRComponent) -> str
```

Render a Switch component to HTML.

##### render_component

```python
render_component(component: SSRComponent) -> str
```

Render a component to HTML without the full document.

### SSRMiddleware

The `SSRMiddleware` class provides middleware for server-side rendering of Switch components.

#### Constructor

```python
SSRMiddleware(app_name: str = "Switch App")
```

- `app_name`: The application name

#### Methods

##### set_ssr_context

```python
set_ssr_context(context: Dict[str, Any]) -> None
```

Set the SSR context.

##### get_ssr_context

```python
get_ssr_context() -> Dict[str, Any]
```

Get the SSR context.

##### register_component

```python
register_component(component: SSRComponent) -> None
```

Register a component for server-side rendering.

##### render_component

```python
render_component(component_id: str, props: Dict[str, Any] = None, context: Dict[str, Any] = None) -> str
```

Render a component to HTML.

##### render_page

```python
render_page(component_id: str, props: Dict[str, Any] = None, context: Dict[str, Any] = None) -> str
```

Render a component as a complete HTML page.

### SSRComponentInstance

The `SSRComponentInstance` class represents an instance of an SSR component.

#### Constructor

```python
SSRComponentInstance(component_class: type, props: Dict[str, Any] = None, store: Store = None)
```

- `component_class`: The component class
- `props`: Optional props
- `store`: Optional store for state management

#### Methods

##### set_ssr_context

```python
set_ssr_context(context: Dict[str, Any]) -> None
```

Set the SSR context.

##### get_ssr_context

```python
get_ssr_context() -> Dict[str, Any]
```

Get the SSR context.

##### use_store

```python
use_store(store: Store) -> None
```

Use a store for state management.

##### create_ssr_component

```python
create_ssr_component() -> SSRComponent
```

Create an SSR component from this instance.

##### render

```python
render(renderer: SSRRenderer) -> str
```

Render the component to HTML.

##### render_page

```python
render_page(renderer: SSRRenderer) -> str
```

Render the component as a complete HTML page.

### create_ssr_component

```python
create_ssr_component(component_class: type, props: Dict[str, Any] = None, store: Store = None) -> SSRComponentInstance
```

Create an SSR component instance.

## UI Kit API

### SwitchUIKit

The `SwitchUIKit` namespace provides access to UI kit components.

#### Components

- `Button`: A customizable button component
- `Card`: A card component with header, body, and footer
- `Modal`: A modal dialog component
- `Tabs`: A tabbed interface component
- `Alert`: An alert component for notifications
- `Dropdown`: A dropdown menu component
- `Table`: A table component with sorting, filtering, and pagination
- `Form`: A form component with validation
- `Tooltip`: A tooltip component for displaying additional information
- `Accordion`: An accordion component for collapsible content
- `Pagination`: A pagination component for navigating through pages
- `Progress`: A progress bar component
- `Spinner`: A loading spinner component
- `Badge`: A badge component for displaying counts or status
- `Avatar`: An avatar component for displaying user images
- `DatePicker`: A date picker component
- `Slider`: A slider component
- `Carousel`: A carousel component

## Deployment API

### mono-switch-deploy

The `mono-switch-deploy` script deploys Mono Switch applications to Vercel.

#### Usage

```bash
mono-switch-deploy [options] <directory>
```

#### Options

- `--name NAME`: Set the project name (default: directory name)
- `--prod`: Deploy to production
- `--no-build`: Skip the build step
- `--no-deploy`: Prepare for deployment but don't deploy
