# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'devicewidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_DeviceWidget(object):
    def setupUi(self, DeviceWidget):
        if not DeviceWidget.objectName():
            DeviceWidget.setObjectName(u"DeviceWidget")
        DeviceWidget.resize(370, 118)
        self.horizontalLayout_2 = QHBoxLayout(DeviceWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.groupBox_2 = QGroupBox(DeviceWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.name = QLabel(self.groupBox_2)
        self.name.setObjectName(u"name")

        self.horizontalLayout_3.addWidget(self.name)

        self.id = QLabel(self.groupBox_2)
        self.id.setObjectName(u"id")

        self.horizontalLayout_3.addWidget(self.id)

        self.deleteButton = QPushButton(self.groupBox_2)
        self.deleteButton.setObjectName(u"deleteButton")
        self.deleteButton.setMaximumSize(QSize(25, 25))

        self.horizontalLayout_3.addWidget(self.deleteButton)

        self.deviceDetailsButton = QPushButton(self.groupBox_2)
        self.deviceDetailsButton.setObjectName(u"deviceDetailsButton")
        self.deviceDetailsButton.setMaximumSize(QSize(60, 25))
        self.deviceDetailsButton.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.deviceDetailsButton)


        self.horizontalLayout_2.addWidget(self.groupBox_2)


        self.retranslateUi(DeviceWidget)

        QMetaObject.connectSlotsByName(DeviceWidget)
    # setupUi

    def retranslateUi(self, DeviceWidget):
        DeviceWidget.setWindowTitle(QCoreApplication.translate("DeviceWidget", u"DeviceWidget", None))
        self.groupBox_2.setTitle("")
        self.name.setText("")
        self.id.setText("")
        self.deleteButton.setText(QCoreApplication.translate("DeviceWidget", u"\u2717", None))
        self.deviceDetailsButton.setText(QCoreApplication.translate("DeviceWidget", u"...", None))
    # retranslateUi

