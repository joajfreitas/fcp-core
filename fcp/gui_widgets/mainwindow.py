import time
from pathlib import Path

from PySide2.QtWidgets import *

from ..config import *
from ..sql import *
from .device_widget import DeviceWidget
from .device_details import DeviceDetails

from ..gui_lib.mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config = config_session()
        self.recent_files()

        self.ui.actionSave.triggered.connect(self.save)

    def save(self):
        print("save")
        self.session.commit()

    def recent_files(self):
        files = File.recent_files(self.config)

        menu = QMenu("recent_files")
        for file in files:
            action = menu.addAction(file.path)
            action.triggered.connect(lambda x : self.load(Path(file.path)))

        self.ui.actionOpen_Recent.setMenu(menu)

    def load(self, path: Path):
        print("path", path)
        File.access(self.config, path)

        self.session = init_session(path)
        self.load_devices()

    def load_devices(self):
        for device in self.session.query(Device).all():
            dev = DeviceWidget(device)
            self.ui.verticalLayout.addWidget(dev)
            dev.open_device.connect(self.open_device_details)

    def open_device_details(self, name, state):
        device = self.session.query(Device).filter(Device.name == name).all().pop()
        dev = DeviceDetails(device)
        self.ui.deviceDetailsLayout.addWidget(dev)


