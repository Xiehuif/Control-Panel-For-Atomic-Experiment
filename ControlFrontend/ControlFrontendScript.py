# third-party libs or system libs
import json

import PyQt6
from PyQt6 import QtWidgets,QtGui,QtCore
from PyQt6.QtCore import QIODevice,QTextStream

import ControlPanel
import sys

# Data control
import DataManager
import DevicesImport

# Modified widgets
import TimelinePlotWidget
import DeviceSelector
import Timeline
import ModifiedLabels

class ControlFrontEnd(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        # parent init
        super().__init__()

        # 连接事件
        form = ControlPanel.Ui_MainWindow()
        form.setupUi(self)
        form.AddOperationBtn.clicked.connect(self.AddBlcokTest)
        form.DeleteOperationBtn.clicked.connect(self.DeleteBlockTest)
        form.Open.triggered.connect(self.OpenFileAction)
        form.Save.triggered.connect(self.SaveFileAction)
        form.ApplyTimescaleBtn.clicked.connect(self.SetTimelineTimescale)

        # 暴露接口
        self.timeScaleEdit = form.TimescaleSetting
        self.addBtn = form.AddOperationBtn
        self.delBtn = form.DeleteOperationBtn
        self.modBtn = form.ModifyOperationBtn
        self.insBtn = form.InsertOperationBtn

        # 控件控制
        self.selector = DeviceSelector.SelectorController(form.OutputDeviceList, form.WaveTypeList)
        self.deviceHandler = DataManager.deviceHandlerInstance
        self.timeLineController = Timeline.TimelinesController(form.TimeLine, self.selector)
        self.plotController = TimelinePlotWidget.TimelinePlotWidgetController(form.waveView,self.timeLineController)
        self.timeLineController.selectionManager.BindSelectionChangeEvent(self.ButtonStateCheck)
        self.ButtonStateCheck()

    def ButtonStateCheck(self):
        selectionMgr = self.timeLineController.selectionManager
        # del btn
        if len(selectionMgr.GetSelected()) == 0:
            self.delBtn.setEnabled(False)
        else:
            self.delBtn.setEnabled(True)
        # ins btn
        if len(selectionMgr.GetSelected()) != 1:
            self.modBtn.setEnabled(False)
            self.insBtn.setEnabled(False)
        else:
            self.modBtn.setEnabled(True)
            self.insBtn.setEnabled(True)

    def SetTimelineTimescale(self):
        newTimescale = self.timeScaleEdit.value()
        if newTimescale > 0:
            self.timeLineController.SetTimescale(newTimescale)
            self.timeLineController.ShowBlocks()
        else:
            closeButton = QtWidgets.QMessageBox.StandardButton.Close
            title = '参数错误'
            message: str = '必须为正'
            result = QtWidgets.QMessageBox.critical(self, title, message, closeButton)

    def OpenFileAction(self):
        # 呼出文件调用窗口
        fileDirList = QtWidgets.QFileDialog.getOpenFileName(self, '打开文件')
        targetStr = None
        if fileDirList is not None:
            # 打开文件并读取
            fileDir = fileDirList[0]
            fileDevice = QtCore.QFile(fileDir)
            if fileDevice.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
                textStream = QTextStream(fileDevice)
                textStream.setEncoding(QtCore.QStringEncoder.Encoding.Utf8)
                targetStr = textStream.readAll()
                fileDevice.close()
            else:
                print('文件打开失败')
                return
        if targetStr is None:
            print('未知读取错误')
        else:
            # 反序列化json为文本字典
            deviceStrDict = json.loads(targetStr)
            # 提交各设备进行波形数据的反序列化

            

    def SaveFileAction(self):
        # 呼出文件调用窗口
        fileDirList = QtWidgets.QFileDialog.getSaveFileName(self, '保存文件')
        if fileDirList is not None:
            # 设备及波形信息序列化
            deviceList = self.deviceHandler.GetDevices()
            targetDict = {}
            for device in deviceList:
                deviceStrDict = device.DeviceSerialization()
                targetDict.update(deviceStrDict)
            targetStr = json.dumps(targetDict)

            # 获取文件保存位置，打开并写入
            fileDir = fileDirList[0]
            fileDevice = QtCore.QFile(fileDir)
            if fileDevice.open(QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text):
                textStream = QTextStream(fileDevice)
                textStream.setEncoding(QtCore.QStringEncoder.Encoding.Utf8)
                textStream << targetStr
                fileDevice.close()
            else:
                print('文件打开失败')


    def RefreshUI(self):
        self.timeLineController.ShowBlocks()
        self.plotController.ReplotDevicesAsynchronously()

    def AddBlcokTest(self):
        waveData = DataManager.WaveData(10, None, 'None')
        self.selector.ShowParameterPanel(waveData,self.Insert)

    def Insert(self, waveData: DataManager.WaveData):
        self.selector.GetCurrentDevice().deviceSchedule.AddWave(waveData)
        self.RefreshUI()

    def DeleteBlockTest(self):
        deletedWaveLabel:list[ModifiedLabels.SelectableLabel] = self.timeLineController.selectionManager.GetSelected()
        while len(deletedWaveLabel) != 0:
            deletedWave: DataManager.WaveData = deletedWaveLabel.pop().attachedObject
            self.selector.GetCurrentDevice().deviceSchedule.DeleteWave(deletedWave)
        self.RefreshUI()

# program entrance
if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = ControlFrontEnd()
    panel.show()
    sys.exit(app.exec())


