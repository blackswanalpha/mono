"""
Switch Package Manager - Manage packages for Switch applications

This module provides functions for managing packages in Switch applications.
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
DEFAULT_REGISTRY = "https://registry.switchframework.org"

# Default cache directory
DEFAULT_CACHE_DIR = ".switch/packages"

class PackageManager:
    """Package manager for Switch applications."""
    
    def __init__(self, app_dir: str = ".", registry: str = DEFAULT_REGISTRY, cache_dir: str = DEFAULT_CACHE_DIR):
        """Initialize the package manager."""
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
                    
                    # Merge devDependencies
                    if "devDependencies" in app_json:
                        config["devDependencies"] = app_json["devDependencies"]
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
                
                # Update packages section
                if "packages" not in mono_config:
                    mono_config["packages"] = {}
                
                mono_config["packages"]["registry"] = self.registry
                mono_config["packages"]["cache"] = self.cache_dir
                
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
                
                # Update devDependencies
                if "devDependencies" in self.config:
                    app_json["devDependencies"] = self.config["devDependencies"]
                
                with open(app_json_path, "w") as f:
                    json.dump(app_json, f, indent=2)
            except Exception as e:
                print(f"Warning: Error updating app.json: {str(e)}")
    
    def list(self, dev: bool = False) -> List[Dict[str, Any]]:
        """List installed packages."""
        packages = []
        
        # Get dependencies from config
        dependencies = {}
        if "dependencies" in self.config:
            dependencies.update(self.config["dependencies"])
        
        # Add devDependencies if requested
        if dev and "devDependencies" in self.config:
            dependencies.update(self.config["devDependencies"])
        
        # Get package details
        for name, version in dependencies.items():
            # Get package details
            package = self.get(name)
            if package:
                packages.append(package)
        
        return packages
    
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get package details."""
        # Check if package is installed
        pkg_dir = os.path.join(self.app_dir, "switch.settings", "pkgs", name)
        if not os.path.isdir(pkg_dir):
            return None
        
        # Get package version
        version = "unknown"
        if "dependencies" in self.config and name in self.config["dependencies"]:
            version = self.config["dependencies"][name]
        elif "devDependencies" in self.config and name in self.config["devDependencies"]:
            version = self.config["devDependencies"][name]
        
        # Parse package file
        pkg_file = os.path.join(pkg_dir, f"{name}.pkg")
        if os.path.isfile(pkg_file):
            try:
                with open(pkg_file, "r") as f:
                    content = f.read()
                    
                    # Extract package details
                    package = {
                        "name": name,
                        "version": version,
                        "description": self._extract_package_property(content, "description"),
                        "author": self._extract_package_property(content, "author"),
                        "license": self._extract_package_property(content, "license"),
                        "dependencies": self._extract_package_dependencies(content),
                        "installed": True
                    }
                    
                    return package
            except Exception as e:
                print(f"Warning: Error parsing package file: {str(e)}")
        
        # Return basic package details
        return {
            "name": name,
            "version": version,
            "description": "",
            "author": "",
            "license": "",
            "dependencies": {},
            "installed": True
        }
    
    def _extract_package_property(self, content: str, property_name: str) -> str:
        """Extract a property from a package file."""
        pattern = rf'{property_name}\s+"([^"]+)"'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return ""
    
    def _extract_package_dependencies(self, content: str) -> Dict[str, str]:
        """Extract dependencies from a package file."""
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
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages in the registry."""
        try:
            # Make request to registry
            response = requests.get(f"{self.registry}/search?q={query}")
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Mark installed packages
            installed_packages = self.list(dev=True)
            installed_names = [pkg["name"] for pkg in installed_packages]
            
            for package in data:
                package["installed"] = package["name"] in installed_names
            
            return data
        except Exception as e:
            print(f"Error searching for packages: {str(e)}")
            return []
    
    def install(self, name: str, version: Optional[str] = None, dev: bool = False) -> bool:
        """Install a package."""
        try:
            # Determine version to install
            if not version:
                # Get latest version
                response = requests.get(f"{self.registry}/{name}/latest")
                response.raise_for_status()
                version = response.json()["version"]
            
            # Download package
            package_url = f"{self.registry}/{name}/{version}"
            response = requests.get(package_url)
            response.raise_for_status()
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save package to temporary file
                package_file = os.path.join(temp_dir, f"{name}-{version}.tgz")
                with open(package_file, "wb") as f:
                    f.write(response.content)
                
                # Extract package
                with tarfile.open(package_file, "r:gz") as tar:
                    tar.extractall(temp_dir)
                
                # Install package
                pkg_dir = os.path.join(self.app_dir, "switch.settings", "pkgs", name)
                os.makedirs(pkg_dir, exist_ok=True)
                
                # Copy package files
                package_dir = os.path.join(temp_dir, "package")
                for item in os.listdir(package_dir):
                    src = os.path.join(package_dir, item)
                    dst = os.path.join(pkg_dir, item)
                    
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            
            # Update configuration
            if dev:
                if "devDependencies" not in self.config:
                    self.config["devDependencies"] = {}
                self.config["devDependencies"][name] = version
            else:
                if "dependencies" not in self.config:
                    self.config["dependencies"] = {}
                self.config["dependencies"][name] = version
            
            # Save configuration
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error installing package: {str(e)}")
            return False
    
    def uninstall(self, name: str) -> bool:
        """Uninstall a package."""
        try:
            # Check if package is installed
            pkg_dir = os.path.join(self.app_dir, "switch.settings", "pkgs", name)
            if not os.path.isdir(pkg_dir):
                print(f"Package {name} is not installed")
                return False
            
            # Remove package directory
            shutil.rmtree(pkg_dir)
            
            # Update configuration
            if "dependencies" in self.config and name in self.config["dependencies"]:
                del self.config["dependencies"][name]
            
            if "devDependencies" in self.config and name in self.config["devDependencies"]:
                del self.config["devDependencies"][name]
            
            # Save configuration
            self._save_config()
            
            return True
        except Exception as e:
            print(f"Error uninstalling package: {str(e)}")
            return False
    
    def publish(self, package_path: str) -> bool:
        """Publish a package to the registry."""
        try:
            # Check if package file exists
            if not os.path.isfile(package_path):
                print(f"Package file not found: {package_path}")
                return False
            
            # Read package file
            with open(package_path, "r") as f:
                content = f.read()
            
            # Extract package details
            package_name = self._extract_package_name(content)
            package_version = self._extract_package_property(content, "version")
            
            if not package_name or not package_version:
                print("Invalid package file: missing name or version")
                return False
            
            # Create package directory
            package_dir = os.path.join(tempfile.gettempdir(), f"{package_name}-{package_version}")
            os.makedirs(package_dir, exist_ok=True)
            
            # Copy package file
            shutil.copy2(package_path, os.path.join(package_dir, f"{package_name}.pkg"))
            
            # Create package.json
            package_json = {
                "name": package_name,
                "version": package_version,
                "description": self._extract_package_property(content, "description"),
                "author": self._extract_package_property(content, "author"),
                "license": self._extract_package_property(content, "license"),
                "dependencies": self._extract_package_dependencies(content)
            }
            
            with open(os.path.join(package_dir, "package.json"), "w") as f:
                json.dump(package_json, f, indent=2)
            
            # Create tarball
            tarball_path = os.path.join(tempfile.gettempdir(), f"{package_name}-{package_version}.tgz")
            with tarfile.open(tarball_path, "w:gz") as tar:
                tar.add(package_dir, arcname="package")
            
            # Upload package
            with open(tarball_path, "rb") as f:
                response = requests.post(
                    f"{self.registry}/publish",
                    files={"package": f},
                    data={"name": package_name, "version": package_version}
                )
                response.raise_for_status()
            
            # Clean up
            shutil.rmtree(package_dir)
            os.remove(tarball_path)
            
            return True
        except Exception as e:
            print(f"Error publishing package: {str(e)}")
            return False
    
    def _extract_package_name(self, content: str) -> str:
        """Extract the package name from a package file."""
        pattern = r'package\s+([a-zA-Z0-9_-]+)\s+{'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        return ""

def install_command(args: List[str]) -> int:
    """Install a package."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Install a package")
    parser.add_argument("name", help="Package name")
    parser.add_argument("--version", help="Package version")
    parser.add_argument("--dev", action="store_true", help="Install as a development dependency")
    parser.add_argument("--registry", help="Package registry URL")
    parser.add_argument("--cache", help="Cache directory")
    
    parsed_args = parser.parse_args(args)
    
    # Create package manager
    registry = parsed_args.registry or DEFAULT_REGISTRY
    cache_dir = parsed_args.cache or DEFAULT_CACHE_DIR
    
    pkg_manager = PackageManager(registry=registry, cache_dir=cache_dir)
    
    # Install package
    success = pkg_manager.install(parsed_args.name, parsed_args.version, parsed_args.dev)
    
    return 0 if success else 1

