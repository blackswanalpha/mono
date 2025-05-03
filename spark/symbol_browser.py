"""
Symbol Browser for Spark Editor

This module provides a dedicated panel for browsing symbols in the current file
and implements a global symbol search across all files.
"""

import os
import re
from typing import Dict, List, Optional, Any, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QSplitter, QMenu, QTabWidget,
    QComboBox, QCompleter, QToolButton, QFrame
)
from PyQt6.QtGui import QIcon, QFont, QTextCursor, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QStringListModel

from .theme import ThemeManager
from .icons import get_icon
from .code_intelligence import MonoSymbol, MonoCodeAnalyzer
from .optimized_code_intelligence import OptimizedMonoCodeAnalyzer

class SymbolTreeItem(QTreeWidgetItem):
    """Tree item for displaying a symbol"""

    def __init__(self, symbol: MonoSymbol, file_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.file_path = file_path
        self.setText(0, symbol.name)
        self.setIcon(0, self._get_icon())

        # Add tooltip with file path if available
        tooltip = symbol.get_signature()
        if file_path:
            tooltip += f"\n{file_path}"
        self.setToolTip(0, tooltip)

    def _get_icon(self) -> QIcon:
        """Get the icon for the symbol"""
        if self.symbol.symbol_type == "component":
            return get_icon("component")
        elif self.symbol.symbol_type == "function":
            return get_icon("function")
        elif self.symbol.symbol_type == "variable":
            return get_icon("variable")
        elif self.symbol.symbol_type == "state":
            return get_icon("state")
        else:
            return get_icon("symbol")

class FileSymbolBrowser(QWidget):
    """Widget for browsing symbols in the current file"""

    symbolSelected = pyqtSignal(MonoSymbol)
    renameSymbolRequested = pyqtSignal(MonoSymbol, str)  # Symbol and file path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()
        self.current_file_path = None

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

        self.title_label = QLabel("File Symbols")
        self.title_label.setObjectName("symbols-title")
        self.header_layout.addWidget(self.title_label)

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter symbols...")
        self.filter_input.textChanged.connect(self._filter_symbols)
        self.filter_input.setClearButtonEnabled(True)
        self.header_layout.addWidget(self.filter_input)

        self.layout.addWidget(self.header)

        # Symbols tree
        self.symbols_tree = QTreeWidget()
        self.symbols_tree.setObjectName("symbols-tree")
        self.symbols_tree.setHeaderHidden(True)
        self.symbols_tree.itemClicked.connect(self._handle_item_clicked)
        self.symbols_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.symbols_tree.customContextMenuRequested.connect(self._show_context_menu)
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

            QLineEdit {{
                background-color: {theme.input_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 4px;
            }}

            QLineEdit:focus {{
                border: 1px solid {theme.primary_color};
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

    def set_symbols(self, symbols: Dict[str, MonoSymbol], file_path: Optional[str] = None):
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
            item = SymbolTreeItem(symbol, file_path)
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
                    func_item = SymbolTreeItem(func, file_path, functions_item)

            # Add variables
            if component_variables:
                variables_item = QTreeWidgetItem(item)
                variables_item.setText(0, "Variables")
                variables_item.setIcon(0, get_icon("variable"))

                for var in sorted(component_variables, key=lambda s: s.name):
                    var_item = SymbolTreeItem(var, file_path, variables_item)

        # Add global functions (not part of any component)
        global_functions = [s for s in functions if not s.scope]
        if global_functions:
            global_functions_item = QTreeWidgetItem()
            global_functions_item.setText(0, "Global Functions")
            global_functions_item.setIcon(0, get_icon("function"))
            self.symbols_tree.addTopLevelItem(global_functions_item)

            for func in sorted(global_functions, key=lambda s: s.name):
                func_item = SymbolTreeItem(func, file_path, global_functions_item)

        # Add global variables (not part of any component)
        global_variables = [s for s in variables if not s.scope]
        if global_variables:
            global_variables_item = QTreeWidgetItem()
            global_variables_item.setText(0, "Global Variables")
            global_variables_item.setIcon(0, get_icon("variable"))
            self.symbols_tree.addTopLevelItem(global_variables_item)

            for var in sorted(global_variables, key=lambda s: s.name):
                var_item = SymbolTreeItem(var, file_path, global_variables_item)

        # Expand all items
        self.symbols_tree.expandAll()

    def _filter_symbols(self, text: str):
        """Filter symbols by name"""
        text = text.lower()

        # Show all items if filter is empty
        if not text:
            for i in range(self.symbols_tree.topLevelItemCount()):
                item = self.symbols_tree.topLevelItem(i)
                self._set_item_visible(item, True)
            return

        # Hide/show items based on filter
        for i in range(self.symbols_tree.topLevelItemCount()):
            top_item = self.symbols_tree.topLevelItem(i)

            # Check if top item matches
            top_visible = text in top_item.text(0).lower()

            # Check children
            child_visible = False
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)

                # Check if child is a category (Functions, Variables)
                if child_item.childCount() > 0:
                    category_visible = False
                    for k in range(child_item.childCount()):
                        symbol_item = child_item.child(k)
                        symbol_visible = text in symbol_item.text(0).lower()
                        self._set_item_visible(symbol_item, symbol_visible)
                        category_visible = category_visible or symbol_visible

                    self._set_item_visible(child_item, category_visible)
                    child_visible = child_visible or category_visible
                else:
                    # Child is a symbol
                    child_visible = text in child_item.text(0).lower()
                    self._set_item_visible(child_item, child_visible)

            # Show top item if it matches or any child matches
            self._set_item_visible(top_item, top_visible or child_visible)

    def _set_item_visible(self, item: QTreeWidgetItem, visible: bool):
        """Set the visibility of an item"""
        item.setHidden(not visible)

    def _handle_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        if isinstance(item, SymbolTreeItem):
            self.symbolSelected.emit(item.symbol)

    def _show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.symbols_tree.itemAt(position)
        if not isinstance(item, SymbolTreeItem):
            return

        # Create context menu
        menu = QMenu(self)

        # Add actions based on symbol type
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.renameSymbolRequested.emit(item.symbol, self.current_file_path))
        menu.addAction(rename_action)

        # Show the menu
        menu.exec(self.symbols_tree.viewport().mapToGlobal(position))

    def set_file_path(self, file_path: str):
        """Set the current file path"""
        self.current_file_path = file_path

class GlobalSymbolSearch(QWidget):
    """Widget for searching symbols across all files"""

    symbolSelected = pyqtSignal(MonoSymbol, str)  # Symbol and file path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()

        # Initialize analyzer
        self.analyzer = MonoCodeAnalyzer()

        # File cache
        self.file_cache: Dict[str, Dict[str, MonoSymbol]] = {}

        # Search timer
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

    def setup_ui(self):
        """Set up the UI elements"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Header
        self.header = QWidget()
        self.header.setObjectName("search-header")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("Global Symbols")
        self.title_label.setObjectName("search-title")
        self.header_layout.addWidget(self.title_label)

        self.layout.addWidget(self.header)

        # Search input
        self.search_container = QWidget()
        self.search_container.setObjectName("search-container")
        self.search_layout = QHBoxLayout(self.search_container)
        self.search_layout.setContentsMargins(10, 5, 10, 5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search symbols...")
        self.search_input.textChanged.connect(self._handle_search_changed)
        self.search_input.setClearButtonEnabled(True)
        self.search_layout.addWidget(self.search_input)

        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItem("Components")
        self.type_filter.addItem("Functions")
        self.type_filter.addItem("Variables")
        self.type_filter.currentIndexChanged.connect(lambda: self._perform_search())
        self.search_layout.addWidget(self.type_filter)

        # Add search options
        self.search_options = QComboBox()
        self.search_options.addItem("Exact Match")
        self.search_options.addItem("Fuzzy Search")
        self.search_options.addItem("Regular Expression")
        self.search_options.currentIndexChanged.connect(lambda: self._perform_search())
        self.search_layout.addWidget(self.search_options)

        self.layout.addWidget(self.search_container)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setObjectName("results-tree")
        self.results_tree.setHeaderHidden(True)
        self.results_tree.itemClicked.connect(self._handle_item_clicked)
        self.layout.addWidget(self.results_tree)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            #search-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}

            #search-title {{
                font-weight: bold;
                color: {theme.text_color};
            }}

            #search-container {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}

            QLineEdit {{
                background-color: {theme.input_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 4px;
            }}

            QLineEdit:focus {{
                border: 1px solid {theme.primary_color};
            }}

            QComboBox {{
                background-color: {theme.input_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 4px;
            }}

            QComboBox:focus {{
                border: 1px solid {theme.primary_color};
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {theme.border_color};
            }}

            #results-tree {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: none;
            }}

            #results-tree::item {{
                padding: 5px;
            }}

            #results-tree::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}

            #results-tree::item:hover:!selected {{
                background-color: {theme.secondary_color};
            }}

            #status-label {{
                background-color: {theme.panel_bg};
                color: {theme.text_dim_color};
                border-top: 1px solid {theme.border_color};
                padding: 5px;
            }}
        """)

    def add_file(self, file_path: str, code: str):
        """Add a file to the search index"""
        # Skip if not a Mono file
        if not file_path.lower().endswith('.mono'):
            return

        # Analyze the file
        self.analyzer.analyze(code, file_path)

        # Cache the symbols
        self.file_cache[file_path] = self.analyzer.symbols.copy()

    def remove_file(self, file_path: str):
        """Remove a file from the search index"""
        if file_path in self.file_cache:
            del self.file_cache[file_path]

    def clear_cache(self):
        """Clear the file cache"""
        self.file_cache.clear()

    def _handle_search_changed(self, text: str):
        """Handle search input changes"""
        # Start the search timer to avoid searching on every keystroke
        self.search_timer.start(300)

    def _perform_search(self):
        """Perform the search"""
        query = self.search_input.text()
        type_filter = self.type_filter.currentText()
        search_option = self.search_options.currentText()

        self.results_tree.clear()

        if not query:
            self.status_label.setText("Enter a search query")
            return

        # Collect matching symbols
        results = []

        # Create an optimized analyzer for fuzzy search
        optimized_analyzer = OptimizedMonoCodeAnalyzer()

        for file_path, symbols in self.file_cache.items():
            # Set the symbols in the optimized analyzer for fuzzy search
            optimized_analyzer.symbols = symbols
            optimized_analyzer._update_symbol_index()

            # Apply search based on selected option
            if search_option == "Exact Match":
                # Exact match search
                for symbol_name, symbol in symbols.items():
                    # Apply type filter
                    if type_filter == "Components" and symbol.symbol_type != "component":
                        continue
                    elif type_filter == "Functions" and symbol.symbol_type != "function":
                        continue
                    elif type_filter == "Variables" and symbol.symbol_type != "variable":
                        continue

                    # Check if symbol matches the query
                    if query.lower() in symbol_name.lower():
                        results.append((symbol, file_path))

            elif search_option == "Fuzzy Search":
                # Fuzzy search using optimized analyzer
                matching_symbols = optimized_analyzer.fuzzy_search(query)

                for symbol in matching_symbols:
                    # Apply type filter
                    if type_filter == "Components" and symbol.symbol_type != "component":
                        continue
                    elif type_filter == "Functions" and symbol.symbol_type != "function":
                        continue
                    elif type_filter == "Variables" and symbol.symbol_type != "variable":
                        continue

                    results.append((symbol, file_path))

            elif search_option == "Regular Expression":
                # Regular expression search
                try:
                    pattern = re.compile(query, re.IGNORECASE)

                    for symbol_name, symbol in symbols.items():
                        # Apply type filter
                        if type_filter == "Components" and symbol.symbol_type != "component":
                            continue
                        elif type_filter == "Functions" and symbol.symbol_type != "function":
                            continue
                        elif type_filter == "Variables" and symbol.symbol_type != "variable":
                            continue

                        # Check if symbol matches the pattern
                        if pattern.search(symbol_name):
                            results.append((symbol, file_path))
                except re.error:
                    # Invalid regular expression
                    self.status_label.setText(f"Invalid regular expression: '{query}'")
                    return

        # Display results
        if not results:
            self.status_label.setText(f"No symbols found for '{query}'")
            return

        # Group results by file
        file_groups = {}
        for symbol, file_path in results:
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append(symbol)

        # Add results to tree
        for file_path, symbols in file_groups.items():
            file_item = QTreeWidgetItem()
            file_item.setText(0, os.path.basename(file_path))
            file_item.setToolTip(0, file_path)
            file_item.setIcon(0, get_icon("mono_file"))
            self.results_tree.addTopLevelItem(file_item)

            # Add symbols
            for symbol in sorted(symbols, key=lambda s: s.name):
                symbol_item = SymbolTreeItem(symbol, file_path, file_item)

        # Expand all items
        self.results_tree.expandAll()

        # Update status
        self.status_label.setText(f"Found {len(results)} symbols in {len(file_groups)} files")

    def _handle_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        if isinstance(item, SymbolTreeItem):
            self.symbolSelected.emit(item.symbol, item.file_path)

class SymbolBrowserWidget(QWidget):
    """Widget containing the symbol browser with tabs for file and global symbols"""

    fileSymbolSelected = pyqtSignal(MonoSymbol)
    globalSymbolSelected = pyqtSignal(MonoSymbol, str)
    renameSymbolRequested = pyqtSignal(MonoSymbol, str)

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

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("symbol-tabs")
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # File symbols tab
        self.file_symbols = FileSymbolBrowser()
        self.file_symbols.symbolSelected.connect(self.fileSymbolSelected.emit)
        self.file_symbols.renameSymbolRequested.connect(self.renameSymbolRequested.emit)
        self.tab_widget.addTab(self.file_symbols, "File")

        # Global symbols tab
        self.global_symbols = GlobalSymbolSearch()
        self.global_symbols.symbolSelected.connect(self.globalSymbolSelected.emit)
        self.tab_widget.addTab(self.global_symbols, "Workspace")

        self.layout.addWidget(self.tab_widget)

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            #symbol-tabs {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: none;
            }}

            #symbol-tabs::pane {{
                border: none;
            }}

            #symbol-tabs::tab-bar {{
                alignment: left;
            }}

            #symbol-tabs QTabBar::tab {{
                background-color: {theme.tab_inactive_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-bottom: none;
                border-top-left-radius: {theme.border_radius}px;
                border-top-right-radius: {theme.border_radius}px;
                padding: 5px 10px;
                margin-right: 2px;
            }}

            #symbol-tabs QTabBar::tab:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}

            #symbol-tabs QTabBar::tab:hover:!selected {{
                background-color: {theme.secondary_color};
            }}
        """)

        # Update child widgets
        self.file_symbols.update_theme()
        self.global_symbols.update_theme()

    def set_file_symbols(self, symbols: Dict[str, MonoSymbol], file_path: Optional[str] = None):
        """Set the symbols for the current file"""
        self.file_symbols.set_symbols(symbols, file_path)

        # Set the file path for refactoring
        if file_path:
            self.file_symbols.set_file_path(file_path)

        # Also add to global search
        if file_path:
            # Get the code from the symbols
            code = ""
            for symbol in symbols.values():
                if symbol.symbol_type == "component":
                    code += f"component {symbol.name} {{\n"
                    code += symbol.details.get("body", "") + "\n"
                    code += "}\n\n"

            self.global_symbols.add_file(file_path, code)

    def add_file_to_global_search(self, file_path: str, code: str):
        """Add a file to the global symbol search"""
        self.global_symbols.add_file(file_path, code)

    def remove_file_from_global_search(self, file_path: str):
        """Remove a file from the global symbol search"""
        self.global_symbols.remove_file(file_path)

    def clear_global_search_cache(self):
        """Clear the global search cache"""
        self.global_symbols.clear_cache()
