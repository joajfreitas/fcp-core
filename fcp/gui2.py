import sys
from pathlib import Path

from PySide2.QtWidgets import *

from .gui_widgets.mainwindow import MainWindow


def gui2(file: Path):
    app = QApplication([])
    window = MainWindow()

    if file is not None:
        window.load(file)

    window.show()
    sys.exit(app.exec_())
