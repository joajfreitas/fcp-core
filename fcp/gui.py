# This Python file uses the following encoding: utf-8
import sys

from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .gui_lib.mainwindow import MainWindow


def gui(file):
    app = QApplication([])
    window = MainWindow()
    if file != None and file != "":
        window.load_json(file)
    window.show()
    sys.exit(app.exec_())
