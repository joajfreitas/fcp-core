# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'signalwidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SignalWidget(object):
    def setupUi(self, SignalWidget):
        if not SignalWidget.objectName():
            SignalWidget.setObjectName(u"SignalWidget")
        SignalWidget.resize(348, 77)
        self.horizontalLayout = QHBoxLayout(SignalWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(SignalWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.name = QLabel(self.groupBox)
        self.name.setObjectName(u"name")

        self.verticalLayout_2.addWidget(self.name)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.start = QLabel(self.groupBox)
        self.start.setObjectName(u"start")

        self.horizontalLayout_4.addWidget(self.start)

        self.length = QLabel(self.groupBox)
        self.length.setObjectName(u"length")

        self.horizontalLayout_4.addWidget(self.length)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.deleteButton = QPushButton(self.groupBox)
        self.deleteButton.setObjectName(u"deleteButton")
        self.deleteButton.setMaximumSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.deleteButton)

        self.signalDetailsButton = QPushButton(self.groupBox)
        self.signalDetailsButton.setObjectName(u"signalDetailsButton")
        self.signalDetailsButton.setMaximumSize(QSize(60, 25))
        self.signalDetailsButton.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.signalDetailsButton)


        self.horizontalLayout.addWidget(self.groupBox)


        self.retranslateUi(SignalWidget)

        QMetaObject.connectSlotsByName(SignalWidget)
    # setupUi

    def retranslateUi(self, SignalWidget):
        SignalWidget.setWindowTitle(QCoreApplication.translate("SignalWidget", u"SignalWidget", None))
        self.groupBox.setTitle("")
        self.name.setText("")
        self.start.setText("")
        self.length.setText("")
        self.deleteButton.setText(QCoreApplication.translate("SignalWidget", u"\u2717", None))
        self.signalDetailsButton.setText(QCoreApplication.translate("SignalWidget", u"...", None))
    # retranslateUi

