"""
Diagnostic dialog for Spark Editor.

This module provides a dialog for displaying diagnostic information
and error reports to help users troubleshoot issues.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QTabWidget, QWidget, QListWidget, QListWidgetItem, QSplitter,
    QFileDialog, QMessageBox, QCheckBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from .error_manager import ErrorManager, ErrorType, ErrorContext, save_diagnostic_report

class ErrorListItem(QListWidgetItem):
    """List item for displaying an error in the diagnostic dialog."""
    
    def __init__(self, error_context: ErrorContext):
        super().__init__()
        self.error_context = error_context
        self.setText(f"{error_context.timestamp.strftime('%H:%M:%S')} - {error_context.error_type.value}: {type(error_context.exception).__name__}")
        self.setToolTip(str(error_context.exception))

class DiagnosticDialog(QDialog):
    """Dialog for displaying diagnostic information and error reports."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spark Editor Diagnostics")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_errors()
    
    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Create the tab widget
        self.tab_widget = QTabWidget()
        
        # Create the errors tab
        self.errors_tab = QWidget()
        self.setup_errors_tab()
        self.tab_widget.addTab(self.errors_tab, "Errors")
        
        # Create the system tab
        self.system_tab = QWidget()
        self.setup_system_tab()
        self.tab_widget.addTab(self.system_tab, "System")
        
        # Create the settings tab
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Add the tab widget to the layout
        layout.addWidget(self.tab_widget)
        
        # Create the button layout
        button_layout = QHBoxLayout()
        
        # Create the save report button
        save_report_button = QPushButton("Save Diagnostic Report")
        save_report_button.clicked.connect(self.save_report)
        button_layout.addWidget(save_report_button)
        
        # Create the clear errors button
        clear_errors_button = QPushButton("Clear Error History")
        clear_errors_button.clicked.connect(self.clear_errors)
        button_layout.addWidget(clear_errors_button)
        
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
    
    def setup_errors_tab(self):
        """Set up the errors tab."""
        # Create the layout
        layout = QVBoxLayout(self.errors_tab)
        
        # Create the splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create the error list
        self.error_list = QListWidget()
        self.error_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.error_list.currentItemChanged.connect(self.error_selected)
        splitter.addWidget(self.error_list)
        
        # Create the error details
        self.error_details = QTextEdit()
        self.error_details.setReadOnly(True)
        splitter.addWidget(self.error_details)
        
        # Set the splitter sizes
        splitter.setSizes([200, 400])
        
        # Add the splitter to the layout
        layout.addWidget(splitter)
        
        # Set the layout
        self.errors_tab.setLayout(layout)
    
    def setup_system_tab(self):
        """Set up the system tab."""
        # Create the layout
        layout = QVBoxLayout(self.system_tab)
        
        # Create the system info text edit
        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        layout.addWidget(self.system_info)
        
        # Set the system info
        self.system_info.setText(self.get_system_info())
        
        # Set the layout
        self.system_tab.setLayout(layout)
    
    def setup_settings_tab(self):
        """Set up the settings tab."""
        # Create the layout
        layout = QVBoxLayout(self.settings_tab)
        
        # Create the error handling group
        error_handling_group = QGroupBox("Error Handling")
        error_handling_layout = QVBoxLayout()
        
        # Create the enable error handling checkbox
        self.enable_error_handling = QCheckBox("Enable Error Handling")
        self.enable_error_handling.setChecked(ErrorManager.get_instance().is_enabled())
        self.enable_error_handling.toggled.connect(self.toggle_error_handling)
        error_handling_layout.addWidget(self.enable_error_handling)
        
        # Create the error type checkboxes
        for error_type in ErrorType:
            checkbox = QCheckBox(f"Handle {error_type.value} errors")
            checkbox.setChecked(True)
            error_handling_layout.addWidget(checkbox)
        
        # Set the error handling group layout
        error_handling_group.setLayout(error_handling_layout)
        
        # Add the error handling group to the main layout
        layout.addWidget(error_handling_group)
        
        # Create the recovery group
        recovery_group = QGroupBox("Recovery Strategies")
        recovery_layout = QVBoxLayout()
        
        # Create the recovery strategy checkboxes
        for error_type in ErrorType:
            checkbox = QCheckBox(f"Enable recovery for {error_type.value} errors")
            checkbox.setChecked(True)
            recovery_layout.addWidget(checkbox)
        
        # Set the recovery group layout
        recovery_group.setLayout(recovery_layout)
        
        # Add the recovery group to the main layout
        layout.addWidget(recovery_group)
        
        # Add a spacer
        layout.addStretch()
        
        # Set the layout
        self.settings_tab.setLayout(layout)
    
    def load_errors(self):
        """Load errors from the error manager."""
        # Clear the list
        self.error_list.clear()
        
        # Get the error history
        error_history = ErrorManager.get_instance().get_error_history()
        
        # Add each error to the list
        for error_context in reversed(error_history):
            item = ErrorListItem(error_context)
            self.error_list.addItem(item)
        
        # Select the first item if there are any
        if self.error_list.count() > 0:
            self.error_list.setCurrentRow(0)
    
    def error_selected(self, current, previous):
        """Handle error selection."""
        if current is None:
            self.error_details.clear()
            return
        
        # Get the error context
        error_context = current.error_context
        
        # Set the error details
        self.error_details.setText(str(error_context))
    
    def get_system_info(self) -> str:
        """Get system information."""
        info = []
        info.append("=== System Information ===")
        info.append(f"Python Version: {sys.version}")
        info.append(f"Platform: {sys.platform}")
        info.append(f"PyQt Version: {Qt.qVersion()}")
        
        # Add environment variables
        info.append("\n=== Environment Variables ===")
        for key, value in os.environ.items():
            info.append(f"{key}: {value}")
        
        return "\n".join(info)
    
    def save_report(self):
        """Save a diagnostic report."""
        # Ask for a file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Diagnostic Report", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            # Save the report
            try:
                report_path = save_diagnostic_report(file_path)
                QMessageBox.information(
                    self, "Report Saved", f"Diagnostic report saved to {report_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save diagnostic report: {str(e)}"
                )
    
    def clear_errors(self):
        """Clear the error history."""
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to clear the error history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear the error history
            ErrorManager.get_instance().clear_error_history()
            
            # Reload the errors
            self.load_errors()
    
    def toggle_error_handling(self, enabled):
        """Toggle error handling."""
        if enabled:
            ErrorManager.get_instance().enable()
        else:
            ErrorManager.get_instance().disable()
