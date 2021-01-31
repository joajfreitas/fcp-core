# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cmdarg.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CmdArg(object):
    def setupUi(self, CmdArg):
        if not CmdArg.objectName():
            CmdArg.setObjectName(u"CmdArg")
        CmdArg.resize(400, 300)
        CmdArg.setMinimumSize(QSize(300, 0))
        self.verticalLayout_2 = QVBoxLayout(CmdArg)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(CmdArg)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.idLabel = QLabel(self.groupBox)
        self.idLabel.setObjectName(u"idLabel")

        self.horizontalLayout_2.addWidget(self.idLabel)

        self.idEdit = QLineEdit(self.groupBox)
        self.idEdit.setObjectName(u"idEdit")

        self.horizontalLayout_2.addWidget(self.idEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName(u"nameEdit")

        self.horizontalLayout.addWidget(self.nameEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.commentLabel = QLabel(self.groupBox)
        self.commentLabel.setObjectName(u"commentLabel")

        self.horizontalLayout_3.addWidget(self.commentLabel)

        self.commentEdit = QLineEdit(self.groupBox)
        self.commentEdit.setObjectName(u"commentEdit")

        self.horizontalLayout_3.addWidget(self.commentEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.deleteArgButton = QPushButton(self.groupBox)
        self.deleteArgButton.setObjectName(u"deleteArgButton")

        self.verticalLayout_3.addWidget(self.deleteArgButton)


        self.verticalLayout_2.addWidget(self.groupBox)


        self.retranslateUi(CmdArg)

        QMetaObject.connectSlotsByName(CmdArg)
    # setupUi

    def retranslateUi(self, CmdArg):
        CmdArg.setWindowTitle(QCoreApplication.translate("CmdArg", u"CmdArg", None))
        self.groupBox.setTitle(QCoreApplication.translate("CmdArg", u"Argument", None))
        self.idLabel.setText(QCoreApplication.translate("CmdArg", u"id", None))
        self.nameLabel.setText(QCoreApplication.translate("CmdArg", u"name", None))
        self.commentLabel.setText(QCoreApplication.translate("CmdArg", u"comment", None))
        self.deleteArgButton.setText(QCoreApplication.translate("CmdArg", u"Delete", None))
    # retranslateUi

