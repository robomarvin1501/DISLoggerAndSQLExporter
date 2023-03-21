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
        MainWindow.resize(879, 598)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.TimeLine = QtWidgets.QWidget(self.centralwidget)
        self.TimeLine.setObjectName("TimeLine")
        self.gridLayout.addWidget(self.TimeLine, 3, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonPlay = QtWidgets.QPushButton(self.centralwidget)
        self.buttonPlay.setObjectName("buttonPlay")
        self.horizontalLayout.addWidget(self.buttonPlay)
        self.buttonStop = QtWidgets.QPushButton(self.centralwidget)
        self.buttonStop.setObjectName("buttonStop")
        self.horizontalLayout.addWidget(self.buttonStop)
        self.buttonPause = QtWidgets.QPushButton(self.centralwidget)
        self.buttonPause.setObjectName("buttonPause")
        self.horizontalLayout.addWidget(self.buttonPause)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.buttonDecreaseSpeed = QtWidgets.QPushButton(self.centralwidget)
        self.buttonDecreaseSpeed.setObjectName("buttonDecreaseSpeed")
        self.horizontalLayout.addWidget(self.buttonDecreaseSpeed)
        self.labelPlaybackSpeed = QtWidgets.QLabel(self.centralwidget)
        self.labelPlaybackSpeed.setObjectName("labelPlaybackSpeed")
        self.horizontalLayout.addWidget(self.labelPlaybackSpeed)
        self.buttonIncreaseSpeed = QtWidgets.QPushButton(self.centralwidget)
        self.buttonIncreaseSpeed.setObjectName("buttonIncreaseSpeed")
        self.horizontalLayout.addWidget(self.buttonIncreaseSpeed)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 2, 0, 1, 1)
        self.preciseTime = QtWidgets.QLabel(self.centralwidget)
        self.preciseTime.setObjectName("preciseTime")
        self.gridLayout.addWidget(self.preciseTime, 4, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 879, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpenFile = QtWidgets.QAction(MainWindow)
        self.actionOpenFile.setObjectName("actionOpenFile")
        self.menuFile.addAction(self.actionOpenFile)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.buttonPlay.setText(_translate("MainWindow", "Play"))
        self.buttonStop.setText(_translate("MainWindow", "Stop"))
        self.buttonPause.setText(_translate("MainWindow", "Pause"))
        self.buttonDecreaseSpeed.setText(_translate("MainWindow", "Decrease speed"))
        self.labelPlaybackSpeed.setText(_translate("MainWindow", "1.0x"))
        self.buttonIncreaseSpeed.setText(_translate("MainWindow", "Increase speed"))
        self.preciseTime.setText(_translate("MainWindow", "TextLabel"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpenFile.setText(_translate("MainWindow", "Open"))

