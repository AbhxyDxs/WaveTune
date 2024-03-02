from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication,QMainWindow
import  sys
from app.ui.uilib.windowContainer import WindowContainer
from app.app import Application


class AeroRhytm(Application):
    def __init__(self, p):
        super().__init__(p)

def main():

    app = QApplication(sys.argv)
    app.setFont(QFont("JetBrains Mono"))
    wcon = WindowContainer(window=AeroRhytm)
    wcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


