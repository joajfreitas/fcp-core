# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'logwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_LogWidget(object):
    def setupUi(self, LogWidget):
        if not LogWidget.objectName():
            LogWidget.setObjectName(u"LogWidget")
        LogWidget.resize(400, 300)
        LogWidget.setMinimumSize(QSize(300, 0))
        self.verticalLayout = QVBoxLayout(LogWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(LogWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.LogScrollContents = QWidget()
        self.LogScrollContents.setObjectName(u"LogScrollContents")
        self.LogScrollContents.setGeometry(QRect(0, 0, 356, 209))
        self.verticalLayout_2 = QVBoxLayout(self.LogScrollContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.logContents = QVBoxLayout()
        self.logContents.setObjectName(u"logContents")

        self.verticalLayout_2.addLayout(self.logContents)

        self.scrollArea.setWidget(self.LogScrollContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.addLogButton = QPushButton(self.groupBox)
        self.addLogButton.setObjectName(u"addLogButton")

        self.verticalLayout_3.addWidget(self.addLogButton)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(LogWidget)

        QMetaObject.connectSlotsByName(LogWidget)
    # setupUi

    def retranslateUi(self, LogWidget):
        LogWidget.setWindowTitle(QCoreApplication.translate("LogWidget", u"LogWidget", None))
        self.groupBox.setTitle(QCoreApplication.translate("LogWidget", u"Logs", None))
        self.addLogButton.setText(QCoreApplication.translate("LogWidget", u"Add Log", None))
    # retranslateUi

