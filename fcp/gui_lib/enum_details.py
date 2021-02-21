from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.enumdetails import Ui_EnumDetails
from .node_details import NodeDetails, FakeParent
from .enum_value_details import EnumValueDetails
from ..specs import EnumValue


class EnumDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.name, "name"),
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
