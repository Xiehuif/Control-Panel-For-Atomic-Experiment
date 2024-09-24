import json

from PyQt6 import QtWidgets

import CheckSelectionWidget
import DataManager
import FileManager


class WaveIO:
    @staticmethod
    def OpenFileAction(parent, finishedCallback):
        # 呼出文件调用窗口
        fileDirList = QtWidgets.QFileDialog(parent).getOpenFileName(parent)
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
            CheckDialog = CheckSelectionWidget.CheckWidget(deviceDict, '选择需要读入的设备', parent)
            selectedResult = CheckDialog.ShowItemCheckDialog()
            if selectedResult is None:
                return
            for device in DataManager.deviceHandlerInstance.GetDevices():
                if selectedResult.get(device) is not True:
                    continue
                # 提交各设备进行波形数据的反序列化
                dataStr = deviceStrDict.get(device.deviceName)
                device.Deserialize(dataStr)
            finishedCallback()
        return

    @staticmethod
    def SaveFileAction(parent):
        # 呼出文件调用窗口
        fileDirList = QtWidgets.QFileDialog(parent).getSaveFileName(parent)
        if fileDirList is not None:
            # 设备及波形信息序列化
            deviceList = DataManager.deviceHandlerInstance.GetDevices()
            targetDict = {}
            for device in deviceList:
                deviceStr = device.Serialize()
                targetDict.update({device.deviceName: deviceStr})
            targetStr = json.dumps(targetDict,indent=4)

            # 获取文件保存位置，打开并写入
            fileDir = fileDirList[0]
            FileManager.SerializableIO.WriteStringToFile(fileDir, targetStr)