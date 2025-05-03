"""
Enhanced status bar for Spark Editor
"""

import os
from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from .theme import ThemeManager


class StatusIndicator(QWidget):
    """Status indicator widget for the status bar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.status = "idle"  # idle, running, success, error
        self.update_theme()
    
    def setup_ui(self):
        """Set up the UI elements."""
        self.setFixedSize(16, 16)
    
    def update_theme(self):
        """Update the indicator's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()
        
        # Define status colors
        self.status_colors = {
            "idle": theme.text_dim_color,
            "running": theme.primary_color,
            "success": "#4CAF50",
            "error": "#FF5252"
        }
        
        # Update the indicator
        self.update()
    
    def set_status(self, status):
        """Set the status of the indicator."""
        if status in self.status_colors:
            self.status = status
            self.update()
    
    def paintEvent(self, event):
        """Paint the indicator."""
        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get the color for the current status
        color = QColor(self.status_colors[self.status])
        
        # Draw the indicator
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        if self.status == "running":
            # Draw a spinning animation
            painter.drawEllipse(4, 4, 8, 8)
        else:
            # Draw a circle
            painter.drawEllipse(2, 2, 12, 12)


class EnhancedStatusBar(QStatusBar):
    """Enhanced status bar with more information."""
    
    # Signals
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()
        
        # Start the timer for updating the status indicator animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status_indicator)
        self.timer.start(500)  # Update every 500ms
        
        # Initialize the rotation angle for the animation
        self.rotation_angle = 0
    
    def setup_ui(self):
        """Set up the UI elements."""
        # Status indicator
        self.status_indicator = StatusIndicator()
        self.addPermanentWidget(self.status_indicator)
        
        # File info label
        self.file_info_label = QLabel()
        self.file_info_label.setObjectName("status-file-info")
        self.addPermanentWidget(self.file_info_label)
        
        # Position label
        self.position_label = QLabel()
        self.position_label.setObjectName("status-position")
        self.addPermanentWidget(self.position_label)
        
        # Theme selector
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(5)
        
        theme_label = QLabel("Theme:")
        theme_label.setObjectName("status-theme-label")
        theme_layout.addWidget(theme_label)
        
        # Theme buttons
        self.theme_buttons = {}
        for theme_name in ["dark", "light", "nord"]:
            theme_btn = QLabel(theme_name.capitalize())
            theme_btn.setObjectName(f"status-theme-{theme_name}")
            theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            theme_btn.mousePressEvent = lambda event, name=theme_name: self.change_theme(name)
            theme_layout.addWidget(theme_btn)
            self.theme_buttons[theme_name] = theme_btn
        
        self.addPermanentWidget(theme_widget)
        
        # Set initial status
        self.set_status("idle", "Ready")
        self.set_file_info(None)
        self.set_position(1, 1)
    
    def update_theme(self):
        """Update the status bar's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()
        
        # Update the status indicator
        self.status_indicator.update_theme()
        
        # Update the status bar
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border-top: 1px solid {theme.border_color};
            }}
            
            #status-file-info, #status-position, #status-theme-label {{
                color: {theme.text_dim_color};
                padding: 0 5px;
            }}
            
            #status-theme-dark, #status-theme-light, #status-theme-nord {{
                color: {theme.text_dim_color};
                padding: 2px 5px;
                border-radius: {theme.border_radius}px;
            }}
            
            #status-theme-dark:hover, #status-theme-light:hover, #status-theme-nord:hover {{
                background-color: {theme.button_hover_bg};
                color: {theme.text_color};
            }}
            
            #status-theme-{ThemeManager.current_theme} {{
                color: {theme.primary_color};
                font-weight: bold;
            }}
        """)
    
    def set_status(self, status, message):
        """Set the status and message."""
        self.status_indicator.set_status(status)
        self.showMessage(message)
    
    def set_file_info(self, file_path):
        """Set the file info."""
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            self.file_info_label.setText(f"{file_name} ({size_str})")
        else:
            self.file_info_label.setText("")
    
    def set_position(self, line, column):
        """Set the cursor position."""
        self.position_label.setText(f"Ln {line}, Col {column}")
    
    def update_status_indicator(self):
        """Update the status indicator animation."""
        if self.status_indicator.status == "running":
            self.rotation_angle = (self.rotation_angle + 30) % 360
            self.status_indicator.update()
    
    def change_theme(self, theme_name):
        """Change the theme."""
        if ThemeManager.apply_theme(QApplication.instance(), theme_name):
            self.update_theme()
            self.theme_changed.emit(theme_name)
