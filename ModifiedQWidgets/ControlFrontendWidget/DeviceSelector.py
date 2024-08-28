from PyQt6 import QtWidgets
import DataManager
from enum import Enum

class ParameterWidgetHandler:
    class StaticClarification(Enum):
        titleClarification = ['标题', str]
        durationClarification = ['时长', float]

    def __init__(self, parentController, dataEnum, waveData: DataManager.WaveData, confirmAction):
        self.titleItem = self.StaticClarification.titleClarification
        self.durationItem = self.StaticClarification.durationClarification
        self.controller = parentController
        self.parameterWidget = QtWidgets.QDialog()
        self.parameterWidget.setWindowTitle('参数表')
        self.waveData = waveData
        self.waveData.type = dataEnum
        dataClarifications = self.GetDataClarifications(dataEnum)
        self.collector = self.SetWidgetUI(self.parameterWidget,dataClarifications)
        self.confirmAction = confirmAction
        self.parameterWidget.exec()



    def GetDataClarifications(self,dataEnum) -> list:
        dataClarifications = []
        for clarificationName,clarification in dataEnum.value[1].__members__.items():
            dataClarifications.append(clarification)
        return dataClarifications


    def SetWidgetUI(self,widget:QtWidgets.QWidget,dataClarifications:list) -> dict:
        dataCollector = {}
        mainLayout = QtWidgets.QVBoxLayout()
        widget.setLayout(mainLayout)
        # 时长 和 标题
        mainLayout.addLayout(self.CreateItemUI(self.durationItem,dataCollector))
        mainLayout.addLayout(self.CreateItemUI(self.titleItem,dataCollector))
        # 其他数据
        for clarification in dataClarifications:
            mainLayout.addLayout(self.CreateItemUI(clarification,dataCollector))
        checkButton = QtWidgets.QPushButton('确认')
        cancelButton = QtWidgets.QPushButton('取消')
        mainLayout.addWidget(checkButton)
        mainLayout.addWidget(cancelButton)
        checkButton.clicked.connect(self.Check)
        cancelButton.clicked.connect(self.Cancel)
        return dataCollector

    def Check(self):
        parameter = {}
        closeButton = QtWidgets.QMessageBox.StandardButton.Close
        for target in self.collector:
            editLine: QtWidgets.QLineEdit = target
            content: str = editLine.text()
            # 处理标题 和 时长
            if self.collector[target] == self.StaticClarification.titleClarification:
                self.waveData.title = content
            elif self.collector[target] == self.StaticClarification.durationClarification:
                try:
                    duration = float(content)
                except ValueError:
                    result = self._ParameterConvertErrorDialog(self.collector[target].value[0], content, str(type),
                                                               closeButton)
                    if result == closeButton:
                        return
                self.waveData.duration = duration
            else:
                # 处理一般参数
                type = self.collector[target].value[1]
                try:
                    parameterValue = type(content)
                except ValueError:
                    result = self._ParameterConvertErrorDialog(self.collector[target].value[0], content, str(type),
                                                               closeButton)
                    if result == closeButton:
                        return
                parameter.update({self.collector[target]: parameterValue})
        self.waveData.parameter = parameter
        self.confirmAction(self.waveData)
        self.parameterWidget.close()

    def _ParameterConvertErrorDialog(self,parameterName:str,content:str,type:str,closeButton:QtWidgets.QMessageBox.StandardButton) -> QtWidgets.QMessageBox.StandardButton:
        icon = QtWidgets.QMessageBox.Icon.Critical
        title = '参数错误'
        message: str = ('在处理参数： ' + parameterName
                        + ' 时,读取到值为：' + content + '，无法转换类型到： '
                        + type
                        + ' ，请检查格式是否匹配')
        result = QtWidgets.QMessageBox.critical(self.parameterWidget, title, message, closeButton)
        return result


    def Cancel(self):
        del self.waveData
        self.parameterWidget.close()

    def CreateItemUI(self,clarification,collector) -> QtWidgets.QHBoxLayout:
        itemLayout = QtWidgets.QHBoxLayout()
        name = clarification.value[0]
        itemLayout.addWidget(QtWidgets.QLabel(name))
        editLine = QtWidgets.QLineEdit()
        collector.update({editLine:clarification})
        itemLayout.addWidget(editLine)
        return itemLayout



class SelectorController:
    def __init__(self,deviceQList:QtWidgets.QListWidget,waveQList:QtWidgets.QListWidget):
        self.deviceQList = deviceQList
        self.waveQList = waveQList
        self.deviceNameList = DataManager.deviceHandlerInstance.devicesNameList
        self.deviceQList.addItems(self.deviceNameList)
        self.deviceQList.currentRowChanged.connect(self._LoadWaveList)
        self.parameterPanel = None


    def GetCurrentDevice(self) -> DataManager.Device:
        currentItem = self.deviceQList.currentItem()
        if currentItem is None:
            currentItem = self.deviceQList.item(0)
        if currentItem is None:
            print('No regstered device')
            return None
        return DataManager.deviceHandlerInstance.devices.get(currentItem.text())

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

    def ShowParameterPanel(self, waveData: DataManager.WaveData, confirmAction):
        dataEnum = self.GetCurrentDataEnum()
        if dataEnum is None:
            return None
        else:
            self.parameterPanel = ParameterWidgetHandler(self,dataEnum,waveData,confirmAction)
        return None


