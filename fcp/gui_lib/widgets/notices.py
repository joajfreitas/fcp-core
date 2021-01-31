# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'notices.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Notices(object):
    def setupUi(self, Notices):
        if not Notices.objectName():
            Notices.setObjectName(u"Notices")
        Notices.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Notices)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.top_label = QLabel(Notices)
        self.top_label.setObjectName(u"top_label")

        self.verticalLayout.addWidget(self.top_label)

        self.label = QLabel(Notices)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.buttonBox = QDialogButtonBox(Notices)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Notices)

        QMetaObject.connectSlotsByName(Notices)
    # setupUi

    def retranslateUi(self, Notices):
        Notices.setWindowTitle(QCoreApplication.translate("Notices", u"Form", None))
        self.top_label.setText("")
        self.label.setText("")
    # retranslateUi

