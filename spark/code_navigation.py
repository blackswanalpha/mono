"""
Code Navigation for Spark Editor
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QPushButton, QSplitter, QTextEdit, QDialog, QDialogButtonBox, QMenu
)
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QIcon, QTextCursor, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from .theme import ThemeManager
from .icons import get_icon
from .code_intelligence import MonoSymbol

class SymbolTreeItem(QTreeWidgetItem):
    """Tree item for displaying a symbol"""
    
    def __init__(self, symbol, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.setText(0, symbol.name)
        self.setIcon(0, self._get_icon())
        
        # Add tooltip
        self.setToolTip(0, symbol.get_signature())
        
        # Add child items for component symbols
        if symbol.symbol_type == "component":
            # Add state variables
            state_vars = symbol.details.get("state", [])
            if state_vars:
                state_item = QTreeWidgetItem(self)
                state_item.setText(0, "State")
                state_item.setIcon(0, self._get_icon("state"))
                
                for var in state_vars:
                    var_item = QTreeWidgetItem(state_item)
                    var_item.setText(0, f"{var.get('name')}: {var.get('type', 'any')}")
                    var_item.setIcon(0, self._get_icon("variable"))
    
    def _get_icon(self, symbol_type=None):
        """Get the icon for the symbol"""
        if not symbol_type:
            symbol_type = self.symbol.symbol_type
        
        if symbol_type == "component":
            return get_icon("component")
        elif symbol_type == "function":
            return get_icon("function")
        elif symbol_type == "variable":
            return get_icon("variable")
        elif symbol_type == "state":
            return get_icon("state")
        else:
            return get_icon("symbol")

class SymbolNavigator(QWidget):
    """Widget for navigating symbols in the code"""
    
    symbolSelected = pyqtSignal(MonoSymbol)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()
    
    def setup_ui(self):
        """Set up the UI elements"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = QWidget()
        self.header.setObjectName("symbols-header")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.title_label = QLabel("Symbols")
        self.title_label.setObjectName("symbols-title")
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        self.layout.addWidget(self.header)
        
        # Symbols tree
        self.symbols_tree = QTreeWidget()
        self.symbols_tree.setObjectName("symbols-tree")
        self.symbols_tree.setHeaderHidden(True)
        self.symbols_tree.itemClicked.connect(self._handle_item_clicked)
        self.layout.addWidget(self.symbols_tree)
    
    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            #symbols-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}
            
            #symbols-title {{
                font-weight: bold;
                color: {theme.text_color};
            }}
            
            #symbols-tree {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: none;
            }}
            
            #symbols-tree::item {{
                padding: 5px;
            }}
            
            #symbols-tree::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}
            
            #symbols-tree::item:hover:!selected {{
                background-color: {theme.secondary_color};
            }}
        """)
    
    def set_symbols(self, symbols):
        """Set the symbols to display"""
        self.symbols_tree.clear()
        
        # Group symbols by type
        components = []
        functions = []
        variables = []
        
        for symbol in symbols.values():
            if symbol.symbol_type == "component":
                components.append(symbol)
            elif symbol.symbol_type == "function":
                functions.append(symbol)
            elif symbol.symbol_type == "variable":
                variables.append(symbol)
        
        # Add components
        for symbol in sorted(components, key=lambda s: s.name):
            item = SymbolTreeItem(symbol)
            self.symbols_tree.addTopLevelItem(item)
            
            # Add functions and variables that belong to this component
            component_functions = [s for s in functions if s.scope == symbol.name]
            component_variables = [s for s in variables if s.scope == symbol.name]
            
            # Add functions
            if component_functions:
                functions_item = QTreeWidgetItem(item)
                functions_item.setText(0, "Functions")
                functions_item.setIcon(0, get_icon("function"))
                
                for func in sorted(component_functions, key=lambda s: s.name):
                    func_item = SymbolTreeItem(func, functions_item)
            
            # Add variables
            if component_variables:
                variables_item = QTreeWidgetItem(item)
                variables_item.setText(0, "Variables")
                variables_item.setIcon(0, get_icon("variable"))
                
                for var in sorted(component_variables, key=lambda s: s.name):
                    var_item = SymbolTreeItem(var, variables_item)
        
        # Expand all items
        self.symbols_tree.expandAll()
    
    def _handle_item_clicked(self, item, column):
        """Handle item click"""
        if isinstance(item, SymbolTreeItem):
            self.symbolSelected.emit(item.symbol)

class NavigationManager:
    """Manager for code navigation features"""
    
    def __init__(self, editor):
        self.editor = editor
        self.current_position = None
        self.navigation_history = []
        self.navigation_index = -1
    
    def go_to_definition(self, symbol):
        """Go to the definition of a symbol"""
        if not symbol:
            return
        
        # Save current position
        self._save_current_position()
        
        # Go to the symbol position
        self._go_to_position(symbol.line, symbol.column)
    
    def go_back(self):
        """Go back in the navigation history"""
        if self.navigation_index <= 0:
            return
        
        self.navigation_index -= 1
        position = self.navigation_history[self.navigation_index]
        self._go_to_position(position["line"], position["column"], add_to_history=False)
    
    def go_forward(self):
        """Go forward in the navigation history"""
        if self.navigation_index >= len(self.navigation_history) - 1:
            return
        
        self.navigation_index += 1
        position = self.navigation_history[self.navigation_index]
        self._go_to_position(position["line"], position["column"], add_to_history=False)
    
    def _save_current_position(self):
        """Save the current position to the navigation history"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        
        # Don't save if it's the same as the current position
        if self.current_position and self.current_position["line"] == line and self.current_position["column"] == column:
            return
        
        # Save the position
        self.current_position = {"line": line, "column": column}
        
        # Add to history
        if self.navigation_index < len(self.navigation_history) - 1:
            # Remove forward history
            self.navigation_history = self.navigation_history[:self.navigation_index + 1]
        
        self.navigation_history.append(self.current_position)
        self.navigation_index = len(self.navigation_history) - 1
    
    def _go_to_position(self, line, column, add_to_history=True):
        """Go to a specific position in the editor"""
        # Get the text block
        block = self.editor.document().findBlockByLineNumber(line - 1)
        if not block.isValid():
            return
        
        # Create a cursor at the position
        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, column - 1)
        
        # Set the cursor
        self.editor.setTextCursor(cursor)
        
        # Ensure the cursor is visible
        self.editor.ensureCursorVisible()
        
        # Save the position if needed
        if add_to_history:
            self.current_position = {"line": line, "column": column}
            self.navigation_history.append(self.current_position)
            self.navigation_index = len(self.navigation_history) - 1

