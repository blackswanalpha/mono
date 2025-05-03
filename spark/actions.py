"""
Enhanced quick action panel for Spark Editor
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from .theme import ThemeManager
from .icons import get_icon


class ActionButton(QPushButton):
    """Custom button for quick actions."""
    
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("action-button")
        
        if icon_name:
            self.setIcon(get_icon(icon_name))


class ActionCategory(QFrame):
    """Category widget for grouping actions."""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("action-category")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(5)
        
        # Add title
        title_label = QLabel(title)
        title_label.setObjectName("action-category-title")
        layout.addWidget(title_label)
        
        # Add content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(5)
        layout.addWidget(self.content_widget)
    
    def add_action(self, button):
        """Add an action button to the category."""
        self.content_layout.addWidget(button)


class QuickActionPanel(QWidget):
    """Enhanced quick action panel with categories."""
    
    # Signals
    new_file_clicked = pyqtSignal()
    open_file_clicked = pyqtSignal()
    save_file_clicked = pyqtSignal()
    save_as_clicked = pyqtSignal()
    run_file_clicked = pyqtSignal()
    run_demo_clicked = pyqtSignal()
    
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
        header_widget.setObjectName("actions-header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Header label
        header_label = QLabel("Quick Actions")
        header_label.setObjectName("actions-header-label")
        header_layout.addWidget(header_label)
        
        # Add header to main layout
        main_layout.addWidget(header_widget)
        
        # Content widget
        content_widget = QWidget()
        content_widget.setObjectName("actions-content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # File actions category
        file_category = ActionCategory("File")
        
        # New file button
        new_file_btn = ActionButton("New File", "new_file")
        new_file_btn.clicked.connect(self.new_file_clicked.emit)
        file_category.add_action(new_file_btn)
        
        # Open file button
        open_file_btn = ActionButton("Open File", "open_file")
        open_file_btn.clicked.connect(self.open_file_clicked.emit)
        file_category.add_action(open_file_btn)
        
        # Save file button
        save_file_btn = ActionButton("Save", "save_file")
        save_file_btn.clicked.connect(self.save_file_clicked.emit)
        file_category.add_action(save_file_btn)
        
        # Save as button
        save_as_btn = ActionButton("Save As", "save_file")
        save_as_btn.clicked.connect(self.save_as_clicked.emit)
        file_category.add_action(save_as_btn)
        
        # Add file category to content
        content_layout.addWidget(file_category)
        
        # Run actions category
        run_category = ActionCategory("Run")
        
        # Run file button
        run_file_btn = ActionButton("Run Current File", "run_file")
        run_file_btn.clicked.connect(self.run_file_clicked.emit)
        run_category.add_action(run_file_btn)
        
        # Run demo button
        run_demo_btn = ActionButton("Run Mono Demo", "run_file")
        run_demo_btn.clicked.connect(self.run_demo_clicked.emit)
        run_category.add_action(run_demo_btn)
        
        # Add run category to content
        content_layout.addWidget(run_category)
        
        # Add stretch to push categories to the top
        content_layout.addStretch()
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setObjectName("actions-scroll")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)
    
    def update_theme(self):
        """Update the quick action panel's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()
        
        # Update the panel
        self.setStyleSheet(f"""
            #actions-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}
            
            #actions-header-label {{
                color: {theme.text_color};
                font-weight: bold;
            }}
            
            #actions-content {{
                background-color: {theme.panel_bg};
            }}
            
            #actions-scroll {{
                background-color: {theme.panel_bg};
                border: none;
            }}
            
            #action-category {{
                background-color: transparent;
                border-bottom: 1px solid {theme.border_color};
            }}
            
            #action-category-title {{
                color: {theme.text_dim_color};
                font-weight: bold;
                font-size: 12px;
            }}
            
            #action-button {{
                background-color: {theme.button_bg};
                color: {theme.button_text};
                border: none;
                border-radius: {theme.border_radius}px;
                padding: 8px;
                text-align: left;
            }}
            
            #action-button:hover {{
                background-color: {theme.button_hover_bg};
            }}
            
            #action-button:pressed {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}
        """)
