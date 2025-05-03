"""
Mono Integrated Interpreter - Combines core, reactive, typed, lifecycle, elements, frames, kits, layouts, and packages

This module provides a unified interface for all Mono features, including:
1. Core language features
2. Reactive programming
3. Type checking
4. Component lifecycle
5. Element support
6. Frame support
7. Kit management
8. Layout management
9. Package management
"""

import os
import sys
import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable

from lib.mono_core import run_mono_file as run_basic_mono_file
from lib.mono_reactive import run_mono_file as run_reactive_mono_file
from lib.mono_typed import run_mono_file as run_typed_mono_file
from lib.mono_lifecycle import run_mono_file as run_lifecycle_mono_file
from lib.mono_arithmetic import run_mono_file as run_arithmetic_mono_file
from lib.mono_collections import run_mono_file as run_collections_mono_file
from lib.mono_concurrent import run_mono_file as run_concurrent_mono_file
from lib.mono_element_interpreter import run_mono_file as run_element_mono_file
from lib.mono_frame_interpreter import run_mono_file as run_frame_mono_file
from lib.mono_combined_interpreter import run_mono_file as run_combined_mono_file

from lib.mono_kits import KitRegistry, KitParser, Kit, KitComponent, KitTool
from lib.mono_layouts import parse_layout_file, calculate_layout, render_layout_to_html, render_layout_to_css
from lib.mono_data_structures import (
    DataStructure, TableStructure, TreeStructure, GraphStructure, ListStructure, GridStructure,
    DataStructureManager, run_data_structure_demo
)
from lib.mono_packages import (
    Package, PackageComponent, PackageDependency, PackageRegistry,
    PackageParser, DependencyResolver, SecurityScanner, LicenseChecker,
    PackageManager
)

# Kit management functions
def create_kit(name: str, version: str = "0.1.0", description: str = "", registry_dir: str = None) -> bool:
    """Create a new kit."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")

    registry = KitRegistry(registry_dir)

    # Check if kit already exists
    existing_kit = registry.get_kit(name, version)
    if existing_kit:
        print(f"Error: Kit {name} version {version} already exists")
        return False

    # Create the kit
    kit = Kit(name, version, description)

    # Register the kit
    registry.register_kit(kit)

    print(f"Created kit {name} version {version}")
    return True

def list_kits(registry_dir: str = None) -> List[Dict[str, Any]]:
    """List all kits in the registry."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")

    registry = KitRegistry(registry_dir)
    kits = registry.list_kits()

    if not kits:
        print("No kits found in the registry")
        return []

    print(f"Found {len(kits)} kits in the registry:")
    for kit in kits:
        print(f"- {kit['name']} v{kit['version']}: {kit['description']}")
        print(f"  Components: {kit['components']}")
        print(f"  Tools: {kit['tools']}")
        if kit['dependencies']:
            print(f"  Dependencies: {', '.join([f'{name} {version}' for name, version in kit['dependencies'].items()])}")
        print()

    return kits

def search_kits(query: str, registry_dir: str = None) -> List[Dict[str, Any]]:
    """Search for kits by name or description."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")

    registry = KitRegistry(registry_dir)
    kits = registry.search_kits(query)

    if not kits:
        print(f"No kits found matching '{query}'")
        return []

    print(f"Found {len(kits)} kits matching '{query}':")
    for kit in kits:
        print(f"- {kit['name']} v{kit['version']}: {kit['description']}")
        print(f"  Components: {kit['components']}")
        print(f"  Tools: {kit['tools']}")
        if kit['dependencies']:
            print(f"  Dependencies: {', '.join([f'{name} {version}' for name, version in kit['dependencies'].items()])}")
        print()

    return kits

def show_kit(name: str, version: str = None, registry_dir: str = None) -> Optional[Kit]:
    """Show details of a kit."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")

    registry = KitRegistry(registry_dir)
    kit = registry.get_kit(name, version)

    if not kit:
        print(f"Kit {name} not found")
        return None

    print(f"Kit: {kit.name} v{kit.version}")
    print(f"Description: {kit.description}")

    if kit.components:
        print("\nComponents:")
        for name, component in kit.components.items():
            print(f"- {name}: {component.description}")
            print(f"  Source: {component.source_path}")

    if kit.tools:
        print("\nTools:")
        for name, tool in kit.tools.items():
            print(f"- {name}: {tool.description}")
            print(f"  Command: {tool.command}")

    if kit.dependencies:
        print("\nDependencies:")
        for name, version in kit.dependencies.items():
            print(f"- {name} {version}")

    return kit

