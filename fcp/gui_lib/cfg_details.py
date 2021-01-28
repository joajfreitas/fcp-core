from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.cfgdetails import Ui_CfgDetails
from .node_details import NodeDetails, FakeParent


class CfgDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.name, "name"),
            (ui.idEdit, node.id, "id"),
            (ui.commentEdit, node.comment, "comment"),
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
