# This Python file uses the following encoding: utf-8
import sys
import json
from datetime import datetime
import webbrowser
from pathlib import Path
import yaml

from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .gui_lib.mainwindow import Ui_MainWindow
from .gui_lib.devicewidget import Ui_DeviceWidget
from .gui_lib.devicedetails import Ui_DeviceDetails
from .gui_lib.messagewidget import Ui_MessageWidget
from .gui_lib.messagedetails import Ui_MessageDetails
from .gui_lib.signalwidget import Ui_SignalWidget
from .gui_lib.signaldetails import Ui_SignalDetails
from .gui_lib.logwidget import Ui_LogWidget
from .gui_lib.enumwidget import Ui_EnumWidget
from .gui_lib.enumdetails import Ui_EnumDetails
from .gui_lib.logdetails import Ui_LogDetails
from .gui_lib.cfgwidget import Ui_CfgWidget
from .gui_lib.cfgdetails import Ui_CfgDetails
from .gui_lib.cmdwidget import Ui_CmdWidget
from .gui_lib.cmddetails import Ui_CmdDetails
from .gui_lib.cmdarg import Ui_CmdArg
from .gui_lib.enumvalue import Ui_EnumValue

from .spec import *
from .validator import validate


class FakeParent:
    def __init__(self):
        return

    def setVisible(self, visibility: bool):
        return


class NodeDetails(QWidget):
    """ Node (Device, Message, Signal, Log, Config, Command) interface """

    def __init__(self, gui, node, parent=None, details=None, layout=None):
        QWidget.__init__(self)
        self.node = node
        self.gui = gui
        self.parent = parent
        self.atts = []
        self.details = None
        self.Details = details
        self.layout = layout
        self.children = []
        self.details_button = None

    def load_atts(self, ui, node):
        self.atts = []
        return

    def connect_atts(self):
        def store(att, set_f):
            def closure():
                set_f(att.text())
                self.gui.reload()

            return closure

        for att, _, set_f in self.atts:
            att.editingFinished.connect(store(att, set_f))

    def save(self):
        for child in self.children:
            child.save()

        for att, get_f, set_f in self.atts:
            set_f(att.text())

        self.gui.reload()

    def delete(self):
        r = self.gui.spec.rm_node(self.node)
        self.setVisible(False)
        self.parent.setVisible(False)
        return

    def reload(self):
        for child in self.children:
            child.reload()

        for att, get_f, set_f in self.atts:
            att.setText(str(get_f()))

    def raise_widget(self, checked):
        self.setVisible(checked)

    def open_details(self, checked):
        if checked == False:
            for child in self.children:
                child.open_details(False)
                if child.details_button is not None:
                    child.details_button.setChecked(False)

        if self.details_button is None:
            return

        if self.details is None:
            self.details = self.Details(self.gui, self.node, self)
            self.layout.addWidget(self.details)
            self.children.append(self.details)

        self.details.setVisible(checked)


class SignalDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.get_name, node.set_name),
            (ui.startEdit, node.get_start, node.set_start),
            (ui.lengthEdit, node.get_length, node.set_length),
            (ui.muxEdit, node.get_mux, node.set_mux),
            (ui.muxCountEdit, node.get_mux_count, node.set_mux_count),
            (ui.typeEdit, node.get_type, node.set_type),
            (ui.commentEdit, node.get_comment, node.set_comment),
            (ui.minValueEdit, node.get_min_value, node.set_min_value),
            (ui.maxValueEdit, node.get_max_value, node.set_max_value),
            (ui.byteOrderEdit, node.get_byte_order, node.set_byte_order),
            (ui.scaleEdit, node.get_scale, node.set_scale),
            (ui.offsetEdit, node.get_offset, node.set_offset),
            (ui.aliasEdit, node.get_alias, node.set_alias),
        ]

    def __init__(self, gui, node: "Signal", parent):
        NodeDetails.__init__(self, gui, node, parent)

        ui = self.ui = Ui_SignalDetails()
        self.ui.setupUi(self)

        self.load_atts(ui, node)
        self.connect_atts()

        self.ui.signalDeleteButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(False)

        self.children = []


class SignalWidget(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.name, node.get_name, node.set_name),
            (ui.start, node.get_start, node.set_start),
            (ui.length, node.get_length, node.set_length),
        ]

    def __init__(self, gui, node, details=None, layout=None):
        NodeDetails.__init__(self, gui, node, details=details, layout=layout)

        ui = self.ui = Ui_SignalWidget()
        self.ui.setupUi(self)

        self.load_atts(self.ui, self.node)

        self.details_button = self.ui.signalDetailsButton
        self.details_button.clicked.connect(self.open_details)

        self.reload()


class MessageDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.get_name, node.set_name),
            (ui.idEdit, node.get_id, node.set_id),
            (ui.dlcEdit, node.get_dlc, node.set_dlc),
            (ui.frequencyEdit, node.get_frequency, node.set_frequency),
            (ui.descriptionEdit, node.get_description, node.set_description),
        ]

    def __init__(self, gui, node: "Message", parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_MessageDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        for sig in self.node.signals.values():
            self.add_node(sig)

        self.ui.deleteMessageButton.clicked.connect(self.delete)
        self.ui.addButton.clicked.connect(self.add_node)

        self.reload()
        self.setVisible(False)

    def add_node(self, node=None):
        if node == None or node == False:
            node = Signal(self.node)

        self.node.signals[node.name] = node
        s = SignalWidget(self.gui, node, SignalDetails, self.gui.ui.signalDetailsLayout)
        self.ui.verticalLayout_2.addWidget(s)
        self.children.append(s)


class MessageWidget(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.id, node.get_id, node.set_id),
            (ui.name, node.get_name, node.set_name),
            (ui.dlc, node.get_dlc, node.set_dlc),
            (ui.frequency, node.get_frequency, node.set_frequency),
        ]

    def __init__(self, gui, node: "Message", details=None, layout=None):
        NodeDetails.__init__(self, gui, node, details=details, layout=layout)
        self.ui = Ui_MessageWidget()
        self.ui.setupUi(self)

        self.load_atts(self.ui, self.node)
        self.reload()

        self.details_button = self.ui.messageDetailsButton
        self.details_button.clicked.connect(self.open_details)


class ArgDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.get_name, node.set_name),
            (ui.commentEdit, node.get_comment, node.set_comment),
            (ui.idEdit, node.get_id, node.set_id),
        ]

    def __init__(self, gui, node: "Argument", parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_CmdArg()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.deleteArgButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)


class CmdDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (self.ui.nameEdit, node.get_name, node.set_name),
            (self.ui.n_argsEdit, node.get_n_args, node.set_n_args),
            (self.ui.commentEdit, node.get_comment, node.set_comment),
            (self.ui.idEdit, node.get_id, node.set_id),
        ]

    def __init__(self, gui, node, parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_CmdDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.deleteCmdButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)

        self.ui.addArgButton.clicked.connect(self.add_arg)

        for arg in node.args.values():
            self.add_arg(arg)

    def add_arg(self, arg=None):
        if arg == None or arg == False:
            arg = Argument()

        self.node.args[arg.name] = arg
        arg_widget = ArgDetails(self.gui, arg, FakeParent())
        self.children.append(arg_widget)
        self.ui.CmdArgContents.addWidget(arg_widget)


class CmdWidget(QWidget):
    def __init__(self, gui, parent):
        QWidget.__init__(self)
        self.ui = Ui_CmdWidget()
        self.ui.setupUi(self)

        self.setVisible(False)

        self.parent = parent

        self.gui = gui

        self.details_button = None

        self.children = []

        self.ui.addCmdButton.clicked.connect(self.add_cmd)
        for cmd in self.parent.cmds.values():
            self.add_cmd(cmd)

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def reload(self):
        for child in self.children:
            child.reload()

    def add_cmd(self, cmd=None):
        if not cmd:
            cmd = Command()

        self.parent.cmds[cmd.name] = cmd
        cmd_details = CmdDetails(self.gui, cmd, FakeParent())
        self.ui.CmdScrollContents.addWidget(cmd_details)
        self.children.append(cmd_details)

    def open_details(self, checked):
        for child in self.children:
            child.open_details(False)
            if not child.details_button is None:
                child.details_button.setChecked(False)


class CfgDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.get_name, node.set_name),
            (ui.idEdit, node.get_id, node.set_id),
            (ui.commentEdit, node.get_comment, node.set_comment),
        ]

    def __init__(self, gui, node, parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_CfgDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.deleteCfgButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)


