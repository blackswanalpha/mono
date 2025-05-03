"""
Wayland error handling for Spark Editor.

This module provides utilities to handle Wayland-specific errors
and ensure the application can run properly on Wayland.
"""

import os
import logging
import datetime
from PyQt6.QtCore import QLibraryInfo

# Configure logging
logger = logging.getLogger('spark_editor.wayland')

def check_xcb_dependencies():
    """
    Check if the required XCB dependencies are installed.

    Returns:
        bool: True if the dependencies are installed, False otherwise
    """
    try:
        # Try to check if xcb-cursor is installed
        import subprocess
        result = subprocess.run(
            ["ldconfig", "-p"],
            capture_output=True,
            text=True,
            check=False
        )

        # Check if xcb-cursor is in the output
        if "libxcb-cursor" in result.stdout:
            logger.info("Found libxcb-cursor")
            return True

        # If not found, check if the package is installed
        result = subprocess.run(
            ["dpkg", "-l", "libxcb-cursor0"],
            capture_output=True,
            text=True,
            check=False
        )

        if "ii" in result.stdout and "libxcb-cursor0" in result.stdout:
            logger.info("Found libxcb-cursor0 package")
            return True

        logger.warning("XCB cursor dependencies not found")
        return False
    except Exception as e:
        logger.error(f"Error checking XCB dependencies: {e}")
        return False

def get_available_platforms():
    """
    Get a list of available Qt platform plugins.

    Returns:
        list: A list of available platform plugins
    """
    try:
        # Try to get the available platforms from Qt
        from PyQt6.QtGui import QGuiApplication
        platforms = QGuiApplication.platformPluginArguments()
        logger.info(f"Available platforms from Qt: {platforms}")
        return platforms
    except Exception as e:
        logger.error(f"Error getting available platforms: {e}")
        # Fallback to a common list of platforms
        return ["wayland", "xcb", "wayland-egl", "offscreen", "minimal"]

def setup_wayland_integration():
    """
    Set up Wayland integration and fallback mechanisms.

    This function configures the application to handle Wayland errors
    gracefully and fall back to X11 if necessary.
    """
    # Check if running on Wayland
    wayland_display = os.environ.get('WAYLAND_DISPLAY')

    if wayland_display:
        logger.info(f"Detected Wayland display: {wayland_display}")

        # Check if we've previously had Wayland errors and should use XCB directly
        wayland_error_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'wayland_error.flag')

        # Check if XCB dependencies are installed
        xcb_available = check_xcb_dependencies()

        if os.path.exists(wayland_error_file) and xcb_available:
            logger.info("Previous Wayland errors detected, using XCB directly")
            os.environ['QT_QPA_PLATFORM'] = 'xcb'
        elif os.path.exists(wayland_error_file) and not xcb_available:
            logger.warning("Previous Wayland errors detected, but XCB dependencies are missing")
            logger.warning("Using wayland-egl as fallback")
            os.environ['QT_QPA_PLATFORM'] = 'wayland-egl;wayland;offscreen'
        else:
            # Set environment variables to help with Wayland compatibility
            if xcb_available:
                os.environ['QT_QPA_PLATFORM'] = 'wayland;xcb'  # Try Wayland, fall back to XCB
            else:
                os.environ['QT_QPA_PLATFORM'] = 'wayland;wayland-egl;offscreen'  # Try Wayland, fall back to other platforms

        # Common Wayland settings
        os.environ['QT_WAYLAND_DISABLE_WINDOWDECORATION'] = '1'  # Let the Wayland compositor handle decorations
        os.environ['QT_WAYLAND_SHELL_INTEGRATION'] = 'xdg-shell'

        # Prevent surface role conflicts
        os.environ['QT_WAYLAND_DISABLE_WINDOWDECORATION'] = '1'
        os.environ['QT_WAYLAND_FORCE_DPI'] = '96'
        os.environ['QT_QPA_PLATFORMTHEME'] = 'gnome'

        # Disable problematic features
        os.environ['QT_SCALE_FACTOR'] = '1'
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'

        # Log Qt platform plugin paths for debugging
        plugin_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
        logger.info(f"Qt plugins path: {plugin_path}")

        # Set up error handler for Wayland protocol errors
        setup_wayland_error_handler()
    else:
        logger.info("Not running on Wayland")

        # Check if XCB dependencies are installed
        if not check_xcb_dependencies():
            logger.warning("XCB dependencies are missing, using alternative platform")
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def setup_wayland_error_handler():
    """
    Set up an error handler for Wayland protocol errors.

    This function installs a custom error handler to catch and handle
    Wayland protocol errors gracefully.
    """
    # Unfortunately, PyQt doesn't provide direct access to Wayland error handlers
    # We'll use environment variables to configure Qt's behavior

    # Tell Qt to ignore specific Wayland errors
    os.environ['QT_WAYLAND_SHELL_INTEGRATION'] = 'xdg-shell'

    # Disable client-side decorations to avoid some common errors
    os.environ['QT_WAYLAND_DISABLE_WINDOWDECORATION'] = '1'

    logger.info("Wayland error handler configured")

