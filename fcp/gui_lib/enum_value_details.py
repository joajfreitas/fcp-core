from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.enumvalue import Ui_EnumValue
from .node_details import NodeDetails, FakeParent


class EnumValueDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.valueEdit, node.value, "value"),
            (ui.nameEdit, node.name, "name"),
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
