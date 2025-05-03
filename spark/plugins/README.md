# Spark Editor Plugins

This directory contains plugins for the Spark Editor. Plugins can extend the functionality of the editor with new features, themes, and integrations.

## Plugin Structure

Each plugin is contained in its own directory with the following structure:

```
plugin-id/
  ├── plugin.json    # Plugin metadata
  ├── main.py        # Main plugin code
  ├── resources/     # Plugin resources (optional)
  └── README.md      # Plugin documentation (optional)
```

## Plugin Metadata

The `plugin.json` file contains metadata about the plugin:

```json
{
  "id": "plugin-id",
  "name": "Plugin Name",
  "version": "1.0.0",
  "description": "A description of the plugin.",
  "author": "Plugin Author",
  "website": "https://example.com",
  "repository": "https://github.com/author/plugin-repo",
  "dependencies": {
    "other-plugin": "^1.0.0"
  },
  "tags": ["tag1", "tag2"]
}
```

## Plugin Code

The `main.py` file contains the main plugin code. It must define a `Plugin` class that inherits from `PluginInterface`:

```python
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
```

## Installing Plugins

Plugins can be installed from the Plugin Manager in the Spark Editor. You can access the Plugin Manager from the Tools menu.

## Creating Plugins

To create a plugin, create a new directory in the `plugins` directory with the structure described above. Then, implement the `Plugin` class in the `main.py` file.

## Example Plugins

- **syntax-highlighter**: Adds enhanced syntax highlighting for Mono files.
- **git-integration**: Adds Git integration to Spark Editor.
- **theme-pack**: Adds additional themes to Spark Editor.
