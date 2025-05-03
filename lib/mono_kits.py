"""
Mono Kits - Pre-baked component suites for the Mono language

This module provides support for:
1. Kit Definition: Define collections of components, tools, and utilities
2. Kit Versioning: Semantic versioning for backward compatibility
3. Kit Registry: Central repository for discovering kits
4. Kit Tools: CLI generators, linters, or debuggers bundled with kits
"""

import os
import re
import json
import shutil
import importlib
import semver
from typing import Dict, List, Any, Optional, Set, Tuple, Union

class KitComponent:
    """
    Represents a component in a kit.
    """
    def __init__(self, name: str, source_path: str, description: str = ""):
        self.name = name
        self.source_path = source_path
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "source_path": self.source_path,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KitComponent':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            source_path=data["source_path"],
            description=data.get("description", "")
        )

class KitTool:
    """
    Represents a tool in a kit.
    """
    def __init__(self, name: str, command: str, description: str = ""):
        self.name = name
        self.command = command
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "command": self.command,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KitTool':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            command=data["command"],
            description=data.get("description", "")
        )

class Kit:
    """
    Represents a kit (collection of components, tools, and utilities).
    """
    def __init__(self, name: str, version: str, description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.components: Dict[str, KitComponent] = {}
        self.tools: Dict[str, KitTool] = {}
        self.dependencies: Dict[str, str] = {}  # Kit name -> version requirement
    
    def add_component(self, component: KitComponent) -> None:
        """Add a component to the kit."""
        self.components[component.name] = component
    
    def add_tool(self, tool: KitTool) -> None:
        """Add a tool to the kit."""
        self.tools[tool.name] = tool
    
    def add_dependency(self, kit_name: str, version_requirement: str) -> None:
        """Add a dependency on another kit."""
        self.dependencies[kit_name] = version_requirement
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "components": {name: comp.to_dict() for name, comp in self.components.items()},
            "tools": {name: tool.to_dict() for name, tool in self.tools.items()},
            "dependencies": self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Kit':
        """Create from dictionary."""
        kit = cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", "")
        )
        
        # Add components
        for name, comp_data in data.get("components", {}).items():
            kit.add_component(KitComponent.from_dict(comp_data))
        
        # Add tools
        for name, tool_data in data.get("tools", {}).items():
            kit.add_tool(KitTool.from_dict(tool_data))
        
        # Add dependencies
        for dep_name, dep_version in data.get("dependencies", {}).items():
            kit.add_dependency(dep_name, dep_version)
        
        return kit
    
    def save(self, directory: str) -> None:
        """Save the kit to a directory."""
        # Create the kit directory if it doesn't exist
        kit_dir = os.path.join(directory, self.name)
        os.makedirs(kit_dir, exist_ok=True)
        
        # Save the kit metadata
        with open(os.path.join(kit_dir, "kit.json"), "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        # Create directories for components and tools
        components_dir = os.path.join(kit_dir, "components")
        tools_dir = os.path.join(kit_dir, "tools")
        os.makedirs(components_dir, exist_ok=True)
        os.makedirs(tools_dir, exist_ok=True)
        
        # Copy component source files
        for name, component in self.components.items():
            source_path = component.source_path
            if os.path.isfile(source_path):
                dest_path = os.path.join(components_dir, os.path.basename(source_path))
                shutil.copy2(source_path, dest_path)
        
        # Create tool scripts
        for name, tool in self.tools.items():
            tool_path = os.path.join(tools_dir, name)
            with open(tool_path, "w") as f:
                f.write("#!/bin/bash\n\n")
                f.write(f"# {tool.description}\n\n")
                f.write(tool.command)
            os.chmod(tool_path, 0o755)  # Make executable

class KitRegistry:
    """
    Registry for kits.
    """
    def __init__(self, registry_dir: str):
        self.registry_dir = registry_dir
        self.kits: Dict[str, Dict[str, Kit]] = {}  # name -> version -> Kit
        self.load_kits()
    
    def load_kits(self) -> None:
        """Load all kits from the registry directory."""
        if not os.path.isdir(self.registry_dir):
            os.makedirs(self.registry_dir, exist_ok=True)
            return
        
        for kit_name in os.listdir(self.registry_dir):
            kit_dir = os.path.join(self.registry_dir, kit_name)
            if os.path.isdir(kit_dir):
                kit_file = os.path.join(kit_dir, "kit.json")
                if os.path.isfile(kit_file):
                    try:
                        with open(kit_file, "r") as f:
                            kit_data = json.load(f)
                        kit = Kit.from_dict(kit_data)
                        
                        # Add to registry
                        if kit.name not in self.kits:
                            self.kits[kit.name] = {}
                        self.kits[kit.name][kit.version] = kit
                    except Exception as e:
                        print(f"Error loading kit {kit_name}: {e}")
    
    def register_kit(self, kit: Kit) -> None:
        """Register a kit in the registry."""
        # Check if the kit already exists
        if kit.name in self.kits and kit.version in self.kits[kit.name]:
            raise ValueError(f"Kit {kit.name} version {kit.version} already exists")
        
        # Add to registry
        if kit.name not in self.kits:
            self.kits[kit.name] = {}
        self.kits[kit.name][kit.version] = kit
        
        # Save the kit
        kit.save(self.registry_dir)
    
    def get_kit(self, name: str, version: Optional[str] = None) -> Optional[Kit]:
        """
        Get a kit by name and version.
        If version is None, returns the latest version.
        """
        if name not in self.kits:
            return None
        
        if version is not None:
            return self.kits[name].get(version)
        
        # Find the latest version
        versions = list(self.kits[name].keys())
        if not versions:
            return None
        
        # Sort versions using semver
        versions.sort(key=lambda v: semver.VersionInfo.parse(v), reverse=True)
        return self.kits[name][versions[0]]
    
    def list_kits(self) -> List[Dict[str, Any]]:
        """List all kits in the registry."""
        result = []
        for name, versions in self.kits.items():
            for version, kit in versions.items():
                result.append({
                    "name": name,
                    "version": version,
                    "description": kit.description,
                    "components": len(kit.components),
                    "tools": len(kit.tools),
                    "dependencies": kit.dependencies
                })
        return result
    
    def search_kits(self, query: str) -> List[Dict[str, Any]]:
        """Search for kits by name or description."""
        query = query.lower()
        result = []
        for name, versions in self.kits.items():
            for version, kit in versions.items():
                if query in name.lower() or query in kit.description.lower():
                    result.append({
                        "name": name,
                        "version": version,
                        "description": kit.description,
                        "components": len(kit.components),
                        "tools": len(kit.tools),
                        "dependencies": kit.dependencies
                    })
        return result

class KitParser:
    """
    Parser for kit definition files.
    """
    def __init__(self, registry: KitRegistry):
        self.registry = registry
    
    def parse_file(self, file_path: str) -> Kit:
        """Parse a kit definition file."""
        with open(file_path, "r") as f:
            content = f.read()
        return self.parse(content)
    
    def parse(self, content: str) -> Kit:
        """Parse kit definition content."""
        # Remove comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Find kit definition
        kit_match = re.search(r'kit\s+(\w+)(?:\s+version\s+([0-9]+\.[0-9]+\.[0-9]+))?\s*{([^}]*)}', content, re.DOTALL)
        if not kit_match:
            raise ValueError("No kit definition found")
        
        kit_name = kit_match.group(1)
        kit_version = kit_match.group(2) or "0.1.0"  # Default version
        kit_body = kit_match.group(3)
        
        # Create the kit
        kit = Kit(kit_name, kit_version)
        
        # Find description
        desc_match = re.search(r'description\s+"([^"]*)"', kit_body)
        if desc_match:
            kit.description = desc_match.group(1)
        
        # Find components
        components_match = re.search(r'collect\s+{([^}]*)}', kit_body)
        if components_match:
            components_list = components_match.group(1)
            for comp in re.finditer(r'(\w+)(?:\s+from\s+"([^"]*)")?(?:\s+as\s+"([^"]*)")?', components_list):
                comp_name = comp.group(1)
                comp_path = comp.group(2) or f"components/{comp_name}.mono"
                comp_desc = comp.group(3) or f"{comp_name} component"
                kit.add_component(KitComponent(comp_name, comp_path, comp_desc))
        
        # Find tools
        tools_match = re.search(r'tools\s+{([^}]*)}', kit_body)
        if tools_match:
            tools_list = tools_match.group(1)
            for tool in re.finditer(r'(\w+)\s+"([^"]*)"(?:\s+as\s+"([^"]*)")?', tools_list):
                tool_name = tool.group(1)
                tool_command = tool.group(2)
                tool_desc = tool.group(3) or f"{tool_name} tool"
                kit.add_tool(KitTool(tool_name, tool_command, tool_desc))
        
        # Find dependencies
        deps_match = re.search(r'depends\s+{([^}]*)}', kit_body)
        if deps_match:
            deps_list = deps_match.group(1)
            for dep in re.finditer(r'(\w+)(?:\s+version\s+([0-9]+\.[0-9]+\.[0-9]+|\^[0-9]+\.[0-9]+\.[0-9]+|~[0-9]+\.[0-9]+\.[0-9]+))?', deps_list):
                dep_name = dep.group(1)
                dep_version = dep.group(2) or "*"  # Any version
                kit.add_dependency(dep_name, dep_version)
        
        return kit

class KitLoader:
    """
    Loader for kits.
    """
    def __init__(self, registry: KitRegistry):
        self.registry = registry
        self.loaded_kits: Dict[str, Kit] = {}
    
    def load_kit(self, name: str, version: Optional[str] = None) -> Optional[Kit]:
        """
        Load a kit by name and version.
        If version is None, loads the latest version.
        """
        # Check if already loaded
        key = f"{name}@{version or 'latest'}"
        if key in self.loaded_kits:
            return self.loaded_kits[key]
        
        # Get the kit from the registry
        kit = self.registry.get_kit(name, version)
        if not kit:
            return None
        
        # Load dependencies
        for dep_name, dep_version in kit.dependencies.items():
            self.load_kit(dep_name, dep_version)
        
        # Mark as loaded
        self.loaded_kits[key] = kit
        return kit
    
    def get_component(self, kit_name: str, component_name: str, version: Optional[str] = None) -> Optional[KitComponent]:
        """Get a component from a kit."""
        kit = self.load_kit(kit_name, version)
        if not kit:
            return None
        return kit.components.get(component_name)
    
    def get_tool(self, kit_name: str, tool_name: str, version: Optional[str] = None) -> Optional[KitTool]:
        """Get a tool from a kit."""
        kit = self.load_kit(kit_name, version)
        if not kit:
            return None
        return kit.tools.get(tool_name)

# Global registry
_registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")
kit_registry = KitRegistry(_registry_dir)
kit_loader = KitLoader(kit_registry)

def get_kit_registry() -> KitRegistry:
    """Get the global kit registry."""
    return kit_registry

def get_kit_loader() -> KitLoader:
    """Get the global kit loader."""
    return kit_loader
