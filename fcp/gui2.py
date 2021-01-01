import sys

from PySide2.QtWidgets import *

from .gui_widgets.mainwindow import MainWindow


def json_to_sqlite(fcp_json):
    fcp_json

def gui2(file, logger):
    app = QApplication([])
    window = MainWindow(logger)

    window.show()
    sys.exit(app.exec_())
