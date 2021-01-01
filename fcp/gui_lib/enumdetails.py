# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'enumdetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_EnumDetails(object):
    def setupUi(self, EnumDetails):
        if not EnumDetails.objectName():
            EnumDetails.setObjectName(u"EnumDetails")
        EnumDetails.resize(418, 288)
        self.verticalLayout = QVBoxLayout(EnumDetails)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.nameLabel = QLabel(EnumDetails)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout_2.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(EnumDetails)
        self.nameEdit.setObjectName(u"nameEdit")

        self.horizontalLayout_2.addWidget(self.nameEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.enumContents = QScrollArea(EnumDetails)
        self.enumContents.setObjectName(u"enumContents")
        self.enumContents.setWidgetResizable(True)
        self._EnumValueContents = QWidget()
        self._EnumValueContents.setObjectName(u"_EnumValueContents")
        self._EnumValueContents.setGeometry(QRect(0, 0, 396, 204))
        self.verticalLayout_4 = QVBoxLayout(self._EnumValueContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.EnumValueContents = QVBoxLayout()
        self.EnumValueContents.setObjectName(u"EnumValueContents")

        self.verticalLayout_4.addLayout(self.EnumValueContents)

        self.enumContents.setWidget(self._EnumValueContents)

        self.verticalLayout_2.addWidget(self.enumContents)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.enumDeleteButton = QPushButton(EnumDetails)
        self.enumDeleteButton.setObjectName(u"enumDeleteButton")

        self.horizontalLayout.addWidget(self.enumDeleteButton)

        self.valueAddButton = QPushButton(EnumDetails)
        self.valueAddButton.setObjectName(u"valueAddButton")

        self.horizontalLayout.addWidget(self.valueAddButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(EnumDetails)

        QMetaObject.connectSlotsByName(EnumDetails)
    # setupUi

    def retranslateUi(self, EnumDetails):
        EnumDetails.setWindowTitle(QCoreApplication.translate("EnumDetails", u"EnumValue", None))
        self.nameLabel.setText(QCoreApplication.translate("EnumDetails", u"name", None))
        self.enumDeleteButton.setText(QCoreApplication.translate("EnumDetails", u"Delete", None))
        self.valueAddButton.setText(QCoreApplication.translate("EnumDetails", u"Add Value", None))
    # retranslateUi

