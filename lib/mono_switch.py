"""
Mono Switch - Bridge between Mono and the Switch frontend framework

This module provides integration between the Mono language and the Switch frontend framework.
It handles:
1. Serving the Switch framework files
2. Component serialization for client-side rendering
3. Client-server communication
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from .mono_http import Response, Request, HttpStatus
from .mono_switch_store import Store, create_store

# Path to the Switch framework files
SWITCH_DIR = os.path.join(os.path.dirname(__file__), '..', 'switch')

class SwitchComponent:
    """
    Represents a Switch component that can be rendered on the client-side.
    """
    def __init__(self, name: str, props: Dict[str, Any] = None, children: List['SwitchComponent'] = None, store: Store = None):
        self.name = name
        self.props = props or {}
        self.children = children or []
        self.state = {}
        self.events = {}
        self.id = f"switch-{name.lower()}-{id(self)}"
        self.store = store
        self.store_namespace = None
        self.store_watchers = []

    def add_child(self, child: 'SwitchComponent') -> None:
        """Add a child component."""
        self.children.append(child)

    def set_prop(self, name: str, value: Any) -> None:
        """Set a prop value."""
        self.props[name] = value

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the component state."""
        self.state = state

    def add_event(self, event: str, handler: str) -> None:
        """Add an event handler."""
        self.events[event] = handler

    def use_store(self, store: Store, namespace: str = None) -> None:
        """
        Use a store for state management.

        Args:
            store: The store to use
            namespace: Optional namespace for store access
        """
        self.store = store
        self.store_namespace = namespace

    def map_state(self, mapping: Dict[str, str]) -> None:
        """
        Map store state to component props.

        Args:
            mapping: A mapping of component prop names to store state paths
        """
        if not self.store:
            raise ValueError("No store is attached to this component")

        # Create watchers for each mapping
        for prop_name, state_path in mapping.items():
            # Create the full path if using a namespace
            full_path = f"{self.store_namespace}/{state_path}" if self.store_namespace else state_path

            # Create a watcher function
            def watcher(new_value, old_value, prop=prop_name):
                self.props[prop] = new_value

            # Watch the state path
            unwatch = self.store.watch(full_path, watcher, {'immediate': True})

            # Store the unwatch function
            self.store_watchers.append(unwatch)

    def map_actions(self, mapping: Dict[str, str]) -> None:
        """
        Map store actions to component methods.

        Args:
            mapping: A mapping of component method names to store action types
        """
        if not self.store:
            raise ValueError("No store is attached to this component")

        # Create methods for each mapping
        for method_name, action_type in mapping.items():
            # Create the full action type if using a namespace
            full_action_type = f"{self.store_namespace}/{action_type}" if self.store_namespace else action_type

            # Create a method that dispatches the action
            def dispatch_action(payload=None, action=full_action_type):
                return self.store.dispatch(action, payload)

            # Add the method to the component
            setattr(self, method_name, dispatch_action)

    def commit(self, mutation_type: str, payload: Any = None) -> None:
        """
        Commit a mutation to the store.

        Args:
            mutation_type: The mutation type
            payload: The mutation payload
        """
        if not self.store:
            raise ValueError("No store is attached to this component")

        # Create the full mutation type if using a namespace
        full_mutation_type = f"{self.store_namespace}/{mutation_type}" if self.store_namespace else mutation_type

        # Commit the mutation
        self.store.commit(full_mutation_type, payload)

    def dispatch(self, action_type: str, payload: Any = None) -> Any:
        """
        Dispatch an action to the store.

        Args:
            action_type: The action type
            payload: The action payload

        Returns:
            The action result
        """
        if not self.store:
            raise ValueError("No store is attached to this component")

        # Create the full action type if using a namespace
        full_action_type = f"{self.store_namespace}/{action_type}" if self.store_namespace else action_type

        # Dispatch the action
        return self.store.dispatch(full_action_type, payload)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary for serialization."""
        result = {
            'id': self.id,
            'name': self.name,
            'props': self.props,
            'state': self.state,
            'events': self.events,
            'children': [child.to_dict() for child in self.children]
        }

        # Add store information if available
        if self.store:
            result['store'] = {
                'namespace': self.store_namespace
            }

        return result

    def to_json(self) -> str:
        """Convert the component to a JSON string."""
        return json.dumps(self.to_dict())

class SwitchRenderer:
    """
    Renders Switch components to HTML.
    """
    def __init__(self, title: str = "Switch App", scripts: List[str] = None, styles: List[str] = None):
        self.title = title
        self.scripts = scripts or []
        self.styles = styles or []

        # Add the core Switch framework script
        self.scripts.insert(0, "/switch/switch.js")

        # Add the Switch store
        self.scripts.insert(1, "/switch/store.js")

        # Add the Switch components
        self.scripts.insert(2, "/switch/components.js")

        # Add the core Switch framework style
        self.styles.insert(0, "/switch/switch.css")

    def render(self, component: SwitchComponent) -> str:
        """Render a Switch component to HTML."""
        # Check if this is an HMR component
        is_hmr = hasattr(component, 'hmr_id')

        # Create HMR-specific JavaScript
        hmr_js = ""
        if is_hmr:
            hmr_js = """
            // Register component for HMR
            if (window.Switch.hmr) {
                Switch.hmr.register(component);
            }
            """

        # Create HMR-specific script tags
        hmr_script = ""
        if is_hmr:
            hmr_script = """
        window.SWITCH_HMR = true;
        window.SWITCH_HMR_CONFIG = { debug: true, interval: 2000 };
        """

        # Create the HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>

    <!-- Switch Framework Styles -->
    {self._render_styles()}

    <!-- Initial Component Data -->
    <script>
        window.SWITCH_INITIAL_DATA = {component.to_json()};
        {hmr_script}
    </script>
</head>
<body>
    <!-- Root Element -->
    <div id="switch-root"></div>

    <!-- Switch Framework Scripts -->
    {self._render_scripts()}

    <!-- Initialize Component -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Create the component
            const component = Switch.createComponent({component.to_json()});

            // Render the component
            Switch.renderComponent(component, document.getElementById('switch-root'));
            {hmr_js}
        }});
    </script>
</body>
</html>"""

        return html

    def _render_styles(self) -> str:
        """Render the style links."""
        return "\n".join([f'<link rel="stylesheet" href="{style}">' for style in self.styles])

    def _render_scripts(self) -> str:
        """Render the script tags."""
        return "\n".join([f'<script src="{script}"></script>' for script in self.scripts])

