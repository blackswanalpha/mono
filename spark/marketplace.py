"""
Plugin marketplace UI for Spark Editor.
"""

import os
import sys
from typing import Dict, List, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QTabWidget, QScrollArea, QFrame,
    QDialog, QMessageBox, QProgressBar, QSplitter, QTextEdit, QCheckBox,
    QGroupBox, QFormLayout, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QThread, QObject

from .plugin_system import get_plugin_manager, get_marketplace, PluginMetadata, PluginInterface

class PluginListItem(QWidget):
    """Widget for displaying a plugin in a list."""
    
    def __init__(self, plugin_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.plugin_data = plugin_data
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create the icon label
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        # In a real implementation, this would load the plugin icon
        # For now, we'll use a placeholder
        icon_label.setText("🔌")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)
        
        # Create the info layout
        info_layout = QVBoxLayout()
        
        # Create the name label
        name_label = QLabel(self.plugin_data["name"])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        # Create the description label
        description_label = QLabel(self.plugin_data["description"])
        description_label.setWordWrap(True)
        info_layout.addWidget(description_label)
        
        # Create the metadata layout
        metadata_layout = QHBoxLayout()
        
        # Create the author label
        author_label = QLabel(f"Author: {self.plugin_data['author']}")
        metadata_layout.addWidget(author_label)
        
        # Create the version label
        version_label = QLabel(f"Version: {self.plugin_data['version']}")
        metadata_layout.addWidget(version_label)
        
        # Create the rating label
        if "rating" in self.plugin_data:
            rating_label = QLabel(f"Rating: {self.plugin_data['rating']}/5.0")
            metadata_layout.addWidget(rating_label)
        
        # Create the downloads label
        if "downloads" in self.plugin_data:
            downloads_label = QLabel(f"Downloads: {self.plugin_data['downloads']}")
            metadata_layout.addWidget(downloads_label)
        
        # Add a spacer
        metadata_layout.addStretch()
        
        # Add the metadata layout to the info layout
        info_layout.addLayout(metadata_layout)
        
        # Add the info layout to the main layout
        layout.addLayout(info_layout)
        
        # Create the action button
        self.action_button = QPushButton("Install")
        self.action_button.setFixedWidth(100)
        layout.addWidget(self.action_button)
        
        # Set the layout
        self.setLayout(layout)

