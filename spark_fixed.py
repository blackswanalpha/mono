#!/usr/bin/env python3
"""
Fixed version of Spark editor
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog,
    QMenuBar, QMenu, QStatusBar, QToolBar, QSplitter, QTabWidget,
    QHBoxLayout, QLabel, QPushButton, QTreeView, QDockWidget, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon, QFont
from PyQt6.QtCore import Qt, QSize, QDir, QFileSystemModel

from spark.editor_fixed import CodeEditor
from spark.theme import ThemeManager

class MainWindow(QMainWindow):
    """Main window for the Spark editor"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spark Editor (Fixed)")
        self.resize(1200, 800)

        # Set up the UI
        self.setup_ui()

        # Set up the theme
        self.theme = ThemeManager.get_current_theme()
        self.update_theme()

    def setup_ui(self):
        """Set up the UI"""
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.main_splitter)

        # File browser
        self.file_browser = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        self.file_browser.setModel(self.file_model)
        self.file_browser.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.file_browser.setHeaderHidden(True)
        self.file_browser.setColumnHidden(1, True)
        self.file_browser.setColumnHidden(2, True)
        self.file_browser.setColumnHidden(3, True)
        self.file_browser.clicked.connect(self.file_clicked)

        # Editor tabs
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)

        # Add widgets to the splitter
        self.main_splitter.addWidget(self.file_browser)
        self.main_splitter.addWidget(self.editor_tabs)
        self.main_splitter.setSizes([200, 1000])

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Cursor position label
        self.cursor_position_label = QLabel("Line: 1, Column: 1")
        self.status_bar.addPermanentWidget(self.cursor_position_label)

        # Menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        # File menu
        self.file_menu = QMenu("File")
        self.menu_bar.addMenu(self.file_menu)

        # New file action
        self.new_file_action = QAction("New File")
        self.new_file_action.triggered.connect(self.new_file)
        self.file_menu.addAction(self.new_file_action)

        # Open file action
        self.open_file_action = QAction("Open File...")
        self.open_file_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_file_action)

        # Save file action
        self.save_file_action = QAction("Save")
        self.save_file_action.triggered.connect(self.save_file)
        self.file_menu.addAction(self.save_file_action)

        # Save file as action
        self.save_file_as_action = QAction("Save As...")
        self.save_file_as_action.triggered.connect(self.save_file_as)
        self.file_menu.addAction(self.save_file_as_action)

        # Exit action
        self.exit_action = QAction("Exit")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        # Edit menu
        self.edit_menu = QMenu("Edit")
        self.menu_bar.addMenu(self.edit_menu)

        # Undo action
        self.undo_action = QAction("Undo")
        self.undo_action.triggered.connect(self.undo)
        self.edit_menu.addAction(self.undo_action)

        # Redo action
        self.redo_action = QAction("Redo")
        self.redo_action.triggered.connect(self.redo)
        self.edit_menu.addAction(self.redo_action)

        # Cut action
        self.cut_action = QAction("Cut")
        self.cut_action.triggered.connect(self.cut)
        self.edit_menu.addAction(self.cut_action)

        # Copy action
        self.copy_action = QAction("Copy")
        self.copy_action.triggered.connect(self.copy)
        self.edit_menu.addAction(self.copy_action)

        # Paste action
        self.paste_action = QAction("Paste")
        self.paste_action.triggered.connect(self.paste)
        self.edit_menu.addAction(self.paste_action)

        # Select all action
        self.select_all_action = QAction("Select All")
        self.select_all_action.triggered.connect(self.select_all)
        self.edit_menu.addAction(self.select_all_action)

        # View menu
        self.view_menu = QMenu("View")
        self.menu_bar.addMenu(self.view_menu)

        # Toggle file browser action
        self.toggle_file_browser_action = QAction("Toggle File Browser")
        self.toggle_file_browser_action.triggered.connect(self.toggle_file_browser)
        self.view_menu.addAction(self.toggle_file_browser_action)

        # Help menu
        self.help_menu = QMenu("Help")
        self.menu_bar.addMenu(self.help_menu)

        # About action
        self.about_action = QAction("About")
        self.about_action.triggered.connect(self.about)
        self.help_menu.addAction(self.about_action)

    def update_theme(self):
        """Update the theme"""
        # Set the main window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.theme.bg_color};
                color: {self.theme.text_color};
            }}

            QTabWidget::pane {{
                border: 1px solid {self.theme.border_color};
                background-color: {self.theme.bg_color};
            }}

            QTabBar::tab {{
                background-color: {self.theme.tab_bg};
                color: {self.theme.text_color};
                border: 1px solid {self.theme.border_color};
                border-bottom-color: {self.theme.border_color};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }}

            QTabBar::tab:selected {{
                background-color: {self.theme.tab_selected_bg};
                border-bottom-color: {self.theme.tab_selected_bg};
            }}

            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}

            QTreeView {{
                background-color: {self.theme.panel_bg};
                color: {self.theme.text_color};
                border: none;
            }}

            QTreeView::item:selected {{
                background-color: {self.theme.selection_bg};
                color: {self.theme.selection_fg};
            }}

            QStatusBar {{
                background-color: {self.theme.status_bar_bg};
                color: {self.theme.text_color};
                border-top: 1px solid {self.theme.border_color};
            }}

            QMenuBar {{
                background-color: {self.theme.menu_bar_bg};
                color: {self.theme.text_color};
                border-bottom: 1px solid {self.theme.border_color};
            }}

            QMenuBar::item:selected {{
                background-color: {self.theme.selection_bg};
                color: {self.theme.selection_fg};
            }}

            QMenu {{
                background-color: {self.theme.menu_bg};
                color: {self.theme.text_color};
                border: 1px solid {self.theme.border_color};
            }}

            QMenu::item:selected {{
                background-color: {self.theme.selection_bg};
                color: {self.theme.selection_fg};
            }}
        """)

    def new_file(self):
        """Create a new file"""
        editor = CodeEditor()
        editor.cursorPositionChanged.connect(self.update_cursor_position)
        self.editor_tabs.addTab(editor, "Untitled")
        self.editor_tabs.setCurrentWidget(editor)

    def open_file(self):
        """Open a file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            self.open_file_path(file_path)

    def open_file_path(self, file_path):
        """Open a file at the given path"""
        # Check if the file is already open
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if editor.current_file == file_path:
                self.editor_tabs.setCurrentIndex(i)
                return

        # Create a new editor
        editor = CodeEditor()
        editor.cursorPositionChanged.connect(self.update_cursor_position)

        # Load the file
        if editor.load_file(file_path):
            # Add the editor to the tabs
            file_name = os.path.basename(file_path)
            self.editor_tabs.addTab(editor, file_name)
            self.editor_tabs.setCurrentWidget(editor)

            # Update the status bar
            self.status_bar.showMessage(f"Opened {file_path}")
        else:
            # Show an error message
            self.status_bar.showMessage(f"Error opening {file_path}")

    def save_file(self):
        """Save the current file"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            if editor.current_file:
                if editor.save_file():
                    self.status_bar.showMessage(f"Saved {editor.current_file}")
                else:
                    self.status_bar.showMessage(f"Error saving {editor.current_file}")
            else:
                self.save_file_as()

    def save_file_as(self):
        """Save the current file as"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File As")
            if file_path:
                if editor.save_file(file_path):
                    # Update the tab text
                    file_name = os.path.basename(file_path)
                    self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), file_name)

                    # Update the status bar
                    self.status_bar.showMessage(f"Saved {file_path}")
                else:
                    self.status_bar.showMessage(f"Error saving {file_path}")

    def close_tab(self, index):
        """Close a tab"""
        self.editor_tabs.removeTab(index)

    def file_clicked(self, index):
        """Handle file clicks in the file browser"""
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.open_file_path(file_path)

    def update_cursor_position(self, line, column):
        """Update the cursor position label"""
        self.cursor_position_label.setText(f"Line: {line}, Column: {column}")

    def toggle_file_browser(self):
        """Toggle the file browser visibility"""
        if self.file_browser.isVisible():
            self.file_browser.hide()
        else:
            self.file_browser.show()

    def undo(self):
        """Undo the last action"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.undo()

    def redo(self):
        """Redo the last action"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.redo()

    def cut(self):
        """Cut the selected text"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.cut()

    def copy(self):
        """Copy the selected text"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.copy()

    def paste(self):
        """Paste the clipboard text"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.paste()

    def select_all(self):
        """Select all text"""
        editor = self.editor_tabs.currentWidget()
        if editor:
            editor.selectAll()

    def about(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About Spark Editor", "Spark Editor is a code editor for the Mono language.")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Create a new file by default
    window.new_file()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
