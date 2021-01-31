# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'messagedetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MessageDetails(object):
    def setupUi(self, MessageDetails):
        if not MessageDetails.objectName():
            MessageDetails.setObjectName(u"MessageDetails")
        MessageDetails.resize(342, 308)
        self.verticalLayout = QVBoxLayout(MessageDetails)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(MessageDetails)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
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

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.dlcLabel = QLabel(self.groupBox)
        self.dlcLabel.setObjectName(u"dlcLabel")

        self.horizontalLayout_3.addWidget(self.dlcLabel)

        self.dlcEdit = QLineEdit(self.groupBox)
        self.dlcEdit.setObjectName(u"dlcEdit")

        self.horizontalLayout_3.addWidget(self.dlcEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.frequencyLabel = QLabel(self.groupBox)
        self.frequencyLabel.setObjectName(u"frequencyLabel")

        self.horizontalLayout_4.addWidget(self.frequencyLabel)

        self.frequencyEdit = QLineEdit(self.groupBox)
        self.frequencyEdit.setObjectName(u"frequencyEdit")

        self.horizontalLayout_4.addWidget(self.frequencyEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.descriptionLabel = QLabel(self.groupBox)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.horizontalLayout_6.addWidget(self.descriptionLabel)

        self.descriptionEdit = QLineEdit(self.groupBox)
        self.descriptionEdit.setObjectName(u"descriptionEdit")

        self.horizontalLayout_6.addWidget(self.descriptionEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.signalContents = QWidget()
        self.signalContents.setObjectName(u"signalContents")
        self.signalContents.setGeometry(QRect(0, 0, 298, 60))
        self.verticalLayout_2 = QVBoxLayout(self.signalContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea.setWidget(self.signalContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.addButton = QPushButton(self.groupBox)
        self.addButton.setObjectName(u"addButton")

        self.horizontalLayout_5.addWidget(self.addButton)

        self.deleteMessageButton = QPushButton(self.groupBox)
        self.deleteMessageButton.setObjectName(u"deleteMessageButton")

        self.horizontalLayout_5.addWidget(self.deleteMessageButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(MessageDetails)

        QMetaObject.connectSlotsByName(MessageDetails)
    # setupUi

    def retranslateUi(self, MessageDetails):
        MessageDetails.setWindowTitle(QCoreApplication.translate("MessageDetails", u"MessageDetails", None))
        self.groupBox.setTitle(QCoreApplication.translate("MessageDetails", u"Message", None))
        self.nameLabel.setText(QCoreApplication.translate("MessageDetails", u"name", None))
        self.idLabel.setText(QCoreApplication.translate("MessageDetails", u"id", None))
        self.dlcLabel.setText(QCoreApplication.translate("MessageDetails", u"dlc", None))
        self.frequencyLabel.setText(QCoreApplication.translate("MessageDetails", u"frequency", None))
        self.descriptionLabel.setText(QCoreApplication.translate("MessageDetails", u"description", None))
        self.addButton.setText(QCoreApplication.translate("MessageDetails", u"Add", None))
        self.deleteMessageButton.setText(QCoreApplication.translate("MessageDetails", u"Delete", None))
    # retranslateUi

