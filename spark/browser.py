"""
Enhanced project browser for Spark Editor
"""

import os
import logging
from PyQt6.QtWidgets import (
    QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QPushButton, QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction, QFileSystemModel, QAbstractFileIconProvider
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QFileInfo

from .theme import ThemeManager
from .icons import get_icon

# Configure logger
logger = logging.getLogger('spark_editor.browser')


class ProjectBrowser(QTreeView):
    """Enhanced file system browser for projects."""

    # Signals
    file_opened = pyqtSignal(str)
    file_run = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        """Set up the UI elements."""
        # Set up the model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.setModel(self.model)
        self.setRootIndex(self.model.index(QDir.currentPath()))

        # Hide unnecessary columns
        for i in range(1, self.model.columnCount()):
            self.hideColumn(i)

        # Hide header
        self.setHeaderHidden(True)

        # Set selection mode
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)

        # Set context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Connect double-click signal
        self.doubleClicked.connect(self.handle_double_click)

        # Set icons for files and folders
        self.model.setIconProvider(FileIconProvider())

    def update_theme(self):
        """Update the project browser's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()

        # Set colors
        self.setStyleSheet(f"""
            QTreeView {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: none;
                selection-background-color: {theme.primary_color};
                selection-color: {theme.text_bright_color};
                outline: none;
                padding: 5px;
            }}

            QTreeView::item {{
                padding: 5px;
                border-radius: {theme.border_radius}px;
            }}

            QTreeView::item:hover {{
                background-color: {theme.button_hover_bg};
            }}

            QTreeView::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}
        """)

    def show_context_menu(self, position):
        """Show context menu for the selected item."""
        try:
            index = self.indexAt(position)
            if not index.isValid():
                # Show context menu for the empty area
                self.show_empty_context_menu(position)
                return

            file_path = self.model.filePath(index)

            # Create context menu
            menu = QMenu()

            if os.path.isdir(file_path):
                # Directory context menu
                new_file_action = menu.addAction(get_icon("new_file"), "New File")
                new_folder_action = menu.addAction(get_icon("folder"), "New Folder")
                menu.addSeparator()
                open_in_explorer_action = menu.addAction("Open in File Explorer")
                menu.addSeparator()
                rename_action = menu.addAction("Rename")
                delete_action = menu.addAction("Delete")
            else:
                # File context menu
                open_action = menu.addAction(get_icon("open_file"), "Open")
                run_action = menu.addAction(get_icon("run_file"), "Run with Mono")
                menu.addSeparator()
                rename_action = menu.addAction("Rename")
                delete_action = menu.addAction("Delete")

            # Show the menu and get the selected action
            action = menu.exec(self.mapToGlobal(position))

            # Handle the selected action
            if action is None:
                return

            if os.path.isdir(file_path):
                # Directory actions
                if action == new_file_action:
                    self.create_new_file(file_path)
                elif action == new_folder_action:
                    self.create_new_folder(file_path)
                elif action == open_in_explorer_action:
                    self.open_in_explorer(file_path)
                elif action == rename_action:
                    self.rename_item(file_path)
                elif action == delete_action:
                    self.delete_item(file_path)
            else:
                # File actions
                if action == open_action:
                    self.file_opened.emit(file_path)
                elif action == run_action:
                    self.file_run.emit(file_path)
                elif action == rename_action:
                    self.rename_item(file_path)
                elif action == delete_action:
                    self.delete_item(file_path)
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt in show_context_menu")
        except Exception as e:
            logger.error(f"Error in show_context_menu: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def show_empty_context_menu(self, position):
        """Show context menu for the empty area."""
        try:
            menu = QMenu()

            new_file_action = menu.addAction(get_icon("new_file"), "New File")
            new_folder_action = menu.addAction(get_icon("folder"), "New Folder")
            menu.addSeparator()
            refresh_action = menu.addAction("Refresh")

            action = menu.exec(self.mapToGlobal(position))

            if action is None:
                return

            if action == new_file_action:
                self.create_new_file(QDir.currentPath())
            elif action == new_folder_action:
                self.create_new_folder(QDir.currentPath())
            elif action == refresh_action:
                self.model.setRootPath(QDir.currentPath())
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt in show_empty_context_menu")
        except Exception as e:
            logger.error(f"Error in show_empty_context_menu: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def handle_double_click(self, index):
        """Handle double click on an item."""
        try:
            file_path = self.model.filePath(index)

            if os.path.isfile(file_path):
                self.file_opened.emit(file_path)
        except KeyboardInterrupt:
            # Handle keyboard interrupt gracefully
            logger.warning("KeyboardInterrupt in handle_double_click")
        except Exception as e:
            # Log any other exceptions
            logger.error(f"Error in handle_double_click: {str(e)}")
            # Show error message to user
            QMessageBox.warning(self, "Error", f"Could not open file: {str(e)}")

    def create_new_file(self, directory):
        """Create a new file in the specified directory."""
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:")

        if ok and file_name:
            # Add .mono extension if not specified
            if not file_name.endswith(".mono"):
                file_name += ".mono"

            file_path = os.path.join(directory, file_name)

            try:
                with open(file_path, 'w') as f:
                    f.write("")

                # Open the new file
                self.file_opened.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file: {str(e)}")

    def create_new_folder(self, directory):
        """Create a new folder in the specified directory."""
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")

        if ok and folder_name:
            folder_path = os.path.join(directory, folder_name)

            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder: {str(e)}")

    def open_in_explorer(self, directory):
        """Open the directory in the system file explorer."""
        import subprocess
        import platform

        try:
            if platform.system() == "Windows":
                os.startfile(directory)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", directory])
            else:  # Linux
                subprocess.call(["xdg-open", directory])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open directory: {str(e)}")

    def rename_item(self, path):
        """Rename a file or folder."""
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)

        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)

            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename: {str(e)}")

    def delete_item(self, path):
        """Delete a file or folder."""
        item_type = "folder" if os.path.isdir(path) else "file"
        item_name = os.path.basename(path)

        reply = QMessageBox.question(self, "Delete", f"Are you sure you want to delete the {item_type} '{item_name}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete: {str(e)}")


class FileIconProvider(QAbstractFileIconProvider):
    """Custom icon provider for the file system model."""

    def __init__(self):
        super().__init__()

    def icon(self, type_or_info):
        """Return an icon for the given file info."""
        if isinstance(type_or_info, QFileInfo):
            if type_or_info.isDir():
                return get_icon("folder")
            elif type_or_info.suffix().lower() == "mono":
                return get_icon("mono_file")  # Use specific mono_file icon
            else:
                return QIcon()
        else:
            return QIcon()


class ProjectBrowserWidget(QWidget):
    """Widget containing the project browser with a header and toolbar."""

    # Signals
    file_opened = pyqtSignal(str)
    file_run = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        """Set up the UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setObjectName("browser-header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Header label
        header_label = QLabel("Projects")
        header_label.setObjectName("browser-header-label")
        header_layout.addWidget(header_label)

        # Add header to main layout
        main_layout.addWidget(header_widget)

        # Toolbar
        toolbar_widget = QWidget()
        toolbar_widget.setObjectName("browser-toolbar")
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)

        # Toolbar buttons
        new_file_btn = QPushButton()
        new_file_btn.setIcon(get_icon("new_file"))
        new_file_btn.setToolTip("New File")
        new_file_btn.setObjectName("browser-toolbar-button")
        new_file_btn.clicked.connect(self.create_new_file)

        new_folder_btn = QPushButton()
        new_folder_btn.setIcon(get_icon("folder"))
        new_folder_btn.setToolTip("New Folder")
        new_folder_btn.setObjectName("browser-toolbar-button")
        new_folder_btn.clicked.connect(self.create_new_folder)

        refresh_btn = QPushButton()
        refresh_btn.setIcon(get_icon("search"))
        refresh_btn.setToolTip("Refresh")
        refresh_btn.setObjectName("browser-toolbar-button")
        refresh_btn.clicked.connect(self.refresh)

        # Add buttons to toolbar
        toolbar_layout.addWidget(new_file_btn)
        toolbar_layout.addWidget(new_folder_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(refresh_btn)

        # Add toolbar to main layout
        main_layout.addWidget(toolbar_widget)

        # Project browser
        self.browser = ProjectBrowser()
        self.browser.file_opened.connect(self.file_opened.emit)
        self.browser.file_run.connect(self.file_run.emit)
        main_layout.addWidget(self.browser)

    def update_theme(self):
        """Update the project browser widget's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()

        # Update the browser
        self.browser.update_theme()

        # Update the header and toolbar
        self.setStyleSheet(f"""
            #browser-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}

            #browser-header-label {{
                color: {theme.text_color};
                font-weight: bold;
            }}

            #browser-toolbar {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}

            #browser-toolbar-button {{
                background-color: transparent;
                border: none;
                border-radius: {theme.border_radius}px;
                padding: 5px;
                icon-size: 16px;
            }}

            #browser-toolbar-button:hover {{
                background-color: {theme.button_hover_bg};
            }}

            #browser-toolbar-button:pressed {{
                background-color: {theme.primary_color};
            }}
        """)

    def create_new_file(self):
        """Create a new file in the current directory."""
        self.browser.create_new_file(QDir.currentPath())

    def create_new_folder(self):
        """Create a new folder in the current directory."""
        self.browser.create_new_folder(QDir.currentPath())

    def refresh(self):
        """Refresh the project browser."""
        self.browser.model.setRootPath(QDir.currentPath())
