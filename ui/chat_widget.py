"""
Chat Widget
Displays conversation history between user and assistant.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
import config


class ChatBubble(QFrame):
    """Individual chat message bubble."""
    
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Message text
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Bahnschrift", 10))
        message_label.setStyleSheet("color: #f2fbff; background: transparent;")
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        time_label = QLabel(timestamp)
        time_label.setFont(QFont("Consolas", 8))
        time_label.setStyleSheet("color: rgba(210,230,240,0.65); background: transparent;")
        time_label.setAlignment(Qt.AlignRight if is_user else Qt.AlignLeft)
        
        layout.addWidget(message_label)
        layout.addWidget(time_label)
        self.setLayout(layout)
        
        # Borderless text style (no chat boxes).
        if is_user:
            self.setStyleSheet(
                """
                QFrame {
                    background: transparent;
                    border: none;
                    margin-left: 32px;
                    margin-right: 4px;
                }
                """
            )
        else:
            self.setStyleSheet(
                """
                QFrame {
                    background: transparent;
                    border: none;
                    margin-left: 4px;
                    margin-right: 32px;
                }
                """
            )


class ChatWidget(QWidget):
    """Chat display widget showing conversation history."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the chat UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#chatViewport {
                background: transparent;
                border: none;
                border-radius: 12px;
            }
            QScrollBar:vertical {
                background: rgba(16, 24, 31, 0.45);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(126, 243, 255, 0.45);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container for chat bubbles
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chatViewport")
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def add_message(self, text, is_user=True):
        """
        Add a message to the chat.
        
        Args:
            text: Message text
            is_user: True if user message, False if assistant message
        """
        # Remove stretch before adding new bubble
        self.chat_layout.takeAt(self.chat_layout.count() - 1)
        
        # Add chat bubble
        bubble = ChatBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        
        # Add stretch at the end
        self.chat_layout.addStretch()
        
        # Auto-scroll to bottom
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        """Scroll chat to the bottom."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_chat(self):
        """Clear all messages from chat."""
        while self.chat_layout.count() > 1:  # Keep the stretch
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
