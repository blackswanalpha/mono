#!/usr/bin/env python3
"""
Spark - A modern editor for Mono language
"""

import sys
import os
import logging
import traceback
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QSplitter, QTabWidget, QToolBar, QFileDialog,
    QMessageBox, QMenu, QTabBar, QPushButton
)
from PyQt6.QtCore import Qt, QDir, QSize, QTimer
from PyQt6.QtGui import QAction, QIcon, QTextCursor

# Add the parent directory to the Python path to access Mono modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, 'spark.log'))
    ]
)
logger = logging.getLogger('spark_editor.main')

# Import custom modules
from .theme import ThemeManager
from .icons import get_icon
from .editor import CodeEditor
from .terminal import TerminalWidget
from .browser import ProjectBrowserWidget
from .actions import QuickActionPanel
from .assistant import AIAssistantWidget
from .welcome import WelcomeScreen
from .splash import create_splash_screen
from .symbol_browser import SymbolBrowserWidget
from .refactoring import RefactoringManager
from .plugin_system import get_plugin_manager, get_marketplace
from .marketplace import PluginDialog
from .error_manager import ErrorManager
from .diagnostic_dialog import DiagnosticDialog
from .wayland_handler import setup_wayland_integration, handle_wayland_error, get_platform_info

class SparkEditor(QMainWindow):
    """Main window for the Spark editor."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

        # Apply theme
        ThemeManager.apply_theme(QApplication.instance())

        # Show the window
        self.setWindowTitle("Spark - Mono Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 700)  # Set minimum window size
        self.setWindowIcon(get_icon("app_icon"))

    def setup_ui(self):
        """Set up the UI elements."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create left panel (project browser, symbol browser, and quick actions)
        left_panel = QSplitter(Qt.Orientation.Vertical)
        left_panel.setChildrenCollapsible(False)  # Prevent widgets from being collapsed

        # Project browser
        self.project_browser = ProjectBrowserWidget()
        self.project_browser.file_opened.connect(self.open_file)
        self.project_browser.file_run.connect(self.run_mono_file)
        left_panel.addWidget(self.project_browser)

        # Symbol browser
        self.symbol_browser = SymbolBrowserWidget()
        self.symbol_browser.fileSymbolSelected.connect(self.goto_symbol)
        self.symbol_browser.globalSymbolSelected.connect(self.goto_global_symbol)
        self.symbol_browser.renameSymbolRequested.connect(self.rename_symbol)
        left_panel.addWidget(self.symbol_browser)

        # Initialize refactoring manager
        self.refactoring_manager = RefactoringManager(self)

        # Quick actions
        self.quick_actions = QuickActionPanel()
        self.quick_actions.new_file_clicked.connect(self.new_file)
        self.quick_actions.open_file_clicked.connect(self.open_file_dialog)
        self.quick_actions.save_file_clicked.connect(self.save_current_file)
        self.quick_actions.save_as_clicked.connect(self.save_as)
        self.quick_actions.run_file_clicked.connect(self.run_current_file)
        self.quick_actions.run_demo_clicked.connect(self.create_demo_file)
        left_panel.addWidget(self.quick_actions)

        # Set sizes for left panel
        left_panel.setSizes([400, 300, 200])

        # Create center panel (editor and terminal)
        center_panel = QSplitter(Qt.Orientation.Vertical)
        center_panel.setChildrenCollapsible(False)  # Prevent widgets from being collapsed

        # Editor tabs
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.editor_tabs.currentChanged.connect(self.handle_tab_changed)
        self.editor_tabs.setMinimumHeight(300)  # Set minimum height for editor

        # Set custom close button icon
        self.setup_tab_close_buttons()

        # Welcome screen
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.new_file_clicked.connect(self.new_file)
        self.welcome_screen.open_file_clicked.connect(self.open_file_dialog)
        self.welcome_screen.run_demo_clicked.connect(self.create_demo_file)

        # Add welcome screen to editor tabs
        self.editor_tabs.addTab(self.welcome_screen, "Welcome")

        # Terminal
        self.terminal_widget = TerminalWidget()
        self.terminal_widget.setMinimumHeight(100)  # Set minimum height for terminal

        # Add editor and terminal to center panel
        center_panel.addWidget(self.editor_tabs)
        center_panel.addWidget(self.terminal_widget)
        center_panel.setSizes([700, 300])  # Adjust the split ratio to give more space to editor

        # Create right panel with AI assistant
        right_panel = AIAssistantWidget()

        # Add panels to main splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(center_panel)
        self.main_splitter.addWidget(right_panel)

        # Set minimum widths to prevent panels from disappearing
        left_panel.setMinimumWidth(150)
        center_panel.setMinimumWidth(500)
        right_panel.setMinimumWidth(150)

        # Set the main splitter to be non-collapsible
        self.main_splitter.setChildrenCollapsible(False)

        # Set sizes for the main splitter
        self.main_splitter.setSizes([200, 800, 200])

        # Add main splitter to layout
        main_layout.addWidget(self.main_splitter)

        # Create status bar
        self.statusBar().showMessage("Ready")

        # Create toolbar
        self.create_toolbar()

        # Create menu
        self.create_menu()

    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add actions
        new_action = QAction(get_icon("new_file"), "New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        open_action = QAction(get_icon("open_file"), "Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)

        save_action = QAction(get_icon("save_file"), "Save", self)
        save_action.triggered.connect(self.save_current_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        run_action = QAction(get_icon("run_file"), "Run", self)
        run_action.triggered.connect(self.run_current_file)
        toolbar.addAction(run_action)

    def create_menu(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)

        # Run menu
        run_menu = menu_bar.addMenu("Run")

        run_action = QAction("Run Current File", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_current_file)
        run_menu.addAction(run_action)

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")

        plugin_manager_action = QAction("Plugin Manager", self)
        plugin_manager_action.triggered.connect(self.show_plugin_manager)
        tools_menu.addAction(plugin_manager_action)

        # Add a separator
        tools_menu.addSeparator()

        # Add the diagnostic dialog action
        diagnostic_action = QAction("Diagnostics", self)
        diagnostic_action.triggered.connect(self.show_diagnostic_dialog)
        tools_menu.addAction(diagnostic_action)

        run_demo_action = QAction("Run Mono Demo", self)
        run_demo_action.triggered.connect(self.create_demo_file)
        run_menu.addAction(run_demo_action)

        # View menu
        view_menu = menu_bar.addMenu("View")

        theme_menu = view_menu.addMenu("Theme")

        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme_action)

        nord_theme_action = QAction("Nord", self)
        nord_theme_action.triggered.connect(lambda: self.change_theme("nord"))
        theme_menu.addAction(nord_theme_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def update_theme(self, _=None):
        """Update the theme for all components."""
        # Update project browser
        self.project_browser.update_theme()

        # Update symbol browser
        self.symbol_browser.update_theme()

        # Update quick actions
        self.quick_actions.update_theme()

        # Update terminal
        self.terminal_widget.update_theme()

        # Update AI assistant
        self.main_splitter.widget(2).update_theme()

        # Update welcome screen
        self.welcome_screen.update_theme()

        # Update editors
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'update_theme'):
                widget.update_theme()

        # Update status bar
        self.statusBar().showMessage("Theme updated")

    def goto_symbol(self, symbol):
        """Go to a symbol in the current file."""
        editor = self.editor_tabs.currentWidget()
        if not editor or not hasattr(editor, 'document'):
            return

        # Go to the symbol position
        line = symbol.line
        column = symbol.column

        # Get the text block
        block = editor.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            # Create a cursor at the position
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, column - 1)

            # Set the cursor
            editor.setTextCursor(cursor)

            # Ensure the cursor is visible
            editor.ensureCursorVisible()

            # Update status bar
            self.statusBar().showMessage(f"Navigated to {symbol.symbol_type} '{symbol.name}'")

    def goto_global_symbol(self, symbol, file_path):
        """Go to a symbol in a specific file."""
        # Open the file if it's not already open
        self.open_file(file_path)

        # Go to the symbol
        self.goto_symbol(symbol)

    def change_theme(self, theme_name):
        """Change the theme."""
        if ThemeManager.apply_theme(QApplication.instance(), theme_name):
            self.update_theme()

    def handle_tab_changed(self, index):
        """Handle tab changed event."""
        if index == -1:
            # No tabs
            self.statusBar().showMessage("No file open")
            # Clear symbol browser
            self.symbol_browser.set_file_symbols({})
            return

        # Update status bar
        widget = self.editor_tabs.widget(index)
        if hasattr(widget, 'current_file') and widget.current_file:
            file_name = os.path.basename(widget.current_file)

            # Update cursor position
            if hasattr(widget, 'textCursor'):
                cursor = widget.textCursor()
                line = cursor.blockNumber() + 1
                column = cursor.columnNumber() + 1
                self.statusBar().showMessage(f"{file_name} - Line: {line}, Column: {column}")
            else:
                self.statusBar().showMessage(f"{file_name}")

            # Update symbol browser if the widget has code intelligence
            if hasattr(widget, 'code_intelligence'):
                symbols = widget.code_intelligence.analyzer.symbols
                self.symbol_browser.set_file_symbols(symbols, widget.current_file)
        else:
            self.statusBar().showMessage("No file open")
            # Clear symbol browser
            self.symbol_browser.set_file_symbols({})

    def new_file(self):
        """Create a new file."""
        editor = CodeEditor(self)
        editor.cursorPositionChanged.connect(self.update_cursor_position)
        self.editor_tabs.addTab(editor, "Untitled")
        self.editor_tabs.setCurrentWidget(editor)

        # Update tab close buttons
        QTimer.singleShot(50, self.setup_tab_close_buttons)

    def open_file_dialog(self):
        """Open a file dialog to select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Mono Files (*.mono);;All Files (*)"
        )
        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path):
        """Open a file in the editor."""
        # Check if the file is already open
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'current_file') and widget.current_file == file_path:
                self.editor_tabs.setCurrentIndex(i)
                return

        # Create a new editor and load the file
        editor = CodeEditor(self)
        editor.cursorPositionChanged.connect(self.update_cursor_position)
        if editor.load_file(file_path):
            file_name = os.path.basename(file_path)
            tab_index = self.editor_tabs.addTab(editor, file_name)

            # Set the Mono logo as the tab icon for .mono files
            if file_path.lower().endswith('.mono'):
                self.editor_tabs.setTabIcon(tab_index, get_icon("mono_file"))

            self.editor_tabs.setCurrentWidget(editor)
            self.statusBar().showMessage(f"Opened {file_path}")

            # Update tab close buttons
            QTimer.singleShot(50, self.setup_tab_close_buttons)

            # Add file to global symbol search if it's a Mono file
            if file_path.lower().endswith('.mono') and hasattr(editor, 'toPlainText'):
                self.symbol_browser.add_file_to_global_search(file_path, editor.toPlainText())

    def save_current_file(self):
        """Save the current file."""
        try:
            editor = self.editor_tabs.currentWidget()
            if not editor or not hasattr(editor, 'save_file'):
                return

            if not hasattr(editor, 'current_file') or not editor.current_file:
                self.save_as()
            else:
                if editor.save_file():
                    self.statusBar().showMessage(f"Saved {editor.current_file}")

                    # Update file in global symbol search if it's a Mono file
                    if editor.current_file.lower().endswith('.mono') and hasattr(editor, 'toPlainText'):
                        self.symbol_browser.add_file_to_global_search(editor.current_file, editor.toPlainText())
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt in save_current_file")
            self.statusBar().showMessage("Save operation interrupted")
        except Exception as e:
            logger.error(f"Error in save_current_file: {str(e)}")
            self.statusBar().showMessage(f"Error saving file: {str(e)}")
            QMessageBox.warning(self, "Save Error", f"Could not save file: {str(e)}")

    def save_as(self):
        """Save the current file with a new name."""
        try:
            editor = self.editor_tabs.currentWidget()
            if not editor or not hasattr(editor, 'save_file'):
                return

            # Use a safer approach with a try-except block for the file dialog
            try:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save File", "", "Mono Files (*.mono);;All Files (*)"
                )
            except KeyboardInterrupt:
                logger.warning("KeyboardInterrupt in file dialog")
                self.statusBar().showMessage("Save As operation interrupted")
                return
            except Exception as e:
                logger.error(f"Error in file dialog: {str(e)}")
                self.statusBar().showMessage(f"Error in file dialog: {str(e)}")
                QMessageBox.warning(self, "Save Error", f"Could not open save dialog: {str(e)}")
                return

            if file_path:
                if editor.save_file(file_path):
                    file_name = os.path.basename(file_path)
                    self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), file_name)
                    self.statusBar().showMessage(f"Saved {file_path}")

                    # Update file in global symbol search if it's a Mono file
                    if file_path.lower().endswith('.mono') and hasattr(editor, 'toPlainText'):
                        self.symbol_browser.add_file_to_global_search(file_path, editor.toPlainText())
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt in save_as")
            self.statusBar().showMessage("Save As operation interrupted")
        except Exception as e:
            logger.error(f"Error in save_as: {str(e)}")
            self.statusBar().showMessage(f"Error saving file: {str(e)}")
            QMessageBox.warning(self, "Save Error", f"Could not save file: {str(e)}")

    def close_tab(self, index):
        """Close a tab."""
        try:
            widget = self.editor_tabs.widget(index)

            # Check if the file has unsaved changes
            if hasattr(widget, 'document') and widget.document().isModified():
                try:
                    reply = QMessageBox.question(
                        self, "Unsaved Changes",
                        "The file has unsaved changes. Do you want to save them?",
                        QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                    )
                except Exception as e:
                    logger.error(f"Error showing message box: {str(e)}")
                    # Default to Cancel if the dialog fails
                    return

                if reply == QMessageBox.StandardButton.Save:
                    # Save the file
                    if hasattr(widget, 'current_file') and widget.current_file:
                        try:
                            widget.save_file()
                        except Exception as e:
                            logger.error(f"Error saving file: {str(e)}")
                            QMessageBox.warning(self, "Save Error", f"Could not save file: {str(e)}")
                            return
                    else:
                        # Use a safer approach with a try-except block for the file dialog
                        try:
                            file_path, _ = QFileDialog.getSaveFileName(
                                self, "Save File", "", "Mono Files (*.mono);;All Files (*)"
                            )
                        except KeyboardInterrupt:
                            logger.warning("KeyboardInterrupt in file dialog")
                            self.statusBar().showMessage("Save operation interrupted")
                            return
                        except Exception as e:
                            logger.error(f"Error in file dialog: {str(e)}")
                            QMessageBox.warning(self, "Save Error", f"Could not open save dialog: {str(e)}")
                            return

                        if file_path:
                            try:
                                widget.save_file(file_path)
                            except Exception as e:
                                logger.error(f"Error saving file: {str(e)}")
                                QMessageBox.warning(self, "Save Error", f"Could not save file: {str(e)}")
                                return
                        else:
                            # User cancelled the save dialog
                            return
                elif reply == QMessageBox.StandardButton.Cancel:
                    # Cancel the close operation
                    return

            # Remove file from global symbol search if it's a Mono file
            if hasattr(widget, 'current_file') and widget.current_file and widget.current_file.lower().endswith('.mono'):
                try:
                    self.symbol_browser.remove_file_from_global_search(widget.current_file)
                except Exception as e:
                    logger.error(f"Error removing file from symbol search: {str(e)}")
                    # Continue with tab closing even if symbol removal fails

            # Remove the tab
            self.editor_tabs.removeTab(index)

            # If there are no tabs left, show the welcome screen
            if self.editor_tabs.count() == 0:
                self.editor_tabs.addTab(self.welcome_screen, "Welcome")
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt in close_tab")
            self.statusBar().showMessage("Tab close operation interrupted")
        except Exception as e:
            logger.error(f"Error in close_tab: {str(e)}")
            self.statusBar().showMessage(f"Error closing tab: {str(e)}")
            QMessageBox.warning(self, "Error", f"Could not close tab: {str(e)}")

    def run_current_file(self):
        """Run the current file with Mono."""
        editor = self.editor_tabs.currentWidget()
        if not editor or not hasattr(editor, 'current_file') or not editor.current_file:
            QMessageBox.warning(self, "Warning", "No file to run.")
            return

        self.run_mono_file(editor.current_file)

    def run_mono_file(self, file_path):
        """Run a Mono file."""
        # Save the file first
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'current_file') and editor.current_file == file_path:
            editor.save_file()

        # Update status
        self.statusBar().showMessage(f"Running {os.path.basename(file_path)}...")

        # Run the file with Mono
        mono_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "mono")
        command = f"{mono_path} run {file_path}"
        self.terminal_widget.run_command(command)

        # Connect to terminal signals
        self.terminal_widget.terminal.command_finished.connect(self.handle_command_finished)

    def handle_command_finished(self, exit_code, _):
        """Handle command completion."""
        if exit_code == 0:
            self.statusBar().showMessage("Command completed successfully.")
        else:
            self.statusBar().showMessage(f"Command failed with exit code {exit_code}.")

    def update_cursor_position(self):
        """Update the cursor position in the status bar."""
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'textCursor'):
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.statusBar().showMessage(f"Line: {line}, Column: {column}")

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Spark",
            "<h3>Spark - A Modern Editor for Mono Language</h3>"
            "<p>Version 0.1.0</p>"
            "<p>Spark is a modern, intuitive editor designed specifically for the Mono language.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Syntax highlighting for Mono</li>"
            "<li>Integrated terminal</li>"
            "<li>Project browser</li>"
            "<li>Quick actions</li>"
            "<li>AI assistant</li>"
            "</ul>"
            "<p>© 2023 Mono Team</p>"
        )

    def undo(self):
        """Undo the last action."""
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'undo'):
            editor.undo()

    def redo(self):
        """Redo the last undone action."""
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'redo'):
            editor.redo()

    def cut(self):
        """Cut the selected text."""
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'cut'):
            editor.cut()

    def copy(self):
        """Copy the selected text."""
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'copy'):
            editor.copy()

    def paste(self):
        """Paste the clipboard text."""
        editor = self.editor_tabs.currentWidget()
        if editor and hasattr(editor, 'paste'):
            editor.paste()

    def rename_symbol(self, symbol, file_path):
        """Rename a symbol across the codebase."""
        # Use the refactoring manager to rename the symbol
        self.refactoring_manager.rename_symbol(symbol, file_path)

    def show_plugin_manager(self):
        """Show the plugin manager dialog."""
        dialog = PluginDialog(self)
        dialog.exec()

    def show_diagnostic_dialog(self):
        """Show the diagnostic dialog."""
        dialog = DiagnosticDialog(self)
        dialog.exec()

    def setup_tab_close_buttons(self):
        """Set up custom close buttons for tabs."""
        # Apply the icon to all tab close buttons
        def update_tab_close_buttons():
            # This is a bit of a hack to access the internal tab bar
            tab_bar = self.editor_tabs.findChild(QTabBar)
            if tab_bar:
                for i in range(tab_bar.count()):
                    # Skip the welcome tab
                    if self.editor_tabs.tabText(i) == "Welcome":
                        continue

                    # Set the close button icon for this tab
                    tab_bar.setTabButton(i, QTabBar.ButtonPosition.RightSide,
                                        self.create_tab_close_button(i))

        # Connect to tabBarClicked signal to update buttons when tabs are clicked
        self.editor_tabs.tabBarClicked.connect(lambda: update_tab_close_buttons())

        # Connect to tabAdded signal to update buttons when tabs are added
        self.editor_tabs.tabBarDoubleClicked.connect(lambda: update_tab_close_buttons())

        # Initial update
        QTimer.singleShot(100, update_tab_close_buttons)

    def create_tab_close_button(self, tab_index):
        """Create a custom close button for a tab."""
        button = QPushButton()
        button.setIcon(get_icon("close"))
        button.setFixedSize(16, 16)
        button.setFlat(True)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.2);
                border-radius: 8px;
            }
        """)
        button.clicked.connect(lambda: self.close_tab(tab_index))
        return button

    def new_file_from_template(self, template_path, file_name):
        """Create a new file from a template."""
        try:
            # Read the template content
            with open(template_path, 'r') as f:
                template_content = f.read()

            # Create a new editor and set the content
            editor = CodeEditor(self)
            editor.cursorPositionChanged.connect(self.update_cursor_position)
            editor.setPlainText(template_content)

            # Add the tab
            tab_index = self.editor_tabs.addTab(editor, file_name)

            # Set the Mono logo as the tab icon for .mono files
            if file_name.lower().endswith('.mono'):
                self.editor_tabs.setTabIcon(tab_index, get_icon("mono_file"))

            self.editor_tabs.setCurrentWidget(editor)

            # Show a status message
            self.statusBar().showMessage(f"Created new file from template: {os.path.basename(template_path)}")

            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create file from template: {str(e)}")
            return False

    def create_demo_file(self):
        """Create a demo Mono file and run it."""
        demo_content = """//  __  __
// |  \/  | ___  _ __   ___
// | |\/| |/ _ \| '_ \ / _ \
// | |  | | (_) | | | | (_) |
// |_|  |_|\___/|_| |_|\___/
//
// Mono Language - A simple demo created with Spark Editor

component DemoApp {
    state {
        message: string = "Hello from Spark Editor!";
        count: number = 0;
    }

    function increment() {
        this.count = this.count + 1;
        print "Count incremented to " + this.count;
    }

    function run() {
        print this.message;
        print "Starting counter...";

        for var i = 0; i < 5; i++ {
            this.increment();
        }

        print "Demo completed!";
    }
}

component Main {
    function start() {
        print "Starting Spark Demo App...";
        var app = new DemoApp();
        app.run();
    }
}
"""

        # Create a new editor and set the content
        editor = CodeEditor(self)
        editor.cursorPositionChanged.connect(self.update_cursor_position)
        editor.setPlainText(demo_content)

        # Save the file
        demo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "spark_demo.mono")

        # Create the templates directory if it doesn't exist
        os.makedirs(os.path.dirname(demo_path), exist_ok=True)

        editor.save_file(demo_path)

        # Add the tab
        tab_index = self.editor_tabs.addTab(editor, "spark_demo.mono")

        # Set the Mono logo as the tab icon
        self.editor_tabs.setTabIcon(tab_index, get_icon("mono_file"))

        self.editor_tabs.setCurrentWidget(editor)

        # Run the demo
        self.run_mono_file(demo_path)

        return demo_path

