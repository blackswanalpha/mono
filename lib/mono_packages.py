"""
Mono Package Manager - Package management system for the Mono language

This module provides support for:
1. Package Definition: Define packages with components, dependencies, and metadata
2. Package Registry: Central repository for discovering and sharing packages
3. Dependency Management: Resolve and manage package dependencies
4. Security Scanning: Detect vulnerabilities in dependencies
5. License Compliance: Enforce licensing rules
"""

import os
import re
import json
import shutil
import hashlib
import semver
import requests
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field

# Constants
DEFAULT_REGISTRY_DIR = os.path.expanduser("~/.mono/packages")
DEFAULT_REGISTRY_URL = "https://registry.mono-lang.org"
DEFAULT_CONFIG_FILE = os.path.expanduser("~/.mono/config.json")

@dataclass
class PackageDependency:
    """Represents a dependency on another package."""
    name: str
    version_requirement: str  # Semver requirement (e.g., "^1.0.0", "~2.3.4", ">=1.0.0 <2.0.0")
    is_dev: bool = False  # Whether this is a development dependency
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version_requirement": self.version_requirement,
            "is_dev": self.is_dev
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageDependency':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version_requirement=data["version_requirement"],
            is_dev=data.get("is_dev", False)
        )
    
    def satisfies(self, version: str) -> bool:
        """Check if a version satisfies this dependency requirement."""
        try:
            return semver.VersionInfo.parse(version).match(self.version_requirement)
        except ValueError:
            return False

@dataclass
class PackageComponent:
    """Represents a component in a package."""
    name: str
    source_path: str
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "source_path": self.source_path,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageComponent':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            source_path=data["source_path"],
            description=data.get("description", "")
        )

