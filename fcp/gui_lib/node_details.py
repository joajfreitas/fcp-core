from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt, Signal

from .undo_redo import UndoRedo, UndoState, UndoUpdate


class FakeParent:
    def __init__(self):
        return

    def setVisible(self, visibility: bool):
        return


class NodeDetails(QWidget):
    """ Node (Device, Message, Signal, Log, Config, Command) interface """

    reload_sig = Signal(str)

    def __init__(self, gui, node, parent=None, details=None, layout=None):
        QWidget.__init__(self)
        self.node = node
        self.gui = gui
        self.parent = parent
        self.atts = []
        self.details = None
        self.Details = details
        self.layout = layout
        self.children = []
        self.details_button = None
        self.reload_sig.connect(self.gui.reload_service)

    def load_atts(self, ui, node):
        self.atts = []
        return

    def connect_atts(self):
        def store(obj, var, att):
            def closure():
                old = getattr(obj,var)
                value = type(old)(att.text())
                setattr(obj, "_" + var, value)

                self.gui.undo_redo.push(UndoUpdate(obj, var, old, att.text()))
                self.gui.reload()
                self.reload_sig.emit("")

            return closure

        for att, var, var_name in self.atts:
            att.editingFinished.connect(store(self.node, var_name, att))

    def save(self):
        for child in self.children:
            child.save()

        for att, var, var_name in self.atts:
            var = att.text()

        self.gui.reload()

    def delete(self):
        r = self.gui.spec.rm_node(self.node)
        self.setVisible(False)
        if self.parent:
            self.parent.setVisible(False)

        if self.details:
            self.details.setVisible(False)
        return

    def reload(self):
        for child in self.children:
            child.reload()

        for att, var, var_name in self.atts:
            att.setText(str(getattr(self.node, var_name)))

    def raise_widget(self, checked):
        self.setVisible(checked)

    def open_details(self, checked):
        if checked == False:
            for child in self.children:
                child.open_details(False)
                if child.details_button is not None:
                    child.details_button.setChecked(False)

        if self.details_button is None:
            return

        if self.details is None:
            self.details = self.Details(self.gui, self.node, self)
            self.layout.addWidget(self.details)
            self.children.append(self.details)

        self.details.setVisible(checked)

    def show(self):
        if self.parent:
            self.parent.setVisible(True)

        if self.details:
            self.details.setVisible(True)
            self.details_button.setFlat(False)

        self.setVisible(True)
