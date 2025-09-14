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
            MessageDetails.setObjectName("MessageDetails")
        MessageDetails.resize(342, 308)
        self.verticalLayout = QVBoxLayout(MessageDetails)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QGroupBox(MessageDetails)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName("nameLabel")

        self.horizontalLayout.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName("nameEdit")

        self.horizontalLayout.addWidget(self.nameEdit)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.idLabel = QLabel(self.groupBox)
        self.idLabel.setObjectName("idLabel")

        self.horizontalLayout_2.addWidget(self.idLabel)

        self.idEdit = QLineEdit(self.groupBox)
        self.idEdit.setObjectName("idEdit")

        self.horizontalLayout_2.addWidget(self.idEdit)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.dlcLabel = QLabel(self.groupBox)
        self.dlcLabel.setObjectName("dlcLabel")

        self.horizontalLayout_3.addWidget(self.dlcLabel)

        self.dlcEdit = QLineEdit(self.groupBox)
        self.dlcEdit.setObjectName("dlcEdit")

        self.horizontalLayout_3.addWidget(self.dlcEdit)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frequencyLabel = QLabel(self.groupBox)
        self.frequencyLabel.setObjectName("frequencyLabel")

        self.horizontalLayout_4.addWidget(self.frequencyLabel)

        self.frequencyEdit = QLineEdit(self.groupBox)
        self.frequencyEdit.setObjectName("frequencyEdit")

        self.horizontalLayout_4.addWidget(self.frequencyEdit)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.descriptionLabel = QLabel(self.groupBox)
        self.descriptionLabel.setObjectName("descriptionLabel")

        self.horizontalLayout_6.addWidget(self.descriptionLabel)

        self.descriptionEdit = QLineEdit(self.groupBox)
        self.descriptionEdit.setObjectName("descriptionEdit")

        self.horizontalLayout_6.addWidget(self.descriptionEdit)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.signalContents = QWidget()
        self.signalContents.setObjectName("signalContents")
        self.signalContents.setGeometry(QRect(0, 0, 298, 60))
        self.verticalLayout_2 = QVBoxLayout(self.signalContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea.setWidget(self.signalContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.addButton = QPushButton(self.groupBox)
        self.addButton.setObjectName("addButton")

        self.horizontalLayout_5.addWidget(self.addButton)

        self.deleteMessageButton = QPushButton(self.groupBox)
        self.deleteMessageButton.setObjectName("deleteMessageButton")

        self.horizontalLayout_5.addWidget(self.deleteMessageButton)

        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(MessageDetails)

        QMetaObject.connectSlotsByName(MessageDetails)

    # setupUi

    def retranslateUi(self, MessageDetails):
        MessageDetails.setWindowTitle(
            QCoreApplication.translate("MessageDetails", "MessageDetails", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate("MessageDetails", "Message", None)
        )
        self.nameLabel.setText(
            QCoreApplication.translate("MessageDetails", "name", None)
        )
        self.idLabel.setText(QCoreApplication.translate("MessageDetails", "id", None))
        self.dlcLabel.setText(QCoreApplication.translate("MessageDetails", "dlc", None))
        self.frequencyLabel.setText(
            QCoreApplication.translate("MessageDetails", "frequency", None)
        )
        self.descriptionLabel.setText(
            QCoreApplication.translate("MessageDetails", "description", None)
        )
        self.addButton.setText(
            QCoreApplication.translate("MessageDetails", "Add", None)
        )
        self.deleteMessageButton.setText(
            QCoreApplication.translate("MessageDetails", "Delete", None)
        )

    # retranslateUi
