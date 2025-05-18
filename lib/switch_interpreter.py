"""
Switch Interpreter - Interpreter for the Switch frontend framework

This module provides an interpreter for the Switch frontend framework.
It extends the Mono HTTP interpreter to add support for Switch components.
"""

import os
import json
import re
import traceback
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from .mono_http_interpreter import HttpInterpreter, HttpComponentInstance, HttpComponent
from .mono_http import Response, Request, HttpStatus
from .mono_switch import SwitchComponent, SwitchRenderer, SwitchMiddleware, get_switch_middleware
from .mono_switch_ssr import SSRComponent, SSRRenderer, SSRMiddleware, get_ssr_middleware
from .mono_switch_hmr import HMRComponent, HMRMiddleware, get_hmr_middleware, start_hmr_watcher
from .mono_switch_kit import SwitchKit, SwitchKitManager, SwitchKitMiddleware, get_kit_middleware, get_kit_manager
from .mono_switch_app import SwitchApp, get_switch_app, set_switch_app
from .mono_switch_error import (
    SwitchError, SwitchRenderError, SwitchComponentError, SwitchStateError,
    SwitchEventError, SwitchRouteError, SwitchKitError, SwitchErrorHandler,
    SwitchErrorMiddleware, get_error_handler, get_error_middleware, set_debug_mode
)

class SwitchComponentInstance(HttpComponentInstance):
    """
    Represents an instance of a Switch component.
    """
    def __init__(self, component: HttpComponent, interpreter: 'SwitchInterpreter'):
        super().__init__(component, interpreter)
        self.switch_component = SwitchComponent(component.name)
        self.client_events = {}
        self.server_events = {}

    def render_to_switch(self) -> SwitchComponent:
        """Render this component to a Switch component."""
        # Convert state to props
        for key, value in self.state.items():
            self.switch_component.set_prop(key, value)

        # Add client events
        for event, handler in self.client_events.items():
            self.switch_component.add_event(event, handler)

        return self.switch_component

    def add_client_event(self, event: str, handler: str) -> None:
        """Add a client-side event handler."""
        self.client_events[event] = handler
        self.switch_component.add_event(event, handler)

    def add_server_event(self, event: str, handler: str) -> None:
        """Add a server-side event handler."""
        self.server_events[event] = handler

    def handle_event(self, event: str, data: Any) -> Any:
        """Handle a server-side event."""
        if event in self.server_events:
            handler = self.server_events[event]
            if hasattr(self, handler):
                method = getattr(self, handler)
                return method(data)
        return None