def import_kit(file_path: str, registry_dir: str = None) -> bool:
    """Import a kit from a definition file."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kits")

    registry = KitRegistry(registry_dir)
    parser = KitParser(registry)

    try:
        kit = parser.parse_file(file_path)
        registry.register_kit(kit)
        print(f"Imported kit {kit.name} version {kit.version}")
    except Exception as e:
        print(f"Error importing kit: {e}")
        return False

    return True

def run_kit_demo() -> bool:
    """Run the kits demo."""
    script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "kits_demo.mono")

    if not os.path.isfile(script_file):
        print(f"Error: Demo file not found at {script_file}")
        return False

    print("Running Mono Kits Demo...")
    run_combined_mono_file(script_file)
    return True

# Data structure management functions
def create_data_structure(type_name: str, name: str, description: str = "") -> Any:
    """Create a new data structure."""
    manager = DataStructureManager()
    return manager.create_structure(type_name, name, description)

def list_data_structures() -> List[str]:
    """List all data structures."""
    manager = DataStructureManager()
    structures = manager.list_structures()

    if not structures:
        print("No data structures found")
        return []

    print(f"Found {len(structures)} data structures:")
    for name in structures:
        structure = manager.get_structure(name)
        print(f"- {name}: {structure.description}")

    return structures

def save_data_structure(name: str, file_path: str) -> bool:
    """Save a data structure to a file."""
    manager = DataStructureManager()
    return manager.save_structure(name, file_path)

def load_data_structure(file_path: str) -> Any:
    """Load a data structure from a file."""
    manager = DataStructureManager()
    return manager.load_structure(file_path)

def render_data_structure(name: str, format: str = "html") -> Optional[str]:
    """Render a data structure."""
    manager = DataStructureManager()
    return manager.render_structure(name, format)

def run_data_structures_demo() -> bool:
    """Run the data structures demo."""
    return run_data_structure_demo()

# Layout management functions
def parse_layout(file_path: str, verbose: bool = False) -> Any:
    """Parse a layout definition file."""
    try:
        layout = parse_layout_file(file_path)
        print(f"Successfully parsed layout '{layout.name}' from {file_path}")

        if verbose:
            print("\nLayout structure:")
            print_layout_structure(layout.root, 0)

        return layout
    except Exception as e:
        print(f"Error parsing layout: {e}")
        return None

def print_layout_structure(box, indent):
    """Print the structure of a layout box."""
    indent_str = "  " * indent
    print(f"{indent_str}{box.element_id or 'root'} ({box.width.value}{box.width.unit} x {box.height.value}{box.height.unit})")

    for child in box.children:
        print_layout_structure(child, indent + 1)

def render_layout(file_path: str, format: str = "html", output: str = None, width: int = 800, height: int = 600) -> str:
    """Render a layout to HTML or CSS."""
    layout = parse_layout_file(file_path)

    # Calculate layout
    layout = calculate_layout(layout, width, height)

    # Render
    if format == "html":
        output_content = render_layout_to_html(layout)
    else:
        output_content = render_layout_to_css(layout)

    # Write to file or return
    if output:
        with open(output, "w") as f:
            f.write(output_content)
        print(f"Layout rendered to {output}")

    return output_content

def run_layout_demo() -> bool:
    """Run the layouts demo."""
    script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "layouts_demo.mono")

    if not os.path.isfile(script_file):
        print(f"Error: Demo file not found at {script_file}")
        return False

    print("Running Mono Layouts Demo...")
    run_combined_mono_file(script_file)
    return True

# Package management functions
def create_package(name: str, version: str = "0.1.0", description: str = "", registry_dir: str = None) -> Package:
    """Create a new package."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    package = manager.create_package(name, version, description)

    print(f"Created package {name} version {version}")
    return package

def list_packages(registry_dir: str = None) -> List[Package]:
    """List all packages in the registry."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    packages = manager.list_packages()

    if not packages:
        print("No packages found in the registry")
        return []

    print(f"Found {len(packages)} packages in the registry:")
    for package in packages:
        print(f"- {package.name}@{package.version}: {package.description}")
        if package.components:
            print(f"  Components: {', '.join(package.components.keys())}")
        if package.dependencies:
            print(f"  Dependencies: {', '.join([f'{name} {dep.version_requirement}' for name, dep in package.dependencies.items()])}")
        print()

    return packages

def search_packages(query: str, registry_dir: str = None) -> List[Package]:
    """Search for packages by name or description."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    packages = manager.search_packages(query)

    if not packages:
        print(f"No packages found matching '{query}'")
        return []

    print(f"Found {len(packages)} packages matching '{query}':")
    for package in packages:
        print(f"- {package.name}@{package.version}: {package.description}")
        if package.components:
            print(f"  Components: {', '.join(package.components.keys())}")
        if package.dependencies:
            print(f"  Dependencies: {', '.join([f'{name} {dep.version_requirement}' for name, dep in package.dependencies.items()])}")
        print()

    return packages

