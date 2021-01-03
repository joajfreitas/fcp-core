from PySide2.QtWidgets import *
from PySide2.QtCore import Signal

from ..gui_lib.devicedetails import Ui_DeviceDetails

class DeviceDetails(QWidget):
    #open_device = Signal(str, bool)

    def __init__(self, dev):
        QWidget.__init__(self)
        self.ui = Ui_DeviceDetails()
        self.ui.setupUi(self)

        self.dev = dev

        self.atts = [
            (self.ui.idEdit, self.dev.id),
            (self.ui.nameEdit, self.dev.name),
        ]
        
        self.connect_ui()
        self.reload()

        #self.ui.deviceDetailsButton.clicked.connect(self.details)
        #self.ui.deleteButton.clicked.connect(self.delete)

    def connect_ui(self):
        def assign(var):
            def closure(value):
                print(var, value)
                var = value
            return closure

        for att, var in self.atts:
            att.textEdited.connect(assign(var))

    def reload(self):
        for att, var in self.atts:
            att.setText(str(var))

    #def details(self, checked):
    #    self.open_device.emit(self.dev.name, checked)

    #def delete(self):
    #    print("delete")
