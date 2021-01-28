from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.messagewidget import Ui_MessageWidget
from .node_details import NodeDetails, FakeParent


class MessageWidget(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.id, node.id, "id"),
            (ui.name, node.name, "name"),
            (ui.dlc, node.dlc, "dlc"),
            (ui.frequency, node.frequency, "frequency"),
        ]

    def __init__(self, gui, node: "Message", details=None, layout=None):
        NodeDetails.__init__(self, gui, node, details=details, layout=layout)
        self.ui = Ui_MessageWidget()
        self.ui.setupUi(self)

        self.load_atts(self.ui, self.node)
        self.reload()

        self.details_button = self.ui.messageDetailsButton
        self.details_button.clicked.connect(self.open_details)

        self.button_button = self.ui.deleteButton
        self.button_button.clicked.connect(self.delete)
