from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.cmddetails import Ui_CmdDetails
from .node_details import NodeDetails, FakeParent
from .arg_details import ArgDetails

from ..specs import Argument


class CmdDetails(NodeDetails):
    def load_atts(self, ui, node):
        self.atts = [
            (self.ui.nameEdit, node.name, "name"),
            (self.ui.n_argsEdit, node.n_args, "n_args"),
            (self.ui.commentEdit, node.comment, "comment"),
            (self.ui.idEdit, node.id, "id"),
        ]

    def __init__(self, gui, node, parent):
        NodeDetails.__init__(self, gui, node, parent)

        self.ui = Ui_CmdDetails()
        self.ui.setupUi(self)

        self.load_atts(self.ui, node)
        self.connect_atts()

        self.ui.deleteCmdButton.clicked.connect(self.delete)

        self.reload()
        self.setVisible(True)

        self.ui.addArgButton.clicked.connect(self.add_arg)

        for arg in node.args.values():
            self.add_arg(arg)

    def add_arg(self, arg=None):
        if arg == None or arg == False:
            arg = Argument(self.parent)

        self.node.args[arg.name] = arg
        arg_widget = ArgDetails(self.gui, arg, FakeParent())
        self.children.append(arg_widget)
        self.ui.CmdArgContents.addWidget(arg_widget)
