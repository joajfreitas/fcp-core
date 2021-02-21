from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt


from .node_details import FakeParent
from .widgets.enumwidget import Ui_EnumWidget
from .enum_details import EnumDetails

from ..specs import Enum


class EnumWidget(QWidget):
    def __init__(self, gui, parent):
        self.Window = True
        QWidget.__init__(self)
        self.ui = Ui_EnumWidget()
        self.ui.setupUi(self)

        self.parent = parent
        self.gui = gui

        self.atts = []

        self.children = []

        self.reload()

        self.details = None

        self.ui.addEnumButton.clicked.connect(self.add_enum)
        for enum in self.parent.enums.values():
            self.add_enum(enum)

    def reload(self):
        for child in self.children:
            child.reload()

        for att, get_f, set_f in self.atts:
            att.setText(str(get_f()))

        return

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def add_enum(self, enum=None):
        if enum == None or enum == False:
            enum = Enum()
        self.parent.enums[enum.name] = enum
        enum_widget = EnumDetails(self.gui, enum, FakeParent())
        self.ui.enumContents.addWidget(enum_widget)
        self.children.append(enum_widget)
