# Form implementation generated from reading ui file 'ControlPanel.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(470, 370)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.AddOperationBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.AddOperationBtn.setObjectName("AddOperationBtn")
        self.gridLayout.addWidget(self.AddOperationBtn, 1, 1, 1, 1)
        self.DeleteOperationBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.DeleteOperationBtn.setObjectName("DeleteOperationBtn")
        self.gridLayout.addWidget(self.DeleteOperationBtn, 2, 1, 1, 1)
        self.OperationList = QtWidgets.QListWidget(parent=self.centralwidget)
        self.OperationList.setObjectName("OperationList")
        self.gridLayout.addWidget(self.OperationList, 1, 0, 2, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.TimeLine = QtWidgets.QScrollArea(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TimeLine.sizePolicy().hasHeightForWidth())
        self.TimeLine.setSizePolicy(sizePolicy)
        self.TimeLine.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.TimeLine.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.TimeLine.setWidgetResizable(True)
        self.TimeLine.setObjectName("TimeLine")
        self.TimelineContents = QtWidgets.QWidget()
        self.TimelineContents.setGeometry(QtCore.QRect(0, 0, 448, 52))
        self.TimelineContents.setObjectName("TimelineContents")
        self.TimeLine.setWidget(self.TimelineContents)
        self.verticalLayout.addWidget(self.TimeLine)
        self.waveView = QtWidgets.QGraphicsView(parent=self.centralwidget)
        self.waveView.setObjectName("waveView")
        self.verticalLayout.addWidget(self.waveView)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.AddOperationBtn.setText(_translate("MainWindow", "Add"))
        self.DeleteOperationBtn.setText(_translate("MainWindow", "Delete"))
