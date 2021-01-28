from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.signalwidget import Ui_SignalWidget

from .node_details import NodeDetails


class SignalWidget(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.name, node.name, "name"),
            (ui.start, node.start, "start"),
            (ui.length, node.length, "length"),
        ]

    def __init__(self, gui, node, details=None, layout=None):
        NodeDetails.__init__(self, gui, node, details=details, layout=layout)

        ui = self.ui = Ui_SignalWidget()
        self.ui.setupUi(self)

        self.load_atts(self.ui, self.node)

        self.details_button = self.ui.signalDetailsButton
        self.details_button.clicked.connect(self.open_details)

        self.delete_button = self.ui.deleteButton
        self.delete_button.clicked.connect(self.delete)

        self.reload()
