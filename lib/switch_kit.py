"""
Switch Kit Manager - Manage UI kits for Switch applications

This module provides functions for managing UI kits in Switch applications.
"""

import os
import sys
import json
import re
import shutil
import tempfile
import zipfile
import tarfile
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Default registry URL
DEFAULT_REGISTRY = "https://registry.switchframework.org/kits"

# Default cache directory
DEFAULT_CACHE_DIR = ".switch/kits"

class KitManager:
    """Kit manager for Switch applications."""
    
    def __init__(self, app_dir: str = ".", registry: str = DEFAULT_REGISTRY, cache_dir: str = DEFAULT_CACHE_DIR):
        """Initialize the kit manager."""
        self.app_dir = os.path.abspath(app_dir)
        self.registry = registry
        self.cache_dir = os.path.join(self.app_dir, cache_dir)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from mono.config or app.json."""
        config = {}
        
        # Try to load mono.config
        mono_config_path = os.path.join(self.app_dir, "mono.config")
        if os.path.isfile(mono_config_path):
            try:
                with open(mono_config_path, "r") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Warning: Error reading mono.config: {str(e)}")
        
        # Try to load app.json
        app_json_path = os.path.join(self.app_dir, "app.json")
        if os.path.isfile(app_json_path):
            try:
                with open(app_json_path, "r") as f:
                    app_json = json.load(f)
                    
                    # Merge dependencies
                    if "dependencies" in app_json:
                        config["dependencies"] = app_json["dependencies"]
            except Exception as e:
                print(f"Warning: Error reading app.json: {str(e)}")
        
        return config
    
    def _save_config(self) -> None:
        """Save configuration to mono.config and app.json."""
        # Save to mono.config
        mono_config_path = os.path.join(self.app_dir, "mono.config")
        if os.path.isfile(mono_config_path):
            try:
                with open(mono_config_path, "r") as f:
                    mono_config = json.load(f)
                
                # Update kits section
                if "kits" not in mono_config:
                    mono_config["kits"] = {}
                
                mono_config["kits"]["registry"] = self.registry
                mono_config["kits"]["cache"] = self.cache_dir
                
                with open(mono_config_path, "w") as f:
                    json.dump(mono_config, f, indent=2)
            except Exception as e:
                print(f"Warning: Error updating mono.config: {str(e)}")
        
        # Save to app.json
        app_json_path = os.path.join(self.app_dir, "app.json")
        if os.path.isfile(app_json_path):
            try:
                with open(app_json_path, "r") as f:
                    app_json = json.load(f)
                
                # Update dependencies
                if "dependencies" in self.config:
                    app_json["dependencies"] = self.config["dependencies"]
                
                with open(app_json_path, "w") as f:
                    json.dump(app_json, f, indent=2)
            except Exception as e:
                print(f"Warning: Error updating app.json: {str(e)}")
    
    def list(self) -> List[Dict[str, Any]]:
        """List installed kits."""
        kits = []
        
        # Get dependencies from config
        dependencies = {}
        if "dependencies" in self.config:
            dependencies.update(self.config["dependencies"])
        
        # Get kit details
        for name, version in dependencies.items():
            # Check if this is a kit
            if name.endswith("Kit"):
                # Get kit details
                kit = self.get(name)
                if kit:
                    kits.append(kit)
        
        return kits
    
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get kit details."""
        # Check if kit is installed
        kit_dir = os.path.join(self.app_dir, "switch.settings", "kits", name)
        if not os.path.isdir(kit_dir):
            return None
        
        # Get kit version
        version = "unknown"
        if "dependencies" in self.config and name in self.config["dependencies"]:
            version = self.config["dependencies"][name]
        
        # Parse kit file
        kit_file = os.path.join(kit_dir, f"{name}.kit")
        if os.path.isfile(kit_file):
            try:
                with open(kit_file, "r") as f:
                    content = f.read()
                    
                    # Extract kit details
                    kit = {
                        "name": name,
                        "version": version,
                        "description": self._extract_kit_property(content, "description"),
                        "author": self._extract_kit_property(content, "author"),
                        "license": self._extract_kit_property(content, "license"),
                        "dependencies": self._extract_kit_dependencies(content),
                        "components": self._extract_kit_components(content),
                        "installed": True
                    }
                    
                    return kit
            except Exception as e:
                print(f"Warning: Error parsing kit file: {str(e)}")
        
        # Return basic kit details
        return {
            "name": name,
            "version": version,
            "description": "",
            "author": "",
            "license": "",
            "dependencies": {},
            "components": [],
            "installed": True
        }
    
    def _extract_kit_property(self, content: str, property_name: str) -> str:
        """Extract a property from a kit file."""
        pattern = rf'{property_name}\s+"([^"]+)"'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return ""
    
    def _extract_kit_dependencies(self, content: str) -> Dict[str, str]:
        """Extract dependencies from a kit file."""
        dependencies = {}
        
        # Find the depends block
        depends_match = re.search(r'depends\s+{([^}]+)}', content, re.DOTALL)
        if depends_match:
            depends_block = depends_match.group(1)
            
            # Extract dependencies
            for line in depends_block.split('\n'):
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == "version":
                        name = parts[0]
                        version = parts[2].strip('"')
                        dependencies[name] = version
        
        return dependencies
    
    def _extract_kit_components(self, content: str) -> List[str]:
        """Extract components from a kit file."""
        components = []
        
        # Find the components block
        components_match = re.search(r'components\s+{([^}]+)}', content, re.DOTALL)
        if components_match:
            components_block = components_match.group(1)
            
            # Extract components
            for line in components_block.split('\n'):
                line = line.strip()
                if line and not line.startswith("//"):
                    components.append(line)
        
        return components
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for kits in the registry."""
        try:
            # Make request to registry
            response = requests.get(f"{self.registry}/search?q={query}")
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Mark installed kits
            installed_kits = self.list()
            installed_names = [kit["name"] for kit in installed_kits]
            
            for kit in data:
                kit["installed"] = kit["name"] in installed_names
            
            return data
        except Exception as e:
            print(f"Error searching for kits: {str(e)}")
            return []
    
    def install(self, name: str, version: Optional[str] = None) -> bool:
        """Install a kit."""
        try:
            # Determine version to install
            if not version:
                # Get latest version
                response = requests.get(f"{self.registry}/{name}/latest")
                response.raise_for_status()
                version = response.json()["version"]
            
            # Download kit
            kit_url = f"{self.registry}/{name}/{version}"
            response = requests.get(kit_url)
            response.raise_for_status()
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save kit to temporary file
                kit_file = os.path.join(temp_dir, f"{name}-{version}.tgz")
                with open(kit_file, "wb") as f:
                    f.write(response.content)
                
                # Extract kit
                with tarfile.open(kit_file, "r:gz") as tar:
                    tar.extractall(temp_dir)
                
                # Install kit
                kit_dir = os.path.join(self.app_dir, "switch.settings", "kits", name)
                os.makedirs(kit_dir, exist_ok=True)
                
                # Copy kit files
                kit_dir_src = os.path.join(temp_dir, "kit")
                for item in os.listdir(kit_dir_src):
                    src = os.path.join(kit_dir_src, item)
                    dst = os.path.join(kit_dir, item)
                    
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            
            # Update configuration
            if "dependencies" not in self.config:
                self.config["dependencies"] = {}
            self.config["dependencies"][name] = version
            
            # Save configuration
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error installing kit: {str(e)}")
            return False
    
    def uninstall(self, name: str) -> bool:
        """Uninstall a kit."""
        try:
            # Check if kit is installed
            kit_dir = os.path.join(self.app_dir, "switch.settings", "kits", name)
            if not os.path.isdir(kit_dir):
                print(f"Kit {name} is not installed")
                return False
            
            # Remove kit directory
            shutil.rmtree(kit_dir)
            
            # Update configuration
            if "dependencies" in self.config and name in self.config["dependencies"]:
                del self.config["dependencies"][name]
            
            # Save configuration
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error uninstalling kit: {str(e)}")
            return False
    
    def publish(self, kit_path: str) -> bool:
        """Publish a kit to the registry."""
        try:
            # Check if kit file exists
            if not os.path.isfile(kit_path):
                print(f"Kit file not found: {kit_path}")
                return False
            
            # Read kit file
            with open(kit_path, "r") as f:
                content = f.read()
            
            # Extract kit details
            kit_name = self._extract_kit_name(content)
            kit_version = self._extract_kit_property(content, "version")
            
            if not kit_name or not kit_version:
                print("Invalid kit file: missing name or version")
                return False
            
            # Create kit directory
            kit_dir = os.path.join(tempfile.gettempdir(), f"{kit_name}-{kit_version}")
            os.makedirs(kit_dir, exist_ok=True)
            
            # Copy kit file
            shutil.copy2(kit_path, os.path.join(kit_dir, f"{kit_name}.kit"))
            
            # Create kit.json
            kit_json = {
                "name": kit_name,
                "version": kit_version,
                "description": self._extract_kit_property(content, "description"),
                "author": self._extract_kit_property(content, "author"),
                "license": self._extract_kit_property(content, "license"),
                "dependencies": self._extract_kit_dependencies(content),
                "components": self._extract_kit_components(content)
            }
            
            with open(os.path.join(kit_dir, "kit.json"), "w") as f:
                json.dump(kit_json, f, indent=2)
            
            # Create tarball
            tarball_path = os.path.join(tempfile.gettempdir(), f"{kit_name}-{kit_version}.tgz")
            with tarfile.open(tarball_path, "w:gz") as tar:
                tar.add(kit_dir, arcname="kit")
            
            # Upload kit
            with open(tarball_path, "rb") as f:
                response = requests.post(
                    f"{self.registry}/publish",
                    files={"kit": f},
                    data={"name": kit_name, "version": kit_version}
                )
                response.raise_for_status()
            
            # Clean up
            shutil.rmtree(kit_dir)
            os.remove(tarball_path)
            
            return True
        except Exception as e:
            print(f"Error publishing kit: {str(e)}")
            return False
    
    def _extract_kit_name(self, content: str) -> str:
        """Extract the kit name from a kit file."""
        pattern = r'kit\s+([a-zA-Z0-9_-]+)\s+{'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return ""

def install_command(args: List[str]) -> int:
    """Install a kit."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Install a kit")
    parser.add_argument("name", help="Kit name")
    parser.add_argument("--version", help="Kit version")
    parser.add_argument("--registry", help="Kit registry URL")
    parser.add_argument("--cache", help="Cache directory")
    
    parsed_args = parser.parse_args(args)
    
    # Create kit manager
    registry = parsed_args.registry or DEFAULT_REGISTRY
    cache_dir = parsed_args.cache or DEFAULT_CACHE_DIR
    
    kit_manager = KitManager(registry=registry, cache_dir=cache_dir)
    
    # Install kit
    success = kit_manager.install(parsed_args.name, parsed_args.version)
    
    return 0 if success else 1

