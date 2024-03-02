from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    Qt, pyqtSignal, QPoint
)

class WindowTitleNotch(QtWidgets.QFrame):
    def __init__(self, p, title):
        super(WindowTitleNotch, self).__init__(p)
        self.setObjectName("window-title-notch")
        self.hbox = QtWidgets.QHBoxLayout(self)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.title = QtWidgets.QLabel(title, self)
        self.title.setObjectName("window-title")
        self.title.adjustSize()
        self.setFixedSize(self.title.width() + 25, 20)
        self.hbox.addWidget(self.title, alignment=Qt.AlignCenter)

    def setTitle(self, title):
        self.title.setText(title)
        self.title.adjustSize()
        self.setFixedSize(self.title.width()+35, 20)
        self.parent().centerTitleNotch()

class TitleBar(QtWidgets.QFrame):
    def __init__(self,p=None):
        super(TitleBar,self).__init__(p)
        self.setObjectName("titlebar")
        self.hlay=QtWidgets.QHBoxLayout(self)
        self.hlay.setContentsMargins(0, 0, 9, 0)
        self.hlay.setSpacing(11)
        self.hlay.setAlignment(Qt.AlignRight)
        self.windowNotch = WindowTitleNotch(self, "Window")

        self.closeButton = QtWidgets.QPushButton(self)
        self.sizeButton = QtWidgets.QPushButton(self)
        self.minimizeButton = QtWidgets.QPushButton(self)

        self.closeButton.setToolTip("Close")
        self.sizeButton.setToolTip("Maximize/Restore")
        self.minimizeButton.setToolTip("Minimize")

        self.closeButton.clicked.connect(self.parent().parent().windowCloseEvent)
        self.sizeButton.clicked.connect(self.parent().parent().sizeEvent)
        self.minimizeButton.clicked.connect(self.parent().parent().minimizeEvent)

        self.closeButton.setObjectName("control-close")
        self.sizeButton.setObjectName("control-size")
        self.minimizeButton.setObjectName("control-minimize")

        for button in self.findChildren(QtWidgets.QPushButton):
            button.setFixedSize(12, 12)


        self.hlay.addWidget(self.minimizeButton)
        self.hlay.addWidget(self.sizeButton)
        self.hlay.addWidget(self.closeButton)

    def centerTitleNotch(self):
        self.windowNotch.move((self.width() // 2) - self.windowNotch.width() // 2, 0)

    def resizeEvent(self, a0) -> None:
        self.centerTitleNotch()

    def mousePressEvent(self, event) -> None:
        self.window().windowHandle().startSystemMove()
        self.parent().setUpdateState(True)
        QtWidgets.QFrame.mousePressEvent(self, event)

    def mouseReleaseEvent(self, a0) -> None:
        self.parent().setUpdateState(False)
        QtWidgets.QFrame.mouseReleaseEvent(self, a0)

class Window(QtWidgets.QFrame):

    onMove = pyqtSignal(QPoint)

    def __init__(self, p, width: int = 640, height: int = 480):
        super(Window, self).__init__(p)
        self.setWindowTitle("Window")
        self.setObjectName("main-window")
        self.resize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.titlebar = TitleBar(self)
        self.opacity = 500
        self.isUpdating = False
        self.closingQueue = []

    def raiseBaseWidget(self):
        self.titlebar.raise_()

    def moveEvent(self, a0) -> None:
        self.onMove.emit(self.pos())
        QWidget.moveEvent(self, a0)

    def resizeEvent(self, event) -> None:
        self.titlebar.resize(self.width(), 30)
        QWidget.resizeEvent(self, event)

    def setOpacity(self, opacity: int):
        self.opacity = opacity

    def setUpdateState(self, isUpdating):
        self.isUpdating = isUpdating


