# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'signaldetails.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SignalDetails(object):
    def setupUi(self, SignalDetails):
        if not SignalDetails.objectName():
            SignalDetails.setObjectName("SignalDetails")
        SignalDetails.resize(473, 580)
        self.verticalLayout_2 = QVBoxLayout(SignalDetails)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QGroupBox(SignalDetails)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName("nameLabel")

        self.horizontalLayout_14.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName("nameEdit")

        self.horizontalLayout_14.addWidget(self.nameEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.aliasLabel = QLabel(self.groupBox)
        self.aliasLabel.setObjectName("aliasLabel")

        self.horizontalLayout_15.addWidget(self.aliasLabel)

        self.aliasEdit = QLineEdit(self.groupBox)
        self.aliasEdit.setObjectName("aliasEdit")

        self.horizontalLayout_15.addWidget(self.aliasEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.commentLabel = QLabel(self.groupBox)
        self.commentLabel.setObjectName("commentLabel")

        self.horizontalLayout_13.addWidget(self.commentLabel)

        self.commentEdit = QLineEdit(self.groupBox)
        self.commentEdit.setObjectName("commentEdit")

        self.horizontalLayout_13.addWidget(self.commentEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.startLabel = QLabel(self.groupBox)
        self.startLabel.setObjectName("startLabel")

        self.horizontalLayout_12.addWidget(self.startLabel)

        self.startEdit = QLineEdit(self.groupBox)
        self.startEdit.setObjectName("startEdit")

        self.horizontalLayout_12.addWidget(self.startEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.lengthLabel = QLabel(self.groupBox)
        self.lengthLabel.setObjectName("lengthLabel")

        self.horizontalLayout_11.addWidget(self.lengthLabel)

        self.lengthEdit = QLineEdit(self.groupBox)
        self.lengthEdit.setObjectName("lengthEdit")

        self.horizontalLayout_11.addWidget(self.lengthEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.typeLabel = QLabel(self.groupBox)
        self.typeLabel.setObjectName("typeLabel")

        self.horizontalLayout_9.addWidget(self.typeLabel)

        self.typeEdit = QLineEdit(self.groupBox)
        self.typeEdit.setObjectName("typeEdit")

        self.horizontalLayout_9.addWidget(self.typeEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.unitLabel = QLabel(self.groupBox)
        self.unitLabel.setObjectName("unitLabel")

        self.horizontalLayout_8.addWidget(self.unitLabel)

        self.unitEdit = QLineEdit(self.groupBox)
        self.unitEdit.setObjectName("unitEdit")

        self.horizontalLayout_8.addWidget(self.unitEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.minValueLabel = QLabel(self.groupBox)
        self.minValueLabel.setObjectName("minValueLabel")

        self.horizontalLayout_7.addWidget(self.minValueLabel)

        self.minValueEdit = QLineEdit(self.groupBox)
        self.minValueEdit.setObjectName("minValueEdit")

        self.horizontalLayout_7.addWidget(self.minValueEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.maxValueLabel = QLabel(self.groupBox)
        self.maxValueLabel.setObjectName("maxValueLabel")

        self.horizontalLayout_6.addWidget(self.maxValueLabel)

        self.maxValueEdit = QLineEdit(self.groupBox)
        self.maxValueEdit.setObjectName("maxValueEdit")

        self.horizontalLayout_6.addWidget(self.maxValueEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.muxLabel = QLabel(self.groupBox)
        self.muxLabel.setObjectName("muxLabel")

        self.horizontalLayout_5.addWidget(self.muxLabel)

        self.muxEdit = QLineEdit(self.groupBox)
        self.muxEdit.setObjectName("muxEdit")

        self.horizontalLayout_5.addWidget(self.muxEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.muxCountLabel = QLabel(self.groupBox)
        self.muxCountLabel.setObjectName("muxCountLabel")

        self.horizontalLayout_4.addWidget(self.muxCountLabel)

        self.muxCountEdit = QLineEdit(self.groupBox)
        self.muxCountEdit.setObjectName("muxCountEdit")

        self.horizontalLayout_4.addWidget(self.muxCountEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.byteOrderLabel = QLabel(self.groupBox)
        self.byteOrderLabel.setObjectName("byteOrderLabel")

        self.horizontalLayout_3.addWidget(self.byteOrderLabel)

        self.byteOrderEdit = QLineEdit(self.groupBox)
        self.byteOrderEdit.setObjectName("byteOrderEdit")

        self.horizontalLayout_3.addWidget(self.byteOrderEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scaleLabel = QLabel(self.groupBox)
        self.scaleLabel.setObjectName("scaleLabel")

        self.horizontalLayout_2.addWidget(self.scaleLabel)

        self.scaleEdit = QLineEdit(self.groupBox)
        self.scaleEdit.setObjectName("scaleEdit")

        self.horizontalLayout_2.addWidget(self.scaleEdit)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.offsetLabel = QLabel(self.groupBox)
        self.offsetLabel.setObjectName("offsetLabel")

        self.horizontalLayout.addWidget(self.offsetLabel)

        self.offsetEdit = QLineEdit(self.groupBox)
        self.offsetEdit.setObjectName("offsetEdit")

        self.horizontalLayout.addWidget(self.offsetEdit)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.saveSignal = QPushButton(self.groupBox)
        self.saveSignal.setObjectName("saveSignal")

        self.horizontalLayout_10.addWidget(self.saveSignal)

        self.signalDeleteButton = QPushButton(self.groupBox)
        self.signalDeleteButton.setObjectName("signalDeleteButton")

        self.horizontalLayout_10.addWidget(self.signalDeleteButton)

        self.verticalLayout.addLayout(self.horizontalLayout_10)

        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(SignalDetails)

        QMetaObject.connectSlotsByName(SignalDetails)

    # setupUi

    def retranslateUi(self, SignalDetails):
        SignalDetails.setWindowTitle(
            QCoreApplication.translate("SignalDetails", "SignalDetails", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate("SignalDetails", "Signal", None)
        )
        self.nameLabel.setText(
            QCoreApplication.translate("SignalDetails", "name", None)
        )
        self.aliasLabel.setText(
            QCoreApplication.translate("SignalDetails", "alias", None)
        )
        self.commentLabel.setText(
            QCoreApplication.translate("SignalDetails", "comment", None)
        )
        self.startLabel.setText(
            QCoreApplication.translate("SignalDetails", "start", None)
        )
        self.lengthLabel.setText(
            QCoreApplication.translate("SignalDetails", "length", None)
        )
        self.typeLabel.setText(
            QCoreApplication.translate("SignalDetails", "type", None)
        )
        self.unitLabel.setText(
            QCoreApplication.translate("SignalDetails", "unit", None)
        )
        self.minValueLabel.setText(
            QCoreApplication.translate("SignalDetails", "min_value", None)
        )
        self.maxValueLabel.setText(
            QCoreApplication.translate("SignalDetails", "max_value", None)
        )
        self.muxLabel.setText(QCoreApplication.translate("SignalDetails", "mux", None))
        self.muxCountLabel.setText(
            QCoreApplication.translate("SignalDetails", "mux_count", None)
        )
        self.byteOrderLabel.setText(
            QCoreApplication.translate("SignalDetails", "byte_order", None)
        )
        self.scaleLabel.setText(
            QCoreApplication.translate("SignalDetails", "scale", None)
        )
        self.offsetLabel.setText(
            QCoreApplication.translate("SignalDetails", "offset", None)
        )
        self.saveSignal.setText(
            QCoreApplication.translate("SignalDetails", "Save", None)
        )
        self.signalDeleteButton.setText(
            QCoreApplication.translate("SignalDetails", "Delete", None)
        )

    # retranslateUi
