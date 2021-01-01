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
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(450, 323)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionValidate = QAction(MainWindow)
        self.actionValidate.setObjectName(u"actionValidate")
        self.actionLogs = QAction(MainWindow)
        self.actionLogs.setObjectName(u"actionLogs")
        self.action_software10e_help = QAction(MainWindow)
        self.action_software10e_help.setObjectName(u"action_software10e_help")
        self.action_fcp_help = QAction(MainWindow)
        self.action_fcp_help.setObjectName(u"action_fcp_help")
        self.actionOpen_Recent = QAction(MainWindow)
        self.actionOpen_Recent.setObjectName(u"actionOpen_Recent")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 9)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMaximumSize(QSize(400, 16777215))
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaContents = QWidget()
        self.scrollAreaContents.setObjectName(u"scrollAreaContents")
        self.scrollAreaContents.setGeometry(QRect(0, 0, 374, 165))
        self.verticalLayout = QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaContents)

        self.horizontalLayout_3.addWidget(self.scrollArea)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.horizontalLayout_3.setStretch(1, 10)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.addButton = QPushButton(self.tab)
        self.addButton.setObjectName(u"addButton")
        self.addButton.setMaximumSize(QSize(400, 16777215))

        self.horizontalLayout_2.addWidget(self.addButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.tab, "")
        self.Logs = QWidget()
        self.Logs.setObjectName(u"Logs")
        self.verticalLayout_4 = QVBoxLayout(self.Logs)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.logDetailsLayout = QVBoxLayout()
        self.logDetailsLayout.setObjectName(u"logDetailsLayout")

        self.verticalLayout_4.addLayout(self.logDetailsLayout)

        self.tabWidget.addTab(self.Logs, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_5 = QVBoxLayout(self.tab_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.enumDetailsLayout = QVBoxLayout()
        self.enumDetailsLayout.setObjectName(u"enumDetailsLayout")

        self.verticalLayout_5.addLayout(self.enumDetailsLayout)

        self.tabWidget.addTab(self.tab_3, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        self.deviceDetailsLayout = QVBoxLayout()
        self.deviceDetailsLayout.setObjectName(u"deviceDetailsLayout")

        self.horizontalLayout.addLayout(self.deviceDetailsLayout)

        self.messageDetailsLayout = QVBoxLayout()
        self.messageDetailsLayout.setObjectName(u"messageDetailsLayout")

        self.horizontalLayout.addLayout(self.messageDetailsLayout)

        self.signalDetailsLayout = QVBoxLayout()
        self.signalDetailsLayout.setObjectName(u"signalDetailsLayout")

        self.horizontalLayout.addLayout(self.signalDetailsLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 450, 27))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionValidate.setText(QCoreApplication.translate("MainWindow", u"Validate", None))
        self.actionLogs.setText(QCoreApplication.translate("MainWindow", u"Logs", None))
        self.action_software10e_help.setText(QCoreApplication.translate("MainWindow", u"Software10e FCP", None))
        self.action_fcp_help.setText(QCoreApplication.translate("MainWindow", u"FCP Help", None))
        self.actionOpen_Recent.setText(QCoreApplication.translate("MainWindow", u"Open Recent", None))
        self.addButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Devices", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Logs), QCoreApplication.translate("MainWindow", u"Logs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Enums", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

