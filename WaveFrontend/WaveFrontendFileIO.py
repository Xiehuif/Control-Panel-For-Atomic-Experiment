import json

from PyQt6 import QtWidgets

import CheckSelectionWidget
import DataManager
import FileManager
import LogManager


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
            LogManager.Log('WaveIO: Read Err. : Can not read string, you may have canceled your reading action.'
                           'Otherwise, there is an exception have occured.', LogManager.LogType.Error)
        else:
            # 反序列化json为文本字典
            deviceStrDict:dict = json.loads(targetStr)
            deviceDict = {}
            # 生成针对设备的读取对话框
            for device in DataManager.deviceHandlerInstance.GetObjects():
                deviceDict.update({device: device.deviceName})
            CheckDialog = CheckSelectionWidget.CheckWidget(deviceDict, '选择需要读入的设备', parent)
            selectedResult = CheckDialog.ShowItemCheckDialog()
            if selectedResult is None:
                return
            # 进行序列化操作
            for device in DataManager.deviceHandlerInstance.GetObjects():
                # 未在先前的对话框中被选中则跳过
                if selectedResult.get(device) is not True:
                    continue
                # 提交各设备进行波形数据的反序列化
                dataStr = deviceStrDict.get(device.deviceName)
                device.Deserialize(dataStr)
            # 界面刷新回调
            finishedCallback()
        return

    @staticmethod
    def SaveFileAction(parent):
        # 呼出文件调用窗口
        fileDirList = QtWidgets.QFileDialog(parent).getSaveFileName(parent)
        if fileDirList is not None:
            # 创建以设备名为Key，设备的波形计划的序列化字符串为Value的字典
            deviceList = DataManager.deviceHandlerInstance.GetObjects()
            targetDict = {}
            # 对每一个设备都进行序列化操作获取其波形计划的序列化所得字符串并写入字典
            for device in deviceList:
                deviceStr = device.Serialize()
                targetDict.update({device.deviceName: deviceStr})
            # 对
            targetStr = json.dumps(targetDict,indent=4)
            # 获取文件保存位置，打开并写入
            fileDir = fileDirList[0]
            FileManager.SerializableIO.WriteStringToFile(fileDir, targetStr)

class LogIO:

    @staticmethod
    def _NullFunction():
        # 空函数，用于填充空的回调
        return

    @staticmethod
    def SaveFileAction(logData: LogManager.LogData, parent = None):
        # 获得目标文件位置和序列化的对象
        targetStr = logData.Serialize()
        fileDirList = QtWidgets.QFileDialog(parent).getSaveFileName(parent)
        # 写入文件
        if fileDirList is not None:
            fileDir = fileDirList[0]
            FileManager.SerializableIO.WriteStringToFile(fileDir, targetStr)

    @staticmethod
    def OpenFileAction(logData: LogManager.LogData, parent = None, refreshCallBack = None):
        # 获取文件位置
        fileDirList = QtWidgets.QFileDialog(parent).getOpenFileName(parent)
        if fileDirList is not None:
            # 读文件
            fileDir = fileDirList[0]
            targetStr = FileManager.SerializableIO.ReadStringFromFile(fileDir)
            # 空字符串检查
            if targetStr is None:
                return
            # 反序列化
            logData.Deserialize(targetStr)
        # 触发刷新回调
        if refreshCallBack is not None:
            refreshCallBack()