class NavigationContextMenu(QMenu):
    """Context menu for code navigation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_actions()
        self.update_theme()
    
    def setup_actions(self):
        """Set up the menu actions"""
        # Go to definition
        self.go_to_definition_action = QAction("Go to Definition", self)
        self.go_to_definition_action.setIcon(get_icon("goto"))
        self.go_to_definition_action.setShortcut("F12")
        self.addAction(self.go_to_definition_action)
        
        # Find all references
        self.find_references_action = QAction("Find All References", self)
        self.find_references_action.setIcon(get_icon("references"))
        self.find_references_action.setShortcut("Shift+F12")
        self.addAction(self.find_references_action)
        
        # Separator
        self.addSeparator()
        
        # Go back
        self.go_back_action = QAction("Go Back", self)
        self.go_back_action.setIcon(get_icon("back"))
        self.go_back_action.setShortcut("Alt+Left")
        self.addAction(self.go_back_action)
        
        # Go forward
        self.go_forward_action = QAction("Go Forward", self)
        self.go_forward_action.setIcon(get_icon("forward"))
        self.go_forward_action.setShortcut("Alt+Right")
        self.addAction(self.go_forward_action)
    
    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QMenu {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
            }}
            
            QMenu::item {{
                padding: 5px 30px 5px 30px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {theme.border_color};
                margin: 5px 0px 5px 0px;
            }}
        """)
    
    def set_actions_enabled(self, can_go_to_definition, can_find_references, can_go_back, can_go_forward):
        """Set the enabled state of the actions"""
        self.go_to_definition_action.setEnabled(can_go_to_definition)
        self.find_references_action.setEnabled(can_find_references)
        self.go_back_action.setEnabled(can_go_back)
        self.go_forward_action.setEnabled(can_go_forward)
