"""
Theme management for Spark Editor
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

class SparkTheme:
    """Base class for Spark themes."""

    # Theme name
    name = "Base Theme"

    # Main colors
    primary_color = "#007ACC"
    secondary_color = "#0098FF"
    accent_color = "#FF5722"

    # Background colors
    window_bg = "#1E1E1E"
    panel_bg = "#252526"
    editor_bg = "#1E1E1E"
    terminal_bg = "#1E1E1E"
    input_bg = "#333333"

    # Text colors
    text_color = "#CCCCCC"
    text_dim_color = "#888888"
    text_bright_color = "#FFFFFF"

    # UI element colors
    button_bg = "#333333"
    button_hover_bg = "#444444"
    button_text = "#CCCCCC"

    # Tab colors
    tab_active_bg = "#1E1E1E"
    tab_inactive_bg = "#2D2D2D"
    tab_active_text = "#FFFFFF"
    tab_inactive_text = "#AAAAAA"

    # Border colors
    border_color = "#444444"

    # Syntax highlighting colors
    syntax_keyword = "#569CD6"
    syntax_number = "#B5CEA8"
    syntax_string = "#CE9178"
    syntax_comment = "#6A9955"
    syntax_element = "#4EC9B0"
    syntax_function = "#DCDCAA"
    syntax_class = "#4EC9B0"
    syntax_variable = "#9CDCFE"

    # Diagnostic colors
    error_color = "#F44747"
    warning_color = "#DDB100"
    info_color = "#75BEFF"

    # Fonts
    font_family = "Consolas, 'Courier New', monospace"
    font_size = 10
    font_size_small = 9
    font_size_large = 12

    # Spacing
    padding = 8
    margin = 8
    border_radius = 4

    @classmethod
    def apply_to_app(cls, app):
        """Apply the theme to the entire application."""
        palette = QPalette()

        # Set window and widget background colors
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.window_bg))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.text_color))
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.panel_bg))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.window_bg))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(cls.panel_bg))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(cls.text_color))

        # Set text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.text_color))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(cls.text_bright_color))

        # Set button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.button_bg))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.button_text))

        # Set highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.primary_color))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.text_bright_color))

        # Set link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(cls.secondary_color))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(cls.primary_color))

        # Apply palette to application
        app.setPalette(palette)

        # Set application stylesheet
        app.setStyleSheet(cls.get_stylesheet())

    @classmethod
    def get_stylesheet(cls):
        """Get the stylesheet for the theme."""
        return f"""
        /* Global Styles */
        QWidget {{
            background-color: {cls.window_bg};
            color: {cls.text_color};
            font-family: {cls.font_family};
            font-size: {cls.font_size}pt;
        }}

        /* Main Window */
        QMainWindow {{
            background-color: {cls.window_bg};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {cls.panel_bg};
            color: {cls.text_color};
            border-bottom: 1px solid {cls.border_color};
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 10px;
        }}

        QMenuBar::item:selected {{
            background-color: {cls.primary_color};
            color: {cls.text_bright_color};
        }}

        QMenu {{
            background-color: {cls.panel_bg};
            border: 1px solid {cls.border_color};
            padding: 5px;
        }}

        QMenu::item {{
            padding: 5px 30px 5px 20px;
            border-radius: {cls.border_radius}px;
        }}

        QMenu::item:selected {{
            background-color: {cls.primary_color};
            color: {cls.text_bright_color};
        }}

        /* Tool Bar */
        QToolBar {{
            background-color: {cls.panel_bg};
            border-bottom: 1px solid {cls.border_color};
            spacing: 5px;
            padding: 5px;
        }}

        QToolBar QToolButton {{
            background-color: transparent;
            border-radius: {cls.border_radius}px;
            padding: 5px;
        }}

        QToolBar QToolButton:hover {{
            background-color: {cls.button_hover_bg};
        }}

        QToolBar QToolButton:pressed {{
            background-color: {cls.primary_color};
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {cls.panel_bg};
            color: {cls.text_color};
            border-top: 1px solid {cls.border_color};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {cls.border_color};
            background-color: {cls.editor_bg};
        }}

        QTabBar::tab {{
            background-color: {cls.tab_inactive_bg};
            color: {cls.tab_inactive_text};
            border-top-left-radius: {cls.border_radius}px;
            border-top-right-radius: {cls.border_radius}px;
            padding: 8px 12px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.tab_active_bg};
            color: {cls.tab_active_text};
            border-bottom: 2px solid {cls.primary_color};
        }}

        QTabBar::tab:hover {{
            background-color: {cls.button_hover_bg};
        }}

        QTabBar::close-button {{
            image: url(:/icons/close.png);
            subcontrol-position: right;
        }}

        QTabBar::close-button:hover {{
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {cls.border_color};
        }}

        QSplitter::handle:horizontal {{
            width: 1px;
        }}

        QSplitter::handle:vertical {{
            height: 1px;
        }}

        /* Text Edit (Editor) */
        QTextEdit {{
            background-color: {cls.editor_bg};
            color: {cls.text_color};
            border: none;
            selection-background-color: {cls.primary_color};
            selection-color: {cls.text_bright_color};
        }}

        /* Line Edit */
        QLineEdit {{
            background-color: {cls.panel_bg};
            color: {cls.text_color};
            border: 1px solid {cls.border_color};
            border-radius: {cls.border_radius}px;
            padding: 5px;
        }}

        QLineEdit:focus {{
            border: 1px solid {cls.primary_color};
        }}

        /* Push Button */
        QPushButton {{
            background-color: {cls.button_bg};
            color: {cls.button_text};
            border: none;
            border-radius: {cls.border_radius}px;
            padding: 8px 16px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {cls.button_hover_bg};
        }}

        QPushButton:pressed {{
            background-color: {cls.primary_color};
        }}

        QPushButton:disabled {{
            background-color: {cls.button_bg};
            color: {cls.text_dim_color};
        }}

        /* Tree View */
        QTreeView {{
            background-color: {cls.panel_bg};
            alternate-background-color: {cls.window_bg};
            color: {cls.text_color};
            border: none;
            show-decoration-selected: 1;
        }}

        QTreeView::item {{
            padding: 5px;
            border-radius: {cls.border_radius}px;
        }}

        QTreeView::item:hover {{
            background-color: {cls.button_hover_bg};
        }}

        QTreeView::item:selected {{
            background-color: {cls.primary_color};
            color: {cls.text_bright_color};
        }}

        QTreeView::branch:has-siblings:!adjoins-item {{
            border-image: url(:/icons/vline.png) 0;
        }}

        QTreeView::branch:has-siblings:adjoins-item {{
            border-image: url(:/icons/branch-more.png) 0;
        }}

        QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: url(:/icons/branch-end.png) 0;
        }}

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/branch-closed.png);
        }}

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/branch-open.png);
        }}

        /* Scroll Bar */
        QScrollBar:vertical {{
            background-color: {cls.window_bg};
            width: 12px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.button_bg};
            min-height: 20px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.button_hover_bg};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background-color: {cls.window_bg};
            height: 12px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {cls.button_bg};
            min-width: 20px;
            border-radius: 6px;
            margin: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.button_hover_bg};
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Labels */
        QLabel {{
            color: {cls.text_color};
            padding: 2px;
        }}

        /* Group Box */
        QGroupBox {{
            border: 1px solid {cls.border_color};
            border-radius: {cls.border_radius}px;
            margin-top: 20px;
            padding-top: 10px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {cls.text_color};
        }}
        """


class DarkTheme(SparkTheme):
    """Dark theme for Spark Editor."""

    name = "Dark"

    # Main colors
    primary_color = "#007ACC"
    secondary_color = "#0098FF"
    accent_color = "#FF5722"

    # Background colors
    window_bg = "#1E1E1E"
    panel_bg = "#252526"
    editor_bg = "#1E1E1E"
    terminal_bg = "#1E1E1E"
    input_bg = "#333333"

    # Text colors
    text_color = "#CCCCCC"
    text_dim_color = "#888888"
    text_bright_color = "#FFFFFF"


class LightTheme(SparkTheme):
    """Light theme for Spark Editor."""

    name = "Light"

    # Main colors
    primary_color = "#0078D7"
    secondary_color = "#0098FF"
    accent_color = "#FF5722"

    # Background colors
    window_bg = "#F5F5F5"
    panel_bg = "#FFFFFF"
    editor_bg = "#FFFFFF"
    terminal_bg = "#F8F8F8"
    input_bg = "#F0F0F0"

    # Text colors
    text_color = "#333333"
    text_dim_color = "#888888"
    text_bright_color = "#000000"

    # UI element colors
    button_bg = "#E0E0E0"
    button_hover_bg = "#D0D0D0"
    button_text = "#333333"

    # Tab colors
    tab_active_bg = "#FFFFFF"
    tab_inactive_bg = "#ECECEC"
    tab_active_text = "#333333"
    tab_inactive_text = "#777777"

    # Border colors
    border_color = "#CCCCCC"

    # Syntax highlighting colors
    syntax_keyword = "#0000FF"
    syntax_number = "#098658"
    syntax_string = "#A31515"
    syntax_comment = "#008000"
    syntax_element = "#800000"
    syntax_function = "#795E26"
    syntax_class = "#267F99"
    syntax_variable = "#001080"


class NordTheme(SparkTheme):
    """Nord theme for Spark Editor."""

    name = "Nord"

    # Main colors
    primary_color = "#88C0D0"
    secondary_color = "#81A1C1"
    accent_color = "#B48EAD"

    # Background colors
    window_bg = "#2E3440"
    panel_bg = "#3B4252"
    editor_bg = "#2E3440"
    terminal_bg = "#2E3440"
    input_bg = "#434C5E"

    # Text colors
    text_color = "#D8DEE9"
    text_dim_color = "#7B88A1"
    text_bright_color = "#ECEFF4"

    # UI element colors
    button_bg = "#434C5E"
    button_hover_bg = "#4C566A"
    button_text = "#E5E9F0"

    # Tab colors
    tab_active_bg = "#3B4252"
    tab_inactive_bg = "#2E3440"
    tab_active_text = "#ECEFF4"
    tab_inactive_text = "#D8DEE9"

    # Border colors
    border_color = "#4C566A"

    # Syntax highlighting colors
    syntax_keyword = "#81A1C1"
    syntax_number = "#B48EAD"
    syntax_string = "#A3BE8C"
    syntax_comment = "#616E88"
    syntax_element = "#88C0D0"
    syntax_function = "#EBCB8B"
    syntax_class = "#8FBCBB"
    syntax_variable = "#D8DEE9"


class ThemeManager:
    """Manage themes for Spark Editor."""

    # Available themes
    themes = {
        "dark": DarkTheme,
        "light": LightTheme,
        "nord": NordTheme
    }

    # Current theme
    current_theme = "dark"

    @classmethod
    def apply_theme(cls, app, theme_name=None):
        """Apply a theme to the application."""
        if theme_name is None:
            theme_name = cls.current_theme

        if theme_name in cls.themes:
            cls.current_theme = theme_name
            cls.themes[theme_name].apply_to_app(app)
            return True
        return False

    @classmethod
    def get_theme_names(cls):
        """Get a list of available theme names."""
        return list(cls.themes.keys())

    @classmethod
    def get_current_theme(cls):
        """Get the current theme class."""
        return cls.themes[cls.current_theme]
