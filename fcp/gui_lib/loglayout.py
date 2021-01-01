# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loglayout.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_LogLayout(object):
    def setupUi(self, LogLayout):
        if not LogLayout.objectName():
            LogLayout.setObjectName(u"LogLayout")
        LogLayout.resize(400, 300)
        self.verticalLayout = QVBoxLayout(LogLayout)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(LogLayout)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.logContents = QWidget()
        self.logContents.setObjectName(u"logContents")
        self.logContents.setGeometry(QRect(0, 0, 380, 280))
        self.verticalLayout_2 = QVBoxLayout(self.logContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea.setWidget(self.logContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(LogLayout)

        QMetaObject.connectSlotsByName(LogLayout)
    # setupUi

    def retranslateUi(self, LogLayout):
        LogLayout.setWindowTitle(QCoreApplication.translate("LogLayout", u"LogLayout", None))
    # retranslateUi

