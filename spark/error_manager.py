"""
Error management system for Spark Editor.

This module provides a comprehensive error handling system to detect,
log, and recover from various types of errors in the Spark Editor.
"""

import os
import sys
import traceback
import logging
import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Type, Union

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create a logger
logger = logging.getLogger('spark_editor')
logger.setLevel(logging.DEBUG)

# Create file handler
log_file = os.path.join(log_dir, f'spark_editor_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class ErrorType(Enum):
    """Enumeration of error types that can occur in the editor."""
    GENERAL = "general_error"
    TYPING = "typing_error"
    TYPING_CURSOR = "typing_cursor_error"
    TYPING_COMPLETION = "typing_completion_error"
    TYPING_SELECTION = "typing_selection_error"
    TYPING_INDENT = "typing_indent_error"
    COMPLETION = "completion_error"
    NAVIGATION = "navigation_error"
    SYNTAX_HIGHLIGHTING = "syntax_highlighting_error"
    CODE_INTELLIGENCE = "code_intelligence_error"
    UI = "ui_error"
    FILE_IO = "file_io_error"
    PLUGIN = "plugin_error"
    CRITICAL = "critical_error"

class ErrorContext:
    """Context information for an error."""

    def __init__(self,
                 error_type: ErrorType,
                 exception: Exception,
                 method_name: str,
                 additional_info: Dict[str, Any] = None):
        self.error_type = error_type
        self.exception = exception
        self.method_name = method_name
        self.additional_info = additional_info or {}
        self.timestamp = datetime.datetime.now()
        self.traceback = traceback.format_exc()

    def __str__(self) -> str:
        """Return a string representation of the error context."""
        return (f"Error: {self.error_type.value}\n"
                f"Exception: {type(self.exception).__name__}: {str(self.exception)}\n"
                f"Method: {self.method_name}\n"
                f"Time: {self.timestamp}\n"
                f"Additional Info: {self.additional_info}\n"
                f"Traceback:\n{self.traceback}")

class ErrorManager:
    """Manager for handling errors in the Spark Editor."""

    # Singleton instance
    _instance = None

    # Error handlers
    _error_handlers: Dict[ErrorType, List[Callable[[ErrorContext], None]]] = {}

    # Error history
    _error_history: List[ErrorContext] = []

    # Maximum number of errors to keep in history
    _max_history_size = 100

    # Flag to enable/disable error handling
    _enabled = True

    # Recovery strategies
    _recovery_strategies: Dict[ErrorType, Callable[[ErrorContext], bool]] = {}

    @classmethod
    def get_instance(cls) -> 'ErrorManager':
        """Get the singleton instance of the ErrorManager."""
        if cls._instance is None:
            cls._instance = ErrorManager()
        return cls._instance

    def __init__(self):
        """Initialize the ErrorManager."""
        # Register default error handlers
        for error_type in ErrorType:
            self._error_handlers[error_type] = []

        # Register default recovery strategies
        self._register_default_recovery_strategies()

    def _register_default_recovery_strategies(self):
        """Register default recovery strategies for different error types."""
        self._recovery_strategies[ErrorType.TYPING] = self._recover_from_typing_error
        self._recovery_strategies[ErrorType.TYPING_CURSOR] = self._recover_from_typing_cursor_error
        self._recovery_strategies[ErrorType.TYPING_COMPLETION] = self._recover_from_typing_completion_error
        self._recovery_strategies[ErrorType.TYPING_SELECTION] = self._recover_from_typing_selection_error
        self._recovery_strategies[ErrorType.TYPING_INDENT] = self._recover_from_typing_indent_error
        self._recovery_strategies[ErrorType.COMPLETION] = self._recover_from_completion_error
        self._recovery_strategies[ErrorType.NAVIGATION] = self._recover_from_navigation_error
        self._recovery_strategies[ErrorType.SYNTAX_HIGHLIGHTING] = self._recover_from_syntax_highlighting_error
        self._recovery_strategies[ErrorType.CODE_INTELLIGENCE] = self._recover_from_code_intelligence_error
        self._recovery_strategies[ErrorType.UI] = self._recover_from_ui_error
        self._recovery_strategies[ErrorType.FILE_IO] = self._recover_from_file_io_error
        self._recovery_strategies[ErrorType.PLUGIN] = self._recover_from_plugin_error
        self._recovery_strategies[ErrorType.CRITICAL] = self._recover_from_critical_error

    def register_error_handler(self, error_type: ErrorType, handler: Callable[[ErrorContext], None]):
        """Register an error handler for a specific error type."""
        if error_type not in self._error_handlers:
            self._error_handlers[error_type] = []
        self._error_handlers[error_type].append(handler)

    def unregister_error_handler(self, error_type: ErrorType, handler: Callable[[ErrorContext], None]):
        """Unregister an error handler for a specific error type."""
        if error_type in self._error_handlers and handler in self._error_handlers[error_type]:
            self._error_handlers[error_type].remove(handler)

    def handle_error(self, error_context: ErrorContext) -> bool:
        """Handle an error and return whether it was successfully recovered from."""
        if not self._enabled:
            return False

        # Add to error history
        self._add_to_history(error_context)

        # Log the error
        self._log_error(error_context)

        # Call error handlers
        self._call_error_handlers(error_context)

        # Try to recover from the error
        return self._try_recover(error_context)

    def _add_to_history(self, error_context: ErrorContext):
        """Add an error to the history."""
        self._error_history.append(error_context)

        # Trim history if it gets too large
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]

    def _log_error(self, error_context: ErrorContext):
        """Log an error."""
        logger.error(str(error_context))

    def _call_error_handlers(self, error_context: ErrorContext):
        """Call all registered error handlers for the given error type."""
        # Call handlers for the specific error type
        if error_context.error_type in self._error_handlers:
            for handler in self._error_handlers[error_context.error_type]:
                try:
                    handler(error_context)
                except Exception as e:
                    logger.error(f"Error in error handler: {str(e)}")

        # Call handlers for general errors
        if error_context.error_type != ErrorType.GENERAL and ErrorType.GENERAL in self._error_handlers:
            for handler in self._error_handlers[ErrorType.GENERAL]:
                try:
                    handler(error_context)
                except Exception as e:
                    logger.error(f"Error in general error handler: {str(e)}")

    def _try_recover(self, error_context: ErrorContext) -> bool:
        """Try to recover from an error."""
        # Check if there's a recovery strategy for this error type
        if error_context.error_type in self._recovery_strategies:
            try:
                return self._recovery_strategies[error_context.error_type](error_context)
            except Exception as e:
                logger.error(f"Error in recovery strategy: {str(e)}")

        # No recovery strategy or recovery failed
        return False

    def get_error_history(self) -> List[ErrorContext]:
        """Get the error history."""
        return self._error_history.copy()

    def clear_error_history(self):
        """Clear the error history."""
        self._error_history = []

    def enable(self):
        """Enable error handling."""
        self._enabled = True

    def disable(self):
        """Disable error handling."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if error handling is enabled."""
        return self._enabled

    def set_max_history_size(self, size: int):
        """Set the maximum number of errors to keep in history."""
        self._max_history_size = size

        # Trim history if it's already too large
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]

    def get_max_history_size(self) -> int:
        """Get the maximum number of errors to keep in history."""
        return self._max_history_size

    def _recover_from_typing_error(self, error_context: ErrorContext) -> bool:
        """Recover from a general typing error."""
        # Try more specific recovery strategies first
        if "completion_list" in str(error_context.exception):
            return self._recover_from_typing_completion_error(error_context)
        elif "cursor" in str(error_context.exception) or "QTextCursor" in str(error_context.exception):
            return self._recover_from_typing_cursor_error(error_context)
        elif "selection" in str(error_context.exception) or "selected" in str(error_context.exception):
            return self._recover_from_typing_selection_error(error_context)
        elif "indent" in str(error_context.exception) or "tab" in str(error_context.exception):
            return self._recover_from_typing_indent_error(error_context)

        # Generic recovery for typing errors
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']

                # Try to reset the editor state
                if hasattr(editor, 'completion_list') and editor.completion_list.isVisible():
                    editor.completion_list.hide()

                # Reset cursor
                if hasattr(editor, 'textCursor'):
                    cursor = editor.textCursor()
                    cursor.clearSelection()
                    editor.setTextCursor(cursor)

                # Disable code intelligence temporarily
                if hasattr(editor, 'code_intelligence'):
                    editor.code_intelligence = None

                logger.info("Applied generic typing error recovery")
                return True
        except Exception as e:
            logger.error(f"Error in generic typing recovery: {str(e)}")

        return False

    def _recover_from_typing_cursor_error(self, error_context: ErrorContext) -> bool:
        """Recover from a typing error related to the cursor."""
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']

                # Reset cursor
                if hasattr(editor, 'textCursor'):
                    cursor = editor.textCursor()
                    cursor.clearSelection()
                    editor.setTextCursor(cursor)

                    # Move cursor to a safe position (start of document)
                    cursor.movePosition(editor.textCursor().Start)
                    editor.setTextCursor(cursor)

                    logger.info("Reset cursor position after cursor error")
                    return True
        except Exception as e:
            logger.error(f"Error in cursor error recovery: {str(e)}")

        return False

    def _recover_from_typing_completion_error(self, error_context: ErrorContext) -> bool:
        """Recover from a typing error related to code completion."""
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']

                # Hide completion list
                if hasattr(editor, 'completion_list'):
                    editor.completion_list.hide()

                # Disable completion timer
                if hasattr(editor, 'completion_timer'):
                    editor.completion_timer.stop()

                logger.info("Disabled code completion after completion error")
                return True
        except Exception as e:
            logger.error(f"Error in completion error recovery: {str(e)}")

        return False

    def _recover_from_typing_selection_error(self, error_context: ErrorContext) -> bool:
        """Recover from a typing error related to text selection."""
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']

                # Clear selection
                if hasattr(editor, 'textCursor'):
                    cursor = editor.textCursor()
                    cursor.clearSelection()
                    editor.setTextCursor(cursor)

                    logger.info("Cleared text selection after selection error")
                    return True
        except Exception as e:
            logger.error(f"Error in selection error recovery: {str(e)}")

        return False

    def _recover_from_typing_indent_error(self, error_context: ErrorContext) -> bool:
        """Recover from a typing error related to indentation."""
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']

                # Just insert a space instead of trying to indent
                if hasattr(editor, 'textCursor') and hasattr(editor, 'insertPlainText'):
                    editor.insertPlainText(" ")

                    logger.info("Inserted space after indent error")
                    return True
        except Exception as e:
            logger.error(f"Error in indent error recovery: {str(e)}")

        return False

    def _recover_from_completion_error(self, error_context: ErrorContext) -> bool:
        """Recover from a completion error."""
        # Try to hide the completion list
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']
                if hasattr(editor, 'completion_list'):
                    editor.completion_list.hide()
                return True
        except Exception:
            pass

        return False

    def _recover_from_navigation_error(self, error_context: ErrorContext) -> bool:
        """Recover from a navigation error."""
        # Not much we can do here except log the error
        return False

    def _recover_from_syntax_highlighting_error(self, error_context: ErrorContext) -> bool:
        """Recover from a syntax highlighting error."""
        # Try to reset the syntax highlighter
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']
                if hasattr(editor, 'highlighter'):
                    editor.highlighter.setDocument(None)
                    editor.highlighter.setDocument(editor.document())
                    return True
        except Exception:
            pass

        return False

    def _recover_from_code_intelligence_error(self, error_context: ErrorContext) -> bool:
        """Recover from a code intelligence error."""
        # Try to reset the code intelligence
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']
                if hasattr(editor, 'code_intelligence'):
                    # Just disable it for now
                    editor.code_intelligence = None
                    return True
        except Exception:
            pass

        return False

    def _recover_from_ui_error(self, error_context: ErrorContext) -> bool:
        """Recover from a UI error."""
        # Not much we can do here except log the error
        return False

    def _recover_from_file_io_error(self, error_context: ErrorContext) -> bool:
        """Recover from a file I/O error."""
        # Not much we can do here except log the error
        return False

    def _recover_from_plugin_error(self, error_context: ErrorContext) -> bool:
        """Recover from a plugin error."""
        # Try to disable the plugin
        try:
            if 'plugin_id' in error_context.additional_info:
                plugin_id = error_context.additional_info['plugin_id']
                from .plugin_system import get_plugin_manager
                plugin_manager = get_plugin_manager()
                plugin_manager.disable_plugin(plugin_id)
                return True
        except Exception:
            pass

        return False

    def _recover_from_critical_error(self, error_context: ErrorContext) -> bool:
        """Recover from a critical error."""
        # This is a last resort - we'll try to save any unsaved work
        try:
            if 'editor' in error_context.additional_info:
                editor = error_context.additional_info['editor']
                if hasattr(editor, 'current_file') and editor.current_file:
                    # Try to save the file with a .backup extension
                    backup_file = f"{editor.current_file}.backup"
                    with open(backup_file, 'w') as f:
                        f.write(editor.toPlainText())
                    logger.info(f"Saved backup to {backup_file}")
                    return True
        except Exception:
            pass

        return False

