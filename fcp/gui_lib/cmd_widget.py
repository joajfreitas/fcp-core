from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.cmdwidget import Ui_CmdWidget
from .node_details import NodeDetails, FakeParent
from .cmd_details import CmdDetails

from ..specs import Command


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
            cmd = Command(self.parent)

        self.parent.cmds[cmd.name] = cmd
        cmd_details = CmdDetails(self.gui, cmd, FakeParent())
        self.ui.CmdScrollContents.addWidget(cmd_details)
        self.children.append(cmd_details)

    def open_details(self, checked):
        for child in self.children:
            child.open_details(False)
            if not child.details_button is None:
                child.details_button.setChecked(False)
