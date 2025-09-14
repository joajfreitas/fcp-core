# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'logdetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_LogDetails(object):
    def setupUi(self, LogDetails):
        if not LogDetails.objectName():
            LogDetails.setObjectName("LogDetails")
        LogDetails.resize(400, 300)
        LogDetails.setMinimumSize(QSize(200, 0))
        self.verticalLayout = QVBoxLayout(LogDetails)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QGroupBox(LogDetails)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName("nameLabel")

        self.horizontalLayout_2.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName("nameEdit")

        self.horizontalLayout_2.addWidget(self.nameEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.idLabel = QLabel(self.groupBox)
        self.idLabel.setObjectName("idLabel")

        self.horizontalLayout_3.addWidget(self.idLabel)

        self.idEdit = QLineEdit(self.groupBox)
        self.idEdit.setObjectName("idEdit")

        self.horizontalLayout_3.addWidget(self.idEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.n_argsLabel = QLabel(self.groupBox)
        self.n_argsLabel.setObjectName("n_argsLabel")

        self.horizontalLayout_4.addWidget(self.n_argsLabel)

        self.n_argsEdit = QLineEdit(self.groupBox)
        self.n_argsEdit.setObjectName("n_argsEdit")

        self.horizontalLayout_4.addWidget(self.n_argsEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.commentLabel = QLabel(self.groupBox)
        self.commentLabel.setObjectName("commentLabel")

        self.horizontalLayout_5.addWidget(self.commentLabel)

        self.commentEdit = QLineEdit(self.groupBox)
        self.commentEdit.setObjectName("commentEdit")

        self.horizontalLayout_5.addWidget(self.commentEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stringLabel = QLabel(self.groupBox)
        self.stringLabel.setObjectName("stringLabel")

        self.horizontalLayout.addWidget(self.stringLabel)

        self.stringEdit = QLineEdit(self.groupBox)
        self.stringEdit.setObjectName("stringEdit")

        self.horizontalLayout.addWidget(self.stringEdit)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.logDeleteButton = QPushButton(self.groupBox)
        self.logDeleteButton.setObjectName("logDeleteButton")

        self.verticalLayout_2.addWidget(self.logDeleteButton)

        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(LogDetails)

        QMetaObject.connectSlotsByName(LogDetails)

    # setupUi

    def retranslateUi(self, LogDetails):
        LogDetails.setWindowTitle(
            QCoreApplication.translate("LogDetails", "LogDetails", None)
        )
        self.groupBox.setTitle(QCoreApplication.translate("LogDetails", "Log", None))
        self.nameLabel.setText(QCoreApplication.translate("LogDetails", "name", None))
        self.idLabel.setText(QCoreApplication.translate("LogDetails", "id", None))
        self.n_argsLabel.setText(
            QCoreApplication.translate("LogDetails", "n_args", None)
        )
        self.commentLabel.setText(
            QCoreApplication.translate("LogDetails", "comment", None)
        )
        self.stringLabel.setText(
            QCoreApplication.translate("LogDetails", "string", None)
        )
        self.logDeleteButton.setText(
            QCoreApplication.translate("LogDetails", "Delete", None)
        )

    # retranslateUi
