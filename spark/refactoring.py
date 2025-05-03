"""
Refactoring tools for Spark Editor
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDialogButtonBox, QCheckBox, QListWidget, QListWidgetItem, QMessageBox,
    QProgressDialog, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from .code_intelligence import MonoSymbol
from .optimized_code_intelligence import OptimizedMonoCodeAnalyzer

class RenameSymbolDialog(QDialog):
    """Dialog for renaming symbols"""
    
    def __init__(self, symbol: MonoSymbol, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements"""
        self.setWindowTitle("Rename Symbol")
        self.resize(400, 200)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Symbol info
        self.info_label = QLabel(f"Rename {self.symbol.symbol_type} '{self.symbol.name}'")
        self.info_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.info_label)
        
        # New name input
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("New name:")
        self.name_input = QLineEdit(self.symbol.name)
        self.name_input.selectAll()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)
        self.layout.addLayout(self.name_layout)
        
        # Options
        self.preview_checkbox = QCheckBox("Preview changes")
        self.preview_checkbox.setChecked(True)
        self.layout.addWidget(self.preview_checkbox)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
    
    def get_new_name(self) -> str:
        """Get the new name for the symbol"""
        return self.name_input.text()
    
    def should_preview(self) -> bool:
        """Check if changes should be previewed"""
        return self.preview_checkbox.isChecked()