# Decorator for error handling
def handle_errors(error_type: ErrorType = ErrorType.GENERAL):
    """Decorator for handling errors in methods."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except KeyboardInterrupt:
                # Handle KeyboardInterrupt specially
                logger.warning(f"KeyboardInterrupt in {func.__name__} - handled safely")
                # Don't propagate the interrupt
                return None
            except Exception as e:
                # Create error context
                error_context = ErrorContext(
                    error_type=error_type,
                    exception=e,
                    method_name=func.__name__,
                    additional_info={'editor': self, 'args': args, 'kwargs': kwargs}
                )

                # Handle the error
                error_manager = ErrorManager.get_instance()
                recovered = error_manager.handle_error(error_context)

                # If we couldn't recover, re-raise the exception
                if not recovered and error_type == ErrorType.CRITICAL:
                    raise
        return wrapper
    return decorator

# Function to detect the type of error
def detect_error_type(exception: Exception, method_name: str) -> ErrorType:
    """Detect the type of error based on the exception and method name."""
    exception_str = str(exception)
    exception_type = type(exception).__name__

    # Check for typing errors
    if method_name == 'keyPressEvent' or 'key' in method_name.lower():
        # Check for more specific typing errors
        if 'cursor' in exception_str or 'QTextCursor' in exception_str:
            return ErrorType.TYPING_CURSOR
        elif 'completion' in exception_str or 'completion_list' in exception_str:
            return ErrorType.TYPING_COMPLETION
        elif 'selection' in exception_str or 'selected' in exception_str:
            return ErrorType.TYPING_SELECTION
        elif 'indent' in exception_str or 'tab' in exception_str:
            return ErrorType.TYPING_INDENT
        else:
            return ErrorType.TYPING

    # Check for completion errors
    if 'completion' in method_name.lower() or 'completion_list' in exception_str:
        return ErrorType.COMPLETION

    # Check for navigation errors
    if 'navigation' in method_name.lower() or 'go_to' in method_name.lower():
        return ErrorType.NAVIGATION

    # Check for syntax highlighting errors
    if 'highlight' in method_name.lower() or 'syntax' in method_name.lower():
        return ErrorType.SYNTAX_HIGHLIGHTING

    # Check for code intelligence errors
    if 'intelligence' in method_name.lower() or 'code_intelligence' in exception_str:
        return ErrorType.CODE_INTELLIGENCE

    # Check for UI errors
    if 'ui' in method_name.lower() or 'widget' in exception_str or 'layout' in exception_str:
        return ErrorType.UI

    # Check for file I/O errors
    if 'file' in method_name.lower() or 'open' in method_name.lower() or 'save' in method_name.lower():
        return ErrorType.FILE_IO

    # Check for plugin errors
    if 'plugin' in method_name.lower() or 'plugin' in exception_str:
        return ErrorType.PLUGIN

    # Default to general error
    return ErrorType.GENERAL

# Function to create a diagnostic report
def create_diagnostic_report() -> str:
    """Create a diagnostic report with information about the system and recent errors."""
    error_manager = ErrorManager.get_instance()
    error_history = error_manager.get_error_history()

    report = []
    report.append("=== Spark Editor Diagnostic Report ===")
    report.append(f"Time: {datetime.datetime.now()}")
    report.append(f"Python Version: {sys.version}")
    report.append(f"Platform: {sys.platform}")
    report.append(f"Error History Size: {len(error_history)}")

    # Add error counts by type
    error_counts = {}
    for error_context in error_history:
        error_type = error_context.error_type.value
        if error_type not in error_counts:
            error_counts[error_type] = 0
        error_counts[error_type] += 1

    report.append("\n=== Error Counts ===")
    for error_type, count in error_counts.items():
        report.append(f"{error_type}: {count}")

    # Add recent errors
    report.append("\n=== Recent Errors ===")
    for i, error_context in enumerate(reversed(error_history[-10:])):
        report.append(f"\n--- Error {i+1} ---")
        report.append(str(error_context))

    return "\n".join(report)

# Function to save a diagnostic report to a file
def save_diagnostic_report(file_path: Optional[str] = None) -> str:
    """Save a diagnostic report to a file and return the file path."""
    if file_path is None:
        file_path = os.path.join(
            log_dir,
            f'spark_diagnostic_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )

    report = create_diagnostic_report()

    with open(file_path, 'w') as f:
        f.write(report)

    return file_path
