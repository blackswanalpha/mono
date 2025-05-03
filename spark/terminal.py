"""
Enhanced terminal widget for Spark Editor
"""

from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
from PyQt6.QtCore import Qt, QProcess, pyqtSignal

from .theme import ThemeManager


class Terminal(QTextEdit):
    """Enhanced terminal widget for running commands."""

    # Signals
    command_started = pyqtSignal(str)
    command_finished = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.command_history = []
        self.history_index = 0

        # Initialize text colors with default values
        self.text_colors = {
            "system": QColor("#888888"),
            "prompt": QColor("#007ACC"),
            "command": QColor("#FFFFFF"),
            "output": QColor("#CCCCCC"),
            "error": QColor("#FF5252"),
            "success": QColor("#4CAF50")
        }

        # Set up the UI
        self.setup_ui()

        # Update theme
        self.update_theme()

    def setup_ui(self):
        """Set up the UI elements."""
        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.setUndoRedoEnabled(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        # Set minimum size to ensure terminal content is visible
        self.setMinimumHeight(100)

        # Set the welcome message
        self.append_text("Welcome to Spark Terminal\n", "system")
        self.append_text("Type commands to interact with Mono\n", "system")
        self.append_text("> ", "prompt")

    def update_theme(self):
        """Update the terminal's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()

        # Set font
        font = QFont(theme.font_family, theme.font_size)
        self.setFont(font)

        # Set colors
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.terminal_bg};
                color: {theme.text_color};
                border: none;
                selection-background-color: {theme.primary_color};
                selection-color: {theme.text_bright_color};
                padding: 8px;
            }}
        """)

        # Define text colors
        self.text_colors = {
            "system": QColor(theme.text_dim_color),
            "prompt": QColor(theme.primary_color),
            "command": QColor(theme.text_bright_color),
            "output": QColor(theme.text_color),
            "error": QColor("#FF5252"),
            "success": QColor("#4CAF50")
        }

    def append_text(self, text, text_type="output"):
        """Append text with the specified color."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Create text format with the appropriate color
        format = QTextCharFormat()
        format.setForeground(self.text_colors.get(text_type, self.text_colors["output"]))

        # If it's an error, make it bold
        if text_type == "error":
            format.setFontWeight(QFont.Weight.Bold)

        # Insert the text with the format
        cursor.setCharFormat(format)
        cursor.insertText(text)

        # Move cursor to the end
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        # Ensure the cursor is visible
        self.ensureCursorVisible()

    def run_command(self, command):
        """Run a command in the terminal."""
        # Append the command to the terminal
        self.append_text(command + "\n", "command")

        # Add command to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # Emit signal
        self.command_started.emit(command)

        # Kill any running process
        if self.process is not None and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()

        # Create a new process
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)

        # Split the command into program and arguments
        parts = command.split()
        program = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Start the process
        self.process.start(program, args)

    def handle_stdout(self):
        """Handle standard output from the process."""
        data = self.process.readAllStandardOutput().data().decode()
        self.append_text(data, "output")

    def handle_stderr(self):
        """Handle standard error from the process."""
        data = self.process.readAllStandardError().data().decode()
        self.append_text(data, "error")

    def handle_finished(self, exit_code, _):
        """Handle process completion."""
        if exit_code == 0:
            self.append_text("\nCommand completed successfully.\n", "success")
        else:
            self.append_text(f"\nCommand failed with exit code {exit_code}.\n", "error")

        # Add a new prompt
        self.append_text("> ", "prompt")

        # Emit signal
        self.command_finished.emit(exit_code, "Command finished")

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Enter key - run the command
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Get the current line
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
            line = cursor.selectedText()

            # Extract the command (remove the prompt)
            if line.startswith("> "):
                command = line[2:].strip()
                if command:
                    self.run_command(command)
                else:
                    # Just add a new prompt if the command is empty
                    self.append_text("\n> ", "prompt")
            else:
                # If we're not at a prompt, just add a new line
                super().keyPressEvent(event)

            return

        # Up arrow - previous command in history
        if event.key() == Qt.Key.Key_Up:
            if self.command_history and self.history_index > 0:
                # Get the current line
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                line = cursor.selectedText()

                # If we're at a prompt, replace it with the previous command
                if line.startswith("> "):
                    self.history_index -= 1
                    command = self.command_history[self.history_index]

                    # Replace the current line with the prompt and command
                    cursor.removeSelectedText()
                    cursor.insertText(f"> {command}")

            return

        # Down arrow - next command in history
        if event.key() == Qt.Key.Key_Down:
            if self.command_history and self.history_index < len(self.command_history):
                # Get the current line
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                line = cursor.selectedText()

                # If we're at a prompt, replace it with the next command
                if line.startswith("> "):
                    self.history_index += 1

                    if self.history_index < len(self.command_history):
                        command = self.command_history[self.history_index]
                    else:
                        command = ""

                    # Replace the current line with the prompt and command
                    cursor.removeSelectedText()
                    cursor.insertText(f"> {command}")

            return

        # Only allow editing at the prompt
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line = cursor.selectedText()

        if line.startswith("> "):
            # Get the cursor position within the line
            pos = self.textCursor().positionInBlock()

            # Only allow editing after the prompt
            if pos >= 2:
                # Handle backspace to prevent deleting the prompt
                if event.key() == Qt.Key.Key_Backspace and pos == 2:
                    return

                # Allow editing
                self.setReadOnly(False)
                super().keyPressEvent(event)
                self.setReadOnly(True)
        else:
            # If we're not at a prompt, don't allow editing
            pass


class TerminalWidget(QWidget):
    """Widget containing the terminal with a header."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

        # Set minimum size to ensure terminal is visible
        self.setMinimumHeight(150)

        self.update_theme()

    def setup_ui(self):
        """Set up the UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setObjectName("terminal-header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Header label
        header_label = QLabel("Terminal")
        header_label.setObjectName("terminal-header-label")
        header_layout.addWidget(header_label)

        # Add header to main layout
        main_layout.addWidget(header_widget)

        # Terminal
        self.terminal = Terminal()
        main_layout.addWidget(self.terminal)

    def update_theme(self):
        """Update the terminal widget's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()

        # Update the terminal
        self.terminal.update_theme()

        # Update the header
        self.setStyleSheet(f"""
            #terminal-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}

            #terminal-header-label {{
                color: {theme.text_color};
                font-weight: bold;
            }}
        """)

    def run_command(self, command):
        """Run a command in the terminal."""
        self.terminal.run_command(command)
