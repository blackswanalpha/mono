"""
Welcome screen for Spark Editor
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QSpacerItem, QSizePolicy, QTabWidget, QScrollArea
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSignal

from .icons import get_pixmap
from .theme import ThemeManager
from .templates import TemplateBrowser


class WelcomeScreen(QWidget):
    """Welcome screen for Spark Editor."""

    # Signals
    new_file_clicked = pyqtSignal()
    open_file_clicked = pyqtSignal()
    run_demo_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        """Set up the UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Logo and title
        logo_layout = QHBoxLayout()
        logo_label = QLabel()

        # Try to load the Mono logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mono_logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
        else:
            logo_pixmap = get_pixmap("app_icon")

        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        logo_layout.addWidget(logo_label)
        logo_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(logo_layout)

        # Title
        title_label = QLabel("Welcome to Spark Editor")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("welcome-title")
        main_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("A modern editor for Mono language")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setObjectName("welcome-subtitle")
        main_layout.addWidget(subtitle_label)

        # Tab widget for different sections
        tab_widget = QTabWidget()
        tab_widget.setObjectName("welcome-tabs")

        # Get Started tab
        get_started_widget = QWidget()
        get_started_layout = QVBoxLayout(get_started_widget)
        get_started_layout.setContentsMargins(20, 20, 20, 20)
        get_started_layout.setSpacing(15)

        # Actions
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)

        # New file button
        new_file_btn = QPushButton("Create New File")
        new_file_btn.setObjectName("welcome-button")
        new_file_btn.clicked.connect(self.new_file_clicked.emit)
        actions_layout.addWidget(new_file_btn)

        # Open file button
        open_file_btn = QPushButton("Open Existing File")
        open_file_btn.setObjectName("welcome-button")
        open_file_btn.clicked.connect(self.open_file_clicked.emit)
        actions_layout.addWidget(open_file_btn)

        # Run demo button
        run_demo_btn = QPushButton("Run Mono Demo")
        run_demo_btn.setObjectName("welcome-button")
        run_demo_btn.clicked.connect(self.run_demo_clicked.emit)
        actions_layout.addWidget(run_demo_btn)

        # Add actions to get started layout
        get_started_layout.addLayout(actions_layout)
        get_started_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Templates tab
        templates_widget = QWidget()
        templates_layout = QVBoxLayout(templates_widget)
        templates_layout.setContentsMargins(0, 0, 0, 0)

        # Template browser
        self.template_browser = TemplateBrowser()
        templates_layout.addWidget(self.template_browser)

        # Add tabs
        tab_widget.addTab(get_started_widget, "Get Started")
        tab_widget.addTab(templates_widget, "Templates")

        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)

        # Footer
        footer_label = QLabel("Spark Editor v1.0.0 - Mono Language")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setObjectName("welcome-footer")
        main_layout.addWidget(footer_label)

    def update_theme(self):
        """Update the welcome screen's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()

        # Update template browser
        if hasattr(self, 'template_browser'):
            self.template_browser.update_theme()

        # Set background color
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.window_bg};
                color: {theme.text_color};
            }}

            #welcome-title {{
                font-size: 28px;
                font-weight: bold;
                color: {theme.text_bright_color};
                margin-top: 10px;
            }}

            #welcome-subtitle {{
                font-size: 16px;
                color: {theme.text_dim_color};
                margin-bottom: 20px;
            }}

            #welcome-footer {{
                font-size: 12px;
                color: {theme.text_dim_color};
                margin-top: 10px;
            }}

            #welcome-button {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
                border: none;
                border-radius: {theme.border_radius}px;
                padding: 12px;
                font-size: 14px;
                min-width: 200px;
            }}

            #welcome-button:hover {{
                background-color: {theme.secondary_color};
            }}

            #welcome-button:pressed {{
                background-color: {theme.accent_color};
            }}

            #welcome-tabs {{
                background-color: {theme.window_bg};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
            }}

            #welcome-tabs::pane {{
                border: none;
                background-color: {theme.panel_bg};
                border-radius: {theme.border_radius}px;
            }}

            #welcome-tabs::tab-bar {{
                alignment: center;
            }}

            #welcome-tabs QTabBar::tab {{
                background-color: {theme.button_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-bottom: none;
                border-top-left-radius: {theme.border_radius}px;
                border-top-right-radius: {theme.border_radius}px;
                padding: 8px 16px;
                margin-right: 4px;
            }}

            #welcome-tabs QTabBar::tab:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}

            #welcome-tabs QTabBar::tab:hover:!selected {{
                background-color: {theme.secondary_color};
            }}
        """)
