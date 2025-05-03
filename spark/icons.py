"""
Icon management for Spark Editor
"""

import os
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QBrush
from PyQt6.QtCore import Qt, QSize, QPoint, QRect

from .theme import ThemeManager

# Icon cache
_icon_cache = {}

def get_icon(name):
    """Get an icon by name."""
    # Check cache first
    if name in _icon_cache:
        return _icon_cache[name]

    # File icons
    if name == "file" or name == "mono_file":
        # Use Mono logo for files, especially .mono files
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mono_logo.png")
        if os.path.exists(logo_path):
            icon = QIcon(logo_path)
            _icon_cache[name] = icon
            return icon

    # App icon
    if name == "app_icon":
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mono_logo.png")
        if os.path.exists(logo_path):
            icon = QIcon(logo_path)
            _icon_cache[name] = icon
            return icon

    # Code intelligence icons
    if name in ["error", "warning", "info", "component", "function", "variable", "state", "symbol",
                "goto", "references", "back", "forward"]:
        # Create a programmatic icon based on the name
        icon = create_programmatic_icon(name)
        _icon_cache[name] = icon
        return icon

    # Return a simple empty icon for other cases
    return QIcon()

def create_programmatic_icon(name):
    """Create a programmatic icon based on the name."""
    theme = ThemeManager.get_current_theme()
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)

    # Create a painter to draw on the pixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if name == "close":
        # Red X icon for closing tabs
        painter.setPen(QPen(QColor("#FF5555"), 2))
        painter.drawLine(4, 4, 12, 12)
        painter.drawLine(12, 4, 4, 12)

    elif name == "error":
        # Red circle with X
        painter.setPen(QPen(QColor(theme.error_color), 1))
        painter.setBrush(QBrush(QColor(theme.error_color).lighter(150)))
        painter.drawEllipse(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLine(5, 5, 11, 11)
        painter.drawLine(11, 5, 5, 11)

    elif name == "warning":
        # Yellow triangle with !
        painter.setPen(QPen(QColor(theme.warning_color), 1))
        painter.setBrush(QBrush(QColor(theme.warning_color).lighter(150)))
        painter.drawPolygon([QPoint(8, 2), QPoint(14, 14), QPoint(2, 14)])
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLine(8, 6, 8, 10)
        painter.drawPoint(8, 12)

    elif name == "info":
        # Blue circle with i
        painter.setPen(QPen(QColor(theme.primary_color), 1))
        painter.setBrush(QBrush(QColor(theme.primary_color).lighter(150)))
        painter.drawEllipse(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLine(8, 6, 8, 10)
        painter.drawPoint(8, 4)

    elif name == "component":
        # Component icon (C)
        painter.setPen(QPen(QColor(theme.syntax_class), 1))
        painter.setBrush(QBrush(QColor(theme.syntax_class).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "C")

    elif name == "function":
        # Function icon (F)
        painter.setPen(QPen(QColor(theme.syntax_function), 1))
        painter.setBrush(QBrush(QColor(theme.syntax_function).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "F")

    elif name == "variable":
        # Variable icon (V)
        painter.setPen(QPen(QColor(theme.syntax_variable), 1))
        painter.setBrush(QBrush(QColor(theme.syntax_variable).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "V")

    elif name == "state":
        # State icon (S)
        painter.setPen(QPen(QColor(theme.syntax_variable), 1))
        painter.setBrush(QBrush(QColor(theme.syntax_variable).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "S")

    elif name == "symbol":
        # Symbol icon (*)
        painter.setPen(QPen(QColor(theme.text_color), 1))
        painter.setBrush(QBrush(QColor(theme.text_color).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "*")

    elif name == "goto":
        # Go to definition icon (→)
        painter.setPen(QPen(QColor(theme.primary_color), 1))
        painter.setBrush(QBrush(QColor(theme.primary_color).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "→")

    elif name == "references":
        # Find references icon (⊙)
        painter.setPen(QPen(QColor(theme.primary_color), 1))
        painter.setBrush(QBrush(QColor(theme.primary_color).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "⊙")

    elif name == "back":
        # Go back icon (←)
        painter.setPen(QPen(QColor(theme.primary_color), 1))
        painter.setBrush(QBrush(QColor(theme.primary_color).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "←")

    elif name == "forward":
        # Go forward icon (→)
        painter.setPen(QPen(QColor(theme.primary_color), 1))
        painter.setBrush(QBrush(QColor(theme.primary_color).lighter(150)))
        painter.drawRect(2, 2, 12, 12)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(QRect(2, 2, 12, 12), Qt.AlignmentFlag.AlignCenter, "→")

    painter.end()

    return QIcon(pixmap)

def get_pixmap(name):
    """Get a pixmap by name."""
    if name == "mono_logo":
        # Return the Mono logo pixmap
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mono_logo.png")
        if os.path.exists(logo_path):
            return QPixmap(logo_path)

    # For other icons, create a pixmap from the icon
    icon = get_icon(name)
    if not icon.isNull():
        return icon.pixmap(QSize(16, 16))

    # Return a simple empty pixmap for other cases
    return QPixmap()
