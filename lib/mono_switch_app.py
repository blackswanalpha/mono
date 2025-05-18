"""
Mono Switch App - Application renderer for the Switch framework

This module provides a dedicated renderer for Switch applications.
It handles:
1. Application initialization
2. Component rendering
3. Asset management
4. Server-side rendering
5. Client-side hydration
"""

import os
import json
import re
import time
import hashlib
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from pathlib import Path
from .mono_http import Response, Request, HttpStatus
from .mono_switch import SwitchComponent, SwitchRenderer, SwitchMiddleware, get_switch_middleware
from .mono_switch_ssr import SSRComponent, SSRRenderer, get_ssr_middleware
from .mono_switch_hmr import HMRMiddleware, get_hmr_middleware
from .mono_switch_store import Store, create_store

class SwitchApp:
    """
    Represents a Switch application.
    """
    def __init__(self, 
                 name: str = "Switch App", 
                 root_component: Optional[SwitchComponent] = None,
                 use_ssr: bool = False,
                 use_hmr: bool = False,
                 debug: bool = False):
        self.name = name
        self.root_component = root_component
        self.use_ssr = use_ssr
        self.use_hmr = use_hmr
        self.debug = debug
        self.scripts: List[str] = []
        self.styles: List[str] = []
        self.routes: Dict[str, Callable] = {}
        self.store: Optional[Store] = None
        self.static_dir: Optional[str] = None
        self.build_dir: Optional[str] = None
        
        # Add default scripts and styles
        self.add_script("/switch/switch.js")
        self.add_script("/switch/store.js")
        self.add_script("/switch/components.js")
        self.add_style("/switch/switch.css")
        
        # Add SSR script if enabled
        if use_ssr:
            self.add_script("/switch/hydrate.js")
            
        # Add HMR script if enabled
        if use_hmr:
            self.add_script("/switch/hmr.js")

    def set_root_component(self, component: SwitchComponent) -> None:
        """Set the root component for the application."""
        self.root_component = component
        
    def add_script(self, script: str) -> None:
        """Add a script to the application."""
        if script not in self.scripts:
            self.scripts.append(script)
            
    def add_style(self, style: str) -> None:
        """Add a style to the application."""
        if style not in self.styles:
            self.styles.append(style)
            
    def set_store(self, store: Store) -> None:
        """Set the global store for the application."""
        self.store = store
        
    def set_static_dir(self, directory: str) -> None:
        """Set the directory for static assets."""
        self.static_dir = directory
        
    def set_build_dir(self, directory: str) -> None:
        """Set the directory for build output."""
        self.build_dir = directory
        
    def add_route(self, path: str, handler: Callable) -> None:
        """Add a route to the application."""
        self.routes[path] = handler
        
    def render(self) -> str:
        """Render the application to HTML."""
        if not self.root_component:
            raise ValueError("No root component set for the application")
            
        # Create the appropriate renderer
        if self.use_ssr:
            renderer = SSRRenderer(self.name, self.scripts, self.styles, self.store)
            return renderer.render(self.root_component)
        else:
            renderer = SwitchRenderer(self.name, self.scripts, self.styles)
            return renderer.render(self.root_component)
            
    def configure_http_server(self, http_server) -> None:
        """Configure the HTTP server for the application."""
        # Add routes
        for path, handler in self.routes.items():
            http_server.get(path, handler)
            
        # Add static file handling if a static directory is set
        if self.static_dir:
            http_server.get("/static/(.*)", self._handle_static_file)
            
    def _handle_static_file(self, req: Request, res: Response) -> None:
        """Handle a request for a static file."""
        if not self.static_dir:
            res.status(HttpStatus.NOT_FOUND).text("Static directory not configured")
            return
            
        # Extract the file path from the URL
        match = re.match(r"/static/(.*)", req.path)
        if not match:
            res.status(HttpStatus.NOT_FOUND).text("Invalid static file path")
            return
            
        file_path = match.group(1)
        full_path = os.path.join(self.static_dir, file_path)
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            res.status(HttpStatus.NOT_FOUND).text(f"File not found: {file_path}")
            return
            
        # Determine the content type
        content_type = self._get_content_type(file_path)
        
        # Read the file
        with open(full_path, "rb") as f:
            content = f.read()
            
        # Send the response
        res.header("Content-Type", content_type)
        res.binary(content)
        
    def _get_content_type(self, file_path: str) -> str:
        """Get the content type for a file."""
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".eot": "application/vnd.ms-fontobject",
            ".otf": "font/otf",
        }
        
        return content_types.get(ext, "application/octet-stream")
        
    def build(self, output_dir: str) -> None:
        """Build the application for production."""
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Render the application
        html = self.render()
        
        # Write the HTML to the output directory
        with open(os.path.join(output_dir, "index.html"), "w") as f:
            f.write(html)
            
        # Copy static assets if a static directory is set
        if self.static_dir:
            static_output_dir = os.path.join(output_dir, "static")
            os.makedirs(static_output_dir, exist_ok=True)
            
            # Copy all files from the static directory
            for root, _, files in os.walk(self.static_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, self.static_dir)
                    dst_path = os.path.join(static_output_dir, rel_path)
                    
                    # Create the destination directory if it doesn't exist
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Copy the file
                    with open(src_path, "rb") as src_f, open(dst_path, "wb") as dst_f:
                        dst_f.write(src_f.read())

# Global instance
_switch_app = None

def get_switch_app() -> SwitchApp:
    """Get the global Switch application instance."""
    global _switch_app
    if _switch_app is None:
        _switch_app = SwitchApp()
    return _switch_app

def set_switch_app(app: SwitchApp) -> None:
    """Set the global Switch application instance."""
    global _switch_app
    _switch_app = app
