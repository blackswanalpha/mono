"""
Mono Switch SSR - Server-Side Rendering for the Switch framework

This module provides server-side rendering capabilities for the Switch framework.
It allows components to be fully rendered on the server and then hydrated on the client.
"""

import os
import json
import re
import time
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from .mono_http import Response, Request, HttpStatus
from .mono_switch import SwitchComponent, SwitchRenderer, SwitchMiddleware, get_switch_store
from .mono_switch_store import Store

class SSRComponent(SwitchComponent):
    """
    Represents a server-side rendered Switch component.
    """
    def __init__(self, name: str, props: Dict[str, Any] = None, children: List['SSRComponent'] = None, store: Store = None):
        super().__init__(name, props, children, store)
        self.html = ""
        self.hydration_id = f"switch-hydrate-{self.id}"
        self.ssr_data = {}
        self.ssr_context = {}
        self.hydration_strategy = "eager"  # eager, lazy, visible, interactive
        self.critical = False  # Whether this component is critical for initial render
        self.layout = None  # Associated layout
        self.frame = None  # Associated frame

    def render(self, renderer: 'SSRRenderer') -> str:
        """Render the component to HTML."""
        # This method should be implemented by subclasses
        return ""

    def render_to_string(self, renderer: 'SSRRenderer') -> str:
        """
        Render the component to an HTML string.

        This method is used for server-side rendering.
        """
        # Get the component HTML
        html = self.render(renderer)

        # Add hydration attributes
        hydration_attrs = f'id="{self.hydration_id}" data-ssr-component="{self.name}" data-hydration-strategy="{self.hydration_strategy}"'

        # Add critical attribute if needed
        if self.critical:
            hydration_attrs += ' data-critical="true"'

        # Add layout attribute if needed
        if self.layout:
            hydration_attrs += f' data-layout="{self.layout.name}"'

        # Add frame attribute if needed
        if self.frame:
            hydration_attrs += f' data-frame="{self.frame.name}"'

        # Wrap with hydration container
        html = f'<div {hydration_attrs}>{html}</div>'

        return html

    def set_ssr_data(self, key: str, value: Any) -> None:
        """
        Set data for server-side rendering.

        This data will be available during rendering but will not be sent to the client.
        """
        self.ssr_data[key] = value

    def set_hydration_strategy(self, strategy: str) -> None:
        """
        Set the hydration strategy for this component.

        Args:
            strategy: The hydration strategy (eager, lazy, visible, interactive)
        """
        valid_strategies = ["eager", "lazy", "visible", "interactive"]
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid hydration strategy: {strategy}. Must be one of {valid_strategies}")

        self.hydration_strategy = strategy

    def set_critical(self, critical: bool) -> None:
        """
        Set whether this component is critical for initial render.

        Critical components are hydrated first.

        Args:
            critical: Whether this component is critical
        """
        self.critical = critical

    def set_layout(self, layout: 'Layout') -> None:
        """
        Set the layout for this component.

        Args:
            layout: The layout to use
        """
        self.layout = layout

    def set_frame(self, frame: 'Frame') -> None:
        """
        Set the frame for this component.

        Args:
            frame: The frame to use
        """
        self.frame = frame

    def get_ssr_data(self, key: str, default: Any = None) -> Any:
        """
        Get data for server-side rendering.

        Args:
            key: The data key
            default: Default value if the key doesn't exist

        Returns:
            The data value
        """
        return self.ssr_data.get(key, default)

    def set_ssr_context(self, context: Dict[str, Any]) -> None:
        """
        Set the SSR context.

        The context is shared between all components during server-side rendering.
        """
        self.ssr_context = context

    def get_ssr_context(self) -> Dict[str, Any]:
        """
        Get the SSR context.

        Returns:
            The SSR context
        """
        return self.ssr_context

    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary for serialization."""
        data = super().to_dict()
        data['hydration_id'] = self.hydration_id
        return data

class SSRRenderer(SwitchRenderer):
    """
    Renders Switch components on the server.
    """
    def __init__(self, title: str = "Switch App", scripts: List[str] = None, styles: List[str] = None, store: Store = None):
        super().__init__(title, scripts, styles)

        # Add the SSR hydration script
        self.scripts.insert(2, "/switch/hydrate.js")

        # Add the enhanced hydration script
        self.scripts.insert(3, "/src/static/js/enhanced-hydration.js")

        # Store
        self.store = store or get_switch_store()

        # SSR context
        self.ssr_context = {}

        # Streaming mode
        self.streaming = False

        # Cache settings
        self.cache_enabled = False
        self.cache_ttl = 60  # seconds
        self.cache = {}

        # Hydration settings
        self.hydration_enabled = True
        self.selective_hydration = False
        self.hydration_components = []  # List of component IDs to hydrate

    def set_ssr_context(self, context: Dict[str, Any]) -> None:
        """
        Set the SSR context.

        The context is shared between all components during server-side rendering.
        """
        self.ssr_context = context

    def get_ssr_context(self) -> Dict[str, Any]:
        """
        Get the SSR context.

        Returns:
            The SSR context
        """
        return self.ssr_context

    def enable_streaming(self, enabled: bool = True) -> None:
        """
        Enable or disable streaming SSR.

        Args:
            enabled: Whether to enable streaming
        """
        self.streaming = enabled

    def enable_caching(self, enabled: bool = True, ttl: int = 60) -> None:
        """
        Enable or disable component caching.

        Args:
            enabled: Whether to enable caching
            ttl: Cache TTL in seconds
        """
        self.cache_enabled = enabled
        self.cache_ttl = ttl

    def enable_selective_hydration(self, enabled: bool = True, components: List[str] = None) -> None:
        """
        Enable or disable selective hydration.

        Args:
            enabled: Whether to enable selective hydration
            components: List of component IDs to hydrate (if None, all components are hydrated)
        """
        self.selective_hydration = enabled
        if components:
            self.hydration_components = components

    def get_cached_component(self, component_id: str, props: Dict[str, Any] = None) -> Optional[str]:
        """
        Get a cached component.

        Args:
            component_id: The component ID
            props: The component props

        Returns:
            The cached HTML or None if not cached
        """
        if not self.cache_enabled:
            return None

        # Create a cache key
        cache_key = f"{component_id}:{json.dumps(props or {})}"

        # Check if the component is in the cache
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]

            # Check if the cache entry is still valid
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                return cache_entry["html"]

            # Remove the expired cache entry
            del self.cache[cache_key]

        return None

    def cache_component(self, component_id: str, props: Dict[str, Any], html: str) -> None:
        """
        Cache a component.

        Args:
            component_id: The component ID
            props: The component props
            html: The rendered HTML
        """
        if not self.cache_enabled:
            return

        # Create a cache key
        cache_key = f"{component_id}:{json.dumps(props or {})}"

        # Add the component to the cache
        self.cache[cache_key] = {
            "timestamp": time.time(),
            "html": html
        }

    def should_hydrate_component(self, component_id: str) -> bool:
        """
        Check if a component should be hydrated.

        Args:
            component_id: The component ID

        Returns:
            Whether the component should be hydrated
        """
        if not self.hydration_enabled:
            return False

        if not self.selective_hydration:
            return True

        return component_id in self.hydration_components

    def render(self, component: SSRComponent) -> str:
        """Render a Switch component to HTML."""
        # Check if the component is cached
        cached_html = self.get_cached_component(component.id, component.props)
        if cached_html:
            return cached_html

        # Set the store in the component
        if not component.store and self.store:
            component.use_store(self.store)

        # Set the SSR context in the component
        component.set_ssr_context(self.ssr_context)

        # Render the component
        component_html = component.render_to_string(self)

        # Determine hydration settings
        hydration_enabled = self.hydration_enabled
        selective_hydration = self.selective_hydration
        hydration_components = self.hydration_components

        # Create hydration configuration
        hydration_config = {
            "enabled": hydration_enabled,
            "selective": selective_hydration,
            "components": hydration_components if selective_hydration else [],
            "streaming": self.streaming
        }

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
        window.SWITCH_SSR = true;
        window.SWITCH_STORE_STATE = {json.dumps(self.store.state) if self.store else '{}'};
        window.SWITCH_HYDRATION_CONFIG = {json.dumps(hydration_config)};
    </script>
</head>
<body>
    <!-- Root Element -->
    <div id="switch-root" data-ssr="true">{component_html}</div>

    <!-- Switch Framework Scripts -->
    {self._render_scripts()}

    <!-- Hydration Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (window.Switch && window.Switch.hydrate) {{
                // Check if we should use enhanced hydration
                if (window.SwitchEnhanced && window.SwitchEnhanced.hydration) {{
                    // Use enhanced hydration
                    SwitchEnhanced.hydration.hydrateRoot(
                        document.getElementById('switch-root'),
                        window.SWITCH_INITIAL_DATA,
                        window.SWITCH_HYDRATION_CONFIG
                    );
                }} else {{
                    // Use basic hydration
                    Switch.hydrate('{component.hydration_id}', window.SWITCH_INITIAL_DATA);
                }}
            }}
        }});
    </script>
</body>
</html>"""

        # Cache the rendered HTML if caching is enabled
        if self.cache_enabled:
            self.cache_component(component.id, component.props, html)

        return html

    def render_component(self, component: SSRComponent) -> str:
        """
        Render a component to HTML without the full document.

        This is useful for rendering components that will be included in other pages.
        """
        # Set the store in the component
        if not component.store and self.store:
            component.use_store(self.store)

        # Set the SSR context in the component
        component.set_ssr_context(self.ssr_context)

        # Render the component
        return component.render_to_string(self)

