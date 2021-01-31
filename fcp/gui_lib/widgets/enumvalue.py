# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'enumvalue.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_EnumValue(object):
    def setupUi(self, EnumValue):
        if not EnumValue.objectName():
            EnumValue.setObjectName(u"EnumValue")
        EnumValue.resize(400, 85)
        self.verticalLayout = QVBoxLayout(EnumValue)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(EnumValue)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout_2.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName(u"nameEdit")

        self.horizontalLayout_2.addWidget(self.nameEdit)

        self.valueLabel = QLabel(self.groupBox)
        self.valueLabel.setObjectName(u"valueLabel")

        self.horizontalLayout_2.addWidget(self.valueLabel)

        self.valueEdit = QLineEdit(self.groupBox)
        self.valueEdit.setObjectName(u"valueEdit")

        self.horizontalLayout_2.addWidget(self.valueEdit)

        self.enumDeleteButton = QPushButton(self.groupBox)
        self.enumDeleteButton.setObjectName(u"enumDeleteButton")

        self.horizontalLayout_2.addWidget(self.enumDeleteButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(EnumValue)

        QMetaObject.connectSlotsByName(EnumValue)
    # setupUi

    def retranslateUi(self, EnumValue):
        EnumValue.setWindowTitle(QCoreApplication.translate("EnumValue", u"EnumDetails", None))
        self.groupBox.setTitle("")
        self.nameLabel.setText(QCoreApplication.translate("EnumValue", u"name", None))
        self.valueLabel.setText(QCoreApplication.translate("EnumValue", u"value", None))
        self.enumDeleteButton.setText(QCoreApplication.translate("EnumValue", u"Delete", None))
    # retranslateUi

