"""
Diagnostics and Linting for Spark Editor
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QSplitter, QTextEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QIcon, QTextCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from .theme import ThemeManager
from .icons import get_icon

class DiagnosticItem(QListWidgetItem):
    """List item for displaying a diagnostic (error or warning)"""

    def __init__(self, diagnostic, parent=None):
        super().__init__(parent)
        self.diagnostic = diagnostic
        self.setText(self._format_text())
        self.setIcon(self._get_icon())

    def _format_text(self):
        """Format the diagnostic text"""
        message = self.diagnostic.get("message", "")
        line = self.diagnostic.get("line", 0)
        column = self.diagnostic.get("column", 0)
        return f"Line {line}, Column {column}: {message}"

    def _get_icon(self):
        """Get the icon for the diagnostic"""
        severity = self.diagnostic.get("severity", "info")
        if severity == "error":
            return get_icon("error")
        elif severity == "warning":
            return get_icon("warning")
        else:
            return get_icon("info")

class DiagnosticsPanel(QWidget):
    """Panel for displaying diagnostics (errors and warnings)"""

    diagnosticSelected = pyqtSignal(dict)

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
        self.header.setObjectName("diagnostics-header")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("Problems")
        self.title_label.setObjectName("diagnostics-title")
        self.header_layout.addWidget(self.title_label)

        self.error_count = QLabel("0 errors")
        self.error_count.setObjectName("error-count")
        self.header_layout.addWidget(self.error_count)

        self.warning_count = QLabel("0 warnings")
        self.warning_count.setObjectName("warning-count")
        self.header_layout.addWidget(self.warning_count)

        self.header_layout.addStretch()

        self.layout.addWidget(self.header)

        # Diagnostics list
        self.diagnostics_list = QListWidget()
        self.diagnostics_list.setObjectName("diagnostics-list")
        self.diagnostics_list.itemClicked.connect(self._handle_item_clicked)
        self.layout.addWidget(self.diagnostics_list)

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            #diagnostics-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}

            #diagnostics-title {{
                font-weight: bold;
                color: {theme.text_color};
            }}

            #error-count {{
                color: {theme.error_color};
                margin-left: 10px;
            }}

            #warning-count {{
                color: {theme.warning_color};
                margin-left: 10px;
            }}

            #diagnostics-list {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: none;
            }}

            #diagnostics-list::item {{
                padding: 5px;
                border-bottom: 1px solid {theme.border_color};
            }}

            #diagnostics-list::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}

            #diagnostics-list::item:hover:!selected {{
                background-color: {theme.secondary_color};
            }}
        """)

    def set_diagnostics(self, diagnostics):
        """Set the diagnostics to display"""
        self.diagnostics_list.clear()

        error_count = 0
        warning_count = 0

        for diagnostic in diagnostics:
            item = DiagnosticItem(diagnostic)
            self.diagnostics_list.addItem(item)

            severity = diagnostic.get("severity", "info")
            if severity == "error":
                error_count += 1
            elif severity == "warning":
                warning_count += 1

        # Update counts
        self.error_count.setText(f"{error_count} error{'s' if error_count != 1 else ''}")
        self.warning_count.setText(f"{warning_count} warning{'s' if warning_count != 1 else ''}")

    def _handle_item_clicked(self, item):
        """Handle item click"""
        if isinstance(item, DiagnosticItem):
            self.diagnosticSelected.emit(item.diagnostic)

class DiagnosticHighlighter:
    """Highlighter for diagnostics in the editor"""

    def __init__(self, editor):
        self.editor = editor
        self.diagnostics = []
        # Disabled for stability

    def update_theme(self):
        """Update the theme"""
        # Disabled for stability
        pass

    def set_diagnostics(self, diagnostics):
        """Set the diagnostics to highlight"""
        # Disabled for stability
        pass

    def highlight_diagnostics(self):
        """Highlight the diagnostics in the editor"""
        # Disabled for stability
        pass

class DiagnosticTooltip(QDialog):
    """Tooltip for displaying diagnostic information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # Create the header
        self.header = QLabel()
        self.header.setObjectName("diagnostic-header")
        self.layout.addWidget(self.header)

        # Create the content
        self.content = QLabel()
        self.content.setObjectName("diagnostic-content")
        self.content.setWordWrap(True)
        self.layout.addWidget(self.content)

        # Create the buttons
        self.button_box = QDialogButtonBox()
        self.button_box.setObjectName("diagnostic-buttons")
        self.layout.addWidget(self.button_box)

        # Apply theme
        self.update_theme()

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
            }}

            #diagnostic-header {{
                font-weight: bold;
                color: {theme.primary_color};
                border-bottom: 1px solid {theme.border_color};
                padding-bottom: 5px;
            }}

            #diagnostic-content {{
                padding: 5px;
            }}

            #diagnostic-buttons {{
                border-top: 1px solid {theme.border_color};
                padding-top: 5px;
            }}

            QPushButton {{
                background-color: {theme.button_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 5px 10px;
            }}

            QPushButton:hover {{
                background-color: {theme.secondary_color};
            }}
        """)

    def set_diagnostic(self, diagnostic):
        """Set the diagnostic information"""
        if not diagnostic:
            self.hide()
            return

        message = diagnostic.get("message", "")
        severity = diagnostic.get("severity", "info")

        # Set the header
        self.header.setText(f"{severity.capitalize()}")

        # Set the content
        self.content.setText(message)

        # Clear existing buttons
        self.button_box.clear()

        # Add buttons based on diagnostic type
        if severity == "error":
            # Add a "Fix" button if we have a fix
            if diagnostic.get("fix"):
                fix_button = QPushButton("Fix")
                fix_button.clicked.connect(lambda: self._apply_fix(diagnostic.get("fix")))
                self.button_box.addButton(fix_button, QDialogButtonBox.ButtonRole.ActionRole)

        # Add a close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)
        self.button_box.addButton(close_button, QDialogButtonBox.ButtonRole.RejectRole)

        # Resize the widget
        self.adjustSize()

    def _apply_fix(self, fix):
        """Apply a fix for a diagnostic"""
        # This would be implemented based on the fix type
        pass

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)