class CfgWidget(QWidget):
    def __init__(self, gui, parent):
        QWidget.__init__(self)
        self.ui = Ui_CfgWidget()
        self.ui.setupUi(self)

        self.setVisible(False)

        self.parent = parent

        self.gui = gui

        self.ui.addCfgButton.clicked.connect(self.add_cfg)

        self.children = []

        self.details_button = None

        for cfg in self.parent.cfgs.values():
            self.add_cfg(cfg)

    def open_details(self, checked):
        for child in self.children:
            child.open_details(False)
            if not child.details_button is None:
                child.details_button.setChecked(False)

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def reload(self):
        for child in self.children:
            child.reload()

    def add_cfg(self, cfg=None):
        if not cfg:
            cfg = Config()

        self.parent.cfgs[cfg.name] = cfg
        cfg_details = CfgDetails(self.gui, cfg, FakeParent())
        self.ui.CfgScrollContents.addWidget(cfg_details)
        self.children.append(cfg_details)


class DeviceDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.idEdit, node.get_id, node.set_id),
            (ui.nameEdit, node.get_name, node.set_name),
        ]

    def __init__(self, gui, node: "Device", parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_DeviceDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, self.node)
        self.connect_atts()

        self.children = []

        self.cfg_widget = CfgWidget(self.gui, self.node)
        self.children.append(self.cfg_widget)
        self.ui.cfgDetails.addWidget(self.cfg_widget)

        self.cmd_widget = CmdWidget(self.gui, self.node)
        self.children.append(self.cmd_widget)
        self.ui.cmdDetails.addWidget(self.cmd_widget)

        self.ui.addButton.clicked.connect(self.add_node)
        self.ui.cfgsButton.clicked.connect(self.open_cfg)
        self.ui.cmdsButton.clicked.connect(self.open_cmd)

        for msg in self.node.msgs.values():
            self.add_node(msg)

        self.ui.deleteDeviceButton.clicked.connect(self.delete)

        self.reload()

        self.setVisible(False)

    def open_cfg(self, clicked):
        self.cfg_widget.setVisible(clicked)
        return

    def open_cmd(self, clicked):
        self.cmd_widget.setVisible(clicked)
        return

    def add_node(self, node=None):
        if node == None or node == False:
            node = Message(self.node)

        self.node.msgs[node.name] = node
        m = MessageWidget(
            self.gui, node, MessageDetails, self.gui.ui.messageDetailsLayout
        )
        self.ui.verticalLayout.addWidget(m)
        self.children.append(m)


class DeviceWidget(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.id, node.get_id, node.set_id),
            (ui.name, node.get_name, node.set_name),
        ]

    def __init__(self, gui, node, details=None, layout=None):
        NodeDetails.__init__(self, gui, node, details=details, layout=layout)

        self.ui = Ui_DeviceWidget()
        self.ui.setupUi(self)

        self.load_atts(self.ui, self.node)
        self.reload()

        self.children = []

        self.details_button = self.ui.deviceDetailsButton
        self.details_button.clicked.connect(self.open_details)


class EnumValueDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.valueEdit, node.get_value, node.set_value),
            (ui.nameEdit, node.get_name, node.set_name),
        ]

    def __init__(self, gui, node, parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_EnumValue()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.enumDeleteButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)

        self.children = []


class EnumDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.get_name, node.set_name),
        ]

    def __init__(self, gui, node, parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_EnumDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.enumDeleteButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)

        self.children = []

        self.ui.valueAddButton.clicked.connect(self.add_value)

        for enum_value in node.enumeration.values():
            self.add_value(enum_value)

    def add_value(self, enum_value=None):
        if enum_value == None or enum_value == False:
            enum_value = EnumValue(self.node)
            self.node.enumeration[enum_value.name] = enum_value

        enum_widget = EnumValueDetails(self.gui, enum_value, FakeParent())
        self.children.append(enum_widget)
        self.ui.EnumValueContents.addWidget(enum_widget)

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()


class LogDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.idEdit, node.get_id, node.set_id),
            (ui.nameEdit, node.get_name, node.set_name),
            (ui.n_argsEdit, node.get_n_args, node.set_n_args),
            (ui.commentEdit, node.get_comment, node.set_comment),
            (ui.stringEdit, node.get_string, node.set_string),
        ]

    def __init__(self, gui, node, parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_LogDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.logDeleteButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)

        self.children = []