def uninstall_command(args: List[str]) -> int:
    """Uninstall a kit."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Uninstall a kit")
    parser.add_argument("name", help="Kit name")
    
    parsed_args = parser.parse_args(args)
    
    # Create kit manager
    kit_manager = KitManager()
    
    # Uninstall kit
    success = kit_manager.uninstall(parsed_args.name)
    
    return 0 if success else 1

def list_command(args: List[str]) -> int:
    """List installed kits."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="List installed kits")
    
    parsed_args = parser.parse_args(args)
    
    # Create kit manager
    kit_manager = KitManager()
    
    # List kits
    kits = kit_manager.list()
    
    # Print kits
    if kits:
        print("Installed kits:")
        for kit in kits:
            print(f"  {kit['name']}@{kit['version']} - {kit['description']}")
    else:
        print("No kits installed")
    
    return 0

def search_command(args: List[str]) -> int:
    """Search for kits."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Search for kits")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--registry", help="Kit registry URL")
    
    parsed_args = parser.parse_args(args)
    
    # Create kit manager
    registry = parsed_args.registry or DEFAULT_REGISTRY
    kit_manager = KitManager(registry=registry)
    
    # Search kits
    kits = kit_manager.search(parsed_args.query)
    
    # Print kits
    if kits:
        print(f"Search results for '{parsed_args.query}':")
        for kit in kits:
            installed = " (installed)" if kit.get("installed") else ""
            print(f"  {kit['name']}@{kit['version']}{installed} - {kit['description']}")
    else:
        print(f"No kits found for '{parsed_args.query}'")
    
    return 0

def publish_command(args: List[str]) -> int:
    """Publish a kit."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Publish a kit")
    parser.add_argument("kit", help="Kit file path")
    parser.add_argument("--registry", help="Kit registry URL")
    
    parsed_args = parser.parse_args(args)
    
    # Create kit manager
    registry = parsed_args.registry or DEFAULT_REGISTRY
    kit_manager = KitManager(registry=registry)
    
    # Publish kit
    success = kit_manager.publish(parsed_args.kit)
    
    return 0 if success else 1
