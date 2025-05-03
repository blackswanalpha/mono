"""
Splash screen for Spark Editor
"""

import os
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer

def create_splash_screen():
    """Create and return a splash screen."""
    # Try to load the Mono logo
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mono_logo.png")
    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
    else:
        # Create a blank pixmap if logo not found
        pixmap = QPixmap(200, 200)

    splash = QSplashScreen(pixmap)

    # Add method to show and finish
    def show_and_finish(main_window, duration=2000):
        splash.show()
        QTimer.singleShot(duration, lambda: splash.finish(main_window))

    splash.show_and_finish = show_and_finish

    return splash
