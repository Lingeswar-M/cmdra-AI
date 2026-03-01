"""
Main Window - cmdra AI Desktop UI
Text-only assistant interface with dynamic avatar + chat.
"""

import logging

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QFont, QCursor, QPixmap, QPainter, QColor, QIcon, QPainterPath

from ui.chat_widget import ChatWidget
from brain.intent_classifier import IntentClassifier
from services.action_service import ActionService
from services.llm_service import LLMService
from utils.avatar_manager import AvatarManager
import config

logger = logging.getLogger(__name__)


class CommandWorkerThread(QThread):
    """Worker thread for processing text commands without blocking UI."""

    finished = pyqtSignal(dict)
    status_update = pyqtSignal(str)

    def __init__(self, classifier, action_service, llm_service, text_input="", direct_intent=None):
        super().__init__()
        self.classifier = classifier
        self.action_service = action_service
        self.llm_service = llm_service
        self.text_input = text_input
        self.direct_intent = direct_intent

    def run(self):
        try:
            text = self.text_input.strip()
            if not text and not self.direct_intent:
                self.finished.emit({"success": False, "error": "Please enter a command."})
                return

            self.status_update.emit("Processing text...")
            intent = self.direct_intent if self.direct_intent else self.classifier.classify(text)

            self.status_update.emit("Executing task...")
            if intent["category"] != "chat":
                response = self.action_service.execute(intent)
            else:
                response = self.llm_service.ask(text)

            self.finished.emit(
                {
                    "success": True,
                    "user_text": text,
                    "response": response,
                    "intent": intent,
                }
            )

        except Exception as exc:
            logger.exception("Worker thread crashed")
            self.finished.emit({"success": False, "error": str(exc)})


