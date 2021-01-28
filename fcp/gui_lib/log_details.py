from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.logdetails import Ui_LogDetails
from .node_details import NodeDetails, FakeParent


class LogDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.idEdit, node.id, "id"),
            (ui.nameEdit, node.name, "name"),
            (ui.n_argsEdit, node.n_args, "n_args"),
            (ui.commentEdit, node.comment, "comment"),
            (ui.stringEdit, node.string, "string"),
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
