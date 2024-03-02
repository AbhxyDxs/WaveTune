from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    Qt, pyqtSignal, QPoint, QSize
)

from app.ui.uilib.util import shadowify, setElide, mask_image_rndcb


class ControlButton(QtWidgets.QPushButton):
    def __init__(self, iconSize=16, *args, **kwargs):
        super(ControlButton, self).__init__(*args, **kwargs)
        self.iconSize = iconSize
        self.setIconSize(QSize(iconSize, iconSize))

    def changeIcon(self, newIconPath):
        self.setIcon(QIcon(newIconPath))
        self.setIconSize(QSize(self.iconSize, self.iconSize))

class ScrollableButton(ControlButton):

    onValueChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(ScrollableButton, self).__init__(*args, **kwargs)
        self.i_or_d_level=5
        self.currentVolume = 50
        self.minr, self.maxr = 0, 100
        self.tooltip = ToolTip(self)

    def setRange(self, minimum, maximum):
        self.minr, self.maxr = minimum, maximum

    def enterEvent(self, a0) -> None:
        self.tooltip.setText(str(self.currentVolume))
        self.tooltip.show()
        self.tooltip.move(self.mapToGlobal(QPoint(self.pos().x() + (self.width() // 2) - (self.tooltip.width() // 2)
                                                  - 5, self.pos().y() - 45)))
        ControlButton.enterEvent(self, a0)

    def leaveEvent(self, a0) -> None:
        self.tooltip.hide()
        ControlButton.leaveEvent(self, a0)

    def wheelEvent(self, event) -> None:
        if event.angleDelta().y() > 0:
           self.setVolume(True)
        else:
            self.setVolume(False)

        ControlButton.wheelEvent(self, event)

    def setVolume(self,i_or_d):
        if i_or_d:
            if not (self.currentVolume + self.i_or_d_level) > self.maxr:
                self.currentVolume += self.i_or_d_level
        else:
            if not (self.currentVolume - self.i_or_d_level) < self.minr:
                self.currentVolume -= self.i_or_d_level
        if self.currentVolume==self.minr:
            self.changeIcon("res/icons/volume.svg")
        else:
            self.changeIcon("res/icons/volume.svg")

        self.onValueChanged.emit(self.currentVolume)
        self.tooltip.setText(str(self.currentVolume))










class ToolTip(QtWidgets.QFrame):
    def __init__(self, p, text="Placeholder"):
        super(ToolTip, self).__init__(p)
        self.text = QtWidgets.QLabel(self)
        self.text.setAlignment(Qt.AlignCenter)
        self.setWindowFlags(Qt.ToolTip)
        self.setText(text)

    def setText(self, text):
        self.text.setText(text)
        self.text.adjustSize()
        self.setFixedSize(self.text.size())
class Seekbar(QtWidgets.QSlider):
    seek = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(Seekbar, self).__init__(*args, **kwargs)
        self.seeking = False
        self.valueChanged.connect(self.on_seek)

    def on_seek(self, value):
        if self.seeking:
            self.seek.emit(value)

    def updatePosition(self, position):
        if not self.seeking:
            self.setValue(position)

    def mousePressEvent(self, ev) -> None:
        self.seeking = True
        QtWidgets.QSlider.mousePressEvent(self, ev)

    def mouseReleaseEvent(self, ev) -> None:
        self.seeking = False
        QtWidgets.QSlider.mouseReleaseEvent(self, ev)

class SearchBar(QtWidgets.QLineEdit):
    def __init__(self, p):
        super(SearchBar, self).__init__(p)
        self.hlay = QtWidgets.QHBoxLayout(self)
        self.hlay.setContentsMargins(4, 0, 0, 0)
        self.searchButton = QtWidgets.QPushButton(self)
        self.searchButton.setIcon(QIcon("res/icons/search.svg"))
        self.searchButton.setCursor(Qt.PointingHandCursor)
        self.hlay.addWidget(self.searchButton, alignment=Qt.AlignLeft)


class TrackItem(QtWidgets.QFrame):
    onPlay = pyqtSignal(object)

    def __init__(self, p, media):
        super(TrackItem, self).__init__(p)
        self.setFixedSize(128, 170)
        self.setObjectName("track-item")
        self.vlay = QtWidgets.QVBoxLayout(self)
        self.vlay.setContentsMargins(0, 0, 0, 0)
        self.vlay.setSpacing(0)

        self.media = media

        title = media.title
        artist = media.artist
        cover = media.art

        self.searchid = title
        if artist:
            self.searchid += artist
        self.searchid = self.searchid.lower()

        if cover is None:
            cover = "res/icons/cd.png"

        self.cover = QtWidgets.QLabel(self)
        self.cover.setFixedSize(128, 128)

        masked_image_pixmap = mask_image_rndcb(cover, size=128, radius=8)

        if masked_image_pixmap is not None:
            self.cover.setPixmap(masked_image_pixmap)

        self.title = QtWidgets.QLabel(self)
        self.title.setObjectName("track-item-title")
        self.title.resize(150, self.title.height())
        self.artist = QtWidgets.QLabel(self)
        self.artist.setObjectName("track-item-artist")
        self.title.resize(150, self.artist.height())
        self.setTitle(title)
        self.setArtist(artist)

        self.vlay.addWidget(self.cover, alignment=Qt.AlignCenter | Qt.AlignTop)
        self.vlay.addWidget(self.title, alignment=Qt.AlignCenter)
        self.vlay.addSpacing(-10)
        self.vlay.addWidget(self.artist, alignment=Qt.AlignCenter)

        shadowify(self)

    def mouseDoubleClickEvent(self, a0) -> None:
        self.onPlay.emit(self.media)
        QtWidgets.QFrame.mouseDoubleClickEvent(self, a0)

    def setCover(self, imgpath):
        self.cover.setPixmap(mask_image_rndcb(imgpath, size=128, radius=8))

    def setTitle(self, title):
        setElide(self.title, title)
        if "…" in self.title.text():
            self.title.setToolTip(title)

    def setArtist(self, artist):
        setElide(self.artist, artist)
        if "…" in self.artist.text():
            self.artist.setToolTip(artist)