class PreviewChangesDialog(QDialog):
    """Dialog for previewing changes"""
    
    def __init__(self, changes: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.changes = changes
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements"""
        self.setWindowTitle("Preview Changes")
        self.resize(600, 400)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Info label
        self.info_label = QLabel(f"The following {len(self.changes)} changes will be made:")
        self.layout.addWidget(self.info_label)
        
        # Changes list
        self.changes_list = QListWidget()
        for change in self.changes:
            item = QListWidgetItem()
            file_path = change.get("file_path", "")
            line = change.get("line", 0)
            old_text = change.get("old_text", "")
            new_text = change.get("new_text", "")
            
            item.setText(f"{os.path.basename(file_path)}:{line} - Replace '{old_text}' with '{new_text}'")
            item.setToolTip(file_path)
            
            self.changes_list.addItem(item)
        
        self.layout.addWidget(self.changes_list)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

class RefactoringManager:
    """Manager for refactoring operations"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.analyzer = OptimizedMonoCodeAnalyzer()
    
    def rename_symbol(self, symbol: MonoSymbol, file_path: str) -> bool:
        """Rename a symbol across the codebase"""
        # Show the rename dialog
        dialog = RenameSymbolDialog(symbol, self.main_window)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        
        new_name = dialog.get_new_name()
        should_preview = dialog.should_preview()
        
        # Validate the new name
        if not new_name or new_name == symbol.name:
            return False
        
        # Find all occurrences of the symbol
        changes = self._find_symbol_occurrences(symbol, file_path, new_name)
        
        # Preview changes if requested
        if should_preview and changes:
            preview_dialog = PreviewChangesDialog(changes, self.main_window)
            if preview_dialog.exec() != QDialog.DialogCode.Accepted:
                return False
        
        # Apply changes
        if changes:
            self._apply_changes(changes)
            return True
        
        return False
    
    def _find_symbol_occurrences(self, symbol: MonoSymbol, file_path: str, new_name: str) -> List[Dict[str, Any]]:
        """Find all occurrences of a symbol in the codebase"""
        changes = []
        
        # Get all open files
        open_files = {}
        for i in range(self.main_window.editor_tabs.count()):
            editor = self.main_window.editor_tabs.widget(i)
            if hasattr(editor, 'current_file') and editor.current_file:
                open_files[editor.current_file] = editor.toPlainText()
        
        # Start with the current file
        if file_path in open_files:
            file_changes = self._find_symbol_in_file(symbol, file_path, open_files[file_path], new_name)
            changes.extend(file_changes)
        
        # Check other open files
        for other_file, content in open_files.items():
            if other_file != file_path and other_file.lower().endswith('.mono'):
                file_changes = self._find_symbol_in_file(symbol, other_file, content, new_name)
                changes.extend(file_changes)
        
        return changes
    
    def _find_symbol_in_file(self, symbol: MonoSymbol, file_path: str, content: str, new_name: str) -> List[Dict[str, Any]]:
        """Find all occurrences of a symbol in a file"""
        changes = []
        
        # Analyze the file
        self.analyzer.analyze(content, file_path)
        
        # Find the symbol in this file
        file_symbol = None
        for name, s in self.analyzer.symbols.items():
            if s.symbol_type == symbol.symbol_type and s.name == symbol.name and s.scope == symbol.scope:
                file_symbol = s
                break
        
        if not file_symbol:
            return changes
        
        # Find all references to the symbol
        lines = content.split('\n')
        
        # Different search patterns based on symbol type
        if symbol.symbol_type == "component":
            # Find component declarations
            pattern = r'component\s+(' + re.escape(symbol.name) + r')\s*{'
            for i, line in enumerate(lines):
                for match in re.finditer(pattern, line):
                    changes.append({
                        "file_path": file_path,
                        "line": i + 1,
                        "column": match.start(1) + 1,
                        "old_text": symbol.name,
                        "new_text": new_name
                    })
            
            # Find component usages
            pattern = r'<(' + re.escape(symbol.name) + r')[\s/>]'
            for i, line in enumerate(lines):
                for match in re.finditer(pattern, line):
                    changes.append({
                        "file_path": file_path,
                        "line": i + 1,
                        "column": match.start(1) + 1,
                        "old_text": symbol.name,
                        "new_text": new_name
                    })
        
        elif symbol.symbol_type == "function":
            # Find function declarations
            pattern = r'function\s+(' + re.escape(symbol.name) + r')\s*\('
            for i, line in enumerate(lines):
                for match in re.finditer(pattern, line):
                    changes.append({
                        "file_path": file_path,
                        "line": i + 1,
                        "column": match.start(1) + 1,
                        "old_text": symbol.name,
                        "new_text": new_name
                    })
            
            # Find function calls
            if symbol.scope:
                # Method calls
                pattern = r'this\.(' + re.escape(symbol.name) + r')\s*\('
                for i, line in enumerate(lines):
                    for match in re.finditer(pattern, line):
                        changes.append({
                            "file_path": file_path,
                            "line": i + 1,
                            "column": match.start(1) + 1,
                            "old_text": symbol.name,
                            "new_text": new_name
                        })
            else:
                # Global function calls
                pattern = r'(?<!\.)(' + re.escape(symbol.name) + r')\s*\('
                for i, line in enumerate(lines):
                    for match in re.finditer(pattern, line):
                        changes.append({
                            "file_path": file_path,
                            "line": i + 1,
                            "column": match.start(1) + 1,
                            "old_text": symbol.name,
                            "new_text": new_name
                        })
        
        elif symbol.symbol_type == "variable":
            # Find variable declarations
            pattern = r'var\s+(' + re.escape(symbol.name) + r')\s*[=:]'
            for i, line in enumerate(lines):
                for match in re.finditer(pattern, line):
                    changes.append({
                        "file_path": file_path,
                        "line": i + 1,
                        "column": match.start(1) + 1,
                        "old_text": symbol.name,
                        "new_text": new_name
                    })
            
            # Find variable usages
            if symbol.scope:
                # Instance variable
                pattern = r'this\.(' + re.escape(symbol.name) + r')(?!\s*\()'
                for i, line in enumerate(lines):
                    for match in re.finditer(pattern, line):
                        changes.append({
                            "file_path": file_path,
                            "line": i + 1,
                            "column": match.start(1) + 1,
                            "old_text": symbol.name,
                            "new_text": new_name
                        })
            else:
                # Global variable
                pattern = r'(?<!\.)(' + re.escape(symbol.name) + r')(?!\s*\()'
                for i, line in enumerate(lines):
                    for match in re.finditer(pattern, line):
                        # Skip variable declarations (already handled)
                        if re.search(r'var\s+' + re.escape(symbol.name) + r'\s*[=:]', line):
                            continue
                        
                        changes.append({
                            "file_path": file_path,
                            "line": i + 1,
                            "column": match.start(1) + 1,
                            "old_text": symbol.name,
                            "new_text": new_name
                        })
        
        return changes
    
    def _apply_changes(self, changes: List[Dict[str, Any]]) -> None:
        """Apply the changes to the files"""
        # Group changes by file
        file_changes = {}
        for change in changes:
            file_path = change.get("file_path", "")
            if file_path not in file_changes:
                file_changes[file_path] = []
            file_changes[file_path].append(change)
        
        # Create a progress dialog
        progress = QProgressDialog("Applying changes...", "Cancel", 0, len(file_changes), self.main_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Apply changes to each file
        for i, (file_path, changes) in enumerate(file_changes.items()):
            progress.setValue(i)
            QApplication.processEvents()
            
            if progress.wasCanceled():
                break
            
            # Open the file if it's not already open
            self.main_window.open_file(file_path)
            
            # Get the editor for this file
            editor = None
            for j in range(self.main_window.editor_tabs.count()):
                widget = self.main_window.editor_tabs.widget(j)
                if hasattr(widget, 'current_file') and widget.current_file == file_path:
                    editor = widget
                    break
            
            if not editor:
                continue
            
            # Apply changes to the editor
            content = editor.toPlainText()
            lines = content.split('\n')
            
            # Sort changes by line and column in reverse order
            # This ensures that changes to the same line don't affect each other
            sorted_changes = sorted(changes, key=lambda c: (c.get("line", 0), c.get("column", 0)), reverse=True)
            
            for change in sorted_changes:
                line = change.get("line", 0) - 1  # Convert to 0-based index
                column = change.get("column", 0) - 1  # Convert to 0-based index
                old_text = change.get("old_text", "")
                new_text = change.get("new_text", "")
                
                if 0 <= line < len(lines):
                    line_text = lines[line]
                    if column + len(old_text) <= len(line_text):
                        # Replace the text
                        new_line = line_text[:column] + new_text + line_text[column + len(old_text):]
                        lines[line] = new_line
            
            # Update the editor content
            editor.setPlainText('\n'.join(lines))
            
            # Save the file
            editor.save_file()
        
        progress.setValue(len(file_changes))
        
        # Show a success message
        QMessageBox.information(self.main_window, "Rename Symbol", f"Successfully renamed symbol in {len(file_changes)} files.")

class ExtractMethodDialog(QDialog):
    """Dialog for extracting a method"""
    
    def __init__(self, code: str, parent=None):
        super().__init__(parent)
        self.code = code
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements"""
        self.setWindowTitle("Extract Method")
        self.resize(400, 300)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Method name input
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("Method name:")
        self.name_input = QLineEdit("extractedMethod")
        self.name_input.selectAll()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)
        self.layout.addLayout(self.name_layout)
        
        # Code preview
        self.preview_label = QLabel("Code to extract:")
        self.layout.addWidget(self.preview_label)
        
        self.code_preview = QLabel(self.code)
        self.code_preview.setStyleSheet("background-color: #f0f0f0; padding: 10px; font-family: monospace;")
        self.code_preview.setWordWrap(True)
        self.layout.addWidget(self.code_preview)
        
        # Options
        self.return_checkbox = QCheckBox("Add return statement")
        self.layout.addWidget(self.return_checkbox)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
    
    def get_method_name(self) -> str:
        """Get the method name"""
        return self.name_input.text()
    
    def should_add_return(self) -> bool:
        """Check if a return statement should be added"""
        return self.return_checkbox.isChecked()
