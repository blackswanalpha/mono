"""
Mono Switch HMR - Hot Module Replacement for the Switch framework

This module provides hot module replacement capabilities for the Switch framework.
It allows components to be updated without reloading the page.
"""

import os
import json
import re
import time
import threading
import hashlib
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .mono_http import Response, Request, HttpStatus
from .mono_switch import SwitchComponent, SwitchRenderer, SwitchMiddleware, get_switch_middleware

class HMRComponent(SwitchComponent):
    """
    Represents a hot-reloadable Switch component.
    """
    def __init__(self, name: str, props: Dict[str, Any] = None, children: List['HMRComponent'] = None):
        super().__init__(name, props, children)
        self.file_path = ""
        self.file_hash = ""
        self.hmr_id = f"switch-hmr-{self.id}"
    
    def set_file_path(self, file_path: str) -> None:
        """Set the file path for the component."""
        self.file_path = file_path
        self.update_file_hash()
    
    def update_file_hash(self) -> None:
        """Update the file hash."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                content = f.read()
                self.file_hash = hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary for serialization."""
        data = super().to_dict()
        data['hmr_id'] = self.hmr_id
        data['file_path'] = self.file_path
        data['file_hash'] = self.file_hash
        return data

class HMRFileHandler(FileSystemEventHandler):
    """
    Handler for file system events.
    """
    def __init__(self, hmr_middleware):
        self.hmr_middleware = hmr_middleware
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        # Check if the file is a Mono file
        if event.src_path.endswith('.mono'):
            self.hmr_middleware.file_changed(event.src_path)

class HMRMiddleware(SwitchMiddleware):
    """
    Middleware for hot module replacement of Switch components.
    """
    def __init__(self, app_name: str = "Switch App"):
        super().__init__(app_name)
        self.hmr_components: Dict[str, HMRComponent] = {}
        self.file_watchers: Dict[str, Any] = {}
        self.observer = None
        self.watched_paths: Set[str] = set()
    
    def start(self) -> None:
        """Start the HMR middleware."""
        if self.observer is None:
            self.observer = Observer()
            self.observer.start()
    
    def stop(self) -> None:
        """Stop the HMR middleware."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
    
    def watch_file(self, file_path: str) -> None:
        """Watch a file for changes."""
        if file_path in self.watched_paths:
            return
        
        # Get the directory containing the file
        directory = os.path.dirname(os.path.abspath(file_path))
        
        # Create a handler for the directory
        handler = HMRFileHandler(self)
        
        # Schedule the handler
        self.observer.schedule(handler, directory, recursive=False)
        
        # Add the file to the watched paths
        self.watched_paths.add(file_path)
    
    def register_component(self, component: HMRComponent) -> None:
        """Register a component for hot module replacement."""
        self.hmr_components[component.id] = component
        
        # Watch the component's file
        if component.file_path:
            self.watch_file(component.file_path)
    
    def file_changed(self, file_path: str) -> None:
        """Handle a file change event."""
        # Find components that use this file
        components_to_update = []
        for component_id, component in self.hmr_components.items():
            if component.file_path == file_path:
                # Update the file hash
                component.update_file_hash()
                components_to_update.append(component)
        
        # Notify clients about the changes
        if components_to_update:
            print(f"HMR: File changed: {file_path}")
            print(f"HMR: Components to update: {len(components_to_update)}")
            
            # Wait a short time to ensure the file is fully written
            time.sleep(0.1)
    
    def _handle_switch_api(self, req: Request, res: Response) -> None:
        """Handle a Switch API request."""
        # Get the API endpoint
        endpoint = req.path[len("/api/switch/"):]
        
        # Handle the endpoint
        if endpoint == "state":
            self._handle_state_update(req, res)
        elif endpoint == "event":
            self._handle_event(req, res)
        elif endpoint == "hmr":
            self._handle_hmr_request(req, res)
        else:
            res.status(HttpStatus.NOT_FOUND).text("API endpoint not found")
    
    def _handle_hmr_request(self, req: Request, res: Response) -> None:
        """Handle an HMR request."""
        # Get the request body
        data = req.get_json()
        if not data:
            res.status(HttpStatus.BAD_REQUEST).text("Invalid request body")
            return
        
        # Get the component IDs
        component_ids = data.get('componentIds', [])
        if not component_ids:
            res.status(HttpStatus.BAD_REQUEST).text("Missing componentIds")
            return
        
        # Get the components
        components = []
        for component_id in component_ids:
            if component_id in self.hmr_components:
                components.append(self.hmr_components[component_id])
        
        # Check if any components need to be updated
        updates = []
        for component in components:
            # Check if the file has changed
            if os.path.exists(component.file_path):
                with open(component.file_path, "r") as f:
                    content = f.read()
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                
                if file_hash != component.file_hash:
                    # Update the component
                    component.file_hash = file_hash
                    updates.append({
                        'id': component.id,
                        'hash': file_hash
                    })
        
        # Send the response
        res.json({
            'updates': updates
        })

class HMRWatcher(threading.Thread):
    """
    Thread for watching files for changes.
    """
    def __init__(self, hmr_middleware: HMRMiddleware):
        super().__init__()
        self.hmr_middleware = hmr_middleware
        self.running = False
    
    def run(self):
        """Run the watcher thread."""
        self.running = True
        self.hmr_middleware.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.hmr_middleware.stop()
    
    def stop(self):
        """Stop the watcher thread."""
        self.running = False

# Create a global instance of the HMR middleware
hmr_middleware = HMRMiddleware()

def get_hmr_middleware() -> HMRMiddleware:
    """Get the global HMR middleware instance."""
    return hmr_middleware

def start_hmr_watcher() -> HMRWatcher:
    """Start the HMR watcher thread."""
    watcher = HMRWatcher(hmr_middleware)
    watcher.daemon = True
    watcher.start()
    return watcher
