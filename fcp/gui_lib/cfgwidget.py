# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cfgwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CfgWidget(object):
    def setupUi(self, CfgWidget):
        if not CfgWidget.objectName():
            CfgWidget.setObjectName(u"CfgWidget")
        CfgWidget.resize(400, 300)
        CfgWidget.setMinimumSize(QSize(300, 0))
        self.verticalLayout = QVBoxLayout(CfgWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(CfgWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self._CfgScrollContents = QWidget()
        self._CfgScrollContents.setObjectName(u"_CfgScrollContents")
        self._CfgScrollContents.setGeometry(QRect(0, 0, 356, 209))
        self.verticalLayout_2 = QVBoxLayout(self._CfgScrollContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.CfgScrollContents = QVBoxLayout()
        self.CfgScrollContents.setObjectName(u"CfgScrollContents")

        self.verticalLayout_2.addLayout(self.CfgScrollContents)

        self.scrollArea.setWidget(self._CfgScrollContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.addCfgButton = QPushButton(self.groupBox)
        self.addCfgButton.setObjectName(u"addCfgButton")

        self.verticalLayout_3.addWidget(self.addCfgButton)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(CfgWidget)

        QMetaObject.connectSlotsByName(CfgWidget)
    # setupUi

    def retranslateUi(self, CfgWidget):
        CfgWidget.setWindowTitle(QCoreApplication.translate("CfgWidget", u"CfgWidget", None))
        self.groupBox.setTitle(QCoreApplication.translate("CfgWidget", u"Configs", None))
        self.addCfgButton.setText(QCoreApplication.translate("CfgWidget", u"Add Cfg", None))
    # retranslateUi

