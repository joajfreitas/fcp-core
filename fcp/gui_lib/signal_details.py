from .node_details import NodeDetails, FakeParent
from .widgets.signaldetails import Ui_SignalDetails


class SignalDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (ui.nameEdit, node.name, "name"),
            (ui.startEdit, node.start, "start"),
            (ui.lengthEdit, node.length, "length"),
            (ui.muxEdit, node.mux, "mux"),
            (ui.muxCountEdit, node.mux_count, "mux_count"),
            (ui.typeEdit, node.type, "type"),
            (ui.commentEdit, node.comment, "comment"),
            (ui.minValueEdit, node.min_value, "min_value"),
            (ui.maxValueEdit, node.max_value, "max_value"),
            (ui.byteOrderEdit, node.byte_order, "byte_order"),
            (ui.scaleEdit, node.scale, "scale"),
            (ui.offsetEdit, node.offset, "offset"),
            (ui.aliasEdit, node.alias, "alias"),
        ]

    def __init__(self, gui, node: "Signal", parent):
        NodeDetails.__init__(self, gui, node, parent)

        ui = self.ui = Ui_SignalDetails()
        self.ui.setupUi(self)

        self.load_atts(ui, node)
        self.connect_atts()

        self.ui.signalDeleteButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(False)

        self.children = []
