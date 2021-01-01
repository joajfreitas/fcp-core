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
            SignalDetails.setObjectName(u"SignalDetails")
        SignalDetails.resize(473, 580)
        self.verticalLayout_2 = QVBoxLayout(SignalDetails)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(SignalDetails)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.nameLabel = QLabel(self.groupBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.horizontalLayout_14.addWidget(self.nameLabel)

        self.nameEdit = QLineEdit(self.groupBox)
        self.nameEdit.setObjectName(u"nameEdit")

        self.horizontalLayout_14.addWidget(self.nameEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.aliasLabel = QLabel(self.groupBox)
        self.aliasLabel.setObjectName(u"aliasLabel")

        self.horizontalLayout_15.addWidget(self.aliasLabel)

        self.aliasEdit = QLineEdit(self.groupBox)
        self.aliasEdit.setObjectName(u"aliasEdit")

        self.horizontalLayout_15.addWidget(self.aliasEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.commentLabel = QLabel(self.groupBox)
        self.commentLabel.setObjectName(u"commentLabel")

        self.horizontalLayout_13.addWidget(self.commentLabel)

        self.commentEdit = QLineEdit(self.groupBox)
        self.commentEdit.setObjectName(u"commentEdit")

        self.horizontalLayout_13.addWidget(self.commentEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.startLabel = QLabel(self.groupBox)
        self.startLabel.setObjectName(u"startLabel")

        self.horizontalLayout_12.addWidget(self.startLabel)

        self.startEdit = QLineEdit(self.groupBox)
        self.startEdit.setObjectName(u"startEdit")

        self.horizontalLayout_12.addWidget(self.startEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.lengthLabel = QLabel(self.groupBox)
        self.lengthLabel.setObjectName(u"lengthLabel")

        self.horizontalLayout_11.addWidget(self.lengthLabel)

        self.lengthEdit = QLineEdit(self.groupBox)
        self.lengthEdit.setObjectName(u"lengthEdit")

        self.horizontalLayout_11.addWidget(self.lengthEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.typeLabel = QLabel(self.groupBox)
        self.typeLabel.setObjectName(u"typeLabel")

        self.horizontalLayout_9.addWidget(self.typeLabel)

        self.typeEdit = QLineEdit(self.groupBox)
        self.typeEdit.setObjectName(u"typeEdit")

        self.horizontalLayout_9.addWidget(self.typeEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.unitLabel = QLabel(self.groupBox)
        self.unitLabel.setObjectName(u"unitLabel")

        self.horizontalLayout_8.addWidget(self.unitLabel)

        self.unitEdit = QLineEdit(self.groupBox)
        self.unitEdit.setObjectName(u"unitEdit")

        self.horizontalLayout_8.addWidget(self.unitEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.minValueLabel = QLabel(self.groupBox)
        self.minValueLabel.setObjectName(u"minValueLabel")

        self.horizontalLayout_7.addWidget(self.minValueLabel)

        self.minValueEdit = QLineEdit(self.groupBox)
        self.minValueEdit.setObjectName(u"minValueEdit")

        self.horizontalLayout_7.addWidget(self.minValueEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.maxValueLabel = QLabel(self.groupBox)
        self.maxValueLabel.setObjectName(u"maxValueLabel")

        self.horizontalLayout_6.addWidget(self.maxValueLabel)

        self.maxValueEdit = QLineEdit(self.groupBox)
        self.maxValueEdit.setObjectName(u"maxValueEdit")

        self.horizontalLayout_6.addWidget(self.maxValueEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.muxLabel = QLabel(self.groupBox)
        self.muxLabel.setObjectName(u"muxLabel")

        self.horizontalLayout_5.addWidget(self.muxLabel)

        self.muxEdit = QLineEdit(self.groupBox)
        self.muxEdit.setObjectName(u"muxEdit")

        self.horizontalLayout_5.addWidget(self.muxEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.muxCountLabel = QLabel(self.groupBox)
        self.muxCountLabel.setObjectName(u"muxCountLabel")

        self.horizontalLayout_4.addWidget(self.muxCountLabel)

        self.muxCountEdit = QLineEdit(self.groupBox)
        self.muxCountEdit.setObjectName(u"muxCountEdit")

        self.horizontalLayout_4.addWidget(self.muxCountEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.byteOrderLabel = QLabel(self.groupBox)
        self.byteOrderLabel.setObjectName(u"byteOrderLabel")

        self.horizontalLayout_3.addWidget(self.byteOrderLabel)

        self.byteOrderEdit = QLineEdit(self.groupBox)
        self.byteOrderEdit.setObjectName(u"byteOrderEdit")

        self.horizontalLayout_3.addWidget(self.byteOrderEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.scaleLabel = QLabel(self.groupBox)
        self.scaleLabel.setObjectName(u"scaleLabel")

        self.horizontalLayout_2.addWidget(self.scaleLabel)

        self.scaleEdit = QLineEdit(self.groupBox)
        self.scaleEdit.setObjectName(u"scaleEdit")

        self.horizontalLayout_2.addWidget(self.scaleEdit)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.offsetLabel = QLabel(self.groupBox)
        self.offsetLabel.setObjectName(u"offsetLabel")

        self.horizontalLayout.addWidget(self.offsetLabel)

        self.offsetEdit = QLineEdit(self.groupBox)
        self.offsetEdit.setObjectName(u"offsetEdit")

        self.horizontalLayout.addWidget(self.offsetEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.saveSignal = QPushButton(self.groupBox)
        self.saveSignal.setObjectName(u"saveSignal")

        self.horizontalLayout_10.addWidget(self.saveSignal)

        self.signalDeleteButton = QPushButton(self.groupBox)
        self.signalDeleteButton.setObjectName(u"signalDeleteButton")

        self.horizontalLayout_10.addWidget(self.signalDeleteButton)


        self.verticalLayout.addLayout(self.horizontalLayout_10)


        self.verticalLayout_2.addWidget(self.groupBox)


        self.retranslateUi(SignalDetails)

        QMetaObject.connectSlotsByName(SignalDetails)
    # setupUi

    def retranslateUi(self, SignalDetails):
        SignalDetails.setWindowTitle(QCoreApplication.translate("SignalDetails", u"SignalDetails", None))
        self.groupBox.setTitle(QCoreApplication.translate("SignalDetails", u"Signal", None))
        self.nameLabel.setText(QCoreApplication.translate("SignalDetails", u"name", None))
        self.aliasLabel.setText(QCoreApplication.translate("SignalDetails", u"alias", None))
        self.commentLabel.setText(QCoreApplication.translate("SignalDetails", u"comment", None))
        self.startLabel.setText(QCoreApplication.translate("SignalDetails", u"start", None))
        self.lengthLabel.setText(QCoreApplication.translate("SignalDetails", u"length", None))
        self.typeLabel.setText(QCoreApplication.translate("SignalDetails", u"type", None))
        self.unitLabel.setText(QCoreApplication.translate("SignalDetails", u"unit", None))
        self.minValueLabel.setText(QCoreApplication.translate("SignalDetails", u"min_value", None))
        self.maxValueLabel.setText(QCoreApplication.translate("SignalDetails", u"max_value", None))
        self.muxLabel.setText(QCoreApplication.translate("SignalDetails", u"mux", None))
        self.muxCountLabel.setText(QCoreApplication.translate("SignalDetails", u"mux_count", None))
        self.byteOrderLabel.setText(QCoreApplication.translate("SignalDetails", u"byte_order", None))
        self.scaleLabel.setText(QCoreApplication.translate("SignalDetails", u"scale", None))
        self.offsetLabel.setText(QCoreApplication.translate("SignalDetails", u"offset", None))
        self.saveSignal.setText(QCoreApplication.translate("SignalDetails", u"Save", None))
        self.signalDeleteButton.setText(QCoreApplication.translate("SignalDetails", u"Delete", None))
    # retranslateUi

