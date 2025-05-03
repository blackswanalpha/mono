"""
Code Completion Widget for Spark Editor
"""

from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QLabel,
    QStyledItemDelegate, QStyle, QApplication, QHBoxLayout
)
from PyQt6.QtGui import QColor, QTextCharFormat, QPainter, QFont, QIcon, QTextCursor
from PyQt6.QtCore import Qt, QSize, QRect, QEvent, pyqtSignal, QTimer

from .theme import ThemeManager
from .icons import get_icon

class CompletionItemDelegate(QStyledItemDelegate):
    """Custom delegate for rendering completion items"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_theme()

    def update_theme(self):
        """Update the theme colors"""
        theme = ThemeManager.get_current_theme()
        self.keyword_color = QColor(theme.syntax_keyword)
        self.type_color = QColor(theme.syntax_class)
        self.component_color = QColor(theme.syntax_class)
        self.function_color = QColor(theme.syntax_function)
        self.variable_color = QColor(theme.syntax_variable)
        self.state_color = QColor(theme.syntax_variable)
        self.method_color = QColor(theme.syntax_function)
        self.text_color = QColor(theme.text_color)
        self.detail_color = QColor(theme.text_dim_color)

    def paint(self, painter, option, index):
        """Paint the completion item"""
        # Get item data
        item_data = index.data(Qt.ItemDataRole.UserRole)
        if not item_data:
            super().paint(painter, option, index)
            return

        text = item_data.get("text", "")
        item_type = item_data.get("type", "")
        detail = item_data.get("detail", "")

        # Set up the painter
        painter.save()

        # Draw the selection background if selected
        if option.state & QStyle.StateFlag.State_Selected:
            theme = ThemeManager.get_current_theme()
            painter.fillRect(option.rect, QColor(theme.primary_color))
            text_color = QColor(theme.text_bright_color)
            detail_color = QColor(theme.text_bright_color).lighter(150)
        else:
            text_color = self.text_color
            detail_color = self.detail_color

        # Draw the icon based on item type
        icon_rect = QRect(option.rect.left() + 5, option.rect.top() + 5, 16, 16)
        if item_type == "keyword":
            painter.setPen(self.keyword_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "K")
        elif item_type == "type":
            painter.setPen(self.type_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "T")
        elif item_type == "component":
            painter.setPen(self.component_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "C")
        elif item_type == "function":
            painter.setPen(self.function_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "F")
        elif item_type == "variable":
            painter.setPen(self.variable_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "V")
        elif item_type == "state":
            painter.setPen(self.state_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "S")
        elif item_type == "method":
            painter.setPen(self.method_color)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "M")

        # Draw the text
        text_rect = QRect(option.rect.left() + 30, option.rect.top() + 5,
                          option.rect.width() - 35, option.rect.height() // 2)
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)

        # Draw the detail
        if detail:
            detail_rect = QRect(option.rect.left() + 30, option.rect.top() + option.rect.height() // 2,
                               option.rect.width() - 35, option.rect.height() // 2)
            painter.setPen(detail_color)
            painter.setFont(QFont(painter.font().family(), painter.font().pointSize() - 1))
            painter.drawText(detail_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, detail)

        painter.restore()

    def sizeHint(self, option, index):
        """Return the size hint for the item"""
        item_data = index.data(Qt.ItemDataRole.UserRole)
        if not item_data or not item_data.get("detail"):
            return QSize(option.rect.width(), 30)
        else:
            return QSize(option.rect.width(), 45)

class CompletionListWidget(QListWidget):
    """Base list widget for displaying code completion suggestions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Find the editor (parent's parent)
        self.editor = None
        if parent and hasattr(parent, 'editor'):
            self.editor = parent.editor

        # Install event filter
        self.installEventFilter(self)

        # Set up the delegate
        self.delegate = CompletionItemDelegate(self)
        self.setItemDelegate(self.delegate)

    def eventFilter(self, obj, event):
        """Filter events to ensure focus stays with the editor"""
        if event.type() == QEvent.Type.FocusIn:
            # Redirect focus to editor
            if self.editor:
                self.editor.setFocus()
            return True

        # Let other events pass through
        return super().eventFilter(obj, event)

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                color: {theme.text_color};
                border: none;
                padding: 5px;
            }}

            QListWidget::item {{
                padding: 5px;
                border-radius: {theme.border_radius}px;
            }}

            QListWidget::item:selected {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
            }}

            QListWidget::item:hover:!selected {{
                background-color: {theme.secondary_color};
            }}
        """)

        # Update the delegate
        self.delegate.update_theme()


class CompletionList(QWidget):
    """Widget for displaying code completion suggestions with a close button"""

    completionSelected = pyqtSignal(str)
    completionClosed = pyqtSignal()  # Signal for when completion is closed

    # Add methods to mimic QListWidget interface for backward compatibility
    def currentItem(self):
        """Get the current item from the list widget"""
        return self.list_widget.currentItem()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Use Popup window type with WindowStaysOnTopHint to ensure it stays visible but doesn't steal focus
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Store the parent editor for focus management
        self.editor = parent

        # Install event filter to handle focus events
        self.installEventFilter(self)

        # Flag to track if we're currently processing a key event
        self.processing_key_event = False

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create header with close button
        self.header = QWidget()
        self.header.setFixedHeight(20)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(5, 2, 5, 2)

        # Add title label
        self.title_label = QLabel("Completions")
        self.title_label.setStyleSheet("font-size: 9px; color: gray;")
        self.header_layout.addWidget(self.title_label)

        # Add spacer
        self.header_layout.addStretch()

        # Add close button
        self.close_button = QLabel("×")
        self.close_button.setFixedSize(16, 16)
        self.close_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setToolTip("Close completion")
        self.close_button.setStyleSheet("color: gray; font-weight: bold;")
        self.close_button.mousePressEvent = self._close_button_clicked
        self.header_layout.addWidget(self.close_button)

        # Add header to main layout
        self.layout.addWidget(self.header)

        # Create list widget
        self.list_widget = CompletionListWidget()
        self.list_widget.itemClicked.connect(self._handle_item_clicked)
        self.layout.addWidget(self.list_widget)

        # Store all completions for filtering
        self.all_completions = []
        self.current_filter = ""

        # Apply theme
        self.update_theme()

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
            }}
        """)

        # Update header style
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
                border-top-left-radius: {theme.border_radius}px;
                border-top-right-radius: {theme.border_radius}px;
            }}
        """)

        # Update list widget
        self.list_widget.update_theme()

    def _close_button_clicked(self, event):
        """Handle close button click"""
        self.hide()
        self.completionClosed.emit()

    def set_completions(self, completions):
        """Set the completion suggestions"""
        self.all_completions = completions
        self._update_displayed_completions()

    def filter_completions(self, filter_text):
        """Filter completions based on the given text"""
        self.current_filter = filter_text
        self._update_displayed_completions()

    def _update_displayed_completions(self):
        """Update the displayed completions based on the current filter"""
        # Store the currently selected item's text if any
        current_selected_text = ""
        current_item = self.list_widget.currentItem()
        if current_item:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            if item_data:
                current_selected_text = item_data.get("text", "")

        # Remember the current scroll position
        scroll_position = self.list_widget.verticalScrollBar().value()

        # Clear the list
        self.list_widget.clear()

        # If filter is empty, show all completions
        if not self.current_filter:
            filtered_completions = self.all_completions
        else:
            # Filter completions based on the current filter
            filtered_completions = []
            for completion in self.all_completions:
                text = completion.get("text", "").lower()
                filter_lower = self.current_filter.lower()

                # Exact prefix match (highest priority)
                if text.startswith(filter_lower):
                    # Add score for sorting
                    completion_copy = completion.copy()
                    completion_copy["score"] = 1.0
                    filtered_completions.append(completion_copy)
                # Contains filter (medium priority)
                elif filter_lower in text:
                    # Add score for sorting
                    completion_copy = completion.copy()
                    completion_copy["score"] = 0.5
                    filtered_completions.append(completion_copy)
                # Fuzzy match (lowest priority)
                elif self._fuzzy_match(filter_lower, text):
                    # Add score for sorting
                    completion_copy = completion.copy()
                    completion_copy["score"] = 0.3
                    filtered_completions.append(completion_copy)

        # Sort by score if available
        if filtered_completions and "score" in filtered_completions[0]:
            filtered_completions.sort(key=lambda c: c.get("score", 0), reverse=True)

        # Add filtered completions to the list
        selected_index = -1
        for i, completion in enumerate(filtered_completions):
            item = QListWidgetItem()
            # Remove score if it was added
            if "score" in completion:
                completion_copy = completion.copy()
                del completion_copy["score"]
                item.setData(Qt.ItemDataRole.UserRole, completion_copy)
                # Check if this was the previously selected item
                if completion_copy.get("text", "") == current_selected_text:
                    selected_index = i
            else:
                item.setData(Qt.ItemDataRole.UserRole, completion)
                # Check if this was the previously selected item
                if completion.get("text", "") == current_selected_text:
                    selected_index = i
            self.list_widget.addItem(item)

        # Select the previously selected item if it's still in the list
        # Otherwise select the first item if available
        if selected_index >= 0:
            self.list_widget.setCurrentRow(selected_index)
        elif self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

        # Restore the scroll position if possible
        if self.list_widget.count() > 0:
            self.list_widget.verticalScrollBar().setValue(scroll_position)

        # Resize to fit content but limit the height
        self.adjustSize()
        if self.height() > 400:
            self.setFixedHeight(400)

        # Limit width to a reasonable size
        if self.width() > 500:
            self.setFixedWidth(500)

        # Update the title to show filter
        if self.current_filter:
            self.title_label.setText(f"Completions for '{self.current_filter}'")
        else:
            self.title_label.setText("Completions")

    def _fuzzy_match(self, pattern, text):
        """Simple fuzzy matching algorithm"""
        # If pattern is empty, it matches anything
        if not pattern:
            return True

        # If text is empty, it can't match a non-empty pattern
        if not text:
            return False

        # If pattern is longer than text, it can't match
        if len(pattern) > len(text):
            return False

        # Check if all characters in pattern appear in order in text
        i, j = 0, 0
        while i < len(pattern) and j < len(text):
            if pattern[i] == text[j]:
                i += 1
            j += 1

        # If we've gone through all characters in pattern, it's a match
        return i == len(pattern)

    def _handle_item_clicked(self, item):
        """Handle item click"""
        item_data = item.data(Qt.ItemDataRole.UserRole)
        if item_data:
            completion_text = item_data.get("text", "")
            self.completionSelected.emit(completion_text)

            # Only close the completion list if it's not a special completion
            # Special completions are those that end with characters that should trigger new completions
            if not completion_text.endswith(('.', '(')):
                # Emit the closed signal
                self.completionClosed.emit()

    def hideEvent(self, event):
        """Handle hide event"""
        super().hideEvent(event)
        # Emit the closed signal
        self.completionClosed.emit()

    def eventFilter(self, obj, event):
        """Filter events to handle focus and other interactions"""
        if event.type() == QEvent.Type.Show:
            # When shown, ensure the editor has focus
            if self.editor:
                self.editor.setFocus()
                # Raise the completion list to ensure it's visible
                self.raise_()
            return False
        elif event.type() == QEvent.Type.WindowActivate:
            # Prevent activation - keep focus on editor
            if self.editor:
                self.editor.setFocus()
                # Raise the completion list to ensure it's visible
                self.raise_()
            return True
        elif event.type() == QEvent.Type.FocusIn:
            # Redirect focus to editor
            if self.editor:
                self.editor.setFocus()
            return True
        elif event.type() == QEvent.Type.KeyPress and not self.processing_key_event:
            # Prevent recursive event handling
            self.processing_key_event = True

            try:
                # Let the editor handle all key events
                if self.editor:
                    # Only handle navigation keys in the completion list
                    key = event.key()
                    if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
                              Qt.Key.Key_Home, Qt.Key.Key_End, Qt.Key.Key_Tab, Qt.Key.Key_Return,
                              Qt.Key.Key_Enter, Qt.Key.Key_Escape):
                        # Handle these keys in our keyPressEvent
                        self.keyPressEvent(event)
                        return True
                    else:
                        # For all other keys, let the editor handle them
                        # Make sure the editor has focus
                        self.editor.setFocus()

                        # Don't handle the event here - let it propagate to the editor
                        return False
            finally:
                # Reset the flag
                self.processing_key_event = False

        # Let other events pass through
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            # No need to emit completionClosed here as hideEvent will do it
            event.accept()
        elif event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            current_item = self.list_widget.currentItem()
            if current_item:
                item_data = current_item.data(Qt.ItemDataRole.UserRole)
                if item_data:
                    completion_text = item_data.get("text", "")
                    self.completionSelected.emit(completion_text)

                    # Only close the completion list if it's not a special completion
                    if not completion_text.endswith(('.', '(')):
                        self.hide()
            else:
                self.hide()
            event.accept()
        elif event.key() == Qt.Key.Key_Tab:
            current_item = self.list_widget.currentItem()
            if current_item:
                item_data = current_item.data(Qt.ItemDataRole.UserRole)
                if item_data:
                    completion_text = item_data.get("text", "")
                    self.completionSelected.emit(completion_text)

                    # Only close the completion list if it's not a special completion
                    if not completion_text.endswith(('.', '(')):
                        self.hide()
            else:
                self.hide()
            event.accept()
        elif event.key() == Qt.Key.Key_Up:
            # Navigate up in the list
            current_row = self.list_widget.currentRow()
            if current_row > 0:
                self.list_widget.setCurrentRow(current_row - 1)
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            # Navigate down in the list
            current_row = self.list_widget.currentRow()
            if current_row < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(current_row + 1)
            event.accept()
        elif event.key() == Qt.Key.Key_PageUp:
            # Navigate up by a page
            current_row = max(0, self.list_widget.currentRow() - 5)
            self.list_widget.setCurrentRow(current_row)
            event.accept()
        elif event.key() == Qt.Key.Key_PageDown:
            # Navigate down by a page
            current_row = min(self.list_widget.count() - 1, self.list_widget.currentRow() + 5)
            self.list_widget.setCurrentRow(current_row)
            event.accept()
        elif event.key() == Qt.Key.Key_Home:
            # Go to the first item
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
            event.accept()
        elif event.key() == Qt.Key.Key_End:
            # Go to the last item
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(self.list_widget.count() - 1)
            event.accept()
        else:
            # For all other keys, we don't handle them here
            # This allows the editor to receive them
            event.ignore()

            # Make sure the editor has focus for typing
            if self.editor:
                # Ensure the editor gets focus
                self.editor.setFocus()

                # We don't directly forward the event as it would cause recursion
                # The editor will receive it naturally since it has focus

                # If the key is a printable character, we should update the completion list
                # after the editor has processed it
                if len(event.text()) > 0 and event.text().isprintable():
                    # Use a very short timer to update the completion list after the editor has processed the key
                    QTimer.singleShot(10, lambda: self._update_after_key_press())

    def _update_after_key_press(self):
        """Update the completion list after a key press in the editor"""
        if not self.editor:
            return

        try:
            # Get the current word from the editor
            cursor = self.editor.textCursor()
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            current_word = cursor.selectedText()

            # Filter completions based on the current word
            self.filter_completions(current_word)

            # Reposition the completion list
            cursor_rect = self.editor.cursorRect()
            position = self.editor.mapToGlobal(cursor_rect.bottomRight())
            self.move(position)

            # If there are no completions left, hide the list
            if self.list_widget.count() == 0:
                self.hide()
                return

            # Make sure we're visible and on top
            if not self.isVisible():
                self.show()
            self.raise_()

            # Ensure the editor keeps focus
            self.editor.setFocus()
        except Exception as e:
            print(f"Error in _update_after_key_press: {str(e)}")

class CompletionWidget(QWidget):
    """Widget for displaying code completion information"""

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
        self.header = QLabel("Completion")
        self.header.setObjectName("completion-header")
        self.layout.addWidget(self.header)

        # Create the content
        self.content = QLabel()
        self.content.setObjectName("completion-content")
        self.content.setWordWrap(True)
        self.layout.addWidget(self.content)

        # Apply theme
        self.update_theme()

    def update_theme(self):
        """Update the theme"""
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.panel_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
            }}

            #completion-header {{
                font-weight: bold;
                color: {theme.primary_color};
                border-bottom: 1px solid {theme.border_color};
                padding-bottom: 5px;
            }}

            #completion-content {{
                padding: 5px;
            }}
        """)

    def set_completion(self, completion):
        """Set the completion information"""
        if not completion:
            self.hide()
            return

        text = completion.get("text", "")
        item_type = completion.get("type", "")
        detail = completion.get("detail", "")

        # Set the header
        self.header.setText(f"{item_type.capitalize()}: {text}")

        # Set the content
        if detail:
            self.content.setText(detail)
        else:
            self.content.setText("")

        # Resize the widget
        self.adjustSize()

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)
