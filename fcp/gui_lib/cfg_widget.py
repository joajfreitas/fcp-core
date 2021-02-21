from PySide2.QtWidgets import *
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt

from .widgets.cfgwidget import Ui_CfgWidget
from .cfg_details import CfgDetails
from .node_details import NodeDetails, FakeParent

from ..specs import Config


class CfgWidget(QWidget):
    def __init__(self, gui, parent):
        QWidget.__init__(self)
        self.ui = Ui_CfgWidget()
        self.ui.setupUi(self)

        self.setVisible(False)

        self.parent = parent

        self.gui = gui

        self.ui.addCfgButton.clicked.connect(self.add_cfg)

        self.children = []

        self.details_button = None

        for cfg in self.parent.cfgs.values():
            self.add_cfg(cfg)

    def open_details(self, checked):
        for child in self.children:
            child.open_details(False)
            if not child.details_button is None:
                child.details_button.setChecked(False)

    def save(self):
        for child in self.children:
            child.save()

        self.gui.reload()

    def reload(self):
        for child in self.children:
            child.reload()

    def add_cfg(self, cfg=None):
        if not cfg:
            cfg = Config()

        self.parent.cfgs[cfg.name] = cfg
        cfg_details = CfgDetails(self.gui, cfg, FakeParent())
        self.ui.CfgScrollContents.addWidget(cfg_details)
        self.children.append(cfg_details)