class DockBubble(QWidget):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        flags = Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        if config.ALWAYS_ON_TOP:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(config.DOCK_ICON_SIZE, config.DOCK_ICON_SIZE)

        self.button = QPushButton(self)
        self.button.setFixedSize(config.DOCK_ICON_SIZE, config.DOCK_ICON_SIZE)
        self.button.setIconSize(self.button.size())
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        self.button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(15, 31, 48, 0.94);
                border: 1px solid #31587e;
                border-radius: 32px;
            }
            QPushButton:hover {
                border: 1px solid #53b8ff;
                background-color: rgba(20, 49, 75, 0.96);
            }
            """
        )
        self.button.clicked.connect(self.clicked.emit)

    def set_dock_icon(self, icon):
        self.button.setIcon(icon)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.classifier = IntentClassifier()
        self.action_service = ActionService()
        self.llm_service = LLMService()
        self.worker = None
        self.drag_position = QPoint()
        self._allow_close = False
        self._has_shown_once = False
        self.pending_confirmation_intent = None
        self.avatar_manager = AvatarManager()
        self.is_docked = False
        self.expanded_size = (max(config.WINDOW_WIDTH, 420), max(config.WINDOW_HEIGHT, 620))
        self.dock_bubble = DockBubble()
        self.dock_bubble.clicked.connect(self.expand_from_dock)

        self.auto_dock_timer = QTimer(self)
        self.auto_dock_timer.setSingleShot(True)
        self.auto_dock_timer.timeout.connect(self.collapse_to_dock)

        self.init_ui()
        self.update_avatar(state="boot")
        QTimer.singleShot(900, lambda: self.update_avatar(state="idle"))
        logger.info("MainWindow initialized")

    def init_ui(self):
        self.setWindowTitle("cmdra AI")
        self.resize(*self.expanded_size)
        self.setMinimumSize(420, 620)
        self.setWindowOpacity(config.WINDOW_OPACITY)

        flags = Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if config.ALWAYS_ON_TOP:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.full_stylesheet = f"""
            QWidget#root {{
                background-color: #0e1621;
                color: {config.TEXT_COLOR};
                border: 1px solid #1b2a3c;
                border-radius: 16px;
            }}
            QWidget#titleBar {{
                background: #101d2c;
                border: 1px solid #203047;
                border-radius: 12px;
            }}
            QLabel#statusPill {{
                background: #0c2538;
                border: 1px solid #1d5271;
                border-radius: 14px;
                color: #d9f8ff;
                padding: 6px 14px;
            }}
            QWidget#inputRow {{
                background: #101d2c;
                border: 1px solid #203047;
                border-radius: 12px;
            }}
            """
        self.setStyleSheet(self.full_stylesheet)
        self.setObjectName("root")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        self.main_layout = layout

        self.title_bar = self.create_title_bar()
        layout.addWidget(self.title_bar)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(160, 160)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("statusPill")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Bahnschrift SemiBold", 11))
        layout.addWidget(self.status_label)

        self.chat_widget = ChatWidget()
        layout.addWidget(self.chat_widget, 1)

        self.text_row = self.create_text_row()
        layout.addWidget(self.text_row)

        self._apply_dock_icon()

        self.setLayout(layout)
        self.command_input.setFocus()

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 6, 10, 6)

        title_label = QLabel("cmdra AI")
        title_label.setFont(QFont("Bahnschrift SemiBold", 12))
        title_label.setStyleSheet("color: #7ef3ff; letter-spacing: 0.5px;")

        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #ff7f8f;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5468;
                color: white;
                border-radius: 15px;
            }
            """
        )
        close_btn.clicked.connect(self.close)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)

        title_bar.setLayout(title_layout)
        return title_bar

    def create_text_row(self):
        row = QWidget()
        row.setObjectName("inputRow")
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(8, 8, 8, 8)
        row_layout.setSpacing(8)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type a command...")
        self.command_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #2d5371;
                border-radius: 10px;
                padding: 9px;
                background: #0b141e;
                color: #f8feff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3fa6d4;
            }
            """
        )
        self.command_input.returnPressed.connect(self.on_send_clicked)

        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(100)
        self.send_button.setFixedHeight(36)
        self.send_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background-color: #08c7e8;
                color: #001017;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3fe1ff;
            }
            QPushButton:disabled {
                background-color: #3b4950;
                color: #8ea3ae;
            }
            """
        )
        self.send_button.clicked.connect(self.on_send_clicked)

        row_layout.addWidget(self.command_input, 1)
        row_layout.addWidget(self.send_button)
        row.setLayout(row_layout)
        return row

    def on_send_clicked(self):
        if self.worker and self.worker.isRunning():
            return

        text = self.command_input.text().strip()
        if not text:
            self.set_status("Type a command first")
            self.update_avatar(state="cant_hear")
            QTimer.singleShot(1200, self._reset_idle)
            return

        # Handle pending confirmation (yes/no) for delete actions.
        if self.pending_confirmation_intent:
            normalized = text.lower()
            if normalized in {"yes", "confirm", "proceed", "do it", "ok"}:
                intent = self.pending_confirmation_intent
                intent["parameters"]["confirm"] = True
                self.pending_confirmation_intent = None
                self.start_processing(text_input=text, direct_intent=intent)
                return
            if normalized in {"no", "cancel", "stop"}:
                self.pending_confirmation_intent = None
                self.chat_widget.add_message("Cancelled.", is_user=False)
                self.set_status("Cancelled")
                self.command_input.clear()
                self.command_input.setFocus()
                QTimer.singleShot(1200, self._reset_idle)
                return

        self.start_processing(text_input=text)

    def start_processing(self, text_input="", direct_intent=None):
        if self.is_docked:
            self.expand_from_dock()

        self.auto_dock_timer.stop()
        self.command_input.setEnabled(False)
        self.send_button.setEnabled(False)

        self.set_status("Processing text...")
        self.update_avatar(state="processing")

        self.worker = CommandWorkerThread(
            self.classifier,
            self.action_service,
            self.llm_service,
            text_input=text_input,
            direct_intent=direct_intent,
        )
        self.worker.status_update.connect(self.on_status_update)
        self.worker.finished.connect(self.on_processing_complete)
        self.worker.start()

    def on_status_update(self, status):
        self.set_status(status)
        lower = status.lower()
        if "processing" in lower or "executing" in lower:
            self.update_avatar(state="processing")

    def on_processing_complete(self, result):
        self.command_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.command_input.setFocus()

        if result["success"]:
            user_text = result["user_text"]
            response = result["response"]
            intent = result["intent"]

            self.chat_widget.add_message(user_text, is_user=True)
            self.chat_widget.add_message(response, is_user=False)

            if intent.get("action") in {"delete_file", "delete_folder"} and str(response).lower().startswith("please confirm"):
                self.pending_confirmation_intent = intent.copy()

            if intent.get("action") == "exit_app" or str(response).strip() == "__EXIT_APP__":
                self.set_status("Shutting down...")
                self.update_avatar(state="shutdown")
                self._allow_close = True
                QTimer.singleShot(800, self.close)
                return

            self.update_avatar(intent.get("category"), intent.get("action"))
            QTimer.singleShot(900, lambda: self.update_avatar(state="success"))
            self.set_status("Done")
            self.command_input.clear()
            if not self.pending_confirmation_intent:
                self.schedule_auto_dock()

        else:
            error = result.get("error", "Unknown error")
            self.chat_widget.add_message(f"Error: {error}", is_user=False)
            self.update_avatar(state="error")
            self.set_status("Error")
            self.schedule_auto_dock()

        QTimer.singleShot(2400, self._reset_idle)

    def _reset_idle(self):
        self.set_status("Idle")
        self.update_avatar(state="idle")

    def update_avatar(self, category=None, action=None, state=None):
        """Update top avatar label using AvatarManager with safe fallback."""
        image_path = self.avatar_manager.get_avatar(category=category, action=action, state=state)
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            pixmap = self._build_fallback_pixmap()

        self.avatar_label.setPixmap(
            pixmap.scaled(
                self.avatar_label.width(),
                self.avatar_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def _build_fallback_pixmap(self):
        size = self.avatar_label.size()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QColor("#23384c"))
        painter.setPen(QColor("#3f6b8c"))
        painter.drawEllipse(1, 1, size.width() - 2, size.height() - 2)
        painter.end()
        return pixmap

    def _apply_dock_icon(self):
        size = config.DOCK_ICON_SIZE
        source = QPixmap(config.ICON_PATH) if config.ICON_PATH else QPixmap()
        if source.isNull():
            source = QPixmap(self.avatar_manager.base_default)
        if source.isNull():
            return

        source = source.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        circular = QPixmap(size, size)
        circular.fill(Qt.transparent)

        painter = QPainter(circular)
        painter.setRenderHint(QPainter.Antialiasing, True)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, source)
        painter.end()

        self.dock_bubble.set_dock_icon(QIcon(circular))

    def _position_bottom_right(self, window=None):
        target = window or self
        screen = QApplication.primaryScreen()
        if not screen:
            return
        area = screen.availableGeometry()
        x = area.right() - target.width() - config.DOCK_MARGIN
        y = area.bottom() - target.height() - config.DOCK_MARGIN
        target.move(max(area.left(), x), max(area.top(), y))

    def schedule_auto_dock(self):
        if not config.AUTO_DOCK_ENABLED or self.is_docked:
            return
        self.auto_dock_timer.start(config.AUTO_DOCK_TIMEOUT_MS)

    def collapse_to_dock(self):
        if self.is_docked:
            return
        if self.worker and self.worker.isRunning():
            return

        self.is_docked = True
        self.auto_dock_timer.stop()
        self.expanded_size = (self.width(), self.height())
        self.hide()
        self._position_bottom_right(self.dock_bubble)
        self.dock_bubble.show()
        self.dock_bubble.raise_()

    def expand_from_dock(self):
        if not self.is_docked:
            return

        self.is_docked = False
        self.auto_dock_timer.stop()
        self.dock_bubble.hide()
        self.setMinimumSize(420, 620)
        self.setMaximumSize(16777215, 16777215)
        self.resize(*self.expanded_size)
        self.show()
        self._position_bottom_right()
        self.command_input.setFocus()
        self.raise_()

    def set_status(self, status):
        self.status_label.setText(status)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._has_shown_once:
            self._has_shown_once = True

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.is_docked:
            self._position_bottom_right(self.dock_bubble)

    def closeEvent(self, event):
        if not self._allow_close:
            event.ignore()
            self._allow_close = True
            self.set_status("Shutting down...")
            self.update_avatar(state="shutdown")
            QTimer.singleShot(750, self.close)
            return
        self.dock_bubble.hide()
        super().closeEvent(event)


