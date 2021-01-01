# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'enumwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_EnumWidget(object):
    def setupUi(self, EnumWidget):
        if not EnumWidget.objectName():
            EnumWidget.setObjectName(u"EnumWidget")
        EnumWidget.resize(400, 300)
        self.verticalLayout = QVBoxLayout(EnumWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(EnumWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.LogScrollContents = QWidget()
        self.LogScrollContents.setObjectName(u"LogScrollContents")
        self.LogScrollContents.setGeometry(QRect(0, 0, 368, 208))
        self.verticalLayout_2 = QVBoxLayout(self.LogScrollContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.enumContents = QVBoxLayout()
        self.enumContents.setObjectName(u"enumContents")

        self.verticalLayout_2.addLayout(self.enumContents)

        self.scrollArea.setWidget(self.LogScrollContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.addEnumButton = QPushButton(self.groupBox)
        self.addEnumButton.setObjectName(u"addEnumButton")

        self.verticalLayout_3.addWidget(self.addEnumButton)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(EnumWidget)

        QMetaObject.connectSlotsByName(EnumWidget)
    # setupUi

    def retranslateUi(self, EnumWidget):
        EnumWidget.setWindowTitle(QCoreApplication.translate("EnumWidget", u"EnumWidget", None))
        self.groupBox.setTitle(QCoreApplication.translate("EnumWidget", u"Enums", None))
        self.addEnumButton.setText(QCoreApplication.translate("EnumWidget", u"Add Enums", None))
    # retranslateUi