@dataclass
class Package:
    """Represents a package (collection of components and metadata)."""
    name: str
    version: str
    description: str = ""
    author: str = ""
    license: str = ""
    homepage: str = ""
    repository: str = ""
    components: Dict[str, PackageComponent] = field(default_factory=dict)
    dependencies: Dict[str, PackageDependency] = field(default_factory=dict)
    dev_dependencies: Dict[str, PackageDependency] = field(default_factory=dict)
    
    def add_component(self, component: PackageComponent) -> None:
        """Add a component to the package."""
        self.components[component.name] = component
    
    def add_dependency(self, dependency: PackageDependency) -> None:
        """Add a dependency to the package."""
        if dependency.is_dev:
            self.dev_dependencies[dependency.name] = dependency
        else:
            self.dependencies[dependency.name] = dependency
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "homepage": self.homepage,
            "repository": self.repository,
            "components": {name: comp.to_dict() for name, comp in self.components.items()},
            "dependencies": {name: dep.to_dict() for name, dep in self.dependencies.items()},
            "dev_dependencies": {name: dep.to_dict() for name, dep in self.dev_dependencies.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Package':
        """Create from dictionary."""
        package = cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            license=data.get("license", ""),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", "")
        )
        
        # Add components
        for name, comp_data in data.get("components", {}).items():
            package.add_component(PackageComponent.from_dict(comp_data))
        
        # Add dependencies
        for name, dep_data in data.get("dependencies", {}).items():
            dep_data["is_dev"] = False
            package.add_dependency(PackageDependency.from_dict(dep_data))
        
        # Add dev dependencies
        for name, dep_data in data.get("dev_dependencies", {}).items():
            dep_data["is_dev"] = True
            package.add_dependency(PackageDependency.from_dict(dep_data))
        
        return package
    
    def save(self, package_dir: str) -> None:
        """Save the package to disk."""
        # Create package directory
        os.makedirs(package_dir, exist_ok=True)
        
        # Save package.json
        package_file = os.path.join(package_dir, "package.json")
        with open(package_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        # Create directories for components
        components_dir = os.path.join(package_dir, "components")
        os.makedirs(components_dir, exist_ok=True)
        
        # Copy component source files
        for name, component in self.components.items():
            source_path = component.source_path
            if os.path.isfile(source_path):
                dest_path = os.path.join(components_dir, os.path.basename(source_path))
                shutil.copy2(source_path, dest_path)
    
    @classmethod
    def load(cls, package_dir: str) -> Optional['Package']:
        """Load a package from disk."""
        package_file = os.path.join(package_dir, "package.json")
        if not os.path.isfile(package_file):
            return None
        
        try:
            with open(package_file, "r") as f:
                package_data = json.load(f)
            return cls.from_dict(package_data)
        except Exception as e:
            print(f"Error loading package: {e}")
            return None

class PackageRegistry:
    """
    Registry for packages.
    """
    def __init__(self, registry_dir: str = DEFAULT_REGISTRY_DIR):
        self.registry_dir = registry_dir
        self.packages: Dict[str, Dict[str, Package]] = {}  # name -> version -> Package
        self.load_packages()
    
    def load_packages(self) -> None:
        """Load all packages from the registry directory."""
        if not os.path.isdir(self.registry_dir):
            os.makedirs(self.registry_dir, exist_ok=True)
            return
        
        for package_name in os.listdir(self.registry_dir):
            package_dir = os.path.join(self.registry_dir, package_name)
            if os.path.isdir(package_dir):
                for version_dir in os.listdir(package_dir):
                    version_path = os.path.join(package_dir, version_dir)
                    if os.path.isdir(version_path):
                        package = Package.load(version_path)
                        if package:
                            if package.name not in self.packages:
                                self.packages[package.name] = {}
                            self.packages[package.name][package.version] = package
    
    def register_package(self, package: Package) -> None:
        """Register a package in the registry."""
        # Check if the package already exists
        if package.name in self.packages and package.version in self.packages[package.name]:
            raise ValueError(f"Package {package.name} version {package.version} already exists")
        
        # Add to registry
        if package.name not in self.packages:
            self.packages[package.name] = {}
        self.packages[package.name][package.version] = package
        
        # Save the package
        package_dir = os.path.join(self.registry_dir, package.name, package.version)
        package.save(package_dir)
    
    def get_package(self, name: str, version: Optional[str] = None) -> Optional[Package]:
        """
        Get a package by name and version.
        If version is None, returns the latest version.
        """
        if name not in self.packages:
            return None
        
        if version is not None:
            return self.packages[name].get(version)
        
        # Find the latest version
        versions = list(self.packages[name].keys())
        if not versions:
            return None
        
        # Sort versions using semver
        versions.sort(key=lambda v: semver.VersionInfo.parse(v), reverse=True)
        return self.packages[name][versions[0]]
    
    def search_packages(self, query: str) -> List[Package]:
        """Search for packages by name or description."""
        results = []
        query = query.lower()
        
        for name, versions in self.packages.items():
            for version, package in versions.items():
                if (query in name.lower() or 
                    query in package.description.lower()):
                    results.append(package)
                    break  # Only add the latest version of each package
        
        return results
    
    def list_packages(self) -> List[Package]:
        """List all packages in the registry."""
        results = []
        
        for name, versions in self.packages.items():
            # Get the latest version
            latest_version = max(versions.keys(), key=lambda v: semver.VersionInfo.parse(v))
            results.append(versions[latest_version])
        
        return results

class PackageParser:
    """
    Parser for package definition files.
    """
    def __init__(self, registry: PackageRegistry):
        self.registry = registry
    
    def parse_file(self, file_path: str) -> Package:
        """Parse a package definition file."""
        with open(file_path, "r") as f:
            content = f.read()
        
        return self.parse(content)
    
    def parse(self, content: str) -> Package:
        """Parse package definition content."""
        # Extract package header
        header_match = re.search(r'package\s+(\w+)\s+version\s+([0-9]+\.[0-9]+\.[0-9]+)\s*{', content)
        if not header_match:
            raise ValueError("Invalid package definition: missing package header")
        
        package_name = header_match.group(1)
        package_version = header_match.group(2)
        
        # Extract package body
        body_start = header_match.end()
        body_end = content.rfind('}')
        if body_end == -1:
            raise ValueError("Invalid package definition: missing closing brace")
        
        package_body = content[body_start:body_end]
        
        # Create package
        package = Package(package_name, package_version)
        
        # Find description
        desc_match = re.search(r'description\s+"([^"]*)"', package_body)
        if desc_match:
            package.description = desc_match.group(1)
        
        # Find author
        author_match = re.search(r'author\s+"([^"]*)"', package_body)
        if author_match:
            package.author = author_match.group(1)
        
        # Find license
        license_match = re.search(r'license\s+"([^"]*)"', package_body)
        if license_match:
            package.license = license_match.group(1)
        
        # Find homepage
        homepage_match = re.search(r'homepage\s+"([^"]*)"', package_body)
        if homepage_match:
            package.homepage = homepage_match.group(1)
        
        # Find repository
        repo_match = re.search(r'repository\s+"([^"]*)"', package_body)
        if repo_match:
            package.repository = repo_match.group(1)
        
        # Find components
        components_match = re.search(r'components\s+{([^}]*)}', package_body)
        if components_match:
            components_list = components_match.group(1)
            for component in re.finditer(r'(\w+)\s+from\s+"([^"]*)"(?:\s+as\s+"([^"]*)")?', components_list):
                component_name = component.group(1)
                component_path = component.group(2)
                component_desc = component.group(3) or f"{component_name} component"
                package.add_component(PackageComponent(component_name, component_path, component_desc))
        
        # Find dependencies
        deps_match = re.search(r'dependencies\s+{([^}]*)}', package_body)
        if deps_match:
            deps_list = deps_match.group(1)
            for dep in re.finditer(r'(\w+)(?:\s+version\s+([0-9]+\.[0-9]+\.[0-9]+|\^[0-9]+\.[0-9]+\.[0-9]+|~[0-9]+\.[0-9]+\.[0-9]+))?', deps_list):
                dep_name = dep.group(1)
                dep_version = dep.group(2) or "*"  # Any version
                package.add_dependency(PackageDependency(dep_name, dep_version, False))
        
        # Find dev dependencies
        dev_deps_match = re.search(r'dev_dependencies\s+{([^}]*)}', package_body)
        if dev_deps_match:
            dev_deps_list = dev_deps_match.group(1)
            for dep in re.finditer(r'(\w+)(?:\s+version\s+([0-9]+\.[0-9]+\.[0-9]+|\^[0-9]+\.[0-9]+\.[0-9]+|~[0-9]+\.[0-9]+\.[0-9]+))?', dev_deps_list):
                dep_name = dep.group(1)
                dep_version = dep.group(2) or "*"  # Any version
                package.add_dependency(PackageDependency(dep_name, dep_version, True))
        
        return package

class DependencyResolver:
    """
    Resolver for package dependencies.
    """
    def __init__(self, registry: PackageRegistry):
        self.registry = registry
    
    def resolve_dependencies(self, package: Package, include_dev: bool = False) -> Dict[str, Package]:
        """
        Resolve all dependencies for a package.
        
        Args:
            package: The package to resolve dependencies for
            include_dev: Whether to include development dependencies
            
        Returns:
            A dictionary mapping package names to resolved package objects
        """
        resolved: Dict[str, Package] = {}
        pending: List[PackageDependency] = []
        
        # Add direct dependencies
        for dep in package.dependencies.values():
            pending.append(dep)
        
        # Add dev dependencies if requested
        if include_dev:
            for dep in package.dev_dependencies.values():
                pending.append(dep)
        
        # Resolve dependencies
        while pending:
            dep = pending.pop(0)
            
            # Skip if already resolved
            if dep.name in resolved:
                continue
            
            # Find the package
            dep_package = self.registry.get_package(dep.name)
            if not dep_package:
                raise ValueError(f"Package {dep.name} not found")
            
            # Check version compatibility
            if not dep.satisfies(dep_package.version):
                raise ValueError(f"Package {dep.name} version {dep_package.version} does not satisfy requirement {dep.version_requirement}")
            
            # Add to resolved
            resolved[dep.name] = dep_package
            
            # Add transitive dependencies
            for transitive_dep in dep_package.dependencies.values():
                pending.append(transitive_dep)
        
        return resolved
    
    def build_dependency_graph(self, package: Package, include_dev: bool = False) -> Dict[str, Set[str]]:
        """
        Build a dependency graph for a package.
        
        Args:
            package: The package to build the graph for
            include_dev: Whether to include development dependencies
            
        Returns:
            A dictionary mapping package names to sets of dependency names
        """
        graph: Dict[str, Set[str]] = {package.name: set()}
        pending: List[Tuple[str, PackageDependency]] = []
        
        # Add direct dependencies
        for dep in package.dependencies.values():
            graph[package.name].add(dep.name)
            pending.append((package.name, dep))
        
        # Add dev dependencies if requested
        if include_dev:
            for dep in package.dev_dependencies.values():
                graph[package.name].add(dep.name)
                pending.append((package.name, dep))
        
        # Build graph
        while pending:
            parent, dep = pending.pop(0)
            
            # Skip if already in graph
            if dep.name in graph:
                continue
            
            # Find the package
            dep_package = self.registry.get_package(dep.name)
            if not dep_package:
                raise ValueError(f"Package {dep.name} not found")
            
            # Add to graph
            graph[dep.name] = set()
            
            # Add transitive dependencies
            for transitive_dep in dep_package.dependencies.values():
                graph[dep.name].add(transitive_dep.name)
                pending.append((dep.name, transitive_dep))
        
        return graph

class SecurityScanner:
    """
    Scanner for security vulnerabilities in packages.
    """
    def __init__(self, registry: PackageRegistry):
        self.registry = registry
    
    def scan_package(self, package: Package, level: str = "all") -> List[Dict[str, Any]]:
        """
        Scan a package for security vulnerabilities.
        
        Args:
            package: The package to scan
            level: Vulnerability level to report ("low", "medium", "high", "critical", or "all")
            
        Returns:
            A list of vulnerability reports
        """
        # In a real implementation, this would query a vulnerability database
        # For now, we'll just return a mock result
        vulnerabilities = []
        
        # Mock vulnerability check
        if package.name == "example-vulnerable-package":
            vulnerabilities.append({
                "package": package.name,
                "version": package.version,
                "level": "critical",
                "description": "Example vulnerability for demonstration purposes",
                "fix_version": "1.0.1"
            })
        
        # Filter by level
        if level != "all":
            level_priority = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            level_threshold = level_priority.get(level.lower(), 0)
            vulnerabilities = [v for v in vulnerabilities if level_priority.get(v["level"].lower(), 0) >= level_threshold]
        
        return vulnerabilities
    
    def scan_dependencies(self, package: Package, level: str = "all", include_dev: bool = False) -> List[Dict[str, Any]]:
        """
        Scan all dependencies of a package for security vulnerabilities.
        
        Args:
            package: The package to scan dependencies for
            level: Vulnerability level to report ("low", "medium", "high", "critical", or "all")
            include_dev: Whether to include development dependencies
            
        Returns:
            A list of vulnerability reports
        """
        vulnerabilities = []
        
        # Resolve dependencies
        resolver = DependencyResolver(self.registry)
        dependencies = resolver.resolve_dependencies(package, include_dev)
        
        # Scan each dependency
        for dep_name, dep_package in dependencies.items():
            dep_vulns = self.scan_package(dep_package, level)
            vulnerabilities.extend(dep_vulns)
        
        return vulnerabilities

class LicenseChecker:
    """
    Checker for license compliance.
    """
    def __init__(self, registry: PackageRegistry):
        self.registry = registry
        self.allowed_licenses = set([
            "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", 
            "ISC", "Unlicense", "0BSD"
        ])
        self.restricted_licenses = set([
            "GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0"
        ])
    
    def check_license_compliance(self, package: Package, include_dev: bool = False) -> List[Dict[str, Any]]:
        """
        Check license compliance for a package and its dependencies.
        
        Args:
            package: The package to check
            include_dev: Whether to include development dependencies
            
        Returns:
            A list of license compliance issues
        """
        issues = []
        
        # Resolve dependencies
        resolver = DependencyResolver(self.registry)
        dependencies = resolver.resolve_dependencies(package, include_dev)
        
        # Check each dependency
        for dep_name, dep_package in dependencies.items():
            if not dep_package.license:
                issues.append({
                    "package": dep_name,
                    "version": dep_package.version,
                    "issue": "missing_license",
                    "description": "Package does not specify a license"
                })
            elif dep_package.license in self.restricted_licenses:
                issues.append({
                    "package": dep_name,
                    "version": dep_package.version,
                    "issue": "restricted_license",
                    "description": f"Package uses a restricted license: {dep_package.license}"
                })
            elif dep_package.license not in self.allowed_licenses:
                issues.append({
                    "package": dep_name,
                    "version": dep_package.version,
                    "issue": "unknown_license",
                    "description": f"Package uses an unknown license: {dep_package.license}"
                })
        
        return issues

class PackageManager:
    """
    Main package manager class.
    """
    def __init__(self, registry_dir: str = DEFAULT_REGISTRY_DIR):
        self.registry = PackageRegistry(registry_dir)
        self.parser = PackageParser(self.registry)
        self.resolver = DependencyResolver(self.registry)
        self.security_scanner = SecurityScanner(self.registry)
        self.license_checker = LicenseChecker(self.registry)
    
    def install_package(self, name: str, version: Optional[str] = None, dev: bool = False) -> Optional[Package]:
        """
        Install a package.
        
        Args:
            name: Package name
            version: Package version (optional)
            dev: Whether to install as a development dependency
            
        Returns:
            The installed package, or None if not found
        """
        # Find the package
        package = self.registry.get_package(name, version)
        if not package:
            # In a real implementation, this would try to download from a remote registry
            print(f"Package {name} not found")
            return None
        
        # Install dependencies
        dependencies = self.resolver.resolve_dependencies(package, False)
        for dep_name, dep_package in dependencies.items():
            print(f"Installing dependency: {dep_name}@{dep_package.version}")
        
        print(f"Installed {name}@{package.version}")
        return package
    
    def create_package(self, name: str, version: str, description: str = "") -> Package:
        """
        Create a new package.
        
        Args:
            name: Package name
            version: Package version
            description: Package description
            
        Returns:
            The created package
        """
        package = Package(name, version, description)
        return package
    
    def publish_package(self, package: Package) -> bool:
        """
        Publish a package to the registry.
        
        Args:
            package: The package to publish
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.registry.register_package(package)
            return True
        except Exception as e:
            print(f"Error publishing package: {e}")
            return False
    
    def list_packages(self) -> List[Package]:
        """
        List all packages in the registry.
        
        Returns:
            A list of packages
        """
        return self.registry.list_packages()
    
    def search_packages(self, query: str) -> List[Package]:
        """
        Search for packages by name or description.
        
        Args:
            query: Search query
            
        Returns:
            A list of matching packages
        """
        return self.registry.search_packages(query)
    
    def show_package(self, name: str, version: Optional[str] = None) -> Optional[Package]:
        """
        Show details of a package.
        
        Args:
            name: Package name
            version: Package version (optional)
            
        Returns:
            The package, or None if not found
        """
        return self.registry.get_package(name, version)
    
    def audit_package(self, package: Package, level: str = "all", include_dev: bool = False) -> List[Dict[str, Any]]:
        """
        Audit a package for security vulnerabilities.
        
        Args:
            package: The package to audit
            level: Vulnerability level to report ("low", "medium", "high", "critical", or "all")
            include_dev: Whether to include development dependencies
            
        Returns:
            A list of vulnerability reports
        """
        return self.security_scanner.scan_dependencies(package, level, include_dev)
    
    def check_licenses(self, package: Package, include_dev: bool = False) -> List[Dict[str, Any]]:
        """
        Check license compliance for a package.
        
        Args:
            package: The package to check
            include_dev: Whether to include development dependencies
            
        Returns:
            A list of license compliance issues
        """
        return self.license_checker.check_license_compliance(package, include_dev)
    
    def build_dependency_graph(self, package: Package, include_dev: bool = False) -> Dict[str, Set[str]]:
        """
        Build a dependency graph for a package.
        
        Args:
            package: The package to build the graph for
            include_dev: Whether to include development dependencies
            
        Returns:
            A dependency graph
        """
        return self.resolver.build_dependency_graph(package, include_dev)
