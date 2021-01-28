import time
from pathlib import Path
import hjson as json

from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from ..config import *
from ..sql import *
from .device_widget import DeviceWidget
from .device_details import DeviceDetails
from ..undoredo import SQLiteUndoRedo

from ..gui_lib.mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config, _ = config_session()
        self.recent_files()

        self.ui.actionSave.triggered.connect(self.save)

        self.devs_details = {}

        shortcutOpen = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self)
        shortcutOpen.setContext(Qt.ApplicationShortcut)
        shortcutOpen.activated.connect(self.undo)

    def undo(self):
        print("undo")
        ids = self.undo_redo.undo()
        for table, name in ids:
            if table == "devs":
                print("name:", name)
                self.devs_details[name].reload()

    def save(self):
        print("save")
        self.session.commit()

        try:
            filename, _ = QFileDialog.getSaveFileName(self, self.tr("Open JSON"), "")
        except Exception as e:
            msg = QMessageBox(self)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"{filename} is not a valid filename")
            msg.show()
            return

        j = json.dumps(sql_to_json(self.session), indent=4)
        with open(filename, "w") as f:
            f.write(j)

    def recent_files(self):
        files = File.recent_files(self.config)

        menu = QMenu("recent_files")
        for file in files:
            action = menu.addAction(file.path)
            action.triggered.connect(lambda x: self.load(Path(file.path)))

        self.ui.actionOpen_Recent.setMenu(menu)

    def load(self, path: Path):
        File.access(self.config, path)

        self.session, self.engine = init_session(path)
        self.db = self.engine.connect()

        self.undo_redo = SQLiteUndoRedo(self.db)
        self.undo_redo.activate("devs", "msgs", "signals")
        self.load_devices()

    def load_devices(self):
        for device in self.session.query(Device).all():
            dev = DeviceWidget(device)
            self.ui.verticalLayout.addWidget(dev)
            dev.open_device.connect(self.open_device_details)

    def open_device_details(self, name, state):
        device = self.session.query(Device).filter(Device.name == name).all().pop()
        if not device.name in self.devs_details.keys():
            dev = DeviceDetails(device)
            self.ui.deviceDetailsLayout.addWidget(dev)
            self.devs_details[device.name] = dev
            dev.save.connect(self.barrier)

        self.devs_details[device.name].setVisible(state)

    def barrier(self):
        print("commiting")
        self.session.commit()
        self.undo_redo.barrier()
