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
        MainWindow.resize(755, 664)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.gridLayout.addWidget(self.horizontalSlider, 1, 0, 1, 1)
        self.label_current_time = QtWidgets.QLabel(self.centralwidget)
        self.label_current_time.setObjectName("label_current_time")
        self.gridLayout.addWidget(self.label_current_time, 0, 0, 1, 1)
        self.label_maximum_time = QtWidgets.QLabel(self.centralwidget)
        self.label_maximum_time.setObjectName("label_maximum_time")
        self.gridLayout.addWidget(self.label_maximum_time, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 755, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_current_time.setText(_translate("MainWindow", "TextLabel"))
        self.label_maximum_time.setText(_translate("MainWindow", "TextLabel"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))

