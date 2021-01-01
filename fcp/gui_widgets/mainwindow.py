from PySide2.QtWidgets import *
from ..gui_lib.mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, logger):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