def handle_wayland_error(error_message):
    """
    Handle a Wayland error that has occurred.

    Args:
        error_message: The error message from Wayland

    Returns:
        bool: True if the error was handled, False otherwise
    """
    logger.error(f"Wayland error: {error_message}")

    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create a flag file to indicate Wayland errors for future runs
    wayland_error_file = os.path.join(logs_dir, 'wayland_error.flag')
    try:
        with open(wayland_error_file, 'w') as f:
            f.write(f"Wayland error detected: {error_message}\n")
            f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
        logger.info(f"Created Wayland error flag file at {wayland_error_file}")
    except Exception as e:
        logger.error(f"Failed to create Wayland error flag file: {e}")

    # Check if XCB dependencies are installed
    xcb_available = check_xcb_dependencies()

    # Check for common Wayland errors
    if "already has a different role" in error_message:
        logger.warning("Detected 'already has a different role' error - this is a known Wayland issue")

        # Try to recover by forcing a platform switch
        try:
            if xcb_available:
                # Switch to XCB platform
                os.environ['QT_QPA_PLATFORM'] = 'xcb'
                logger.info("Switched to XCB platform as fallback")

                # Inform the user
                print("\nWayland surface role conflict detected. Switching to XCB platform.")
                print("Please restart the application for the changes to take effect.\n")
            else:
                # Switch to alternative platform
                os.environ['QT_QPA_PLATFORM'] = 'wayland-egl;offscreen'
                logger.info("Switched to alternative platform as fallback")

                # Inform the user
                print("\nWayland surface role conflict detected.")
                print("XCB dependencies are missing. Switching to alternative platform.")
                print("Please restart the application for the changes to take effect.\n")
                print("To enable XCB support, install the required dependencies:")
                print("  sudo apt-get install libxcb-cursor0\n")

            return True
        except Exception as e:
            logger.error(f"Failed to switch platforms: {e}")

    elif "Protocol error" in error_message:
        logger.warning("Detected Wayland protocol error")

        # Try to recover by restarting with alternative platform
        try:
            if xcb_available:
                os.environ['QT_QPA_PLATFORM'] = 'xcb'
                logger.info("Set platform to XCB for next restart")

                # Inform the user
                print("\nWayland protocol error detected. Please restart the application.")
                print("The application will use XCB instead of Wayland on next start.\n")
            else:
                os.environ['QT_QPA_PLATFORM'] = 'wayland-egl;offscreen'
                logger.info("Set platform to alternative for next restart")

                # Inform the user
                print("\nWayland protocol error detected. Please restart the application.")
                print("XCB dependencies are missing. The application will use an alternative platform on next start.\n")
                print("To enable XCB support, install the required dependencies:")
                print("  sudo apt-get install libxcb-cursor0\n")

            return True
        except Exception as e:
            logger.error(f"Failed to handle protocol error: {e}")

    elif "Could not load the Qt platform plugin" in error_message and "xcb" in error_message:
        logger.warning("Detected XCB platform plugin loading error")

        # Try to recover by using alternative platform
        try:
            os.environ['QT_QPA_PLATFORM'] = 'wayland-egl;offscreen'
            logger.info("Set platform to alternative for next restart")

            # Inform the user
            print("\nXCB platform plugin loading error detected.")
            print("The required XCB dependencies are missing.")
            print("Please install the required dependencies:")
            print("  sudo apt-get install libxcb-cursor0\n")
            print("The application will use an alternative platform on next start.")
            print("Please restart the application.\n")

            return True
        except Exception as e:
            logger.error(f"Failed to handle XCB platform error: {e}")

    return False

def is_wayland_session():
    """
    Check if the current session is running on Wayland.

    Returns:
        bool: True if running on Wayland, False otherwise
    """
    return os.environ.get('WAYLAND_DISPLAY') is not None

def get_platform_info():
    """
    Get information about the current platform.

    Returns:
        dict: A dictionary containing platform information
    """
    return {
        'wayland': is_wayland_session(),
        'wayland_display': os.environ.get('WAYLAND_DISPLAY'),
        'qt_platform': os.environ.get('QT_QPA_PLATFORM'),
        'desktop': os.environ.get('XDG_CURRENT_DESKTOP'),
        'session_type': os.environ.get('XDG_SESSION_TYPE')
    }
