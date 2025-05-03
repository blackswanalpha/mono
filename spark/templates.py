"""
Template browser for Spark Editor
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QStackedWidget, QTextEdit,
    QDialog, QDialogButtonBox, QLineEdit, QFormLayout
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from .theme import ThemeManager
from .icons import get_icon


class TemplateItem:
    """Represents a template file."""

    def __init__(self, path, name, category):
        self.path = path
        self.name = name
        self.category = category
        self.display_name = self._format_display_name(name)

    def _format_display_name(self, name):
        """Format the file name for display."""
        # Remove extension and replace underscores with spaces
        name = os.path.splitext(name)[0].replace('_', ' ')
        # Capitalize each word
        return ' '.join(word.capitalize() for word in name.split())


class TemplatePreview(QWidget):
    """Widget for previewing a template."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_template = None

    def setup_ui(self):
        """Set up the UI elements."""
        layout = QVBoxLayout(self)

        # Header
        self.header_label = QLabel("Template Preview")
        self.header_label.setObjectName("template-header")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.header_label.setFont(font)
        layout.addWidget(self.header_label)

        # Template name
        self.name_label = QLabel()
        self.name_label.setObjectName("template-name")
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)

        # Template category
        self.category_label = QLabel()
        self.category_label.setObjectName("template-category")
        layout.addWidget(self.category_label)

        # Preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setObjectName("template-preview")
        layout.addWidget(self.preview)

        # Buttons
        button_layout = QHBoxLayout()

        self.use_button = QPushButton("Use Template")
        self.use_button.setObjectName("use-template-button")
        self.use_button.setIcon(get_icon("new_file"))
        self.use_button.clicked.connect(self.use_template)
        button_layout.addWidget(self.use_button)

        layout.addLayout(button_layout)

    def set_template(self, template):
        """Set the template to preview."""
        self.current_template = template

        if template:
            self.name_label.setText(template.display_name)
            self.category_label.setText(f"Category: {template.category.capitalize()}")

            # Load and display the template content
            try:
                with open(template.path, 'r') as f:
                    content = f.read()
                self.preview.setText(content)
            except Exception as e:
                self.preview.setText(f"Error loading template: {str(e)}")

            self.use_button.setEnabled(True)
        else:
            self.name_label.setText("")
            self.category_label.setText("")
            self.preview.setText("")
            self.use_button.setEnabled(False)

    def use_template(self):
        """Use the selected template."""
        if not self.current_template:
            return

        dialog = NewFileDialog(self.current_template, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # The dialog will handle creating the new file
            pass

    def update_theme(self):
        """Update the theme."""
        theme = ThemeManager.get_current_theme()

        self.setStyleSheet(f"""
            #template-header {{
                color: {theme.text_color};
                margin-bottom: 10px;
            }}

            #template-name {{
                color: {theme.primary_color};
                margin-bottom: 5px;
            }}

            #template-category {{
                color: {theme.text_dim_color};
                margin-bottom: 15px;
            }}

            #use-template-button {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}

            #use-template-button:hover {{
                background-color: {theme.secondary_color};
            }}

            #use-template-button:disabled {{
                background-color: #555555;
                color: {theme.text_dim_color};
            }}
        """)


class NewFileDialog(QDialog):
    """Dialog for creating a new file from a template."""

    def __init__(self, template, parent=None):
        super().__init__(parent)
        self.template = template
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI elements."""
        self.setWindowTitle("Create New File from Template")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Form layout for inputs
        form_layout = QFormLayout()

        # File name input
        self.name_input = QLineEdit()
        suggested_name = os.path.splitext(os.path.basename(self.template.path))[0] + ".mono"
        self.name_input.setText(suggested_name)
        form_layout.addRow("File Name:", self.name_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        """Handle dialog acceptance."""
        file_name = self.name_input.text().strip()

        if not file_name:
            return

        if not file_name.endswith(".mono"):
            file_name += ".mono"

        # Get the parent window (should be the main editor)
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'new_file_from_template'):
            main_window = main_window.parent()

        if main_window and hasattr(main_window, 'new_file_from_template'):
            main_window.new_file_from_template(self.template.path, file_name)

        super().accept()


class TemplateBrowser(QWidget):
    """Widget for browsing and selecting templates."""

    template_selected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates = []
        self.setup_ui()
        self.load_templates()
        self.update_theme()

    def setup_ui(self):
        """Set up the UI elements."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Template list
        list_layout = QVBoxLayout()

        self.category_widget = QStackedWidget()

        # Create list widgets for each category
        self.category_lists = {}
        self.category_buttons = {}

        for category in ["basic", "intermediate", "advanced"]:
            list_widget = QListWidget()
            list_widget.setObjectName(f"{category}-list")
            list_widget.itemClicked.connect(self.handle_item_clicked)
            self.category_lists[category] = list_widget
            self.category_widget.addWidget(list_widget)

        # Category buttons
        button_layout = QHBoxLayout()

        for category in ["basic", "intermediate", "advanced"]:
            button = QPushButton(category.capitalize())
            button.setObjectName(f"{category}-button")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, c=category: self.switch_category(c))
            self.category_buttons[category] = button
            button_layout.addWidget(button)

        # Select the first category by default
        self.category_buttons["basic"].setChecked(True)
        self.category_widget.setCurrentWidget(self.category_lists["basic"])

        list_layout.addLayout(button_layout)
        list_layout.addWidget(self.category_widget)

        # Preview
        self.preview = TemplatePreview()

        # Add widgets to main layout
        layout.addLayout(list_layout, 1)
        layout.addWidget(self.preview, 2)

    def load_templates(self):
        """Load templates from the projects directory."""
        self.templates = []

        # Get the projects directory
        projects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")

        if not os.path.exists(projects_dir):
            return

        # Load templates from each category
        for category in ["basic", "intermediate", "advanced"]:
            category_dir = os.path.join(projects_dir, category)

            if not os.path.exists(category_dir):
                continue

            # Get all .mono files in the category directory
            for file_name in os.listdir(category_dir):
                if file_name.endswith(".mono"):
                    file_path = os.path.join(category_dir, file_name)
                    template = TemplateItem(file_path, file_name, category)
                    self.templates.append(template)

                    # Add to the appropriate list widget
                    item = QListWidgetItem(template.display_name)
                    item.setData(Qt.ItemDataRole.UserRole, template)
                    self.category_lists[category].addItem(item)

    def switch_category(self, category):
        """Switch to the specified category."""
        # Update button states
        for cat, button in self.category_buttons.items():
            button.setChecked(cat == category)

        # Switch to the selected category
        self.category_widget.setCurrentWidget(self.category_lists[category])

    def handle_item_clicked(self, item):
        """Handle template item selection."""
        template = item.data(Qt.ItemDataRole.UserRole)
        self.preview.set_template(template)
        self.template_selected.emit(template)

    def update_theme(self):
        """Update the theme."""
        theme = ThemeManager.get_current_theme()

        # Update the preview
        self.preview.update_theme()

        # Update list widgets
        list_style = f"""
            QListWidget {{
                background-color: {theme.panel_bg};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 5px;
            }}

            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}

            QListWidget::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}

            QListWidget::item:hover:!selected {{
                background-color: {theme.secondary_color};
            }}
        """

        for list_widget in self.category_lists.values():
            list_widget.setStyleSheet(list_style)

        # Update category buttons
        button_style = f"""
            QPushButton {{
                background-color: {theme.button_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 8px 16px;
            }}

            QPushButton:hover {{
                background-color: {theme.secondary_color};
            }}

            QPushButton:checked {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}
        """

        for button in self.category_buttons.values():
            button.setStyleSheet(button_style)
