"""
Enhanced code editor for Spark
"""

import re
import logging
from PyQt6.QtWidgets import (
    QTextEdit, QWidget, QPlainTextEdit
)
from PyQt6.QtGui import (
    QColor, QTextFormat, QPainter, QTextCharFormat, QSyntaxHighlighter,
    QFont, QFontMetrics, QTextCursor
)
from PyQt6.QtCore import Qt, QRect, QSize, QTimer

# Configure logger
logger = logging.getLogger('spark_editor.editor')

from .theme import ThemeManager
from .code_intelligence import CodeIntelligenceManager
from .optimized_code_intelligence import OptimizedCodeIntelligenceManager
from .code_completion import CompletionList, CompletionWidget
from .diagnostics import DiagnosticHighlighter, DiagnosticTooltip
from .code_navigation import NavigationManager, NavigationContextMenu
from .error_manager import ErrorManager, ErrorType, ErrorContext, handle_errors, detect_error_type


class LineNumberArea(QWidget):
    """Line number area widget for the code editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        """Return the size hint for the line number area."""
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """Paint the line number area."""
        self.editor.line_number_area_paint_event(event)


class MonoSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Mono language."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_theme()

    def update_theme(self):
        """Update the syntax highlighting colors from the current theme."""
        theme = ThemeManager.get_current_theme()

        self.highlighting_rules = []

        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(theme.syntax_keyword))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            "component", "function", "var", "state", "props", "return",
            "if", "else", "for", "while", "new", "this", "import", "export",
            "true", "false", "null", "undefined", "print", "emit", "on",
            "registerService", "getService", "provideContext", "consumeContext"
        ]

        for word in keywords:
            pattern = f"\\b{word}\\b"
            self.highlighting_rules.append((pattern, keyword_format))

        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(theme.syntax_number))
        self.highlighting_rules.append((r'\b[0-9]+\b', number_format))

        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(theme.syntax_string))
        self.highlighting_rules.append((r'"[^"]*"', string_format))
        self.highlighting_rules.append((r"'[^']*'", string_format))

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(theme.syntax_comment))
        self.highlighting_rules.append((r'//[^\n]*', comment_format))

        # Element format
        element_format = QTextCharFormat()
        element_format.setForeground(QColor(theme.syntax_element))
        self.highlighting_rules.append((r'<[^>]*>', element_format))

        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(theme.syntax_function))
        self.highlighting_rules.append((r'\b[A-Za-z0-9_]+(?=\()', function_format))

        # Class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(theme.syntax_class))
        self.highlighting_rules.append((r'\b[A-Z][A-Za-z0-9_]*\b', class_format))

        # Variable format
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor(theme.syntax_variable))
        self.highlighting_rules.append((r'\bthis\.[A-Za-z0-9_]+\b', variable_format))

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class CodeEditor(QPlainTextEdit):
    """Enhanced code editor with line numbers, syntax highlighting, and intelligent code features."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None

        # Set up the editor
        self.setup_editor()

        # Create the line number area
        self.line_number_area = LineNumberArea(self)

        # Set up code intelligence
        self.setup_code_intelligence()

        # Extra selections for different purposes
        self.current_line_selections = []
        self.diagnostic_selections = []

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self.update_cursor_position)
        self.textChanged.connect(self.handle_text_changed)

        # Initialize the line number area width
        self.update_line_number_area_width(0)

        # Highlight the current line
        self.highlight_current_line()

        # Set minimum size to ensure editor is visible
        self.setMinimumHeight(200)
        self.setMinimumWidth(400)

        # Apply theme
        self.update_theme()

    def setup_editor(self):
        """Set up the editor with default settings."""
        # Set font
        font = QFont("Consolas, 'Courier New', monospace", 10)
        font.setFixedPitch(True)
        self.setFont(font)

        # Set tab width
        metrics = QFontMetrics(font)
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))

        # Create syntax highlighter
        self.highlighter = MonoSyntaxHighlighter(self.document())

        # Enable line wrapping
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # Set placeholder text
        self.setPlaceholderText("Type your Mono code here...")

        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def setup_code_intelligence(self):
        """Set up code intelligence features."""
        # Code intelligence manager (using optimized version)
        self.code_intelligence = OptimizedCodeIntelligenceManager(self)
        self.code_intelligence.completionsUpdated.connect(self.update_completions)
        self.code_intelligence.diagnosticsUpdated.connect(self.update_diagnostics)
        self.code_intelligence.symbolsUpdated.connect(self.update_symbols)

        # Completion list
        self.completion_list = CompletionList(self)  # Pass self as parent
        self.completion_list.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.completion_list.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.completion_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.completion_list.completionSelected.connect(self.insert_completion)
        self.completion_list.completionClosed.connect(self.handle_completion_closed)
        self.completion_list.hide()

        # Completion widget
        self.completion_widget = CompletionWidget()
        self.completion_widget.hide()

        # Diagnostic highlighter
        self.diagnostic_highlighter = DiagnosticHighlighter(self)

        # Diagnostic tooltip
        self.diagnostic_tooltip = DiagnosticTooltip()
        self.diagnostic_tooltip.hide()

        # Navigation manager
        self.navigation_manager = NavigationManager(self)

        # Navigation context menu
        self.navigation_menu = NavigationContextMenu()
        self.navigation_menu.go_to_definition_action.triggered.connect(self.go_to_definition)
        self.navigation_menu.find_references_action.triggered.connect(self.find_references)
        self.navigation_menu.go_back_action.triggered.connect(self.navigation_manager.go_back)
        self.navigation_menu.go_forward_action.triggered.connect(self.navigation_manager.go_forward)

        # Completion timer - faster response time (250ms instead of 500ms)
        self.completion_timer = QTimer(self)
        self.completion_timer.setSingleShot(True)
        self.completion_timer.timeout.connect(self.show_completions)

        # Completion hide timer - to prevent flickering when typing
        self.completion_hide_timer = QTimer(self)
        self.completion_hide_timer.setSingleShot(True)
        self.completion_hide_timer.timeout.connect(self.hide_completions_delayed)

        # Completion state tracking
        self.completion_active = False
        self.last_completion_prefix = ""
        self.last_completion = ""
        self.just_completed = False
        self.completion_closed_event = False  # Track when completion is closed
        self.completion_min_chars = 1  # Show completions after typing at least 1 character

        # Completion trigger characters (characters that should trigger completion)
        self.completion_triggers = ['.', '_', '(', ')', '[', ']', '{', '}']

        # Completion continue characters (characters that should keep completion open)
        self.completion_continue_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.')

        # Current state
        self.current_word = ""
        self.current_line = 0
        self.current_column = 0

    def update_theme(self):
        """Update the editor's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()

        # Update font
        font = QFont(theme.font_family, theme.font_size)
        font.setFixedPitch(True)
        self.setFont(font)

        # Update colors
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.editor_bg};
                color: {theme.text_color};
                border: none;
                selection-background-color: {theme.primary_color};
                selection-color: {theme.text_bright_color};
            }}
        """)

        # Update syntax highlighter
        self.highlighter.update_theme()
        self.highlighter.rehighlight()

        # Update current line highlight
        self.highlight_current_line()

        # Update code intelligence components
        if hasattr(self, 'completion_list'):
            self.completion_list.update_theme()

        if hasattr(self, 'completion_widget'):
            self.completion_widget.update_theme()

        if hasattr(self, 'diagnostic_highlighter'):
            self.diagnostic_highlighter.update_theme()

        if hasattr(self, 'diagnostic_tooltip'):
            self.diagnostic_tooltip.update_theme()

        if hasattr(self, 'navigation_menu'):
            self.navigation_menu.update_theme()

    def line_number_area_width(self):
        """Calculate the width of the line number area."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Update the width of the line number area."""
        # Don't use the decorator here to avoid the KeyboardInterrupt issue
        error_manager = ErrorManager.get_instance()

        try:
            # Get the width safely
            try:
                width = self.line_number_area_width()
            except Exception as width_error:
                logger.error(f"Error calculating line number area width: {str(width_error)}")
                width = 30  # Use a default width as fallback

            # Set the viewport margins safely
            self.setViewportMargins(width, 0, 0, 0)
        except KeyboardInterrupt:
            # Handle keyboard interrupt gracefully
            logger.warning("KeyboardInterrupt in update_line_number_area_width - handled safely")
            # Don't propagate the interrupt
            return
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.UI,
                exception=e,
                method_name='update_line_number_area_width',
                additional_info={
                    'editor': self
                }
            )

            # Handle the error with extra protection
            try:
                error_manager.handle_error(error_context)
            except Exception as handle_error:
                # Last resort error handling
                logger.critical(f"Failed to handle error in update_line_number_area_width: {str(handle_error)}")

            logger.error(f"Error in update_line_number_area_width: {str(e)}")

    def update_line_number_area(self, rect, dy):
        """Update the line number area when the editor's viewport is scrolled."""
        # Don't use the decorator here to avoid the KeyboardInterrupt issue
        error_manager = ErrorManager.get_instance()

        try:
            if dy:
                self.line_number_area.scroll(0, dy)
            else:
                # Only update if the line number area exists and is valid
                if hasattr(self, 'line_number_area') and self.line_number_area:
                    try:
                        width = self.line_number_area.width()
                        self.line_number_area.update(0, rect.y(), width, rect.height())
                    except Exception as inner_e:
                        logger.error(f"Error updating line number area: {str(inner_e)}")
        except KeyboardInterrupt:
            # Handle keyboard interrupt gracefully
            logger.warning("KeyboardInterrupt in update_line_number_area - handled safely")
            # Don't propagate the interrupt
            return
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.UI,
                exception=e,
                method_name='update_line_number_area',
                additional_info={
                    'editor': self,
                    'rect_valid': hasattr(rect, 'y'),
                    'dy': dy
                }
            )

            # Handle the error
            try:
                error_manager.handle_error(error_context)
            except Exception as handle_error:
                # Last resort error handling
                logger.critical(f"Failed to handle error in update_line_number_area: {str(handle_error)}")

            logger.error(f"Error in update_line_number_area: {str(e)}")

    def resizeEvent(self, event):
        """Handle resize events to adjust the line number area."""
        # Don't use the decorator here to avoid the KeyboardInterrupt issue
        error_manager = ErrorManager.get_instance()

        # Always call the parent's resizeEvent first to ensure proper widget resizing
        try:
            super().resizeEvent(event)
        except Exception as parent_error:
            logger.error(f"Error in parent's resizeEvent: {str(parent_error)}")
            # Try again with a clean event if possible
            try:
                # Create a simple event manually if QResizeEvent is not available
                class SimpleResizeEvent:
                    def __init__(self, size):
                        self.size_value = size
                    def size(self):
                        return self.size_value

                simple_event = SimpleResizeEvent(self.size())
                super().resizeEvent(simple_event)
            except Exception as fallback_error:
                logger.error(f"Error in fallback resizeEvent: {str(fallback_error)}")
                # Just continue without retrying

        try:
            # Get the contents rect safely
            try:
                cr = self.contentsRect()
            except Exception as rect_error:
                logger.error(f"Error getting contents rect: {str(rect_error)}")
                return  # Exit early if we can't get the contents rect

            # Get the line number area width safely
            try:
                width = self.line_number_area_width()
            except Exception as width_error:
                logger.error(f"Error getting line number area width: {str(width_error)}")
                width = 30  # Use a default width as fallback

            # Set the geometry safely
            if hasattr(self, 'line_number_area') and self.line_number_area:
                try:
                    self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), width, cr.height()))
                except Exception as geometry_error:
                    logger.error(f"Error setting line number area geometry: {str(geometry_error)}")
        except KeyboardInterrupt:
            # Handle keyboard interrupt gracefully
            logger.warning("KeyboardInterrupt in resizeEvent - handled safely")
            # Don't propagate the interrupt
            return
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.UI,
                exception=e,
                method_name='resizeEvent',
                additional_info={
                    'editor': self,
                    'event_valid': hasattr(event, 'size')
                }
            )

            # Handle the error with extra protection
            try:
                error_manager.handle_error(error_context)
            except Exception as handle_error:
                # Last resort error handling
                logger.critical(f"Failed to handle error in resizeEvent: {str(handle_error)}")

            logger.error(f"Error in resizeEvent: {str(e)}")

    def line_number_area_paint_event(self, event):
        """Paint the line number area."""
        # Don't use the decorator here to avoid the KeyboardInterrupt issue
        error_manager = ErrorManager.get_instance()
        painter = None

        try:
            # Get theme safely
            try:
                theme = ThemeManager.get_current_theme()
            except Exception as theme_error:
                logger.error(f"Error getting theme: {str(theme_error)}")
                # Use default colors as fallback
                panel_bg = "#2D2D30"
                text_dim_color = "#6D6D6D"
            else:
                panel_bg = theme.panel_bg
                text_dim_color = theme.text_dim_color

            # Create painter safely
            try:
                painter = QPainter(self.line_number_area)
                painter.fillRect(event.rect(), QColor(panel_bg))
            except Exception as painter_error:
                logger.error(f"Error creating painter: {str(painter_error)}")
                return  # Exit early if we can't create the painter

            # Get first visible block safely
            try:
                block = self.firstVisibleBlock()
                block_number = block.blockNumber()
                top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
                bottom = top + round(self.blockBoundingRect(block).height())
            except Exception as block_error:
                logger.error(f"Error getting first visible block: {str(block_error)}")
                if painter:
                    painter.end()  # Make sure to end the painter
                return  # Exit early if we can't get the first block

            # Paint line numbers with a limit to prevent infinite loops
            max_iterations = 1000  # Safety limit
            iteration_count = 0

            try:
                while block.isValid() and top <= event.rect().bottom() and iteration_count < max_iterations:
                    if block.isVisible() and bottom >= event.rect().top():
                        number = str(block_number + 1)
                        painter.setPen(QColor(text_dim_color))

                        # Get width safely
                        try:
                            width = self.line_number_area.width() - 5
                        except Exception:
                            width = 25  # Default fallback width

                        # Get height safely
                        try:
                            height = self.fontMetrics().height()
                        except Exception:
                            height = 15  # Default fallback height

                        painter.drawText(0, top, width, height,
                                        Qt.AlignmentFlag.AlignRight, number)

                    # Move to next block safely
                    try:
                        block = block.next()
                        top = bottom
                        bottom = top + round(self.blockBoundingRect(block).height())
                        block_number += 1
                    except Exception as next_block_error:
                        logger.error(f"Error moving to next block: {str(next_block_error)}")
                        break  # Break the loop if we can't move to the next block

                    iteration_count += 1

                if iteration_count >= max_iterations:
                    logger.warning("Reached maximum iterations in line_number_area_paint_event")
            finally:
                # Always end the painter if it exists
                if painter:
                    painter.end()

        except KeyboardInterrupt:
            # Handle keyboard interrupt gracefully
            logger.warning("KeyboardInterrupt in line_number_area_paint_event - handled safely")
            # Make sure to end the painter if it exists
            if painter and painter.isActive():
                try:
                    painter.end()
                except Exception:
                    pass  # Ignore errors when ending the painter
            # Don't propagate the interrupt
            return
        except Exception as e:
            # Make sure to end the painter if it exists
            if painter and painter.isActive():
                try:
                    painter.end()
                except Exception:
                    pass  # Ignore errors when ending the painter

            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.UI,
                exception=e,
                method_name='line_number_area_paint_event',
                additional_info={
                    'editor': self,
                    'event_valid': hasattr(event, 'rect')
                }
            )

            # Handle the error with extra protection
            try:
                error_manager.handle_error(error_context)
            except Exception as handle_error:
                # Last resort error handling
                logger.critical(f"Failed to handle error in line_number_area_paint_event: {str(handle_error)}")

            logger.error(f"Error in line_number_area_paint_event: {str(e)}")

    def highlight_current_line(self):
        """Highlight the current line."""
        try:
            theme = ThemeManager.get_current_theme()

            self.current_line_selections = []

            if not self.isReadOnly():
                selection = QTextEdit.ExtraSelection()

                line_color = QColor(theme.primary_color)
                line_color.setAlpha(40)  # Semi-transparent

                selection.format.setBackground(line_color)
                selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()

                self.current_line_selections.append(selection)

            # Update selections
            self._update_extra_selections()
        except Exception as e:
            # If there's an error, clear all selections
            self.current_line_selections = []
            self.setExtraSelections([])

    def load_file(self, file_path):
        """Load a file into the editor."""
        try:
            with open(file_path, 'r') as f:
                self.setPlainText(f.read())
            self.current_file = file_path
            return True
        except Exception as e:
            return False

    def save_file(self, file_path=None):
        """Save the current content to a file."""
        path = file_path or self.current_file
        if not path:
            return False

        try:
            with open(path, 'w') as f:
                f.write(self.toPlainText())
            self.current_file = path
            return True
        except Exception as e:
            return False

    @handle_errors(ErrorType.TYPING)
    def update_cursor_position(self):
        """Update the current cursor position."""
        # Get the error manager
        error_manager = ErrorManager.get_instance()

        try:
            cursor = self.textCursor()
            self.current_line = cursor.blockNumber() + 1
            self.current_column = cursor.columnNumber() + 1

            # Update code intelligence
            if hasattr(self, 'code_intelligence') and self.code_intelligence:
                self.code_intelligence.set_cursor_position(self.current_line, self.current_column)

            # Get the current word
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.current_word = cursor.selectedText()

            # Check if we should show completions
            if len(self.current_word) >= 2:
                if hasattr(self, 'completion_timer'):
                    self.completion_timer.start(500)  # Delay to avoid showing completions too frequently
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.TYPING,
                exception=e,
                method_name='update_cursor_position',
                additional_info={
                    'editor': self,
                    'current_line': getattr(self, 'current_line', 0),
                    'current_column': getattr(self, 'current_column', 0)
                }
            )

            # Handle the error
            error_manager.handle_error(error_context)
            print(f"Error in update_cursor_position: {str(e)}")

    @handle_errors(ErrorType.TYPING)
    def handle_text_changed(self):
        """Handle text changes."""
        # Get the error manager
        error_manager = ErrorManager.get_instance()

        try:
            # Update code intelligence
            if hasattr(self, 'code_intelligence') and self.code_intelligence:
                self.code_intelligence.set_code(self.toPlainText(), self.current_file)
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.TYPING,
                exception=e,
                method_name='handle_text_changed',
                additional_info={
                    'editor': self,
                    'current_file': getattr(self, 'current_file', None),
                    'text_length': len(self.toPlainText()) if hasattr(self, 'toPlainText') else 0
                }
            )

            # Handle the error
            error_manager.handle_error(error_context)
            print(f"Error in handle_text_changed: {str(e)}")

    def show_completions(self):
        """Show code completions."""
        try:
            # Get the current word and context
            cursor = self.textCursor()

            # Get the current line text up to the cursor
            block = cursor.block()
            line_text = block.text()[:cursor.positionInBlock()]

            # Check if we're in a special context (e.g., after a dot)
            after_dot = line_text.rstrip().endswith('.')
            after_open_paren = line_text.rstrip().endswith('(')

            # Select the current word
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            word = cursor.selectedText()

            # Cancel any pending hide timer
            if hasattr(self, 'completion_hide_timer') and self.completion_hide_timer.isActive():
                self.completion_hide_timer.stop()

            # Special handling for context-sensitive completions
            if after_dot:
                # After a dot, we want to show completions immediately
                # even if the word is empty
                pass
            elif after_open_paren:
                # After an open parenthesis, we might want to show parameter hints
                pass
            # Check if the word meets our criteria for showing completions
            elif len(word) < self.completion_min_chars and not self.completion_active:
                # Word is too short and we're not already showing completions
                return
            elif len(word) < self.completion_min_chars and self.completion_active:
                # Word is too short, but we're already showing completions
                # We'll keep the completion list open and filter it
                pass

            # Save the current word as the last completion prefix
            self.last_completion_prefix = word

            # Set the completion prefix
            if hasattr(self, 'code_intelligence') and self.code_intelligence:
                # If we're after a dot, we need to provide context
                if after_dot:
                    # Get the word before the dot
                    before_dot_match = re.search(r'(\w+)\.$', line_text)
                    if before_dot_match:
                        context = before_dot_match.group(1)
                        self.code_intelligence.set_completion_context(context, '.')

                # Set the completion prefix
                self.code_intelligence.set_completion_prefix(word)

                # If the completion list is already visible, filter it with the current word
                if self.completion_active and self.completion_list.isVisible():
                    # Filter the completions with the current word
                    self.completion_list.filter_completions(word)

                    # If there are no completions left after filtering, hide the list
                    if self.completion_list.list_widget.count() == 0:
                        self.completion_list.hide()
                        self.completion_active = False
                        return

                    # Reposition the completion list
                    cursor_rect = self.cursorRect()
                    position = self.mapToGlobal(cursor_rect.bottomRight())
                    self.completion_list.move(position)

                    # Make sure the completion list is visible
                    if not self.completion_list.isVisible():
                        self.completion_list.show()

                        # Make sure the editor keeps focus
                        self.setFocus()

                        self.completion_active = True

                # Add a tooltip to show keyboard shortcuts
                if hasattr(self, 'statusBar') and self.completion_active:
                    self.statusBar().showMessage("Alt+Up/Down to navigate completions, Tab to accept, Esc to close", 3000)
        except Exception as e:
            logger.error(f"Error in show_completions: {str(e)}")

    def hide_completions_delayed(self):
        """Hide completions after a delay (to prevent flickering)."""
        try:
            # Only hide if the current word is still too short
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            word = cursor.selectedText()

            if len(word) < self.completion_min_chars:
                self.completion_list.hide()
                self.completion_active = False
        except Exception as e:
            logger.error(f"Error in hide_completions_delayed: {str(e)}")

    def update_completions(self):
        """Update the completion list."""
        try:
            if not hasattr(self, 'code_intelligence') or not self.code_intelligence:
                return

            # Get the current word and context
            cursor = self.textCursor()

            # Get the current line text up to the cursor
            block = cursor.block()
            line_text = block.text()[:cursor.positionInBlock()]

            # Check if we're in a special context (e.g., after a dot)
            after_dot = line_text.rstrip().endswith('.')

            # Select the current word
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            current_word = cursor.selectedText()

            # Get completions from code intelligence
            completions = self.code_intelligence.get_completions()

            # Special handling for context-sensitive completions
            if after_dot:
                # After a dot, we always want to show completions
                pass
            # Don't show completions if there are none or the word is too short
            elif not completions or (len(current_word) < self.completion_min_chars and not self.just_completed):
                # Don't hide immediately if we're already showing completions
                if self.completion_active and len(current_word) < self.completion_min_chars:
                    # Start a timer to hide completions if no more typing occurs
                    self.completion_hide_timer.start(300)
                return
            elif not completions:
                # No completions available
                if self.completion_list.isVisible():
                    self.completion_list.hide()
                    self.completion_active = False
                return

            # Set the completions and apply the current word as filter
            self.completion_list.set_completions(completions)

            # If we have a current word, filter the completions
            if current_word:
                self.completion_list.filter_completions(current_word)

                # If there are no completions left after filtering, don't show the list
                if self.completion_list.list_widget.count() == 0:
                    if self.completion_list.isVisible():
                        self.completion_list.hide()
                        self.completion_active = False
                    return

            # Position the completion list
            cursor_rect = self.cursorRect()
            position = self.mapToGlobal(cursor_rect.bottomRight())
            self.completion_list.move(position)

            # Show the completion list if it's not already visible
            if not self.completion_list.isVisible():
                self.completion_list.show()

                # Add a tooltip to show keyboard shortcuts
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage("Alt+Up/Down to navigate completions, Tab to accept, Esc to close", 3000)

            # Make sure the editor keeps focus
            self.setFocus()

            # Ensure the completion list stays on top
            self.completion_list.raise_()

            # Mark completion as active
            self.completion_active = True

            # Reset the just_completed flag
            self.just_completed = False
        except Exception as e:
            logger.error(f"Error in update_completions: {str(e)}")

    def handle_completion_closed(self):
        """Handle the completion closed event."""
        try:
            # Reset completion state
            self.completion_active = False

            # Set focus back to the editor
            self.setFocus()

            # Emit a custom event to notify that completion has been closed
            # This can be used by other components if needed
            self.completion_closed_event = True
        except Exception as e:
            logger.error(f"Error in handle_completion_closed: {str(e)}")

    def _update_completion_after_key_press(self):
        """Update the completion list after a key press."""
        try:
            # Get the current word after the key press
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            current_word = cursor.selectedText()

            # Get the character before the cursor
            is_after_dot = False
            if cursor.position() > 0:
                cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 1)
                if cursor.selectedText() == '.':
                    is_after_dot = True
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, 1)

            # Only update if we have a word or if we're after a dot
            if current_word or is_after_dot:
                # Filter completions based on the current word
                self.completion_list.filter_completions(current_word)

                # Reposition the completion list
                cursor_rect = self.cursorRect()
                position = self.mapToGlobal(cursor_rect.bottomRight())
                self.completion_list.move(position)

                # If there are no completions left, hide the list
                if self.completion_list.list_widget.count() == 0:
                    self.completion_list.hide()
                    self.completion_active = False

                # Update code intelligence with the new text
                if hasattr(self, 'code_intelligence') and self.code_intelligence:
                    self.code_intelligence.set_completion_prefix(current_word)

                    # If we're after a dot, we might need to update completions
                    if is_after_dot:
                        # Get the word before the dot
                        cursor = self.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 2)  # Move before the dot
                        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
                        context = cursor.selectedText()
                        if context:
                            self.code_intelligence.set_completion_context(context, '.')
                            # Request new completions
                            self.completion_timer.start(50)  # Very short delay
        except Exception as e:
            logger.error(f"Error in _update_completion_after_key_press: {str(e)}")

    def insert_completion(self, completion_text, add_space=True):
        """Insert a completion."""
        try:
            # Get the current word
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            # We don't need to use the current_word variable, just get the selection

            # Replace the current word with the completion
            cursor.insertText(completion_text)

            # Add a space after the completion if requested and appropriate
            if add_space and not completion_text.endswith(('.', '(', '[', '{', ')', ']', '}')):
                cursor.insertText(" ")

            # Move cursor to the end of the inserted text
            # This ensures proper cursor positioning after completion
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, 0)
            self.setTextCursor(cursor)

            # Store the completion for potential future use
            self.last_completion = completion_text

            # Set a flag to indicate we just completed something
            # This helps with seamless transitions between completions
            self.just_completed = True

            # Ensure the editor has focus for continued typing
            self.setFocus()

            # If the completion ends with a character that should trigger completions,
            # start the completion timer again with a very short delay for immediate feedback
            if completion_text.endswith('.'):
                self.completion_timer.start(50)  # Very short delay for dot completions
                # Don't close the completion list - we'll show new completions
                return False  # Return False to indicate we don't want to close the completion list
            elif completion_text.endswith('('):
                # For function calls, show parameter hints
                self.completion_timer.start(50)
                # Don't close the completion list - we'll show new completions
                return False  # Return False to indicate we don't want to close the completion list
            else:
                # Start a timer to check for further completions after a short delay
                # This allows for seamless typing after completion
                self.completion_timer.start(300)

            # Return True to indicate we want to close the completion list for non-special completions
            return True
        except Exception as e:
            logger.error(f"Error in insert_completion: {str(e)}")

    def update_diagnostics(self):
        """Update the diagnostics."""
        try:
            # Disabled for stability
            pass
        except Exception as e:
            print(f"Error in update_diagnostics: {str(e)}")

    def update_symbols(self):
        """Update the symbols in the symbol browser."""
        try:
            # This method will be called when symbols are updated
            # The actual update is handled by the main window
            pass
        except Exception as e:
            print(f"Error in update_symbols: {str(e)}")

    def _update_extra_selections(self):
        """Update the extra selections with only current line highlighting."""
        try:
            # Only use current line selections for stability
            if hasattr(self, 'current_line_selections'):
                self.setExtraSelections(self.current_line_selections)
            else:
                self.setExtraSelections([])
        except Exception as e:
            # If there's an error, clear all selections
            self.setExtraSelections([])

    def show_diagnostic_tooltip(self, _position):
        """Show a diagnostic tooltip at the given position."""
        try:
            # Disabled for stability
            pass
        except Exception as e:
            logger.error(f"Error in show_diagnostic_tooltip: {str(e)}")

    def go_to_definition(self):
        """Go to the definition of the symbol under the cursor."""
        try:
            # Get the symbol at the cursor position
            cursor = self.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1

            if hasattr(self, 'code_intelligence') and self.code_intelligence:
                symbol = self.code_intelligence.get_definition(line, column)
                if symbol and hasattr(self, 'navigation_manager'):
                    self.navigation_manager.go_to_definition(symbol)
        except Exception as e:
            print(f"Error in go_to_definition: {str(e)}")

    def find_references(self):
        """Find all references to the symbol under the cursor."""
        try:
            # This would be implemented in a real code intelligence system
            pass
        except Exception as e:
            print(f"Error in find_references: {str(e)}")

    def show_context_menu(self, position):
        """Show the context menu."""
        try:
            # Create the standard context menu
            menu = self.createStandardContextMenu()

            # Add a separator
            menu.addSeparator()

            # Add navigation actions if navigation menu exists
            if hasattr(self, 'navigation_menu') and hasattr(self, 'current_word') and hasattr(self, 'navigation_manager'):
                can_go_to_definition = self.current_word != ""
                can_find_references = self.current_word != ""
                can_go_back = len(self.navigation_manager.navigation_history) > 1 and self.navigation_manager.navigation_index > 0
                can_go_forward = self.navigation_manager.navigation_index < len(self.navigation_manager.navigation_history) - 1

                self.navigation_menu.set_actions_enabled(can_go_to_definition, can_find_references, can_go_back, can_go_forward)

                # Add navigation actions to the menu
                menu.addAction(self.navigation_menu.go_to_definition_action)
                menu.addAction(self.navigation_menu.find_references_action)
                menu.addSeparator()
                menu.addAction(self.navigation_menu.go_back_action)
                menu.addAction(self.navigation_menu.go_forward_action)

            # Show the menu
            menu.exec(self.mapToGlobal(position))
        except Exception as e:
            print(f"Error in show_context_menu: {str(e)}")
            # If there's an error, use the default context menu
            super().customContextMenuRequested.connect(self.mapToGlobal(position))

    @handle_errors(ErrorType.TYPING)
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Get the error manager
        error_manager = ErrorManager.get_instance()

        try:
            # Handle code completion
            if hasattr(self, 'completion_list') and self.completion_list.isVisible():
                # Complete with Tab or Enter
                if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    current_item = self.completion_list.list_widget.currentItem()
                    if current_item:
                        completion_data = current_item.data(Qt.ItemDataRole.UserRole)
                        if completion_data:
                            # Insert the completion and determine if we should close the completion list
                            should_close = self.insert_completion(completion_data.get("text", ""), add_space=True)

                            # If we shouldn't close the completion list, update it
                            if not should_close:
                                # Update the completion list after a short delay
                                self._update_completion_after_key_press()
                            else:
                                # Hide the completion list for non-special completions
                                self.completion_list.hide()
                                self.completion_active = False

                            # Don't return here, allow the event to be processed normally
                            # This allows for proper handling of Enter key (new line) after completion
                            if event.key() == Qt.Key.Key_Tab:
                                return
                    else:
                        # If no item is selected, hide the completion list
                        self.completion_list.hide()
                        self.completion_active = False

                # Close with Escape
                elif event.key() == Qt.Key.Key_Escape:
                    self.completion_list.hide()
                    self.completion_active = False
                    return

                # Navigate with Up/Down - only handle these if Alt is pressed
                elif event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
                    # Forward to completion list
                    self.completion_list.keyPressEvent(event)
                    return

                # Navigate with Home/End - only handle these if Alt is pressed
                elif event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() in (Qt.Key.Key_Home, Qt.Key.Key_End):
                    # Forward to completion list
                    self.completion_list.keyPressEvent(event)
                    return

                # Hide on space if we're not in the middle of a word
                elif event.key() == Qt.Key.Key_Space:
                    self.completion_list.hide()
                    self.completion_active = False
                    # Don't return, allow space to be inserted

                # For all other keys, let the editor handle them first
                # Then update the completion list based on the new text

                # Process the key in the editor
                super().keyPressEvent(event)

                # After processing, update the completion list
                self._update_completion_after_key_press()

                # Hide completions on certain keys
                if event.key() in [Qt.Key.Key_Semicolon, Qt.Key.Key_Comma]:
                    self.completion_list.hide()
                    self.completion_active = False

            # Handle code navigation
            if event.key() == Qt.Key.Key_F12:
                # Go to definition
                self.go_to_definition()
                return

            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.key() == Qt.Key.Key_F12:
                # Find references
                self.find_references()
                return

            if event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_Left:
                # Go back
                if hasattr(self, 'navigation_manager'):
                    self.navigation_manager.go_back()
                return

            if event.modifiers() == Qt.KeyboardModifier.AltModifier and event.key() == Qt.Key.Key_Right:
                # Go forward
                if hasattr(self, 'navigation_manager'):
                    self.navigation_manager.go_forward()
                return

            # Auto-indent
            if event.key() == Qt.Key.Key_Return:
                cursor = self.textCursor()
                block = cursor.block()
                text = block.text()

                # Get the indentation of the current line
                indentation = ""
                for char in text:
                    if char.isspace():
                        indentation += char
                    else:
                        break

                # Add extra indentation if the line ends with '{'
                if text.rstrip().endswith('{'):
                    indentation += "    "

                # Insert the new line and indentation
                super().keyPressEvent(event)
                self.insertPlainText(indentation)
                return

            # Handle tab key
            if event.key() == Qt.Key.Key_Tab:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    # Indent selected lines
                    start_block = self.document().findBlock(cursor.selectionStart())
                    end_block = self.document().findBlock(cursor.selectionEnd())

                    cursor.beginEditBlock()

                    # Set cursor to the start of the first selected line
                    cursor.setPosition(start_block.position())

                    # Iterate through selected blocks and add indentation
                    current_block = start_block
                    while current_block.isValid() and current_block.position() <= end_block.position():
                        cursor.setPosition(current_block.position())
                        cursor.insertText("    ")
                        current_block = current_block.next()

                    cursor.endEditBlock()
                else:
                    # Insert 4 spaces at cursor position
                    cursor.insertText("    ")
                return

            # Handle shift+tab key
            if event.key() == Qt.Key.Key_Backtab:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    # Unindent selected lines
                    start_block = self.document().findBlock(cursor.selectionStart())
                    end_block = self.document().findBlock(cursor.selectionEnd())

                    cursor.beginEditBlock()

                    # Iterate through selected blocks and remove indentation
                    current_block = start_block
                    while current_block.isValid() and current_block.position() <= end_block.position():
                        cursor.setPosition(current_block.position())

                        # Get the first 4 characters of the line
                        line_start = current_block.text()[:4]

                        # Remove up to 4 spaces from the beginning of the line
                        if line_start == "    ":
                            # Remove 4 spaces
                            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 4)
                            cursor.removeSelectedText()
                        elif line_start.startswith(" "):
                            # Remove as many spaces as there are at the beginning
                            spaces = 0
                            for char in line_start:
                                if char == " ":
                                    spaces += 1
                                else:
                                    break

                            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, spaces)
                            cursor.removeSelectedText()

                        current_block = current_block.next()

                    cursor.endEditBlock()
                return

            # Handle other keys
            super().keyPressEvent(event)

            # Handle completion behavior after key press
            if hasattr(self, 'completion_timer'):
                # If we just completed something, reset the flag
                if hasattr(self, 'just_completed') and self.just_completed:
                    self.just_completed = False

                # If we just closed the completion dialog, reset the flag
                if hasattr(self, 'completion_closed_event') and self.completion_closed_event:
                    self.completion_closed_event = False
                    # If the key is a continuation character, start the completion timer again
                    if event.text() in self.completion_continue_chars:
                        self.completion_timer.start(50)

                # Start the completion timer if the key is a letter, number, or trigger character
                if event.text().isalnum() or event.text() in self.completion_triggers:
                    # Use a shorter delay for trigger characters for better responsiveness
                    if event.text() in self.completion_triggers:
                        delay = 50  # Very short delay for trigger characters
                    else:
                        delay = 200  # Short delay for normal typing

                    self.completion_timer.start(delay)

                    # Cancel any pending hide timer
                    if hasattr(self, 'completion_hide_timer') and self.completion_hide_timer.isActive():
                        self.completion_hide_timer.stop()

                # If completion is active and the user types a character that should continue completion
                elif self.completion_active and event.text() in self.completion_continue_chars:
                    # Keep the completion list open and update it
                    self.completion_timer.start(50)

                # Hide completions immediately on certain keys
                elif event.key() in [Qt.Key.Key_Space, Qt.Key.Key_Semicolon, Qt.Key.Key_Comma]:
                    if hasattr(self, 'completion_list') and self.completion_list.isVisible():
                        self.completion_list.hide()
                        # No need to set completion_active = False here as the signal will handle it
        except Exception as e:
            # Create error context
            error_context = ErrorContext(
                error_type=ErrorType.TYPING,
                exception=e,
                method_name='keyPressEvent',
                additional_info={
                    'editor': self,
                    'event_key': event.key(),
                    'event_text': event.text(),
                    'event_modifiers': int(event.modifiers())
                }
            )

            # Handle the error
            recovered = error_manager.handle_error(error_context)

            # If we couldn't recover, use the default key press event
            if not recovered:
                print(f"Error in keyPressEvent: {str(e)}")
                super().keyPressEvent(event)
