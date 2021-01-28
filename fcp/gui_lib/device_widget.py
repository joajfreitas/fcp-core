from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.devicewidget import Ui_DeviceWidget
from .node_details import NodeDetails, FakeParent


class DeviceWidget(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.id, node.id, "id"),
            (ui.name, node.name, "name"),
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

        self.delete_button = self.ui.deleteButton
        self.delete_button.clicked.connect(self.delete)
