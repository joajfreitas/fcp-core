from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.logwidget import Ui_LogWidget
from .node_details import NodeDetails, FakeParent
from .log_details import LogDetails

from .undo_redo import UndoAdd

from ..specs import Log


class LogWidget(QWidget):
    def __init__(self, gui, parent):
        self.Window = True
        QWidget.__init__(self)
        self.ui = Ui_LogWidget()
        self.ui.setupUi(self)

        self.parent = parent
        self.gui = gui

        self.atts = []

        self.children = []

        self.reload()

        self.details = None

        self.ui.addLogButton.clicked.connect(self.add_log)
        logs = [log for log in self.parent.logs.values()]
        for log in logs:
            self.add_log(log)

    def reload(self):
        return

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def add_log(self, log=None):
        new_log = log is None or type(log) is bool
        if log == None or log == False:
            log = Log(self.parent)

        self.parent.logs[log.name] = log
        log_widget = LogDetails(self.gui, log, FakeParent())
        self.ui.logContents.addWidget(log_widget)
        self.children.append(log_widget)
        
        if new_log:
            undo_action = UndoAdd(log, log_widget, log_widget.delete, self.add_log)
            self.gui.undo_redo.push(undo_action)
