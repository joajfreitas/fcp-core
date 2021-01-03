import time
from pathlib import Path

from PySide2.QtWidgets import *

from ..config import *
from ..sql import *
from .device_widget import DeviceWidget

from ..gui_lib.mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config = config_session()
        self.recent_files()

    def recent_files(self):
        files = File.recent_files(self.config)

        menu = QMenu("recent_files")
        for file in files:
            action = menu.addAction(file.path)
            action.triggered.connect(lambda: print(file.path))

        self.ui.actionOpen_Recent.setMenu(menu)

    def load(self, path: Path):
        File.access(self.config, path)

        self.session = init_session(path)
        self.load_devices()

    def load_devices(self):
        for device in self.session.query(Device).all():
            dev = DeviceWidget(device)
            self.ui.verticalLayout.addWidget(dev)


