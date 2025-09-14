# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(450, 323)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionValidate = QAction(MainWindow)
        self.actionValidate.setObjectName("actionValidate")
        self.actionLogs = QAction(MainWindow)
        self.actionLogs.setObjectName("actionLogs")
        self.action_software10e_help = QAction(MainWindow)
        self.action_software10e_help.setObjectName("action_software10e_help")
        self.action_fcp_help = QAction(MainWindow)
        self.action_fcp_help.setObjectName("action_fcp_help")
        self.actionOpen_Recent = QAction(MainWindow)
        self.actionOpen_Recent.setObjectName("actionOpen_Recent")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 9)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setMaximumSize(QSize(400, 16777215))
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaContents = QWidget()
        self.scrollAreaContents.setObjectName("scrollAreaContents")
        self.scrollAreaContents.setGeometry(QRect(0, 0, 374, 165))
        self.verticalLayout = QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaContents)

        self.horizontalLayout_3.addWidget(self.scrollArea)

        self.horizontalSpacer = QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.horizontalLayout_3.setStretch(1, 10)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.addButton = QPushButton(self.tab)
        self.addButton.setObjectName("addButton")
        self.addButton.setMaximumSize(QSize(400, 16777215))

        self.horizontalLayout_2.addWidget(self.addButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.tab, "")
        self.Logs = QWidget()
        self.Logs.setObjectName("Logs")
        self.verticalLayout_4 = QVBoxLayout(self.Logs)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.logDetailsLayout = QVBoxLayout()
        self.logDetailsLayout.setObjectName("logDetailsLayout")

        self.verticalLayout_4.addLayout(self.logDetailsLayout)

        self.tabWidget.addTab(self.Logs, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_5 = QVBoxLayout(self.tab_3)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.enumDetailsLayout = QVBoxLayout()
        self.enumDetailsLayout.setObjectName("enumDetailsLayout")

        self.verticalLayout_5.addLayout(self.enumDetailsLayout)

        self.tabWidget.addTab(self.tab_3, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        self.deviceDetailsLayout = QVBoxLayout()
        self.deviceDetailsLayout.setObjectName("deviceDetailsLayout")

        self.horizontalLayout.addLayout(self.deviceDetailsLayout)

        self.messageDetailsLayout = QVBoxLayout()
        self.messageDetailsLayout.setObjectName("messageDetailsLayout")

        self.horizontalLayout.addLayout(self.messageDetailsLayout)

        self.signalDetailsLayout = QVBoxLayout()
        self.signalDetailsLayout.setObjectName("signalDetailsLayout")

        self.horizontalLayout.addLayout(self.signalDetailsLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 450, 27))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpen_Recent)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionValidate)
        self.menuHelp.addAction(self.action_software10e_help)
        self.menuHelp.addAction(self.action_fcp_help)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", "Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.actionValidate.setText(
            QCoreApplication.translate("MainWindow", "Validate", None)
        )
        self.actionLogs.setText(QCoreApplication.translate("MainWindow", "Logs", None))
        self.action_software10e_help.setText(
            QCoreApplication.translate("MainWindow", "Software10e FCP", None)
        )
        self.action_fcp_help.setText(
            QCoreApplication.translate("MainWindow", "FCP Help", None)
        )
        self.actionOpen_Recent.setText(
            QCoreApplication.translate("MainWindow", "Open Recent", None)
        )
        self.addButton.setText(QCoreApplication.translate("MainWindow", "Add", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab),
            QCoreApplication.translate("MainWindow", "Devices", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.Logs),
            QCoreApplication.translate("MainWindow", "Logs", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_3),
            QCoreApplication.translate("MainWindow", "Enums", None),
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    # retranslateUi