class SwitchMiddleware:
    """
    Middleware for serving Switch framework files and handling Switch requests.
    """
    def __init__(self, app_name: str = "Switch App"):
        self.app_name = app_name
        self.store = None
        self.components = {}
        self.event_handlers = {}

    def set_store(self, store: Store) -> None:
        """
        Set the global store for the application.

        Args:
            store: The store to use
        """
        self.store = store

    def register_component(self, component: SwitchComponent) -> None:
        """
        Register a component for server-side processing.

        Args:
            component: The component to register
        """
        self.components[component.id] = component

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.

        Args:
            event_type: The event type
            handler: The handler function
        """
        self.event_handlers[event_type] = handler

    def handle(self, req: Request, res: Response, next: Callable) -> None:
        """Handle a request."""
        # Check if this is a request for a Switch framework file
        if req.path.startswith("/switch/"):
            self._serve_switch_file(req, res)
            return

        # Check if this is a Switch API request
        if req.path.startswith("/api/switch/"):
            self._handle_switch_api(req, res)
            return

        # Continue to the next middleware
        next()

    def _serve_switch_file(self, req: Request, res: Response) -> None:
        """Serve a Switch framework file."""
        # Get the file path
        file_path = req.path[len("/switch/"):]
        full_path = os.path.join(SWITCH_DIR, file_path)

        # Check if the file exists
        if not os.path.exists(full_path):
            res.status(HttpStatus.NOT_FOUND).text("File not found")
            return

        # Determine the content type
        content_type = self._get_content_type(file_path)

        # Read the file
        with open(full_path, "r") as f:
            content = f.read()

        # Send the response
        res.header("Content-Type", content_type).text(content)

    def _handle_switch_api(self, req: Request, res: Response) -> None:
        """Handle a Switch API request."""
        # Get the API endpoint
        endpoint = req.path[len("/api/switch/"):]

        # Handle the endpoint
        if endpoint == "state":
            self._handle_state_update(req, res)
        elif endpoint == "event":
            self._handle_event(req, res)
        elif endpoint == "store":
            self._handle_store_operation(req, res)
        else:
            res.status(HttpStatus.NOT_FOUND).text("API endpoint not found")

    def _handle_state_update(self, req: Request, res: Response) -> None:
        """Handle a state update request."""
        # Get the request body
        data = req.get_json()
        if not data:
            res.status(HttpStatus.BAD_REQUEST).text("Invalid request body")
            return

        # Check if the component ID is provided
        component_id = data.get('componentId')
        if not component_id:
            res.status(HttpStatus.BAD_REQUEST).text("Component ID is required")
            return

        # Check if the component exists
        component = self.components.get(component_id)
        if not component:
            res.status(HttpStatus.NOT_FOUND).text("Component not found")
            return

        # Update the component state
        new_state = data.get('state', {})
        component.set_state(new_state)

        # Send a success response
        res.json({
            "success": True,
            "component": component.to_dict()
        })

    def _handle_event(self, req: Request, res: Response) -> None:
        """Handle an event request."""
        # Get the request body
        data = req.get_json()
        if not data:
            res.status(HttpStatus.BAD_REQUEST).text("Invalid request body")
            return

        # Check if the component ID is provided
        component_id = data.get('componentId')
        if not component_id:
            res.status(HttpStatus.BAD_REQUEST).text("Component ID is required")
            return

        # Check if the event type is provided
        event_type = data.get('event')
        if not event_type:
            res.status(HttpStatus.BAD_REQUEST).text("Event type is required")
            return

        # Check if the component exists
        component = self.components.get(component_id)
        if not component:
            res.status(HttpStatus.NOT_FOUND).text("Component not found")
            return

        # Check if the component has a handler for this event
        handler_name = component.events.get(event_type)
        if not handler_name:
            res.status(HttpStatus.BAD_REQUEST).text(f"No handler for event: {event_type}")
            return

        # Check if there's a global handler for this event
        handler = self.event_handlers.get(handler_name)
        if not handler:
            res.status(HttpStatus.INTERNAL_SERVER_ERROR).text(f"Handler not found: {handler_name}")
            return

        # Call the handler
        try:
            result = handler(component, data.get('data'))

            # Send a success response
            res.json({
                "success": True,
                "result": result,
                "component": component.to_dict()
            })
        except Exception as e:
            # Send an error response
            res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
                "success": False,
                "error": str(e)
            })

    def _handle_store_operation(self, req: Request, res: Response) -> None:
        """Handle a store operation request."""
        # Check if the store is available
        if not self.store:
            res.status(HttpStatus.INTERNAL_SERVER_ERROR).text("Store not available")
            return

        # Get the request body
        data = req.get_json()
        if not data:
            res.status(HttpStatus.BAD_REQUEST).text("Invalid request body")
            return

        # Check if the operation type is provided
        operation = data.get('operation')
        if not operation:
            res.status(HttpStatus.BAD_REQUEST).text("Operation type is required")
            return

        # Handle the operation
        try:
            if operation == 'commit':
                # Check if the mutation type is provided
                mutation_type = data.get('type')
                if not mutation_type:
                    res.status(HttpStatus.BAD_REQUEST).text("Mutation type is required")
                    return

                # Commit the mutation
                self.store.commit(mutation_type, data.get('payload'))

                # Send a success response
                res.json({
                    "success": True,
                    "state": self.store.state
                })
            elif operation == 'dispatch':
                # Check if the action type is provided
                action_type = data.get('type')
                if not action_type:
                    res.status(HttpStatus.BAD_REQUEST).text("Action type is required")
                    return

                # Dispatch the action
                result = self.store.dispatch(action_type, data.get('payload'))

                # Send a success response
                res.json({
                    "success": True,
                    "result": result,
                    "state": self.store.state
                })
            elif operation == 'getState':
                # Send the current state
                res.json({
                    "success": True,
                    "state": self.store.state
                })
            else:
                res.status(HttpStatus.BAD_REQUEST).text(f"Unknown operation: {operation}")
        except Exception as e:
            # Send an error response
            res.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
                "success": False,
                "error": str(e)
            })

    def _get_content_type(self, file_path: str) -> str:
        """Get the content type for a file."""
        if file_path.endswith(".js"):
            return "application/javascript"
        elif file_path.endswith(".css"):
            return "text/css"
        elif file_path.endswith(".html"):
            return "text/html"
        elif file_path.endswith(".json"):
            return "application/json"
        else:
            return "text/plain"

# Create a global instance of the Switch middleware
switch_middleware = SwitchMiddleware()

# Create a global store
switch_store = None

def get_switch_middleware() -> SwitchMiddleware:
    """Get the global Switch middleware instance."""
    return switch_middleware

def get_switch_store() -> Store:
    """Get the global Switch store instance."""
    global switch_store
    if switch_store is None:
        # Create a default store
        switch_store = create_store()

        # Set the store in the middleware
        switch_middleware.set_store(switch_store)

    return switch_store

def create_switch_store(options: Dict[str, Any] = None) -> Store:
    """
    Create a new Switch store.

    Args:
        options: Store options

    Returns:
        The store
    """
    global switch_store

    # Create the store
    switch_store = create_store(options)

    # Set the store in the middleware
    switch_middleware.set_store(switch_store)

    return switch_store
