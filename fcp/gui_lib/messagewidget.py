# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'messagewidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MessageWidget(object):
    def setupUi(self, MessageWidget):
        if not MessageWidget.objectName():
            MessageWidget.setObjectName(u"MessageWidget")
        MessageWidget.resize(388, 92)
        self.horizontalLayout = QHBoxLayout(MessageWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(MessageWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.name = QLabel(self.groupBox)
        self.name.setObjectName(u"name")

        self.horizontalLayout_2.addWidget(self.name)

        self.id = QLabel(self.groupBox)
        self.id.setObjectName(u"id")

        self.horizontalLayout_2.addWidget(self.id)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.dlc = QLabel(self.groupBox)
        self.dlc.setObjectName(u"dlc")

        self.horizontalLayout_3.addWidget(self.dlc)

        self.frequency = QLabel(self.groupBox)
        self.frequency.setObjectName(u"frequency")

        self.horizontalLayout_3.addWidget(self.frequency)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_4.addLayout(self.verticalLayout)

        self.deleteButton = QPushButton(self.groupBox)
        self.deleteButton.setObjectName(u"deleteButton")
        self.deleteButton.setMaximumSize(QSize(25, 25))

        self.horizontalLayout_4.addWidget(self.deleteButton)

        self.messageDetailsButton = QPushButton(self.groupBox)
        self.messageDetailsButton.setObjectName(u"messageDetailsButton")
        self.messageDetailsButton.setMaximumSize(QSize(60, 25))
        self.messageDetailsButton.setCheckable(True)

        self.horizontalLayout_4.addWidget(self.messageDetailsButton)


        self.horizontalLayout.addWidget(self.groupBox)


        self.retranslateUi(MessageWidget)

        QMetaObject.connectSlotsByName(MessageWidget)
    # setupUi

    def retranslateUi(self, MessageWidget):
        MessageWidget.setWindowTitle(QCoreApplication.translate("MessageWidget", u"MessageWidget", None))
        self.groupBox.setTitle("")
        self.name.setText("")
        self.id.setText("")
        self.dlc.setText("")
        self.frequency.setText("")
        self.deleteButton.setText(QCoreApplication.translate("MessageWidget", u"\u2717", None))
        self.messageDetailsButton.setText(QCoreApplication.translate("MessageWidget", u"...", None))
    # retranslateUi

