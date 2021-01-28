from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

class MessageBox():
    def __init__(self, parent, buttons, icon, text):
        self.msg = QMessageBox(parent)
        self.msg.setStandardButtons(buttons)
        self.msg.setIcon(icon)
        self.msg.setText(text)

    def launch(self):
        self.msg.show()