class SwitchInterpreter(HttpInterpreter):
    """
    Mono language interpreter with support for the Switch frontend framework.
    """
    def __init__(self, use_ssr: bool = False, use_hmr: bool = False, use_kits: bool = True, debug: bool = False):
        super().__init__()
        self.switch_components: Dict[str, SwitchComponent] = {}
        self.switch_instances: Dict[str, SwitchComponentInstance] = {}
        self.switch_middleware = get_switch_middleware()
        self.use_ssr = use_ssr
        self.use_hmr = use_hmr
        self.use_kits = use_kits
        self.debug = debug
        self.hmr_watcher = None

        # Set debug mode for error handling
        set_debug_mode(debug)

        # Add the error middleware first (to catch errors in other middleware)
        self.error_middleware = get_error_middleware()
        self.http_server.use(self.error_middleware.handle)

        # Add the Switch middleware to the HTTP server
        self.http_server.use(self.switch_middleware.handle)

        # Add the SSR middleware if enabled
        if self.use_ssr:
            self.ssr_middleware = get_ssr_middleware()
            self.http_server.use(self.ssr_middleware.handle)

        # Add the HMR middleware if enabled
        if self.use_hmr:
            self.hmr_middleware = get_hmr_middleware()
            self.http_server.use(self.hmr_middleware.handle)

            # Start the HMR watcher
            self.hmr_watcher = start_hmr_watcher()

        # Add the Kit middleware if enabled
        if self.use_kits:
            self.kit_middleware = get_kit_middleware()
            self.kit_manager = get_kit_manager()
            self.http_server.use(self.kit_middleware.handle)

    def create_component_instance(self, component: HttpComponent) -> SwitchComponentInstance:
        """Create a Switch component instance."""
        instance = SwitchComponentInstance(component, self)

        # Store the instance
        if component.name not in self.instances:
            self.instances[component.name] = []
        self.instances[component.name].append(instance)

        # Store the Switch instance
        self.switch_instances[instance.id] = instance

        return instance

    def execute_method(self, method_body: str, instance: SwitchComponentInstance, args: List[Any] = None, initial_local_vars: Dict[str, Any] = None) -> Any:
        """Execute a method with Switch framework support."""
        # Check if this is a special Switch method
        if method_body.strip().startswith('switch.'):
            return self._execute_switch_method(method_body, instance, args, initial_local_vars)

        # Otherwise, use the standard method execution
        return super().execute_method(method_body, instance, args, initial_local_vars)

    def _execute_switch_method(self, method_body: str, instance: SwitchComponentInstance, args: List[Any], initial_local_vars: Dict[str, Any]) -> Any:
        """Execute a Switch method."""
        # Parse the method call
        match = re.match(r'switch\.(\w+)\((.*)\);?', method_body.strip())
        if not match:
            print(f"Error: Invalid Switch method call: {method_body}")
            return None

        method_name = match.group(1)
        args_str = match.group(2)

        # Parse arguments
        call_args = []
        if args_str:
            call_args = [self.evaluate_expression(arg.strip(), initial_local_vars or {}, instance) for arg in args_str.split(',')]

        # Call the appropriate method
        if method_name == 'render':
            return self._switch_render(instance, *call_args)
        elif method_name == 'clientEvent':
            return self._switch_client_event(instance, *call_args)
        elif method_name == 'serverEvent':
            return self._switch_server_event(instance, *call_args)
        elif method_name == 'component':
            return self._switch_component(instance, *call_args)
        else:
            print(f"Error: Unknown Switch method: {method_name}")
            return None

    def _switch_render(self, instance: SwitchComponentInstance, title: str = "Switch App", scripts: List[str] = None, styles: List[str] = None) -> str:
        """Render a Switch component to HTML."""
        # Get the current file path
        current_file = self.current_file

        # Create the component
        switch_component = instance.render_to_switch()

        # Get or create the Switch application
        app = get_switch_app()

        # Set the application name
        app.name = title

        # Set the root component
        app.set_root_component(switch_component)

        # Set SSR and HMR options
        app.use_ssr = self.use_ssr
        app.use_hmr = self.use_hmr
        app.debug = self.debug

        # Add custom scripts and styles
        if scripts:
            for script in scripts:
                app.add_script(script)

        if styles:
            for style in styles:
                app.add_style(style)

        # Check if kits are enabled
        if self.use_kits:
            # Add the SwitchUIKit loader script
            ui_kit = self.kit_manager.get_kit("SwitchUIKit")
            if ui_kit:
                loader_url = ui_kit.get_loader_url()
                if loader_url:
                    app.add_script(loader_url)

                # Add the SwitchUIKit CSS
                css_url = ui_kit.get_css_url()
                if css_url:
                    app.add_style(css_url)

        # Check if HMR is enabled
        if self.use_hmr:
            # Convert the component to an HMR component
            hmr_component = HMRComponent(switch_component.name, switch_component.props, switch_component.children)
            hmr_component.id = switch_component.id
            hmr_component.state = switch_component.state
            hmr_component.events = switch_component.events

            # Set the file path
            if current_file:
                hmr_component.set_file_path(current_file)

            # Register the component with the HMR middleware
            self.hmr_middleware.register_component(hmr_component)

            # Use the HMR component
            app.set_root_component(hmr_component)

        # Render the application
        html = app.render()

        return html

    def _switch_client_event(self, instance: SwitchComponentInstance, event: str, handler: str) -> None:
        """Add a client-side event handler."""
        instance.add_client_event(event, handler)

    def _switch_server_event(self, instance: SwitchComponentInstance, event: str, handler: str) -> None:
        """Add a server-side event handler."""
        instance.add_server_event(event, handler)

    def _switch_component(self, instance: SwitchComponentInstance, name: str, props: Dict[str, Any] = None) -> SwitchComponent:
        """Create a Switch component."""
        component = SwitchComponent(name, props)

        # Store the component
        self.switch_components[component.id] = component

        return component
