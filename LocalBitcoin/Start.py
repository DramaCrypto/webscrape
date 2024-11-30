import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle

from MainController import MainController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # SET FONT
    font = app.font()
    font.setPointSize(12)
    app.setFont(font)
    # SET STYLE
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # INIT CONTROLLER
    controller = MainController()
    controller.initialize()
    sys.exit(app.exec())
