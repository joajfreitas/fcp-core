from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.cmdarg import Ui_CmdArg
from .node_details import NodeDetails, FakeParent


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
