from PySide2.QtWidgets import *

from ..gui_lib.devicewidget import Ui_DeviceWidget

class DeviceWidget(QWidget):
    def __init__(self, dev):
        QWidget.__init__(self)
        self.ui = Ui_DeviceWidget()
        self.ui.setupUi(self)

        self.dev = dev

        self.atts = [
            (self.ui.id, self.dev.id),
            (self.ui.name, self.dev.name),
        ]

        self.reload()

        self.ui.deviceDetailsButton.clicked.connect(self.details)
        self.ui.deleteButton.clicked.connect(self.delete)


    def reload(self):
        for att, var in self.atts:
            att.setText(str(var))

    def details(self, checked):
        print("details", checked)

    def delete(self):
        print("delete")
