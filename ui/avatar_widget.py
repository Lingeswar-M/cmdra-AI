"""
Avatar Widget
Animated emotion-driven avatar for assistant states.
"""

import os
import math
import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPixmap, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect


class AvatarWidget(QWidget):
    """Draws a circular avatar with state-driven glow and subtle animation."""

    STATE_STYLES = {
        "booting": {"color": QColor("#00bcd4"), "glow": 0.34, "pulse": 0.07},
        "idle": {"color": QColor("#88a0b8"), "glow": 0.12, "pulse": 0.02},
        "listening": {"color": QColor("#4fc3f7"), "glow": 0.35, "pulse": 0.08},
        "thinking": {"color": QColor("#ffd166"), "glow": 0.28, "pulse": 0.06},
        "executing": {"color": QColor("#7ae582"), "glow": 0.30, "pulse": 0.06},
        "file_task": {"color": QColor("#9d8df1"), "glow": 0.26, "pulse": 0.05},
        "browser_task": {"color": QColor("#ff9f6e"), "glow": 0.26, "pulse": 0.05},
        "cant_hear": {"color": QColor("#ffcc80"), "glow": 0.30, "pulse": 0.05},
        "success": {"color": QColor("#00e676"), "glow": 0.30, "pulse": 0.04},
        "error": {"color": QColor("#ff5f6d"), "glow": 0.35, "pulse": 0.04},
        "shutdown": {"color": QColor("#b0bec5"), "glow": 0.10, "pulse": 0.01},
    }

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.state = "idle"
        self._phase = 0.0
        self._last_time = time.time()
        self._shake_until = 0.0

        self.base_pixmap = QPixmap()
        self._load_image()

        self.fade = QGraphicsOpacityEffect(self)
        self.fade.setOpacity(1.0)
        self.setGraphicsEffect(self.fade)

        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

        self.setMinimumSize(160, 160)

    def _load_image(self):
        if self.image_path and os.path.exists(self.image_path):
            self.base_pixmap = QPixmap(self.image_path)
        else:
            self.base_pixmap = QPixmap()

    def set_state(self, state):
        if state not in self.STATE_STYLES:
            state = "idle"
        self.state = state
        if state == "error":
            self._shake_until = time.time() + 0.6
        self.update()

    def set_image(self, image_path):
        self.image_path = image_path
        self._load_image()
        self.update()

    def start_boot_animation(self):
        self.set_state("booting")
        self.fade.setOpacity(0.0)
        self._animate_fade(1.0, 850)

    def start_shutdown_animation(self):
        self.set_state("shutdown")
        self._animate_fade(0.0, 700)

    def _animate_fade(self, target, duration_ms):
        start = self.fade.opacity()
        steps = max(1, int(duration_ms / 33))
        step_size = (target - start) / steps

        counter = {"n": 0}

        def _step():
            counter["n"] += 1
            self.fade.setOpacity(max(0.0, min(1.0, self.fade.opacity() + step_size)))
            if counter["n"] >= steps:
                t.stop()
                self.fade.setOpacity(target)

        t = QTimer(self)
        t.setInterval(33)
        t.timeout.connect(_step)
        t.start()

    def _tick(self):
        now = time.time()
        dt = max(0.001, now - self._last_time)
        self._last_time = now
        self._phase += dt * 4.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        size = min(w, h) * 0.78
        style = self.STATE_STYLES[self.state]

        pulse = 1.0 + style["pulse"] * math.sin(self._phase)
        radius = (size * pulse) / 2.0
        cx = w / 2.0
        cy = h / 2.0

        x_jitter = 0.0
        if time.time() < self._shake_until:
            x_jitter = 3.5 * math.sin(self._phase * 20.0)

        cx += x_jitter

        glow_radius = radius + 18
        glow = style["color"]
        glow.setAlphaF(style["glow"])
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(int(cx - glow_radius), int(cy - glow_radius), int(glow_radius * 2), int(glow_radius * 2))

        clip = QPainterPath()
        clip.addEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))
        painter.setClipPath(clip)

        if not self.base_pixmap.isNull():
            scaled = self.base_pixmap.scaled(
                int(radius * 2),
                int(radius * 2),
                Qt.KeepAspectRatioByExpanding,
                Qt.FastTransformation,
            )
            painter.drawPixmap(int(cx - radius), int(cy - radius), scaled)
        else:
            fallback = QColor("#2c3e50")
            painter.fillPath(clip, fallback)

        overlay = style["color"]
        overlay.setAlpha(36)
        painter.fillPath(clip, overlay)

        painter.setClipping(False)
        border = QPen(style["color"], 3)
        painter.setPen(border)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))

