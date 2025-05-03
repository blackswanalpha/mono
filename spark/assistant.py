"""
Enhanced AI assistant panel for Spark Editor
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QScrollArea, QFrame
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt, pyqtSignal

from .theme import ThemeManager


class MessageBubble(QFrame):
    """Message bubble widget for the AI assistant."""
    
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.message = message
        self.setup_ui()
        self.update_theme()
    
    def setup_ui(self):
        """Set up the UI elements."""
        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("user-bubble" if self.is_user else "assistant-bubble")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.message_label)
    
    def update_theme(self):
        """Update the bubble's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()
        
        if self.is_user:
            # User bubble
            self.setStyleSheet(f"""
                #user-bubble {{
                    background-color: {theme.primary_color};
                    color: {theme.text_bright_color};
                    border-radius: {theme.border_radius}px;
                    margin-left: 50px;
                    margin-right: 10px;
                }}
            """)
            self.message_label.setStyleSheet(f"color: {theme.text_bright_color};")
        else:
            # Assistant bubble
            self.setStyleSheet(f"""
                #assistant-bubble {{
                    background-color: {theme.panel_bg};
                    color: {theme.text_color};
                    border-radius: {theme.border_radius}px;
                    margin-left: 10px;
                    margin-right: 50px;
                }}
            """)
            self.message_label.setStyleSheet(f"color: {theme.text_color};")


class AIAssistant(QWidget):
    """Enhanced AI assistant panel."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_theme()
        
        # Initialize responses dictionary
        self.responses = {
            "component": "Components are the basic building blocks in Mono. They can have state, props, and methods.",
            "function": "Functions in Mono are defined using the 'function' keyword inside components.",
            "state": "State in Mono represents the internal mutable data of a component.",
            "props": "Props in Mono are immutable inputs passed from parent components.",
            "element": "Elements in Mono represent UI components that can be rendered.",
            "frame": "Frames in Mono are hierarchical component containers with their own lifecycle.",
            "kit": "Kits in Mono are curated collections of components with versioning and tools.",
            "layout": "Layouts in Mono define how components are arranged visually.",
            "package": "Packages in Mono are reusable modules that can be shared and imported.",
            "concurrency": "Mono supports concurrency with component threads, thread safety, and synchronization.",
        }
        
        # Add welcome message
        self.add_message("Hi! I'm your Mono assistant. Ask me anything about Mono language.", False)
    
    def setup_ui(self):
        """Set up the UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header_widget = QWidget()
        header_widget.setObjectName("assistant-header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Header label
        header_label = QLabel("AI Assistant")
        header_label.setObjectName("assistant-header-label")
        header_layout.addWidget(header_label)
        
        # Add header to main layout
        main_layout.addWidget(header_widget)
        
        # Chat area
        self.chat_widget = QWidget()
        self.chat_widget.setObjectName("assistant-chat")
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        # Scroll area for chat
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.chat_widget)
        scroll_area.setObjectName("assistant-scroll")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)
        
        # Input area
        input_widget = QWidget()
        input_widget.setObjectName("assistant-input")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about Mono...")
        self.input_field.setObjectName("assistant-input-field")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("Ask")
        self.send_button.setObjectName("assistant-send-button")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        # Add input area to main layout
        main_layout.addWidget(input_widget)
    
    def update_theme(self):
        """Update the assistant's appearance based on the current theme."""
        theme = ThemeManager.get_current_theme()
        
        # Update the header
        self.setStyleSheet(f"""
            #assistant-header {{
                background-color: {theme.panel_bg};
                border-bottom: 1px solid {theme.border_color};
            }}
            
            #assistant-header-label {{
                color: {theme.text_color};
                font-weight: bold;
            }}
            
            #assistant-chat {{
                background-color: {theme.window_bg};
            }}
            
            #assistant-scroll {{
                background-color: {theme.window_bg};
                border: none;
            }}
            
            #assistant-input {{
                background-color: {theme.panel_bg};
                border-top: 1px solid {theme.border_color};
            }}
            
            #assistant-input-field {{
                background-color: {theme.editor_bg};
                color: {theme.text_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 8px;
            }}
            
            #assistant-input-field:focus {{
                border: 1px solid {theme.primary_color};
            }}
            
            #assistant-send-button {{
                background-color: {theme.primary_color};
                color: {theme.text_bright_color};
                border: none;
                border-radius: {theme.border_radius}px;
                padding: 8px 16px;
            }}
            
            #assistant-send-button:hover {{
                background-color: {theme.secondary_color};
            }}
            
            #assistant-send-button:pressed {{
                background-color: {theme.accent_color};
            }}
        """)
        
        # Update message bubbles
        for i in range(self.chat_layout.count()):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, MessageBubble):
                widget.update_theme()
    
    def add_message(self, message, is_user=True):
        """Add a message to the chat."""
        # Create message bubble
        bubble = MessageBubble(message, is_user)
        
        # Insert before the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        # Scroll to bottom
        QWidget.repaint(self.chat_widget)
        scroll_area = self.chat_widget.parent()
        if isinstance(scroll_area, QScrollArea):
            scroll_bar = scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
    
    def send_message(self):
        """Send a message to the AI assistant."""
        message = self.input_field.text().strip()
        if not message:
            return
        
        # Add user message
        self.add_message(message, True)
        
        # Clear input field
        self.input_field.clear()
        
        # Generate response
        response = self.generate_response(message)
        
        # Add assistant message
        self.add_message(response, False)
    
    def generate_response(self, message):
        """Generate a response to the user's message."""
        # Simple keyword-based response
        message = message.lower()
        
        # Check for keywords in the message
        for keyword, response in self.responses.items():
            if keyword.lower() in message:
                return response
        
        # Default response
        return "I don't have specific information about that. Try asking about components, functions, state, props, elements, frames, kits, layouts, packages, or concurrency in Mono."


class AIAssistantWidget(QWidget):
    """Widget containing the AI assistant with a header."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # AI assistant
        self.assistant = AIAssistant()
        main_layout.addWidget(self.assistant)
    
    def update_theme(self):
        """Update the AI assistant widget's appearance based on the current theme."""
        self.assistant.update_theme()