def show_package(name: str, version: str = None, registry_dir: str = None) -> Optional[Package]:
    """Show details of a package."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    package = manager.show_package(name, version)

    if not package:
        print(f"Package {name} not found")
        return None

    print(f"Package: {package.name}@{package.version}")
    print(f"Description: {package.description}")

    if package.author:
        print(f"Author: {package.author}")
    if package.license:
        print(f"License: {package.license}")
    if package.homepage:
        print(f"Homepage: {package.homepage}")
    if package.repository:
        print(f"Repository: {package.repository}")

    if package.components:
        print("\nComponents:")
        for name, component in package.components.items():
            print(f"- {name}: {component.description}")
            print(f"  Source: {component.source_path}")

    if package.dependencies:
        print("\nDependencies:")
        for name, dependency in package.dependencies.items():
            print(f"- {name} {dependency.version_requirement}")

    if package.dev_dependencies:
        print("\nDevelopment Dependencies:")
        for name, dependency in package.dev_dependencies.items():
            print(f"- {name} {dependency.version_requirement}")

    return package

def import_package(file_path: str, registry_dir: str = None) -> bool:
    """Import a package from a definition file."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    parser = PackageParser(manager.registry)

    try:
        package = parser.parse_file(file_path)
        success = manager.publish_package(package)
        if success:
            print(f"Imported package {package.name} version {package.version}")
        else:
            print(f"Failed to import package {package.name} version {package.version}")
            return False
    except Exception as e:
        print(f"Error importing package: {e}")
        return False

    return True

def install_package(name: str, version: str = None, dev: bool = False, registry_dir: str = None) -> Optional[Package]:
    """Install a package."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    package = manager.install_package(name, version, dev)

    return package

def audit_package(name: str, version: str = None, level: str = "all", include_dev: bool = False, registry_dir: str = None) -> List[Dict[str, Any]]:
    """Audit a package for security vulnerabilities."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    package = manager.show_package(name, version)

    if not package:
        print(f"Package {name} not found")
        return []

    vulnerabilities = manager.audit_package(package, level, include_dev)

    if not vulnerabilities:
        print(f"No vulnerabilities found in {package.name}@{package.version}")
    else:
        print(f"Found {len(vulnerabilities)} vulnerabilities in {package.name}@{package.version}:")
        for vuln in vulnerabilities:
            print(f"- {vuln['package']}@{vuln['version']}: {vuln['level']} - {vuln['description']}")
            if 'fix_version' in vuln:
                print(f"  Fix: Upgrade to version {vuln['fix_version']} or later")

    return vulnerabilities

def check_licenses(name: str, version: str = None, include_dev: bool = False, registry_dir: str = None) -> List[Dict[str, Any]]:
    """Check license compliance for a package."""
    if registry_dir is None:
        registry_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packages")

    manager = PackageManager(registry_dir)
    package = manager.show_package(name, version)

    if not package:
        print(f"Package {name} not found")
        return []

    issues = manager.check_licenses(package, include_dev)

    if not issues:
        print(f"No license compliance issues found in {package.name}@{package.version}")
    else:
        print(f"Found {len(issues)} license compliance issues in {package.name}@{package.version}:")
        for issue in issues:
            print(f"- {issue['package']}@{issue['version']}: {issue['issue']} - {issue['description']}")

    return issues

def run_package_demo() -> bool:
    """Run the package manager demo."""
    script_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "packages_demo.mono")

    if not os.path.isfile(script_file):
        print(f"Error: Demo file not found at {script_file}")
        return False

    print("Running Mono Package Manager Demo...")
    run_combined_mono_file(script_file)
    return True

# Integrated run function
def run_mono_file(file_path: str, options: Dict[str, Any] = None) -> bool:
    """
    Run a Mono script with all features enabled.

    Args:
        file_path: Path to the Mono script file
        options: Dictionary of options for the interpreter

    Returns:
        True if the script ran successfully, False otherwise
    """
    if options is None:
        options = {}

    # Set default options
    default_options = {
        'reactive': True,
        'type_check': True,
        'lifecycle': True,
        'arithmetic': True,
        'collections': True,
        'concurrent': True,
        'elements': True,
        'frames': True,
        'packages': True,
        'verbose': False
    }

    # Merge options
    for key, value in default_options.items():
        if key not in options:
            options[key] = value

    # Run the script with the combined interpreter
    return run_combined_mono_file(file_path)