def uninstall_command(args: List[str]) -> int:
    """Uninstall a package."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Uninstall a package")
    parser.add_argument("name", help="Package name")
    
    parsed_args = parser.parse_args(args)
    
    # Create package manager
    pkg_manager = PackageManager()
    
    # Uninstall package
    success = pkg_manager.uninstall(parsed_args.name)
    
    return 0 if success else 1

def list_command(args: List[str]) -> int:
    """List installed packages."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="List installed packages")
    parser.add_argument("--dev", action="store_true", help="Include development dependencies")
    
    parsed_args = parser.parse_args(args)
    
    # Create package manager
    pkg_manager = PackageManager()
    
    # List packages
    packages = pkg_manager.list(parsed_args.dev)
    
    # Print packages
    if packages:
        print("Installed packages:")
        for package in packages:
            print(f"  {package['name']}@{package['version']} - {package['description']}")
    else:
        print("No packages installed")
    
    return 0

def search_command(args: List[str]) -> int:
    """Search for packages."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Search for packages")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--registry", help="Package registry URL")
    
    parsed_args = parser.parse_args(args)
    
    # Create package manager
    registry = parsed_args.registry or DEFAULT_REGISTRY
    pkg_manager = PackageManager(registry=registry)
    
    # Search packages
    packages = pkg_manager.search(parsed_args.query)
    
    # Print packages
    if packages:
        print(f"Search results for '{parsed_args.query}':")
        for package in packages:
            installed = " (installed)" if package.get("installed") else ""
            print(f"  {package['name']}@{package['version']}{installed} - {package['description']}")
    else:
        print(f"No packages found for '{parsed_args.query}'")
    
    return 0

def publish_command(args: List[str]) -> int:
    """Publish a package."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Publish a package")
    parser.add_argument("package", help="Package file path")
    parser.add_argument("--registry", help="Package registry URL")
    
    parsed_args = parser.parse_args(args)
    
    # Create package manager
    registry = parsed_args.registry or DEFAULT_REGISTRY
    pkg_manager = PackageManager(registry=registry)
    
    # Publish package
    success = pkg_manager.publish(parsed_args.package)
    
    return 0 if success else 1
