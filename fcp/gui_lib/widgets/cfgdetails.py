# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cfgdetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CfgDetails(object):
    def setupUi(self, CfgDetails):
        if not CfgDetails.objectName():
            CfgDetails.setObjectName("CfgDetails")
        CfgDetails.resize(400, 300)
        CfgDetails.setMinimumSize(QSize(200, 0))
        self.verticalLayout_2 = QVBoxLayout(CfgDetails)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QGroupBox(CfgDetails)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName("nameLabel")

        self.horizontalLayout_3.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName("nameEdit")

        self.horizontalLayout_3.addWidget(self.nameEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.idLabel_2 = QLabel(self.groupBox)
        self.idLabel_2.setObjectName("idLabel_2")

        self.horizontalLayout_2.addWidget(self.idLabel_2)

        self.idEdit = QLineEdit(self.groupBox)
        self.idEdit.setObjectName("idEdit")

        self.horizontalLayout_2.addWidget(self.idEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.commentLabel = QLabel(self.groupBox)
        self.commentLabel.setObjectName("commentLabel")

        self.horizontalLayout.addWidget(self.commentLabel)

        self.commentEdit = QLineEdit(self.groupBox)
        self.commentEdit.setObjectName("commentEdit")

        self.horizontalLayout.addWidget(self.commentEdit)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.deleteCfgButton = QPushButton(self.groupBox)
        self.deleteCfgButton.setObjectName("deleteCfgButton")

        self.verticalLayout.addWidget(self.deleteCfgButton)

        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(CfgDetails)

        QMetaObject.connectSlotsByName(CfgDetails)

    # setupUi

    def retranslateUi(self, CfgDetails):
        CfgDetails.setWindowTitle(
            QCoreApplication.translate("CfgDetails", "CfgDetails", None)
        )
        self.groupBox.setTitle(QCoreApplication.translate("CfgDetails", "Config", None))
        self.nameLabel.setText(QCoreApplication.translate("CfgDetails", "name", None))
        self.idLabel_2.setText(QCoreApplication.translate("CfgDetails", "id", None))
        self.commentLabel.setText(
            QCoreApplication.translate("CfgDetails", "comment", None)
        )
        self.deleteCfgButton.setText(
            QCoreApplication.translate("CfgDetails", "Delete", None)
        )

    # retranslateUi
