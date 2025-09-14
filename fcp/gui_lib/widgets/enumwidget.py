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
            EnumWidget.setObjectName("EnumWidget")
        EnumWidget.resize(400, 300)
        self.verticalLayout = QVBoxLayout(EnumWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QGroupBox(EnumWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.LogScrollContents = QWidget()
        self.LogScrollContents.setObjectName("LogScrollContents")
        self.LogScrollContents.setGeometry(QRect(0, 0, 368, 208))
        self.verticalLayout_2 = QVBoxLayout(self.LogScrollContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.enumContents = QVBoxLayout()
        self.enumContents.setObjectName("enumContents")

        self.verticalLayout_2.addLayout(self.enumContents)

        self.scrollArea.setWidget(self.LogScrollContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.addEnumButton = QPushButton(self.groupBox)
        self.addEnumButton.setObjectName("addEnumButton")

        self.verticalLayout_3.addWidget(self.addEnumButton)

        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(EnumWidget)

        QMetaObject.connectSlotsByName(EnumWidget)

    # setupUi

    def retranslateUi(self, EnumWidget):
        EnumWidget.setWindowTitle(
            QCoreApplication.translate("EnumWidget", "EnumWidget", None)
        )
        self.groupBox.setTitle(QCoreApplication.translate("EnumWidget", "Enums", None))
        self.addEnumButton.setText(
            QCoreApplication.translate("EnumWidget", "Add Enums", None)
        )

    # retranslateUi
