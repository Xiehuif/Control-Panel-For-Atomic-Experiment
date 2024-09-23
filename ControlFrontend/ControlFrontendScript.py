# third-party libs or system libs
import json
import cProfile

import PyQt6
from PyQt6 import QtWidgets,QtGui,QtCore
from PyQt6.QtCore import QIODevice,QTextStream

import CheckSelectionWidget
import ControlPanel
import sys

# Data control
import DataManager
import DevicesImport
import FileManager
import HTMLGenerator
import LogWidget

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

        form.AddOperationBtn.clicked.connect(self.AddBlockTest)
        form.DeleteOperationBtn.clicked.connect(self.DeleteBlockTest)
        form.ModifyOperationBtn.clicked.connect(self.ModifyBlockTest)
        form.InsertOperationBtn.clicked.connect(self.InsertBlockTest)
        form.ExecuteOperationBtn.clicked.connect(self.ExecutionTest)

        form.Open.triggered.connect(self.OpenFileAction)
        form.Save.triggered.connect(self.SaveFileAction)
        form.ApplyTimescaleBtn.clicked.connect(self.SetTimelineTimescale)

        # 暴露接口
        self.timeScaleEdit = form.TimescaleSetting
        self.addBtn = form.AddOperationBtn
        self.delBtn = form.DeleteOperationBtn
        self.modBtn = form.ModifyOperationBtn
        self.insBtn = form.InsertOperationBtn
        self.logPrinter = form.LogBrowser

        # 控件控制
        self.logController = LogWidget.BrowserController(form.LogBrowser, form.LogType, form.LogInfoTransparencySettingBtn)
        self.selector = DeviceSelector.SelectorController(form.OutputDeviceList, form.WaveTypeList)
        self.deviceHandler = DataManager.deviceHandlerInstance
        self.timeLineController = Timeline.TimelinesController(form.TimeLine, self.selector)
        self.plotController = TimelinePlotWidget.TimelinePlotWidgetController(form.waveView,self.timeLineController)
        self.timeLineController.selectionManager.BindSelectionChangeEvent(self.ButtonStateCheck)
        self.ButtonStateCheck()
        self.logController.RefreshLogDisplay()

    def ExecutionTest(self):
        for device in DataManager.deviceHandlerInstance.GetDevices():
            device.DeviceAwake()
        for device in DataManager.deviceHandlerInstance.GetDevices():
            device.DeviceRun()

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
        fileDirList = QtWidgets.QFileDialog(self).getOpenFileName(self)
        targetStr = None
        if fileDirList is not None:
            # 打开文件并读取
            fileDir = fileDirList[0]
            targetStr = FileManager.SerializableIO.ReadStringFromFile(fileDir)
        if targetStr is None:
            print('未知读取错误')
        else:
            # 反序列化json为文本字典
            deviceStrDict:dict = json.loads(targetStr)
            deviceDict = {}
            for device in DataManager.deviceHandlerInstance.GetDevices():
                deviceDict.update({device: device.deviceName})
            CheckDialog = CheckSelectionWidget.CheckWidget(deviceDict, '选择需要读入的设备', self)
            selectedResult = CheckDialog.ShowItemCheckDialog()
            if selectedResult is None:
                return
            for device in DataManager.deviceHandlerInstance.GetDevices():
                if selectedResult.get(device) is not True:
                    continue
                # 提交各设备进行波形数据的反序列化
                dataStr = deviceStrDict.get(device.deviceName)
                device.Deserialize(dataStr)
            self.RefreshUI()
        return

    def SaveFileAction(self):
        # 呼出文件调用窗口
        fileDirList = QtWidgets.QFileDialog(self).getSaveFileName(self)
        if fileDirList is not None:
            # 设备及波形信息序列化
            deviceList = self.deviceHandler.GetDevices()
            targetDict = {}
            for device in deviceList:
                deviceStr = device.Serialize()
                targetDict.update({device.deviceName: deviceStr})
            targetStr = json.dumps(targetDict,indent=4)

            # 获取文件保存位置，打开并写入
            fileDir = fileDirList[0]
            FileManager.SerializableIO.WriteStringToFile(fileDir, targetStr)

    def RefreshUI(self):
        self.timeLineController.ShowBlocks()
        self.plotController.ReplotDevicesAsynchronously()

    def AddBlockTest(self):
        waveData = DataManager.WaveData()
        self.selector.ShowParameterPanel(waveData,lambda: self.AddWaveData(waveData))
        self.RefreshUI()

    def AddWaveData(self, waveData: DataManager.WaveData):
        self.selector.GetCurrentDevice().deviceSchedule.AddWave(waveData)

    def ModifyBlockTest(self):
        selectedWaveLabels = self.timeLineController.selectionManager.GetSelected()
        if len(selectedWaveLabels) != 1:
            return
        selectedWaveData = selectedWaveLabels[0].attachedObject
        newWaveData = DataManager.WaveData()
        newWaveData.CopyFrom(selectedWaveData)
        self.selector.ShowParameterPanel(newWaveData, lambda :selectedWaveData.CopyFrom(newWaveData))
        self.RefreshUI()

    def DeleteBlockTest(self):
        deletedWaveLabel:list[ModifiedLabels.SelectableLabel] = self.timeLineController.selectionManager.GetSelected()
        while len(deletedWaveLabel) != 0:
            deletedWave: DataManager.WaveData = deletedWaveLabel.pop().attachedObject
            self.selector.GetCurrentDevice().deviceSchedule.DeleteWave(deletedWave)
        self.RefreshUI()

    def InsertBlockTest(self):
        selectedWaveLabels = self.timeLineController.selectionManager.GetSelected()
        if len(selectedWaveLabels) != 1:
            return
        selectedWaveData: DataManager.WaveData = selectedWaveLabels[0].attachedObject
        newWaveData = DataManager.WaveData()
        self.selector.ShowParameterPanel(newWaveData, lambda: self.InsertWaveData(self.selector.GetCurrentDevice(),
                                                                                  selectedWaveData,newWaveData))

    def InsertWaveData(self,targetDevice: DataManager.Device,
                       selectedWaveData:DataManager.WaveData,newWaveData:DataManager.WaveData):
        index = targetDevice.deviceSchedule.scheduleData.index(selectedWaveData)
        targetDevice.deviceSchedule.scheduleData.insert(index, newWaveData)

# program entrance
if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = ControlFrontEnd()
    panel.show()
    exitValue = app.exec()
    sys.exit(exitValue)