class SSRMiddleware(SwitchMiddleware):
    """
    Middleware for server-side rendering of Switch components.
    """
    def __init__(self, app_name: str = "Switch App"):
        super().__init__(app_name)
        self.ssr_components: Dict[str, SSRComponent] = {}
        self.ssr_context: Dict[str, Any] = {}

    def set_ssr_context(self, context: Dict[str, Any]) -> None:
        """
        Set the SSR context.

        The context is shared between all components during server-side rendering.
        """
        self.ssr_context = context

    def get_ssr_context(self) -> Dict[str, Any]:
        """
        Get the SSR context.

        Returns:
            The SSR context
        """
        return self.ssr_context

    def register_component(self, component: SSRComponent) -> None:
        """Register a component for server-side rendering."""
        self.ssr_components[component.id] = component

    def render_component(self, component_id: str, props: Dict[str, Any] = None, context: Dict[str, Any] = None) -> str:
        """
        Render a component to HTML.

        Args:
            component_id: The component ID
            props: Optional props to update
            context: Optional SSR context

        Returns:
            The rendered HTML
        """
        if component_id not in self.ssr_components:
            return f"<div>Component not found: {component_id}</div>"

        component = self.ssr_components[component_id]

        # Update props if provided
        if props:
            for key, value in props.items():
                component.set_prop(key, value)

        # Create a renderer
        renderer = SSRRenderer(self.app_name, store=self.store)

        # Set the SSR context
        if context:
            renderer.set_ssr_context(context)
        else:
            renderer.set_ssr_context(self.ssr_context)

        # Render the component
        return renderer.render_component(component)

    def render_page(self, component_id: str, props: Dict[str, Any] = None, context: Dict[str, Any] = None) -> str:
        """
        Render a component as a complete HTML page.

        Args:
            component_id: The component ID
            props: Optional props to update
            context: Optional SSR context

        Returns:
            The rendered HTML page
        """
        if component_id not in self.ssr_components:
            return f"<html><body><div>Component not found: {component_id}</div></body></html>"

        component = self.ssr_components[component_id]

        # Update props if provided
        if props:
            for key, value in props.items():
                component.set_prop(key, value)

        # Create a renderer
        renderer = SSRRenderer(self.app_name, store=self.store)

        # Set the SSR context
        if context:
            renderer.set_ssr_context(context)
        else:
            renderer.set_ssr_context(self.ssr_context)

        # Render the component
        return renderer.render(component)

    def _handle_switch_api(self, req: Request, res: Response) -> None:
        """Handle a Switch API request."""
        # Get the API endpoint
        endpoint = req.path[len("/api/switch/"):]

        # Handle the endpoint
        if endpoint == "state":
            self._handle_state_update(req, res)
        elif endpoint == "event":
            self._handle_event(req, res)
        elif endpoint == "ssr":
            self._handle_ssr_request(req, res)
        elif endpoint == "store":
            self._handle_store_operation(req, res)
        else:
            super()._handle_switch_api(req, res)

    def _handle_ssr_request(self, req: Request, res: Response) -> None:
        """Handle an SSR request."""
        # Get the request body
        data = req.get_json()
        if not data:
            res.status(HttpStatus.BAD_REQUEST).text("Invalid request body")
            return

        # Get the component ID
        component_id = data.get('componentId')
        if not component_id:
            res.status(HttpStatus.BAD_REQUEST).text("Missing componentId")
            return

        # Get the props
        props = data.get('props', {})

        # Get the context
        context = data.get('context', {})

        # Get the render mode
        render_mode = data.get('renderMode', 'component')

        # Render the component
        if render_mode == 'page':
            html = self.render_page(component_id, props, context)
        else:
            html = self.render_component(component_id, props, context)

        # Send the response
        res.json({
            'html': html,
            'componentId': component_id
        })

