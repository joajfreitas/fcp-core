from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt
from PySide2.QtCore import Signal

from .widgets import *

from .node_details import NodeDetails, FakeParent
from .signal_details import SignalDetails
from .signal_widget import SignalWidget
from .message_details import MessageDetails
from .message_widget import MessageWidget
from .arg_details import ArgDetails
from .cmd_details import CmdDetails
from .cmd_widget import CmdWidget
from .cfg_details import CfgDetails
from .cfg_widget import CfgWidget
from .device_details import DeviceDetails
from .device_widget import DeviceWidget
from .enum_value_details import EnumValueDetails
from .enum_details import EnumDetails
from .log_details import LogDetails
from .log_widget import LogWidget
from .enum_widget import EnumWidget

from pathlib import Path
import json
import yaml
import webbrowser
from copy import deepcopy, copy

from ..version import VERSION
from ..specs import *
from ..validator import validate
from ..config import *
from .message_box import MessageBox

from .undo_redo import UndoRedo, UndoAdd


import requests


def nag_intro():
    def version_comparison(v1, v2):
        v1s = [int(v) for v in v1.split(".")]
        v2s = [int(v) for v in v2.split(".")]

        for v1, v2 in zip(v1s, v2s):
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1

        return 0

    try:
        r = requests.get("https://pypi.org/pypi/fcp/json")
    except Exception as e:
        return
    j = json.loads(r.text)
    releases = list(j["releases"].keys())
    releases.sort(key=lambda s: [int(u) for u in s.split('.')])
    upstream_version = releases[-1]

    out = ""

    version_comp = version_comparison(upstream_version, VERSION)
    if version_comp == 1:
        out += f"<p><b>FCP v{upstream_version} is available. Go get it:\nsudo pip install fcp=={upstream_version}</b></p>"
    elif version_comp == 0:
        release_url = f"https://joajfreitas.gitlab.io/fcp-core/v{VERSION}.html"
        r = requests.get(release_url)
        if r.ok:
            out += "\n" + r.text
    elif version_comp == -1:
        out += f"Oh! I see you're running a development version. Good luck."

    return out

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.history = None

        self.spec = Spec()
        self.children = []

        self.connect_buttons()
        self.config_shortcuts()

        self.log_widget = None
        self.enum_widget = None

        self.filename = None

        self.config, _ = config_session()
        self.recent_files()

        self.undo_redo = UndoRedo()



        MessageBox(
            self,
            QMessageBox.Ok,
            QMessageBox.Information,
            nag_intro()).launch()


    def recent_files(self):
        def loads(path):
            def closure():
                self.load(path)

            return closure

        files = File.recent_files(self.config)
        menu = QMenu("recent_files")

        for file in files:
            action = menu.addAction(file.path)
            action.triggered.connect(loads(file.path))

        self.ui.actionOpen_Recent.setMenu(menu)

    def connect_buttons(self):
        def fcp_help(link):
            webbrowser.open(link)

        self.ui.actionOpen.triggered.connect(self.open_json)
        self.ui.actionSave.triggered.connect(self.save_json)
        self.ui.actionValidate.triggered.connect(self.validate)
        self.ui.action_software10e_help.triggered.connect(
            lambda: fcp_help("https://projectofst.gitlab.io/software10e/docs/fcp/")
        )
        self.ui.action_fcp_help.triggered.connect(
            lambda: fcp_help("https://fcp-core.readthedocs.io/en/latest/")
        )
        self.ui.addButton.clicked.connect(self.add_device)

    def shortcut(self, key_sequence, f):
        shortcutSave = QShortcut(key_sequence, self)
        shortcutSave.setContext(Qt.ApplicationShortcut)
        shortcutSave.activated.connect(f)


    def config_shortcuts(self):
        self.shortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self.save_json)
        self.shortcut(QKeySequence(Qt.CTRL + Qt.Key_O), self.open_json)
        self.shortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self.validate)
        self.shortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self.undo)
        self.shortcut(QKeySequence(Qt.CTRL + Qt.Key_R), self.redo)

    def save_history(self):
        old_spec = deepcopy(self.spec)
        self.history.insert(0, old_spec)

    def undo(self):
        self.undo_redo.undo()
        self.reload()


    def redo(self):
        self.undo_redo.redo()
        self.reload()

    def validate(self) -> int:
        failed = validate(self.spec)
        failed_count = len([lvl for lvl, msg in failed if lvl == "error"])
        if len(failed) == 0:
            MessageBox(
                self,
                QMessageBox.Ok,
                QMessageBox.Information,
                "Spec passed").launch()
        else:
            if len(failed) > 5:
                failed = sorted(failed, key = lambda x : 0 if x[0] == "error" else 1)
                failed = [(lvl, msg) for lvl, msg in failed]
                failed = [f"{level}: {msg}" for level, msg in failed]
                errors = "\n".join(failed[:5]) + f"\nand {len(failed)-5} more errors..."
            else:
                failed = [f"{level}: {msg}" for level, msg in failed]
                errors = "\n".join(failed)


            MessageBox(
                self,
                QMessageBox.Ok,
                QMessageBox.Warning,
                errors).launch()

        return failed_count

    def add_device(self, device=None, widget=None):
        new_device = device is None or type(device) == bool

        if new_device:
            device = Device(parent=self.spec, msgs={})

        if type(device) is Device:
            r = self.spec.add_device(device)
            #if r == False:
            #    msg = QMessageBox(self)
            #    msg.setStandardButtons(QMessageBox.Ok)
            #    msg.setIcon(QMessageBox.Warning)
            #    msg.setText("Failed to create device")
            #    msg.show()
            #    return

        if widget is None:
            dev_widget = DeviceWidget(
                self, device, details=DeviceDetails, layout=self.ui.deviceDetailsLayout
            )
        else:
            dev_widget = widget

        if new_device:
            undo_action = UndoAdd(device, dev_widget, dev_widget.delete, self.add_device)
            self.undo_redo.push(undo_action)

        self.ui.verticalLayout.addWidget(dev_widget)
        self.children.append(dev_widget)

    def open_json(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Open JSON"), self.tr("JSON (*.json)")
        )
        self.load_json(filename[0])
        self.history = []
        self.history.append()

    def save_json(self):
        for child in self.children:
            child.save()

        l = self.validate()
        if l > 0:
            return

        if self.filename:
            filename = self.filename
        else:
            try:
                filename = QFileDialog.getSaveFileName(
                    self, self.tr("Open JSON"), str(self.filename)
                )
                filename = filename[0]
            except Exception as e:
                msg = QMessageBox(self)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setIcon(QMessageBox.Warning)
                msg.setText(f"{filename} is not a valid filename")
                msg.show()
                return

        MessageBox(
            self,
            QMessageBox.Ok,
            QMessageBox.Information,
            "Saved").launch()

        with open(filename, "w") as f:
            j = self.spec.compile()
            f.write(json.dumps(j, indent=4))

    def load(self, filename):
        File.access(self.config, filename)
        with open(filename) as f:
            r = f.read()
            j = json.loads(r)

        self.spec.decompile(j)

        self.reload_spec()

        self.filename = Path(filename)
        self.history = [self.spec]

    def load_json(self, filename):
        if filename == "":
            msg = QMessageBox(self)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"'{filename}' is not a valid filename")
            msg.show()
            return


        self.filename = filename

        File.access(self.config, filename)
        self.load(filename)


    def reload_spec(self):
        for device in sorted(self.spec.devices.values(), key=lambda x: x.id):
            self.add_device(device)

        self.add_device(self.spec.common)

        self.log_widget = LogWidget(self, self.spec)
        self.log_widget.setVisible(True)
        self.ui.logDetailsLayout.addWidget(self.log_widget)
        self.children.append(self.log_widget)
        self.enum_widget = EnumWidget(self, self.spec)
        self.enum_widget.setVisible(True)
        self.ui.enumDetailsLayout.addWidget(self.enum_widget)
        self.children.append(self.enum_widget)

    def close_spec(self):
        return

    def reload(self):
        #print("reload:", self.history)
        self.save_history()
        for node in self.children:
            node.reload()

        self.spec.normalize()

    def reload_service(self, path):
        self.reload()
