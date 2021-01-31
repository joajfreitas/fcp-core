# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'devicedetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DeviceDetails(object):
    def setupUi(self, DeviceDetails):
        if not DeviceDetails.objectName():
            DeviceDetails.setObjectName(u"DeviceDetails")
        DeviceDetails.resize(404, 382)
        self.verticalLayout_2 = QVBoxLayout(DeviceDetails)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(DeviceDetails)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName(u"nameEdit")

        self.horizontalLayout.addWidget(self.nameEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.idLabel = QLabel(self.groupBox)
        self.idLabel.setObjectName(u"idLabel")

        self.horizontalLayout_2.addWidget(self.idLabel)

        self.idEdit = QLineEdit(self.groupBox)
        self.idEdit.setObjectName(u"idEdit")

        self.horizontalLayout_2.addWidget(self.idEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.messageContents = QWidget()
        self.messageContents.setObjectName(u"messageContents")
        self.messageContents.setGeometry(QRect(0, 0, 352, 202))
        self.verticalLayout = QVBoxLayout(self.messageContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea.setWidget(self.messageContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.addButton = QPushButton(self.groupBox)
        self.addButton.setObjectName(u"addButton")

        self.horizontalLayout_5.addWidget(self.addButton)

        self.deleteDeviceButton = QPushButton(self.groupBox)
        self.deleteDeviceButton.setObjectName(u"deleteDeviceButton")

        self.horizontalLayout_5.addWidget(self.deleteDeviceButton)

        self.cmdsButton = QPushButton(self.groupBox)
        self.cmdsButton.setObjectName(u"cmdsButton")
        self.cmdsButton.setCheckable(True)

        self.horizontalLayout_5.addWidget(self.cmdsButton)

        self.cfgsButton = QPushButton(self.groupBox)
        self.cfgsButton.setObjectName(u"cfgsButton")
        self.cfgsButton.setCheckable(True)

        self.horizontalLayout_5.addWidget(self.cfgsButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        self.cfgDetails = QVBoxLayout()
        self.cfgDetails.setObjectName(u"cfgDetails")

        self.horizontalLayout_3.addLayout(self.cfgDetails)

        self.cmdDetails = QVBoxLayout()
        self.cmdDetails.setObjectName(u"cmdDetails")

        self.horizontalLayout_3.addLayout(self.cmdDetails)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)


        self.verticalLayout_2.addWidget(self.groupBox)


        self.retranslateUi(DeviceDetails)

        QMetaObject.connectSlotsByName(DeviceDetails)
    # setupUi

    def retranslateUi(self, DeviceDetails):
        DeviceDetails.setWindowTitle(QCoreApplication.translate("DeviceDetails", u"DeviceDetails", None))
        self.groupBox.setTitle(QCoreApplication.translate("DeviceDetails", u"Device", None))
        self.nameLabel.setText(QCoreApplication.translate("DeviceDetails", u"name", None))
        self.idLabel.setText(QCoreApplication.translate("DeviceDetails", u"id", None))
        self.addButton.setText(QCoreApplication.translate("DeviceDetails", u"Add", None))
        self.deleteDeviceButton.setText(QCoreApplication.translate("DeviceDetails", u"Delete", None))
        self.cmdsButton.setText(QCoreApplication.translate("DeviceDetails", u"Cmds", None))
        self.cfgsButton.setText(QCoreApplication.translate("DeviceDetails", u"Cfgs", None))
    # retranslateUi

