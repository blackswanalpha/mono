"""
Enhanced Syntax Highlighter plugin for Spark Editor.
"""

import re
from PyQt6.QtGui import QColor, QTextCharFormat, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QColorDialog

from spark.plugin_system import PluginInterface, PluginMetadata
from spark.theme import ThemeManager

class SyntaxHighlighterSettings(QWidget):
    """Settings widget for the Enhanced Syntax Highlighter plugin."""
    
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI."""
        # Create the layout
        layout = QVBoxLayout(self)
        
        # Create the title label
        title_label = QLabel("Enhanced Syntax Highlighter Settings")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Create the description label
        description_label = QLabel("Configure the enhanced syntax highlighting for Mono files.")
        layout.addWidget(description_label)
        
        # Create the theme selector
        theme_label = QLabel("Highlighting Theme:")
        layout.addWidget(theme_label)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Default", "Vibrant", "Pastel", "Monochrome"])
        self.theme_selector.setCurrentText(self.plugin.get_theme())
        self.theme_selector.currentTextChanged.connect(self.plugin.set_theme)
        layout.addWidget(self.theme_selector)
        
        # Create the keyword color button
        keyword_label = QLabel("Keyword Color:")
        layout.addWidget(keyword_label)
        
        self.keyword_color_button = QPushButton()
        self.keyword_color_button.setStyleSheet(f"background-color: {self.plugin.get_keyword_color().name()};")
        self.keyword_color_button.clicked.connect(self.choose_keyword_color)
        layout.addWidget(self.keyword_color_button)
        
        # Add a spacer
        layout.addStretch()
        
        # Set the layout
        self.setLayout(layout)
    
    def choose_keyword_color(self):
        """Choose a color for keywords."""
        color = QColorDialog.getColor(self.plugin.get_keyword_color(), self, "Choose Keyword Color")
        if color.isValid():
            self.plugin.set_keyword_color(color)
            self.keyword_color_button.setStyleSheet(f"background-color: {color.name()};")

class Plugin(PluginInterface):
    """Enhanced Syntax Highlighter plugin."""
    
    def __init__(self, metadata):
        super().__init__(metadata)
        self.theme = "Default"
        self.keyword_color = QColor("#569CD6")  # Default blue color
        self.settings_widget = None
    
    def initialize(self):
        """Initialize the plugin."""
        print(f"Initializing {self.metadata.name} plugin")
        
        # Register additional syntax highlighting rules
        self.register_highlighting_rules()
        
        return super().initialize()
    
    def cleanup(self):
        """Clean up the plugin."""
        print(f"Cleaning up {self.metadata.name} plugin")
        
        # Remove additional syntax highlighting rules
        self.unregister_highlighting_rules()
        
        return super().cleanup()
    
    def get_settings_widget(self):
        """Get the settings widget."""
        if self.settings_widget is None:
            self.settings_widget = SyntaxHighlighterSettings(self)
        return self.settings_widget
    
    def get_theme(self):
        """Get the current theme."""
        return self.theme
    
    def set_theme(self, theme):
        """Set the theme."""
        self.theme = theme
        self.register_highlighting_rules()
    
    def get_keyword_color(self):
        """Get the keyword color."""
        return self.keyword_color
    
    def set_keyword_color(self, color):
        """Set the keyword color."""
        self.keyword_color = color
        self.register_highlighting_rules()
    
    def register_highlighting_rules(self):
        """Register additional syntax highlighting rules."""
        # This is a mock implementation
        # In a real plugin, this would modify the syntax highlighter
        print(f"Registering highlighting rules with theme: {self.theme} and keyword color: {self.keyword_color.name()}")
    
    def unregister_highlighting_rules(self):
        """Unregister additional syntax highlighting rules."""
        # This is a mock implementation
        # In a real plugin, this would restore the original syntax highlighter
        print("Unregistering highlighting rules")
