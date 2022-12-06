# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\DataExporter.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(964, 667)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 951, 631))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.record_toggle = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.record_toggle.setEnabled(True)
        self.record_toggle.setCheckable(True)
        self.record_toggle.setObjectName("record_toggle")
        self.verticalLayout.addWidget(self.record_toggle)
        self.message_count = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.message_count.setObjectName("message_count")
        self.verticalLayout.addWidget(self.message_count)
        self.stdout_listwidget = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.stdout_listwidget.setObjectName("stdout_listwidget")
        self.verticalLayout.addWidget(self.stdout_listwidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 964, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.record_toggle.setText(_translate("MainWindow", "PushButton"))
        self.message_count.setText(_translate("MainWindow", "0"))

