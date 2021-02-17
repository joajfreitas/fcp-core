from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.messagedetails import Ui_MessageDetails
from .node_details import NodeDetails, FakeParent

from .signal_widget import SignalWidget
from .signal_details import SignalDetails

from ..specs import *


class MessageDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.name, "name"),
            (ui.idEdit, node.id, "id"),
            (ui.dlcEdit, node.dlc, "dlc"),
            (ui.frequencyEdit, node.frequency, "frequency"),
            (ui.descriptionEdit, node.description, "description"),
        ]

    def __init__(self, gui, node: "Message", parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_MessageDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()
 
        sigs = list(self.node.signals.values())
        for sig in sigs:
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
