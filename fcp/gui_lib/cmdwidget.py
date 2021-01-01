# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cmdwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CmdWidget(object):
    def setupUi(self, CmdWidget):
        if not CmdWidget.objectName():
            CmdWidget.setObjectName(u"CmdWidget")
        CmdWidget.resize(400, 300)
        CmdWidget.setMinimumSize(QSize(350, 0))
        self.verticalLayout = QVBoxLayout(CmdWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(CmdWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self._CmdScrollContents = QWidget()
        self._CmdScrollContents.setObjectName(u"_CmdScrollContents")
        self._CmdScrollContents.setGeometry(QRect(0, 0, 368, 208))
        self._CmdScrollContents.setMinimumSize(QSize(300, 0))
        self.verticalLayout_2 = QVBoxLayout(self._CmdScrollContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.CmdScrollContents = QVBoxLayout()
        self.CmdScrollContents.setObjectName(u"CmdScrollContents")

        self.verticalLayout_2.addLayout(self.CmdScrollContents)

        self.scrollArea.setWidget(self._CmdScrollContents)

        self.verticalLayout_4.addWidget(self.scrollArea)

        self.addCmdButton = QPushButton(self.groupBox)
        self.addCmdButton.setObjectName(u"addCmdButton")

        self.verticalLayout_4.addWidget(self.addCmdButton)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(CmdWidget)

        QMetaObject.connectSlotsByName(CmdWidget)
    # setupUi

    def retranslateUi(self, CmdWidget):
        CmdWidget.setWindowTitle(QCoreApplication.translate("CmdWidget", u"CmdWidget", None))
        self.groupBox.setTitle(QCoreApplication.translate("CmdWidget", u"Commands", None))
        self.addCmdButton.setText(QCoreApplication.translate("CmdWidget", u"Add Cmd", None))
    # retranslateUi

