"""
Waveform Widget
Modern animated waveform visualization for cmdra AI.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QLinearGradient, QPen
import random
import config


class WaveformWidget(QWidget):
    """Modern animated waveform visualization."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bar_count = 30
        self.bars = [0.0] * self.bar_count
        self.is_active = False

        self.setMinimumHeight(100)
        self.setStyleSheet("background: transparent;")

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.setInterval(30)  # smoother animation

    # ----------------------------
    # Animation Controls
    # ----------------------------

    def start_animation(self):
        self.is_active = True
        self.timer.start()

    def stop_animation(self):
        self.is_active = False

    # ----------------------------
    # Animation Logic
    # ----------------------------

    def animate(self):
        if self.is_active:
            for i in range(self.bar_count):
                target = random.uniform(0.3, 1.0)
                self.bars[i] += (target - self.bars[i]) * 0.6  # easing
        else:
            for i in range(self.bar_count):
                self.bars[i] *= 0.85  # smooth decay

        self.update()

    # ----------------------------
    # Paint
    # ----------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        panel_gradient = QLinearGradient(0, 0, width, height)
        panel_gradient.setColorAt(0.0, QColor(255, 255, 255, 10))
        panel_gradient.setColorAt(1.0, QColor(255, 255, 255, 3))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.setBrush(QBrush(panel_gradient))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 12, 12)

        bar_width = width / self.bar_count
        center_y = height / 2

        for i, level in enumerate(self.bars):
            bar_height = height * level * 0.8
            x = i * bar_width
            y = center_y - (bar_height / 2)

            color = QColor(config.ACCENT_COLOR)
            color.setAlpha(220 if self.is_active else 120)
            if i % 5 == 0:
                color = QColor("#8df3ff")
                color.setAlpha(220 if self.is_active else 120)

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)

            painter.drawRoundedRect(
                int(x + 3),
                int(y),
                int(bar_width - 6),
                int(bar_height),
                6,
                6
            )