class LogWidget(QWidget):
    def __init__(self, gui, parent):
        self.Window = True
        QWidget.__init__(self)
        self.ui = Ui_LogWidget()
        self.ui.setupUi(self)

        self.parent = parent
        self.gui = gui

        self.atts = []

        self.children = []

        self.reload()

        self.details = None

        self.ui.addLogButton.clicked.connect(self.add_log)
        for log in self.parent.logs.values():
            self.add_log(log)

    def reload(self):
        return

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def add_log(self, log=None):
        if log == None or log == False:
            log = Log(self.parent)

        self.parent.logs[log.name] = log
        log_widget = LogDetails(self.gui, log, FakeParent())
        self.ui.logContents.addWidget(log_widget)
        self.children.append(log_widget)


class EnumWidget(QWidget):
    def __init__(self, gui, parent):
        self.Window = True
        QWidget.__init__(self)
        self.ui = Ui_EnumWidget()
        self.ui.setupUi(self)

        self.parent = parent
        self.gui = gui

        self.atts = []

        self.children = []

        self.reload()

        self.details = None

        self.ui.addEnumButton.clicked.connect(self.add_enum)
        for enum in self.parent.enums.values():
            self.add_enum(enum)

    def reload(self):
        for child in self.children:
            child.reload()

        for att, get_f, set_f in self.atts:
            att.setText(str(get_f()))

        return

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def add_enum(self, enum=None):
        if enum == None or enum == False:
            enum = Enum()
        self.parent.enums[enum.name] = enum
        enum_widget = EnumDetails(self.gui, enum, FakeParent())
        self.ui.enumContents.addWidget(enum_widget)
        self.children.append(enum_widget)


class Gui(QMainWindow):
    def __init__(self, logger):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.logger = logger

        self.spec = Spec()
        self.children = []

        self.connect_buttons()
        self.config_shortcuts()

        self.log_widget = None
        self.enum_widget = None

        self.file_path = Path("")

        menu = QMenu("recent_files")
        try:
            with open(".fcp_gui.yaml") as f:
                y = yaml.safe_load(f.read())
                for f in y.get("recent_files"):
                    action = menu.addAction(f)
                    action.triggered.connect(lambda: self.load_json(f))

        except Exception as e:
            pass

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

    def config_shortcuts(self):
        shortcutSave = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        shortcutSave.setContext(Qt.ApplicationShortcut)
        shortcutSave.activated.connect(self.save_json)

        shortcutOpen = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_O), self)
        shortcutOpen.setContext(Qt.ApplicationShortcut)
        shortcutOpen.activated.connect(self.open_json)

    def validate(self):
        msg = QMessageBox(self)
        msg.setStandardButtons(QMessageBox.Ok)
        failed = validate(self.logger, "{}", self.spec)
        if len(failed) == 0:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Spec passed")
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText("\n".join(failed))

        msg.show()

    def add_device(self, device=None):
        if type(device) != Device and type(device) != Common:
            device = Device(parent=self.spec, id=0, name="", msgs={})

            r = self.spec.add_device(device)
            if r == False:
                self.logger.error("Failed to create device")
                return

        dev_widget = DeviceWidget(
            self, device, details=DeviceDetails, layout=self.ui.deviceDetailsLayout
        )
        self.ui.verticalLayout.addWidget(dev_widget)
        self.children.append(dev_widget)

    def open_json(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Open JSON"), self.tr("JSON (*.json)")
        )
        self.load_json(filename[0])

    def save_json(self):
        for child in self.children:
            child.save()

        self.validate()

        try:
            filename = QFileDialog.getSaveFileName(
                self, self.tr("Open JSON"), str(self.file_path.parent)
            )
        except Exception as e:
            msg = QMessageBox(self)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"{filename} is not a valid filename")
            msg.show()
            return

        with open(filename[0], "w") as f:
            j = self.spec.compile()
            f.write(json.dumps(j, indent=4))

    def load_json(self, filename):
        if filename == "":
            msg = QMessageBox(self)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Warning)
            msg.setText(f"'{filename}' is not a valid filename")
            msg.show()
            return

        try:
            with open(".fcp_gui.yaml") as f:
                y = yaml.safe_load(f.read())

            if filename not in y["recent_files"]:
                y["recent_files"].append(filename)
        except Exception as e:
            y = {}
            y["recent_files"] = []

        with open(".fcp_gui.yaml", "w") as f:
            f.write(yaml.dump(y))

        with open(filename) as f:
            j = json.loads(f.read())

        self.spec.decompile(j)

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

        self.file_path = Path(filename)

    def reload(self):
        for node in self.children:
            node.reload()

        self.spec.normalize()


def gui(file, logger):
    app = QApplication([])
    window = Gui(logger)
    if file != None and file != "":
        window.load_json(file)
    window.show()
    sys.exit(app.exec_())
