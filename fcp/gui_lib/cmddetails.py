# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cmddetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CmdDetails(object):
    def setupUi(self, CmdDetails):
        if not CmdDetails.objectName():
            CmdDetails.setObjectName(u"CmdDetails")
        CmdDetails.resize(422, 429)
        CmdDetails.setMinimumSize(QSize(300, 0))
        self.horizontalLayout_5 = QHBoxLayout(CmdDetails)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.argDetailsLayout = QVBoxLayout()
        self.argDetailsLayout.setObjectName(u"argDetailsLayout")
        self.groupBox = QGroupBox(CmdDetails)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName(u"nameEdit")

        self.horizontalLayout.addWidget(self.nameEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.commentLabel = QLabel(self.groupBox)
        self.commentLabel.setObjectName(u"commentLabel")

        self.horizontalLayout_3.addWidget(self.commentLabel)

        self.commentEdit = QLineEdit(self.groupBox)
        self.commentEdit.setObjectName(u"commentEdit")

        self.horizontalLayout_3.addWidget(self.commentEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.n_argsLabel = QLabel(self.groupBox)
        self.n_argsLabel.setObjectName(u"n_argsLabel")

        self.horizontalLayout_2.addWidget(self.n_argsLabel)

        self.n_argsEdit = QLineEdit(self.groupBox)
        self.n_argsEdit.setObjectName(u"n_argsEdit")

        self.horizontalLayout_2.addWidget(self.n_argsEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.idLabel = QLabel(self.groupBox)
        self.idLabel.setObjectName(u"idLabel")

        self.horizontalLayout_4.addWidget(self.idLabel)

        self.idEdit = QLineEdit(self.groupBox)
        self.idEdit.setObjectName(u"idEdit")

        self.horizontalLayout_4.addWidget(self.idEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.scrollArea = QScrollArea(self.groupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self._CmdArgContents = QWidget()
        self._CmdArgContents.setObjectName(u"_CmdArgContents")
        self._CmdArgContents.setGeometry(QRect(0, 0, 374, 181))
        self.verticalLayout_3 = QVBoxLayout(self._CmdArgContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.CmdArgContents = QVBoxLayout()
        self.CmdArgContents.setObjectName(u"CmdArgContents")

        self.verticalLayout_3.addLayout(self.CmdArgContents)

        self.scrollArea.setWidget(self._CmdArgContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.addArgButton = QPushButton(self.groupBox)
        self.addArgButton.setObjectName(u"addArgButton")

        self.verticalLayout.addWidget(self.addArgButton)


        self.verticalLayout_4.addLayout(self.verticalLayout)

        self.deleteCmdButton = QPushButton(self.groupBox)
        self.deleteCmdButton.setObjectName(u"deleteCmdButton")

        self.verticalLayout_4.addWidget(self.deleteCmdButton)


        self.argDetailsLayout.addWidget(self.groupBox)


        self.horizontalLayout_5.addLayout(self.argDetailsLayout)


        self.retranslateUi(CmdDetails)

        QMetaObject.connectSlotsByName(CmdDetails)
    # setupUi

    def retranslateUi(self, CmdDetails):
        CmdDetails.setWindowTitle(QCoreApplication.translate("CmdDetails", u"CmdDetails", None))
        self.groupBox.setTitle(QCoreApplication.translate("CmdDetails", u"Command", None))
        self.nameLabel.setText(QCoreApplication.translate("CmdDetails", u"name", None))
        self.commentLabel.setText(QCoreApplication.translate("CmdDetails", u"comment", None))
        self.n_argsLabel.setText(QCoreApplication.translate("CmdDetails", u"n_args", None))
        self.idLabel.setText(QCoreApplication.translate("CmdDetails", u"id", None))
        self.addArgButton.setText(QCoreApplication.translate("CmdDetails", u"Add Arg", None))
        self.deleteCmdButton.setText(QCoreApplication.translate("CmdDetails", u"Delete", None))
    # retranslateUi

