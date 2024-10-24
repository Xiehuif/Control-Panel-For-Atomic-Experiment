from PyQt6 import QtWidgets
from DataStructure import DataManager
from enum import Enum

import ModifiedQWidgets.GeneralWidgets.ParameterAcquireDialog as ParameterAcquireDialog

'''

    2024/10/8 ： 评价： 屎。。。
                 当时怎么这么写的 。。。

    FINISHED: 重构 分离为ParameterAcquireDialog 和 本类 以实现参数获取窗口复用
    
    2024/10/8 :  完成重构

'''


class SelectorController:

    class StaticClarification(Enum):
        titleClarification = ['标题', str]

    def __init__(self, deviceQList: QtWidgets.QListWidget, waveQList: QtWidgets.QListWidget):
        self.deviceQList = deviceQList
        self.waveQList = waveQList
        deviceNameList: list[str] = DataManager.deviceHandlerInstance.GetObjectNames()
        self.deviceQList.addItems(deviceNameList)
        self.deviceQList.currentRowChanged.connect(self._LoadWaveList)
        self.parameterPanel = None

    def GetCurrentDevice(self) -> DataManager.Device | None:
        currentItem = self.deviceQList.currentItem()
        if currentItem is None:
            currentItem = self.deviceQList.item(0)
        if currentItem is None:
            print('No registered device')
            return None
        return DataManager.deviceHandlerInstance.GetObject(currentItem.text())

    # slot
    def _LoadWaveList(self):
        self.waveQList.clear()
        targetDevice: DataManager.Device = self.GetCurrentDevice()
        outputModes: dict = targetDevice.GetOutputModes()
        for mode in outputModes:
            waveName = mode
            item = QtWidgets.QListWidgetItem(waveName)
            item.setData(100,outputModes[mode])
            self.waveQList.addItem(item)

    def GetCurrentDataEnum(self):
        item = self.waveQList.currentItem()
        if item is None:
            print('You haven\'t selected any item in wavetype list')
            return None
        dataEnum = item.data(100)
        return dataEnum

    def ShowParameterPanel(self, waveData: DataManager.WaveData, confirmAction) -> bool:
        dataEnum = self.GetCurrentDataEnum()
        if dataEnum is None:
            return False
        else:
            # 构建enumClass的List，这些class指示了应该收集的参数
            enumClassList = [self.GetCurrentDataEnum().value[1], self.StaticClarification]
            # 预设，如果是对已有的WaveData做修改，那么应该由presetting
            presetting = None
            # 获取预设
            if waveData is not None and waveData.parameter is not None:
                presetting = waveData.parameter.copy()
                presetting.update({self.StaticClarification.titleClarification: waveData.title})
            # 基于Dialog收集的信息创造一个Parameter
            argsDialog = ParameterAcquireDialog.AcquireDialog(enumClassList, presetting)
            newData = argsDialog.Activate()
            if newData is None:
                return False
            # 向WaveData中应用
            waveData.title = newData.get(self.StaticClarification.titleClarification)
            newData.pop(self.StaticClarification.titleClarification)
            waveData.parameter = newData
            waveData.type = self.GetCurrentDataEnum()
            # 调用回调
            confirmAction()
        return True