# Create a global instance of the SSR middleware
ssr_middleware = SSRMiddleware()

def get_ssr_middleware() -> SSRMiddleware:
    """Get the global SSR middleware instance."""
    return ssr_middleware

class SSRComponentInstance:
    """
    Represents an instance of an SSR component.
    """
    def __init__(self, component_class: type, props: Dict[str, Any] = None, store: Store = None):
        self.component_class = component_class
        self.props = props or {}
        self.id = f"ssr-{component_class.__name__.lower()}-{id(self)}"
        self.ssr_component = None
        self.store = store
        self.ssr_context = {}

    def set_ssr_context(self, context: Dict[str, Any]) -> None:
        """
        Set the SSR context.

        The context is shared between all components during server-side rendering.
        """
        self.ssr_context = context

    def get_ssr_context(self) -> Dict[str, Any]:
        """
        Get the SSR context.

        Returns:
            The SSR context
        """
        return self.ssr_context

    def use_store(self, store: Store) -> None:
        """
        Use a store for state management.

        Args:
            store: The store to use
        """
        self.store = store

        # Update the SSR component if it exists
        if self.ssr_component:
            self.ssr_component.use_store(store)

    def create_ssr_component(self) -> SSRComponent:
        """Create an SSR component from this instance."""
        if not self.ssr_component:
            self.ssr_component = SSRComponent(self.component_class.__name__, self.props, store=self.store)

            # Set the SSR context
            self.ssr_component.set_ssr_context(self.ssr_context)

        return self.ssr_component

    def render(self, renderer: SSRRenderer) -> str:
        """Render the component to HTML."""
        # Create the SSR component if it doesn't exist
        if not self.ssr_component:
            self.create_ssr_component()

        # Register the component with the SSR middleware
        ssr_middleware.register_component(self.ssr_component)

        # Render the component
        return renderer.render_component(self.ssr_component)

    def render_page(self, renderer: SSRRenderer) -> str:
        """Render the component as a complete HTML page."""
        # Create the SSR component if it doesn't exist
        if not self.ssr_component:
            self.create_ssr_component()

        # Register the component with the SSR middleware
        ssr_middleware.register_component(self.ssr_component)

        # Render the component
        return renderer.render(self.ssr_component)

def create_ssr_component(component_class: type, props: Dict[str, Any] = None, store: Store = None) -> SSRComponentInstance:
    """
    Create an SSR component instance.

    Args:
        component_class: The component class
        props: Optional props
        store: Optional store

    Returns:
        The SSR component instance
    """
    return SSRComponentInstance(component_class, props, store)
