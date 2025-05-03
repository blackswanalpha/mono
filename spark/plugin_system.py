"""
Plugin system for Spark Editor.
"""

import os
import sys
import json
import importlib.util
import shutil
import zipfile
import tempfile
import requests
from typing import Dict, List, Any, Optional, Callable, Type, Union
from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject, pyqtSignal

# Define plugin metadata structure
@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    id: str
    name: str
    version: str
    description: str
    author: str
    website: Optional[str] = None
    repository: Optional[str] = None
    dependencies: Dict[str, str] = None
    tags: List[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """Create a PluginMetadata instance from a dictionary."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            version=data.get('version', '0.0.1'),
            description=data.get('description', ''),
            author=data.get('author', ''),
            website=data.get('website'),
            repository=data.get('repository'),
            dependencies=data.get('dependencies', {}),
            tags=data.get('tags', [])
        )

class PluginInterface:
    """Base interface for all plugins."""

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.is_enabled = False

    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        self.is_enabled = True
        return True

    def cleanup(self) -> bool:
        """Clean up resources when the plugin is disabled or uninstalled."""
        self.is_enabled = False
        return True

    def get_settings_widget(self) -> Optional[QWidget]:
        """Return a widget for plugin settings, or None if no settings."""
        return None

    def get_menu_actions(self) -> List[QAction]:
        """Return a list of actions to add to the plugin menu."""
        return []

class PluginManager(QObject):
    """Manages plugins for the Spark Editor."""

    # Signals
    pluginLoaded = pyqtSignal(str)  # Plugin ID
    pluginUnloaded = pyqtSignal(str)  # Plugin ID
    pluginEnabled = pyqtSignal(str)  # Plugin ID
    pluginDisabled = pyqtSignal(str)  # Plugin ID
    pluginInstalled = pyqtSignal(str)  # Plugin ID
    pluginUninstalled = pyqtSignal(str)  # Plugin ID

    def __init__(self, plugins_dir: str = None):
        super().__init__()

        # Set the plugins directory
        if plugins_dir is None:
            # Default to a 'plugins' directory in the Spark directory
            self.plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        else:
            self.plugins_dir = plugins_dir

        # Create the plugins directory if it doesn't exist
        os.makedirs(self.plugins_dir, exist_ok=True)

        # Dictionary of loaded plugins
        self.plugins: Dict[str, PluginInterface] = {}

        # Dictionary of plugin metadata
        self.plugin_metadata: Dict[str, PluginMetadata] = {}

        # Dictionary of plugin modules
        self.plugin_modules: Dict[str, Any] = {}

        # Dictionary of enabled plugins
        self.enabled_plugins: Dict[str, bool] = {}

        # Load the enabled plugins configuration
        self._load_enabled_plugins()

    def _load_enabled_plugins(self):
        """Load the list of enabled plugins from the configuration file."""
        config_path = os.path.join(self.plugins_dir, 'enabled_plugins.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.enabled_plugins = json.load(f)
            except Exception as e:
                print(f"Error loading enabled plugins: {str(e)}")
                self.enabled_plugins = {}

    def _save_enabled_plugins(self):
        """Save the list of enabled plugins to the configuration file."""
        config_path = os.path.join(self.plugins_dir, 'enabled_plugins.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self.enabled_plugins, f, indent=2)
        except Exception as e:
            print(f"Error saving enabled plugins: {str(e)}")

    def discover_plugins(self) -> List[PluginMetadata]:
        """Discover all available plugins in the plugins directory."""
        discovered_plugins = []

        # Iterate through the plugins directory
        for plugin_dir in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, plugin_dir)

            # Skip files and special directories
            if not os.path.isdir(plugin_path) or plugin_dir.startswith('.'):
                continue

            # Check for plugin.json
            metadata_path = os.path.join(plugin_path, 'plugin.json')
            if not os.path.exists(metadata_path):
                continue

            # Load the metadata
            try:
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)

                metadata = PluginMetadata.from_dict(metadata_dict)
                self.plugin_metadata[metadata.id] = metadata
                discovered_plugins.append(metadata)
            except Exception as e:
                print(f"Error loading plugin metadata from {metadata_path}: {str(e)}")

        return discovered_plugins

    def load_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """Load a plugin by ID."""
        # Check if the plugin is already loaded
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]

        # Check if the plugin exists
        plugin_dir = os.path.join(self.plugins_dir, plugin_id)
        if not os.path.isdir(plugin_dir):
            print(f"Plugin directory not found: {plugin_dir}")
            return None

        # Check for plugin.json
        metadata_path = os.path.join(plugin_dir, 'plugin.json')
        if not os.path.exists(metadata_path):
            print(f"Plugin metadata not found: {metadata_path}")
            return None

        # Load the metadata
        try:
            with open(metadata_path, 'r') as f:
                metadata_dict = json.load(f)

            metadata = PluginMetadata.from_dict(metadata_dict)
            self.plugin_metadata[plugin_id] = metadata
        except Exception as e:
            print(f"Error loading plugin metadata from {metadata_path}: {str(e)}")
            return None

        # Check for main.py
        main_path = os.path.join(plugin_dir, 'main.py')
        if not os.path.exists(main_path):
            print(f"Plugin main.py not found: {main_path}")
            return None

        # Load the module
        try:
            spec = importlib.util.spec_from_file_location(f"spark.plugins.{plugin_id}", main_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Get the plugin class
            plugin_class = getattr(module, 'Plugin', None)
            if plugin_class is None:
                print(f"Plugin class not found in {main_path}")
                return None

            # Create the plugin instance
            plugin = plugin_class(metadata)

            # Store the plugin
            self.plugins[plugin_id] = plugin
            self.plugin_modules[plugin_id] = module

            # Emit the signal
            self.pluginLoaded.emit(plugin_id)

            return plugin
        except Exception as e:
            print(f"Error loading plugin {plugin_id}: {str(e)}")
            return None

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin by ID."""
        # Check if the plugin is loaded
        if plugin_id not in self.plugins:
            return False

        # Get the plugin
        plugin = self.plugins[plugin_id]

        # Disable the plugin if it's enabled
        if plugin.is_enabled:
            self.disable_plugin(plugin_id)

        # Clean up the plugin
        try:
            plugin.cleanup()
        except Exception as e:
            print(f"Error cleaning up plugin {plugin_id}: {str(e)}")

        # Remove the plugin
        del self.plugins[plugin_id]
        del self.plugin_modules[plugin_id]

        # Emit the signal
        self.pluginUnloaded.emit(plugin_id)

        return True

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin by ID."""
        # Check if the plugin is loaded
        if plugin_id not in self.plugins:
            # Try to load the plugin
            plugin = self.load_plugin(plugin_id)
            if plugin is None:
                return False
        else:
            plugin = self.plugins[plugin_id]

        # Check if the plugin is already enabled
        if plugin.is_enabled:
            return True

        # Initialize the plugin
        try:
            if plugin.initialize():
                plugin.is_enabled = True
                self.enabled_plugins[plugin_id] = True
                self._save_enabled_plugins()

                # Emit the signal
                self.pluginEnabled.emit(plugin_id)

                return True
            else:
                print(f"Plugin {plugin_id} failed to initialize")
                return False
        except Exception as e:
            print(f"Error initializing plugin {plugin_id}: {str(e)}")
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin by ID."""
        # Check if the plugin is loaded
        if plugin_id not in self.plugins:
            return False

        # Get the plugin
        plugin = self.plugins[plugin_id]

        # Check if the plugin is already disabled
        if not plugin.is_enabled:
            return True

        # Clean up the plugin
        try:
            if plugin.cleanup():
                plugin.is_enabled = False
                self.enabled_plugins[plugin_id] = False
                self._save_enabled_plugins()

                # Emit the signal
                self.pluginDisabled.emit(plugin_id)

                return True
            else:
                print(f"Plugin {plugin_id} failed to clean up")
                return False
        except Exception as e:
            print(f"Error cleaning up plugin {plugin_id}: {str(e)}")
            return False

    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """Get a plugin by ID."""
        return self.plugins.get(plugin_id)

    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by ID."""
        return self.plugin_metadata.get(plugin_id)

    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """Get all loaded plugins."""
        return self.plugins

    def get_enabled_plugins(self) -> Dict[str, PluginInterface]:
        """Get all enabled plugins."""
        return {plugin_id: plugin for plugin_id, plugin in self.plugins.items() if plugin.is_enabled}

    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """Check if a plugin is enabled."""
        plugin = self.plugins.get(plugin_id)
        return plugin is not None and plugin.is_enabled

    def install_plugin(self, plugin_path: str) -> Optional[str]:
        """Install a plugin from a zip file or directory."""
        try:
            # Check if the path is a zip file
            if os.path.isfile(plugin_path) and plugin_path.endswith('.zip'):
                # Extract the zip file to a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(plugin_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)

                    # Find the plugin.json file
                    metadata_path = None
                    for root, dirs, files in os.walk(temp_dir):
                        if 'plugin.json' in files:
                            metadata_path = os.path.join(root, 'plugin.json')
                            break

                    if metadata_path is None:
                        print(f"Plugin metadata not found in {plugin_path}")
                        return None

                    # Load the metadata
                    with open(metadata_path, 'r') as f:
                        metadata_dict = json.load(f)

                    metadata = PluginMetadata.from_dict(metadata_dict)
                    plugin_id = metadata.id

                    # Create the plugin directory
                    plugin_dir = os.path.join(self.plugins_dir, plugin_id)
                    if os.path.exists(plugin_dir):
                        # Remove the existing plugin
                        if plugin_id in self.plugins:
                            self.unload_plugin(plugin_id)
                        shutil.rmtree(plugin_dir)

                    # Copy the plugin files
                    plugin_root = os.path.dirname(metadata_path)
                    shutil.copytree(plugin_root, plugin_dir)

            # Check if the path is a directory
            elif os.path.isdir(plugin_path):
                # Check for plugin.json
                metadata_path = os.path.join(plugin_path, 'plugin.json')
                if not os.path.exists(metadata_path):
                    print(f"Plugin metadata not found: {metadata_path}")
                    return None

                # Load the metadata
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)

                metadata = PluginMetadata.from_dict(metadata_dict)
                plugin_id = metadata.id

                # Create the plugin directory
                plugin_dir = os.path.join(self.plugins_dir, plugin_id)
                if os.path.exists(plugin_dir):
                    # Remove the existing plugin
                    if plugin_id in self.plugins:
                        self.unload_plugin(plugin_id)
                    shutil.rmtree(plugin_dir)

                # Copy the plugin files
                shutil.copytree(plugin_path, plugin_dir)

            else:
                print(f"Invalid plugin path: {plugin_path}")
                return None

            # Emit the signal
            self.pluginInstalled.emit(plugin_id)

            return plugin_id

        except Exception as e:
            print(f"Error installing plugin from {plugin_path}: {str(e)}")
            return None

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin by ID."""
        # Check if the plugin is loaded
        if plugin_id in self.plugins:
            # Unload the plugin
            self.unload_plugin(plugin_id)

        # Check if the plugin directory exists
        plugin_dir = os.path.join(self.plugins_dir, plugin_id)
        if not os.path.isdir(plugin_dir):
            return False

        # Remove the plugin directory
        try:
            shutil.rmtree(plugin_dir)

            # Remove from enabled plugins
            if plugin_id in self.enabled_plugins:
                del self.enabled_plugins[plugin_id]
                self._save_enabled_plugins()

            # Remove from metadata
            if plugin_id in self.plugin_metadata:
                del self.plugin_metadata[plugin_id]

            # Emit the signal
            self.pluginUninstalled.emit(plugin_id)

            return True
        except Exception as e:
            print(f"Error uninstalling plugin {plugin_id}: {str(e)}")
            return False

    def load_all_plugins(self) -> List[PluginInterface]:
        """Load all available plugins."""
        plugins = []

        # Discover plugins
        discovered_plugins = self.discover_plugins()

        # Load each plugin
        for metadata in discovered_plugins:
            plugin = self.load_plugin(metadata.id)
            if plugin is not None:
                plugins.append(plugin)

        return plugins

    def enable_all_plugins(self) -> List[str]:
        """Enable all loaded plugins."""
        enabled_plugins = []

        # Enable each plugin
        for plugin_id in list(self.plugins.keys()):
            if self.enable_plugin(plugin_id):
                enabled_plugins.append(plugin_id)

        return enabled_plugins

    def disable_all_plugins(self) -> List[str]:
        """Disable all enabled plugins."""
        disabled_plugins = []

        # Disable each plugin
        for plugin_id in list(self.plugins.keys()):
            if self.disable_plugin(plugin_id):
                disabled_plugins.append(plugin_id)

        return disabled_plugins

# Marketplace for plugins
class PluginMarketplace:
    """Marketplace for Spark Editor plugins."""

    def __init__(self, plugin_manager: PluginManager, marketplace_url: str = None):
        self.plugin_manager = plugin_manager

        # Set the marketplace URL
        if marketplace_url is None:
            # Default to a mock marketplace URL
            self.marketplace_url = "https://spark-editor.example.com/marketplace/api"
        else:
            self.marketplace_url = marketplace_url

    def get_available_plugins(self) -> List[Dict[str, Any]]:
        """Get a list of available plugins from the marketplace."""
        try:
            # In a real implementation, this would make an HTTP request to the marketplace API
            # For now, we'll return a mock list of plugins
            return [
                {
                    "id": "syntax-highlighter",
                    "name": "Enhanced Syntax Highlighter",
                    "version": "1.0.0",
                    "description": "Adds enhanced syntax highlighting for Mono files.",
                    "author": "Spark Team",
                    "website": "https://spark-editor.example.com",
                    "repository": "https://github.com/spark-editor/syntax-highlighter",
                    "download_url": "https://spark-editor.example.com/marketplace/plugins/syntax-highlighter-1.0.0.zip",
                    "tags": ["syntax", "highlighting", "editor"],
                    "rating": 4.5,
                    "downloads": 1250
                },
                {
                    "id": "git-integration",
                    "name": "Git Integration",
                    "version": "1.1.2",
                    "description": "Adds Git integration to Spark Editor.",
                    "author": "Spark Team",
                    "website": "https://spark-editor.example.com",
                    "repository": "https://github.com/spark-editor/git-integration",
                    "download_url": "https://spark-editor.example.com/marketplace/plugins/git-integration-1.1.2.zip",
                    "tags": ["git", "version-control", "integration"],
                    "rating": 4.8,
                    "downloads": 2500
                },
                {
                    "id": "theme-pack",
                    "name": "Theme Pack",
                    "version": "2.0.1",
                    "description": "Adds additional themes to Spark Editor.",
                    "author": "Spark Team",
                    "website": "https://spark-editor.example.com",
                    "repository": "https://github.com/spark-editor/theme-pack",
                    "download_url": "https://spark-editor.example.com/marketplace/plugins/theme-pack-2.0.1.zip",
                    "tags": ["theme", "appearance", "customization"],
                    "rating": 4.2,
                    "downloads": 1800
                }
            ]
        except Exception as e:
            print(f"Error getting available plugins: {str(e)}")
            return []

    def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """Search for plugins in the marketplace."""
        try:
            # Get all available plugins
            all_plugins = self.get_available_plugins()

            # Filter plugins by query
            query = query.lower()
            return [
                plugin for plugin in all_plugins
                if query in plugin["name"].lower() or
                   query in plugin["description"].lower() or
                   query in plugin["author"].lower() or
                   any(query in tag.lower() for tag in plugin["tags"])
            ]
        except Exception as e:
            print(f"Error searching plugins: {str(e)}")
            return []

    def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific plugin."""
        try:
            # Get all available plugins
            all_plugins = self.get_available_plugins()

            # Find the plugin by ID
            for plugin in all_plugins:
                if plugin["id"] == plugin_id:
                    return plugin

            return None
        except Exception as e:
            print(f"Error getting plugin details: {str(e)}")
            return None

    def download_plugin(self, plugin_id: str) -> Optional[str]:
        """Download a plugin from the marketplace."""
        try:
            # Get the plugin details
            plugin = self.get_plugin_details(plugin_id)
            if plugin is None:
                return None

            # Get the download URL
            download_url = plugin["download_url"]

            # In a real implementation, this would download the plugin from the URL
            # For now, we'll simulate downloading by creating a mock plugin

            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create the plugin directory
                plugin_dir = os.path.join(temp_dir, plugin_id)
                os.makedirs(plugin_dir, exist_ok=True)

                # Create the plugin.json file
                metadata = {
                    "id": plugin["id"],
                    "name": plugin["name"],
                    "version": plugin["version"],
                    "description": plugin["description"],
                    "author": plugin["author"],
                    "website": plugin["website"],
                    "repository": plugin["repository"],
                    "tags": plugin["tags"]
                }

                with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
                    json.dump(metadata, f, indent=2)

                # Create a mock main.py file
                with open(os.path.join(plugin_dir, "main.py"), "w") as f:
                    f.write(f"""
from spark.plugin_system import PluginInterface, PluginMetadata

class Plugin(PluginInterface):
    def __init__(self, metadata):
        super().__init__(metadata)

    def initialize(self):
        print(f"Initializing {self.metadata.name} plugin")
        return super().initialize()

    def cleanup(self):
        print(f"Cleaning up {self.metadata.name} plugin")
        return super().cleanup()
""")

                # Install the plugin
                return self.plugin_manager.install_plugin(plugin_dir)

        except Exception as e:
            print(f"Error downloading plugin {plugin_id}: {str(e)}")
            return None

    def install_plugin_from_url(self, url: str) -> Optional[str]:
        """Install a plugin from a URL."""
        try:
            # In a real implementation, this would download the plugin from the URL
            # For now, we'll return None
            print(f"Installing plugin from URL: {url}")
            return None
        except Exception as e:
            print(f"Error installing plugin from URL {url}: {str(e)}")
            return None

# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager

# Global marketplace instance
_marketplace = None

def get_marketplace() -> PluginMarketplace:
    """Get the global marketplace instance."""
    global _marketplace
    if _marketplace is None:
        _marketplace = PluginMarketplace(get_plugin_manager())
    return _marketplace
