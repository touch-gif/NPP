from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class HoverableExpandFrame(QFrame):
    def __init__(self, parent: QWidget = None, flags: Qt.WindowFlags = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        self.expanded = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.origingeometry = QRect(1070,-10,141,761)

    def enterEvent(self, event):
        if not self.expanded:
            self.expanded = True
            current_rect = self.geometry()
            self.animation.setStartValue(self.origingeometry)
            self.new_rect = QRect(970, -10,141,761)
            self.animation.setEndValue(self.new_rect)
            self.animation.start()

    def leaveEvent(self, event):
        if self.expanded:
            self.expanded = False
            current_rect = self.geometry()
            self.animation.setStartValue(self.new_rect)
            new_rect = QRect(current_rect.x() + 100, current_rect.y(), current_rect.width(), current_rect.height())
            self.animation.setEndValue(self.origingeometry)
            self.animation.start()

