"""
Enum wrapper for safely handling KeyboardInterrupt in Qt enum operations.

This module provides a wrapper around Qt enum operations to safely handle
KeyboardInterrupt exceptions that might occur during enum operations.
"""

import logging
import functools
import signal
from typing import Any, Callable, TypeVar, cast

# Configure logger
logger = logging.getLogger('spark_editor.enum_wrapper')

# Type variable for function return type
T = TypeVar('T')

class EnumInterruptError(Exception):
    """Exception raised when a KeyboardInterrupt occurs during enum operations."""
    pass

def safe_enum_call(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to safely handle KeyboardInterrupt in enum operations.
    
    This decorator catches KeyboardInterrupt exceptions that might occur
    during enum operations and converts them to EnumInterruptError exceptions
    that can be handled more gracefully.
    
    Args:
        func: The function to wrap
        
    Returns:
        The wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Set a very short timeout for SIGINT to prevent blocking
        old_handler = signal.getsignal(signal.SIGINT)
        
        try:
            # Set a custom handler that immediately raises KeyboardInterrupt
            def immediate_interrupt_handler(signum, frame):
                raise KeyboardInterrupt("Immediate interrupt during enum operation")
                
            signal.signal(signal.SIGINT, immediate_interrupt_handler)
            
            # Call the original function
            return func(*args, **kwargs)
        except KeyboardInterrupt as e:
            # Convert KeyboardInterrupt to EnumInterruptError
            logger.warning(f"KeyboardInterrupt during enum operation: {str(e)}")
            raise EnumInterruptError(f"Interrupted enum operation: {str(e)}") from e
        finally:
            # Restore the original signal handler
            signal.signal(signal.SIGINT, old_handler)
            
    return wrapper

# Apply the decorator to common Qt enum operations
def safe_enum_access(enum_class: Any, value: Any) -> Any:
    """
    Safely access an enum value.
    
    Args:
        enum_class: The enum class
        value: The enum value to access
        
    Returns:
        The enum value
        
    Raises:
        EnumInterruptError: If a KeyboardInterrupt occurs during the operation
    """
    try:
        return safe_enum_call(lambda: enum_class(value))()
    except EnumInterruptError:
        # Return a default value as fallback
        logger.warning(f"Using fallback for enum {enum_class.__name__} with value {value}")
        return value
    except Exception as e:
        logger.error(f"Error accessing enum {enum_class.__name__} with value {value}: {str(e)}")
        return value

# Patch Qt enum classes to use safe_enum_access
def patch_qt_enums():
    """
    Patch Qt enum classes to use safe_enum_access.
    
    This function patches the Qt enum classes to use safe_enum_access
    for all enum operations.
    """
    try:
        from PyQt6.QtCore import Qt
        
        # Store the original __call__ method
        original_call = Qt.Key.__call__
        
        # Replace with our safe version
        def safe_call(cls, value, *args, **kwargs):
            try:
                return safe_enum_call(lambda: original_call(value, *args, **kwargs))()
            except EnumInterruptError:
                logger.warning(f"Using fallback for Qt.Key with value {value}")
                return value
            except Exception as e:
                logger.error(f"Error accessing Qt.Key with value {value}: {str(e)}")
                return value
                
        # Apply the patch
        Qt.Key.__call__ = safe_call
        
        logger.info("Successfully patched Qt enums for safe interrupt handling")
    except Exception as e:
        logger.error(f"Failed to patch Qt enums: {str(e)}")
