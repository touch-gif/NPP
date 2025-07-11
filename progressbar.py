from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget


class ExtendProgressBar(QProgressBar):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)
        