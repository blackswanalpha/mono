"""
Git Integration plugin for Spark Editor.
"""

import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QTreeWidget, QTreeWidgetItem, QMenu
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from spark.plugin_system import PluginInterface, PluginMetadata

class GitStatusWidget(QWidget):
    """Widget for displaying Git status."""

    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QVBoxLayout(self)

        # Create the title label
        title_label = QLabel("Git Status")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Create the status tree
        self.status_tree = QTreeWidget()
        self.status_tree.setHeaderLabels(["File", "Status"])
        self.status_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.status_tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.status_tree)

        # Create the button layout
        button_layout = QHBoxLayout()

        # Create the refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_status)
        button_layout.addWidget(refresh_button)

        # Create the commit button
        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(self.show_commit_dialog)
        button_layout.addWidget(commit_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        # Set the layout
        self.setLayout(layout)

        # Refresh the status
        self.refresh_status()

    def refresh_status(self):
        """Refresh the Git status."""
        # Clear the tree
        self.status_tree.clear()

        # Get the status
        status = self.plugin.get_status()

        # Add items to the tree
        for file_path, file_status in status.items():
            item = QTreeWidgetItem([file_path, file_status])
            self.status_tree.addTopLevelItem(item)

    def show_context_menu(self, position):
        """Show the context menu."""
        # Get the selected item
        item = self.status_tree.itemAt(position)
        if item is None:
            return

        # Create the menu
        menu = QMenu()

        # Add actions
        stage_action = QAction("Stage", self)
        stage_action.triggered.connect(lambda: self.plugin.stage_file(item.text(0)))
        menu.addAction(stage_action)

        unstage_action = QAction("Unstage", self)
        unstage_action.triggered.connect(lambda: self.plugin.unstage_file(item.text(0)))
        menu.addAction(unstage_action)

        menu.addSeparator()

        discard_action = QAction("Discard Changes", self)
        discard_action.triggered.connect(lambda: self.plugin.discard_changes(item.text(0)))
        menu.addAction(discard_action)

        # Show the menu
        menu.exec(self.status_tree.viewport().mapToGlobal(position))

    def show_commit_dialog(self):
        """Show the commit dialog."""
        # This is a mock implementation
        # In a real plugin, this would show a dialog for committing changes
        print("Showing commit dialog")

class Plugin(PluginInterface):
    """Git Integration plugin."""

    def __init__(self, metadata):
        super().__init__(metadata)
        self.status_widget = None

    def initialize(self):
        """Initialize the plugin."""
        print(f"Initializing {self.metadata.name} plugin")
        return super().initialize()

    def cleanup(self):
        """Clean up the plugin."""
        print(f"Cleaning up {self.metadata.name} plugin")
        return super().cleanup()

    def get_settings_widget(self):
        """Get the settings widget."""
        # This plugin doesn't have settings
        return None

    def get_menu_actions(self):
        """Get the menu actions."""
        actions = []

        # Create the Git status action
        status_action = QAction("Git Status", None)
        status_action.triggered.connect(self.show_status)
        actions.append(status_action)

        # Create the Git commit action
        commit_action = QAction("Git Commit", None)
        commit_action.triggered.connect(self.show_commit)
        actions.append(commit_action)

        # Create the Git push action
        push_action = QAction("Git Push", None)
        push_action.triggered.connect(self.push)
        actions.append(push_action)

        # Create the Git pull action
        pull_action = QAction("Git Pull", None)
        pull_action.triggered.connect(self.pull)
        actions.append(pull_action)

        return actions

    def show_status(self):
        """Show the Git status."""
        # This is a mock implementation
        # In a real plugin, this would show a dialog with the Git status
        print("Showing Git status")

        # Create the status widget if it doesn't exist
        if self.status_widget is None:
            self.status_widget = GitStatusWidget(self)

        # Show the status widget
        self.status_widget.show()

    def show_commit(self):
        """Show the Git commit dialog."""
        # This is a mock implementation
        # In a real plugin, this would show a dialog for committing changes
        print("Showing Git commit dialog")

    def push(self):
        """Push changes to the remote repository."""
        # This is a mock implementation
        # In a real plugin, this would push changes to the remote repository
        print("Pushing changes to remote repository")

    def pull(self):
        """Pull changes from the remote repository."""
        # This is a mock implementation
        # In a real plugin, this would pull changes from the remote repository
        print("Pulling changes from remote repository")

    def get_status(self):
        """Get the Git status."""
        # This is a mock implementation
        # In a real plugin, this would get the Git status
        return {
            "file1.mono": "Modified",
            "file2.mono": "Added",
            "file3.mono": "Deleted"
        }

    def stage_file(self, file_path):
        """Stage a file."""
        # This is a mock implementation
        # In a real plugin, this would stage the file
        print(f"Staging file: {file_path}")

    def unstage_file(self, file_path):
        """Unstage a file."""
        # This is a mock implementation
        # In a real plugin, this would unstage the file
        print(f"Unstaging file: {file_path}")

    def discard_changes(self, file_path):
        """Discard changes to a file."""
        # This is a mock implementation
        # In a real plugin, this would discard changes to the file
        print(f"Discarding changes to file: {file_path}")
