#!/usr/bin/env python3
"""
Simple Spark editor
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog,
    QMenuBar, QMenu, QStatusBar, QPlainTextEdit, QLabel
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt

class SimpleEditor(QMainWindow):
    """Simple editor for testing"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Spark")
        self.resize(800, 600)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas, 'Courier New', monospace", 10))
        self.layout.addWidget(self.editor)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        self.file_menu = QMenu("File")
        self.menu_bar.addMenu(self.file_menu)
        
        # Open action
        self.open_action = QAction("Open")
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)
        
        # Save action
        self.save_action = QAction("Save")
        self.save_action.triggered.connect(self.save_file)
        self.file_menu.addAction(self.save_action)
        
        # Exit action
        self.exit_action = QAction("Exit")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # Current file
        self.current_file = None
    
    def open_file(self):
        """Open a file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = file_path
                self.status_bar.showMessage(f"Opened {file_path}")
                self.setWindowTitle(f"Simple Spark - {os.path.basename(file_path)}")
            except Exception as e:
                self.status_bar.showMessage(f"Error opening file: {str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w') as f:
                    f.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Saved {self.current_file}")
            except Exception as e:
                self.status_bar.showMessage(f"Error saving file: {str(e)}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the current file as"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.editor.toPlainText())
                self.current_file = file_path
                self.status_bar.showMessage(f"Saved {file_path}")
                self.setWindowTitle(f"Simple Spark - {os.path.basename(file_path)}")
            except Exception as e:
                self.status_bar.showMessage(f"Error saving file: {str(e)}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    editor = SimpleEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