def main():
    """Main entry point for the application."""
    try:
        # Set up Wayland integration before creating the application
        setup_wayland_integration()

        # Log platform information
        platform_info = get_platform_info()
        logger.info(f"Platform information: {platform_info}")

        # Patch Qt enums for safe interrupt handling
        from .enum_wrapper import patch_qt_enums
        patch_qt_enums()

        # Install a custom exception hook to handle KeyboardInterrupt
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                logger.warning("KeyboardInterrupt detected in main thread - handling gracefully")
                # Don't show traceback for KeyboardInterrupt
                return
            # For other exceptions, use the default exception hook
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        # Install the custom exception hook
        sys.excepthook = custom_excepthook

        # Create the application
        app = QApplication(sys.argv)

        # Set up exception handler for Qt
        def qt_message_handler(mode, _context, message):
            # _context is unused but required by Qt's message handler signature
            if "Wayland" in message and "error" in message.lower():
                logger.error(f"Qt Wayland error: {message}")
                handle_wayland_error(message)
            elif "Could not load the Qt platform plugin" in message and "xcb" in message:
                logger.error(f"Qt XCB error: {message}")
                handle_wayland_error(message)  # Reuse the same handler for XCB errors
            elif mode == QtMsgType.QtFatalMsg:
                logger.critical(f"Qt fatal error: {message}")
            elif mode == QtMsgType.QtCriticalMsg:
                logger.critical(f"Qt critical error: {message}")
            elif mode == QtMsgType.QtWarningMsg:
                logger.warning(f"Qt warning: {message}")
            elif mode == QtMsgType.QtInfoMsg:
                logger.info(f"Qt info: {message}")
            else:
                logger.debug(f"Qt debug: {message}")

        # Install the message handler if possible
        try:
            from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
            qInstallMessageHandler(qt_message_handler)
            logger.info("Installed Qt message handler")
        except ImportError:
            logger.warning("Could not install Qt message handler")

        # Apply the default theme
        ThemeManager.apply_theme(app, "dark")

        # Show splash screen
        splash = create_splash_screen()
        splash.show()

        # Process events to ensure splash is displayed
        app.processEvents()

        # Create main window
        window = SparkEditor()

        # Make sure the window is visible
        window.show()

        # Show splash for 2 seconds, then finish it
        splash.show_and_finish(window, 2000)

        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")

        # Show error message to user
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Fatal Error",
                                f"A fatal error occurred: {str(e)}\n\n"
                                f"Please check the log file for details.")
        except:
            print(f"FATAL ERROR: {str(e)}")
            print(traceback.format_exc())

        sys.exit(1)

if __name__ == "__main__":
    main()