class InstalledPluginListItem(QWidget):
    """Widget for displaying an installed plugin in a list."""
    
    def __init__(self, plugin: PluginInterface, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create the icon label
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        # In a real implementation, this would load the plugin icon
        # For now, we'll use a placeholder
        icon_label.setText("🔌")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)
        
        # Create the info layout
        info_layout = QVBoxLayout()
        
        # Create the name label
        name_label = QLabel(self.plugin.metadata.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        # Create the description label
        description_label = QLabel(self.plugin.metadata.description)
        description_label.setWordWrap(True)
        info_layout.addWidget(description_label)
        
        # Create the metadata layout
        metadata_layout = QHBoxLayout()
        
        # Create the author label
        author_label = QLabel(f"Author: {self.plugin.metadata.author}")
        metadata_layout.addWidget(author_label)
        
        # Create the version label
        version_label = QLabel(f"Version: {self.plugin.metadata.version}")
        metadata_layout.addWidget(version_label)
        
        # Add a spacer
        metadata_layout.addStretch()
        
        # Add the metadata layout to the info layout
        info_layout.addLayout(metadata_layout)
        
        # Add the info layout to the main layout
        layout.addLayout(info_layout)
        
        # Create the action buttons
        action_layout = QVBoxLayout()
        
        # Create the enable/disable button
        self.enable_button = QPushButton("Disable" if self.plugin.is_enabled else "Enable")
        self.enable_button.setFixedWidth(100)
        action_layout.addWidget(self.enable_button)
        
        # Create the uninstall button
        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.setFixedWidth(100)
        action_layout.addWidget(self.uninstall_button)
        
        # Add the action layout to the main layout
        layout.addLayout(action_layout)
        
        # Set the layout
        self.setLayout(layout)

class MarketplaceWidget(QWidget):
    """Widget for browsing and installing plugins from the marketplace."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugin_manager = get_plugin_manager()
        self.marketplace = get_marketplace()
        self.setup_ui()
        self.load_plugins()
    
    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the tab widget
        self.tab_widget = QTabWidget()
        
        # Create the marketplace tab
        self.marketplace_tab = QWidget()
        self.setup_marketplace_tab()
        self.tab_widget.addTab(self.marketplace_tab, "Marketplace")
        
        # Create the installed tab
        self.installed_tab = QWidget()
        self.setup_installed_tab()
        self.tab_widget.addTab(self.installed_tab, "Installed")
        
        # Add the tab widget to the layout
        layout.addWidget(self.tab_widget)
        
        # Set the layout
        self.setLayout(layout)
    
    def setup_marketplace_tab(self):
        """Set up the marketplace tab."""
        # Create the layout
        layout = QVBoxLayout(self.marketplace_tab)
        
        # Create the search layout
        search_layout = QHBoxLayout()
        
        # Create the search label
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        # Create the search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for plugins...")
        self.search_input.textChanged.connect(self.search_plugins)
        search_layout.addWidget(self.search_input)
        
        # Create the search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_plugins)
        search_layout.addWidget(search_button)
        
        # Add the search layout to the main layout
        layout.addLayout(search_layout)
        
        # Create the plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        layout.addWidget(self.plugin_list)
        
        # Set the layout
        self.marketplace_tab.setLayout(layout)
    
    def setup_installed_tab(self):
        """Set up the installed tab."""
        # Create the layout
        layout = QVBoxLayout(self.installed_tab)
        
        # Create the plugin list
        self.installed_list = QListWidget()
        self.installed_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        layout.addWidget(self.installed_list)
        
        # Set the layout
        self.installed_tab.setLayout(layout)
    
    def load_plugins(self):
        """Load plugins from the marketplace and installed plugins."""
        self.load_marketplace_plugins()
        self.load_installed_plugins()
    
    def load_marketplace_plugins(self):
        """Load plugins from the marketplace."""
        # Clear the list
        self.plugin_list.clear()
        
        # Get available plugins
        plugins = self.marketplace.get_available_plugins()
        
        # Add each plugin to the list
        for plugin_data in plugins:
            item = QListWidgetItem(self.plugin_list)
            widget = PluginListItem(plugin_data)
            item.setSizeHint(widget.sizeHint())
            self.plugin_list.addItem(item)
            self.plugin_list.setItemWidget(item, widget)
            
            # Connect the install button
            widget.action_button.clicked.connect(lambda checked, plugin_id=plugin_data["id"]: self.install_plugin(plugin_id))
    
    def load_installed_plugins(self):
        """Load installed plugins."""
        # Clear the list
        self.installed_list.clear()
        
        # Get installed plugins
        plugins = self.plugin_manager.get_all_plugins()
        
        # Add each plugin to the list
        for plugin_id, plugin in plugins.items():
            item = QListWidgetItem(self.installed_list)
            widget = InstalledPluginListItem(plugin)
            item.setSizeHint(widget.sizeHint())
            self.installed_list.addItem(item)
            self.installed_list.setItemWidget(item, widget)
            
            # Connect the enable/disable button
            widget.enable_button.clicked.connect(lambda checked, plugin_id=plugin_id, button=widget.enable_button: self.toggle_plugin(plugin_id, button))
            
            # Connect the uninstall button
            widget.uninstall_button.clicked.connect(lambda checked, plugin_id=plugin_id: self.uninstall_plugin(plugin_id))
    
    def search_plugins(self):
        """Search for plugins in the marketplace."""
        # Get the search query
        query = self.search_input.text()
        
        # Clear the list
        self.plugin_list.clear()
        
        # Get matching plugins
        if query:
            plugins = self.marketplace.search_plugins(query)
        else:
            plugins = self.marketplace.get_available_plugins()
        
        # Add each plugin to the list
        for plugin_data in plugins:
            item = QListWidgetItem(self.plugin_list)
            widget = PluginListItem(plugin_data)
            item.setSizeHint(widget.sizeHint())
            self.plugin_list.addItem(item)
            self.plugin_list.setItemWidget(item, widget)
            
            # Connect the install button
            widget.action_button.clicked.connect(lambda checked, plugin_id=plugin_data["id"]: self.install_plugin(plugin_id))
    
    def install_plugin(self, plugin_id: str):
        """Install a plugin from the marketplace."""
        # Show a progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Installing Plugin")
        progress_dialog.setFixedSize(300, 100)
        
        # Create the layout
        layout = QVBoxLayout(progress_dialog)
        
        # Create the label
        label = QLabel(f"Installing plugin {plugin_id}...")
        layout.addWidget(label)
        
        # Create the progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(progress_bar)
        
        # Set the layout
        progress_dialog.setLayout(layout)
        
        # Show the dialog
        progress_dialog.show()
        
        # Install the plugin
        plugin_id = self.marketplace.download_plugin(plugin_id)
        
        # Close the dialog
        progress_dialog.close()
        
        # Check if the installation was successful
        if plugin_id:
            # Enable the plugin
            self.plugin_manager.enable_plugin(plugin_id)
            
            # Reload the installed plugins
            self.load_installed_plugins()
            
            # Show a success message
            QMessageBox.information(self, "Plugin Installed", f"Plugin {plugin_id} has been installed successfully.")
        else:
            # Show an error message
            QMessageBox.critical(self, "Installation Failed", f"Failed to install plugin {plugin_id}.")
    
    def toggle_plugin(self, plugin_id: str, button: QPushButton):
        """Enable or disable a plugin."""
        # Get the plugin
        plugin = self.plugin_manager.get_plugin(plugin_id)
        if plugin is None:
            return
        
        # Toggle the plugin
        if plugin.is_enabled:
            # Disable the plugin
            if self.plugin_manager.disable_plugin(plugin_id):
                button.setText("Enable")
                QMessageBox.information(self, "Plugin Disabled", f"Plugin {plugin.metadata.name} has been disabled.")
            else:
                QMessageBox.critical(self, "Disable Failed", f"Failed to disable plugin {plugin.metadata.name}.")
        else:
            # Enable the plugin
            if self.plugin_manager.enable_plugin(plugin_id):
                button.setText("Disable")
                QMessageBox.information(self, "Plugin Enabled", f"Plugin {plugin.metadata.name} has been enabled.")
            else:
                QMessageBox.critical(self, "Enable Failed", f"Failed to enable plugin {plugin.metadata.name}.")
    
    def uninstall_plugin(self, plugin_id: str):
        """Uninstall a plugin."""
        # Get the plugin
        plugin = self.plugin_manager.get_plugin(plugin_id)
        if plugin is None:
            return
        
        # Confirm uninstallation
        result = QMessageBox.question(
            self,
            "Confirm Uninstallation",
            f"Are you sure you want to uninstall the plugin {plugin.metadata.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Uninstall the plugin
            if self.plugin_manager.uninstall_plugin(plugin_id):
                # Reload the installed plugins
                self.load_installed_plugins()
                
                # Show a success message
                QMessageBox.information(self, "Plugin Uninstalled", f"Plugin {plugin.metadata.name} has been uninstalled successfully.")
            else:
                # Show an error message
                QMessageBox.critical(self, "Uninstallation Failed", f"Failed to uninstall plugin {plugin.metadata.name}.")

class PluginDialog(QDialog):
    """Dialog for managing plugins."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugin Manager")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Create the marketplace widget
        self.marketplace_widget = MarketplaceWidget()
        layout.addWidget(self.marketplace_widget)
        
        # Create the button layout
        button_layout = QHBoxLayout()
        
        # Add a spacer
        button_layout.addStretch()
        
        # Create the close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        # Add the button layout to the main layout
        layout.addLayout(button_layout)
        
        # Set the layout
        self.setLayout(layout)
