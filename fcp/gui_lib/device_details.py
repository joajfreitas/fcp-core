from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.devicedetails import Ui_DeviceDetails
from .node_details import NodeDetails, FakeParent
from .cfg_widget import CfgWidget
from .cmd_widget import CmdWidget
from .message_widget import MessageWidget
from .message_details import MessageDetails

from .undo_redo import UndoAdd

from ..specs import *


class DeviceDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.idEdit, node.id, "id"),
            (ui.nameEdit, node.name, "name"),
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


        undo_action = UndoAdd(node, m, m.delete, self.add_node)
        self.gui.undo_redo.push(undo_action)
