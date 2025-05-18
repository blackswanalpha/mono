"""
Mono Switch Kit - Kit integration for the Switch framework

This module provides kit integration for the Switch framework.
It allows kits to be loaded and used in Switch applications.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Callable, Set, Tuple, Union
from pathlib import Path
from .mono_switch import SwitchComponent, SwitchRenderer, SwitchMiddleware

class SwitchKit:
    """
    Represents a Switch kit.
    """
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.components = {}
        self.tools = {}
        self.config = {}
        
        # Load the kit configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load the kit configuration."""
        config_path = os.path.join(self.path, "kit.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
                
                # Load components
                if "components" in self.config:
                    self.components = self.config["components"]
                
                # Load tools
                if "tools" in self.config:
                    self.tools = self.config["tools"]
    
    def get_component_path(self, component_name: str) -> Optional[str]:
        """Get the path to a component."""
        if component_name in self.components:
            return os.path.join(self.path, self.components[component_name]["source_path"])
        return None
    
    def get_component_url(self, component_name: str) -> Optional[str]:
        """Get the URL to a component."""
        if component_name in self.components:
            source_path = self.components[component_name]["source_path"]
            return f"/kits/{self.name}/{source_path}"
        return None
    
    def get_loader_url(self) -> str:
        """Get the URL to the kit loader."""
        return f"/kits/{self.name}/loader.js"
    
    def get_css_url(self) -> str:
        """Get the URL to the kit CSS."""
        return f"/kits/{self.name}/switch-ui-kit.css"

class SwitchKitManager:
    """
    Manages Switch kits.
    """
    def __init__(self):
        self.kits = {}
        self.kit_paths = []
        
        # Add default kit paths
        self._add_default_kit_paths()
    
    def _add_default_kit_paths(self) -> None:
        """Add default kit paths."""
        # Add the kits directory in the current working directory
        cwd_kits_path = os.path.join(os.getcwd(), "kits")
        if os.path.exists(cwd_kits_path) and os.path.isdir(cwd_kits_path):
            self.kit_paths.append(cwd_kits_path)
        
        # Add the kits directory in the Mono installation directory
        mono_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        mono_kits_path = os.path.join(mono_dir, "kits")
        if os.path.exists(mono_kits_path) and os.path.isdir(mono_kits_path):
            self.kit_paths.append(mono_kits_path)
    
    def add_kit_path(self, path: str) -> None:
        """Add a kit path."""
        if os.path.exists(path) and os.path.isdir(path):
            self.kit_paths.append(path)
    
    def discover_kits(self) -> None:
        """Discover kits in the kit paths."""
        for kit_path in self.kit_paths:
            # Get all directories in the kit path
            for item in os.listdir(kit_path):
                item_path = os.path.join(kit_path, item)
                if os.path.isdir(item_path):
                    # Check if the directory contains a kit.json file
                    kit_json_path = os.path.join(item_path, "kit.json")
                    if os.path.exists(kit_json_path):
                        # Create a kit
                        kit = SwitchKit(item, item_path)
                        self.kits[item] = kit
    
    def get_kit(self, name: str) -> Optional[SwitchKit]:
        """Get a kit by name."""
        return self.kits.get(name)
    
    def get_all_kits(self) -> Dict[str, SwitchKit]:
        """Get all kits."""
        return self.kits
    
    def get_component_url(self, kit_name: str, component_name: str) -> Optional[str]:
        """Get the URL to a component."""
        kit = self.get_kit(kit_name)
        if kit:
            return kit.get_component_url(component_name)
        return None
    
    def get_loader_url(self, kit_name: str) -> Optional[str]:
        """Get the URL to a kit loader."""
        kit = self.get_kit(kit_name)
        if kit:
            return kit.get_loader_url()
        return None
    
    def get_css_url(self, kit_name: str) -> Optional[str]:
        """Get the URL to a kit CSS."""
        kit = self.get_kit(kit_name)
        if kit:
            return kit.get_css_url()
        return None

class SwitchKitMiddleware(SwitchMiddleware):
    """
    Middleware for serving Switch kits.
    """
    def __init__(self, app_name: str = "Switch App"):
        super().__init__(app_name)
        self.kit_manager = SwitchKitManager()
        
        # Discover kits
        self.kit_manager.discover_kits()
    
    def handle(self, req, res, next):
        """Handle a request."""
        # Check if the request is for a kit resource
        if req.path.startswith("/kits/"):
            # Extract the kit name and resource path
            path_parts = req.path.split("/")
            if len(path_parts) >= 3:
                kit_name = path_parts[2]
                resource_path = "/".join(path_parts[3:])
                
                # Get the kit
                kit = self.kit_manager.get_kit(kit_name)
                if kit:
                    # Serve the resource
                    resource_file_path = os.path.join(kit.path, resource_path)
                    if os.path.exists(resource_file_path) and os.path.isfile(resource_file_path):
                        # Determine content type
                        content_type = "text/plain"
                        if resource_file_path.endswith(".js"):
                            content_type = "application/javascript"
                        elif resource_file_path.endswith(".css"):
                            content_type = "text/css"
                        elif resource_file_path.endswith(".json"):
                            content_type = "application/json"
                        elif resource_file_path.endswith(".html"):
                            content_type = "text/html"
                        
                        # Read the file
                        with open(resource_file_path, "r") as f:
                            content = f.read()
                        
                        # Send the response
                        res.header("Content-Type", content_type)
                        res.text(content)
                        return
        
        # Call the next middleware
        next()

# Create a global instance of the kit middleware
kit_middleware = SwitchKitMiddleware()

def get_kit_middleware() -> SwitchKitMiddleware:
    """Get the global kit middleware instance."""
    return kit_middleware

def get_kit_manager() -> SwitchKitManager:
    """Get the global kit manager instance."""
    return kit_middleware.kit_manager
