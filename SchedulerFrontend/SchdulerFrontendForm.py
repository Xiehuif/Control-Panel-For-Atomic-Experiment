# Form implementation generated from reading ui file 'SchdulerFrontendForm.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SchedulerForm(object):
    def setupUi(self, SchedulerForm):
        SchedulerForm.setObjectName("SchedulerForm")
        SchedulerForm.resize(733, 587)
        self.verticalLayout = QtWidgets.QVBoxLayout(SchedulerForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ScheduleTree = QtWidgets.QTreeWidget(parent=SchedulerForm)
        self.ScheduleTree.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.ScheduleTree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ScheduleTree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ScheduleTree.setObjectName("ScheduleTree")
        self.verticalLayout.addWidget(self.ScheduleTree)
        self.EditLayout = QtWidgets.QHBoxLayout()
        self.EditLayout.setObjectName("EditLayout")
        self.TableEditBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        self.TableEditBtn.setObjectName("TableEditBtn")
        self.EditLayout.addWidget(self.TableEditBtn)
        self.TableDeleteBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        self.TableDeleteBtn.setObjectName("TableDeleteBtn")
        self.EditLayout.addWidget(self.TableDeleteBtn)
        self.TableCopyBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        self.TableCopyBtn.setObjectName("TableCopyBtn")
        self.EditLayout.addWidget(self.TableCopyBtn)
        self.TableCutBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        self.TableCutBtn.setObjectName("TableCutBtn")
        self.EditLayout.addWidget(self.TableCutBtn)
        self.TablePasteBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        self.TablePasteBtn.setObjectName("TablePasteBtn")
        self.EditLayout.addWidget(self.TablePasteBtn)
        self.verticalLayout.addLayout(self.EditLayout)
        self.line = QtWidgets.QFrame(parent=SchedulerForm)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.InteractiveLayout = QtWidgets.QHBoxLayout()
        self.InteractiveLayout.setObjectName("InteractiveLayout")
        self.WavePanelLayout = QtWidgets.QVBoxLayout()
        self.WavePanelLayout.setObjectName("WavePanelLayout")
        self.ImportFromWavePanelBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ImportFromWavePanelBtn.sizePolicy().hasHeightForWidth())
        self.ImportFromWavePanelBtn.setSizePolicy(sizePolicy)
        self.ImportFromWavePanelBtn.setAutoDefault(False)
        self.ImportFromWavePanelBtn.setObjectName("ImportFromWavePanelBtn")
        self.WavePanelLayout.addWidget(self.ImportFromWavePanelBtn)
        self.ExportToWavePanelBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ExportToWavePanelBtn.sizePolicy().hasHeightForWidth())
        self.ExportToWavePanelBtn.setSizePolicy(sizePolicy)
        self.ExportToWavePanelBtn.setObjectName("ExportToWavePanelBtn")
        self.WavePanelLayout.addWidget(self.ExportToWavePanelBtn)
        self.InteractiveLayout.addLayout(self.WavePanelLayout)
        self.LineBetweenFLandIL = QtWidgets.QFrame(parent=SchedulerForm)
        self.LineBetweenFLandIL.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.LineBetweenFLandIL.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.LineBetweenFLandIL.setObjectName("LineBetweenFLandIL")
        self.InteractiveLayout.addWidget(self.LineBetweenFLandIL)
        self.FileBtnLayout = QtWidgets.QVBoxLayout()
        self.FileBtnLayout.setObjectName("FileBtnLayout")
        self.ImportFromFileBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ImportFromFileBtn.sizePolicy().hasHeightForWidth())
        self.ImportFromFileBtn.setSizePolicy(sizePolicy)
        self.ImportFromFileBtn.setAutoDefault(False)
        self.ImportFromFileBtn.setObjectName("ImportFromFileBtn")
        self.FileBtnLayout.addWidget(self.ImportFromFileBtn)
        self.ExportToFileBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ExportToFileBtn.sizePolicy().hasHeightForWidth())
        self.ExportToFileBtn.setSizePolicy(sizePolicy)
        self.ExportToFileBtn.setObjectName("ExportToFileBtn")
        self.FileBtnLayout.addWidget(self.ExportToFileBtn)
        self.InteractiveLayout.addLayout(self.FileBtnLayout)
        self.LineBetweenWLandFL = QtWidgets.QFrame(parent=SchedulerForm)
        self.LineBetweenWLandFL.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.LineBetweenWLandFL.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.LineBetweenWLandFL.setObjectName("LineBetweenWLandFL")
        self.InteractiveLayout.addWidget(self.LineBetweenWLandFL)
        self.InitiateLayout = QtWidgets.QVBoxLayout()
        self.InitiateLayout.setObjectName("InitiateLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ScanArgBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ScanArgBtn.sizePolicy().hasHeightForWidth())
        self.ScanArgBtn.setSizePolicy(sizePolicy)
        self.ScanArgBtn.setObjectName("ScanArgBtn")
        self.horizontalLayout.addWidget(self.ScanArgBtn)
        self.InitBtn = QtWidgets.QPushButton(parent=SchedulerForm)
        self.InitBtn.setObjectName("InitBtn")
        self.horizontalLayout.addWidget(self.InitBtn)
        self.InitiateLayout.addLayout(self.horizontalLayout)
        self.ExecutionProgressBar = QtWidgets.QProgressBar(parent=SchedulerForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ExecutionProgressBar.sizePolicy().hasHeightForWidth())
        self.ExecutionProgressBar.setSizePolicy(sizePolicy)
        self.ExecutionProgressBar.setProperty("value", 24)
        self.ExecutionProgressBar.setObjectName("ExecutionProgressBar")
        self.InitiateLayout.addWidget(self.ExecutionProgressBar)
        self.InteractiveLayout.addLayout(self.InitiateLayout)
        self.verticalLayout.addLayout(self.InteractiveLayout)

        self.retranslateUi(SchedulerForm)
        QtCore.QMetaObject.connectSlotsByName(SchedulerForm)

    def retranslateUi(self, SchedulerForm):
        _translate = QtCore.QCoreApplication.translate
        SchedulerForm.setWindowTitle(_translate("SchedulerForm", "计划表"))
        self.TableEditBtn.setText(_translate("SchedulerForm", "编辑"))
        self.TableDeleteBtn.setText(_translate("SchedulerForm", "删除"))
        self.TableCopyBtn.setText(_translate("SchedulerForm", "复制"))
        self.TableCutBtn.setText(_translate("SchedulerForm", "剪切"))
        self.TablePasteBtn.setText(_translate("SchedulerForm", "粘贴"))
        self.ImportFromWavePanelBtn.setText(_translate("SchedulerForm", "从波形界面导入"))
        self.ExportToWavePanelBtn.setText(_translate("SchedulerForm", "导出到波形界面"))
        self.ImportFromFileBtn.setText(_translate("SchedulerForm", "从文件导入"))
        self.ExportToFileBtn.setText(_translate("SchedulerForm", "导出到文件"))
        self.ScanArgBtn.setText(_translate("SchedulerForm", "扫描所选项目"))
        self.InitBtn.setText(_translate("SchedulerForm", "启动"))
