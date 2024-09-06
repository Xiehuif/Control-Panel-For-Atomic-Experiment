from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, QMutex

import ModifiedLabels
import PlotWidget
import Timeline
import DataManager
import matplotlib
class TimelinePlotWidgetController(PlotWidget.PlotWidgetController):

    def __init__(self,timelinePlotWidget:QtWidgets.QWidget,timeline:Timeline.TimelinesController):
        super().__init__(timelinePlotWidget)
        self.timeline = timeline
        self.timeline.selectionManager.BindSelectionChangeEvent(self.ReplotDevicesAsynchronously)
        self.deviceHandler = DataManager.deviceHandlerInstance
        self.bufferDict = {}
        self.plotLines = []

    def _AddDeviceBuffer(self,device:DataManager.Device,bufferDict:dict):
        selectedDevice = self.timeline.deviceSelector.GetCurrentDevice()
        selectedLabel = self.timeline.selectionManager.GetSelected()
        deviceScheduleData: list[DataManager.WaveData] = device.deviceSchedule.scheduleData
        length = len(deviceScheduleData)
        timeRecord = 0.0
        cycleCondition = True
        if device == selectedDevice:
            # 分类 区分高亮和普通
            highlightBuffer = PlotWidget.FunctionPlotBuffer()
            normalBuffer = PlotWidget.FunctionPlotBuffer()
            bufferDict.update({-1 : highlightBuffer})
            bufferDict.update({device.deviceName:normalBuffer})
            for i in range(0,length):
                targetData: DataManager.WaveData = deviceScheduleData[i]
                func = device.GetPlotMethod(targetData)
                isSelected = False
                for label in selectedLabel:
                    isSelected = (label.attachedObject == targetData)
                if isSelected:
                    highlightBuffer.AddBufferBlock(func, timeRecord, timeRecord + targetData.duration)
                else:
                    normalBuffer.AddBufferBlock(func, timeRecord, timeRecord + targetData.duration)
                timeRecord = timeRecord + targetData.duration
        else:
            buffer = PlotWidget.FunctionPlotBuffer()
            bufferDict.update({device.deviceName:buffer})
            for i in range(0, length):
                targetData : DataManager.WaveData = deviceScheduleData[i]
                func = device.GetPlotMethod(targetData)
                buffer.AddBufferBlock(func,timeRecord,timeRecord + targetData.duration)
                timeRecord = timeRecord + targetData.duration

    def _PlotWaveData(self,startXValue:float,waveData:DataManager.WaveData,device:DataManager.Device,colorGroupName = None,breakPointGroupName = None):
        endXValue:float = startXValue + waveData.duration
        plotMethod = device.GetPlotMethod(waveData)
        func = lambda x : plotMethod(x - startXValue)
        if colorGroupName == None:
            colorGroupName = device.deviceName
        if breakPointGroupName == None:
            breakPointGroupName = device.deviceName
        self.PlotFunction(func,startXValue,endXValue,label=colorGroupName,breakPointGroupName=breakPointGroupName)

    def _PlotDevice(self,device:DataManager.Device):

        # 数据初始化
        time:float = 0
        currentDeviceName = self.timeline.deviceSelector.GetCurrentDevice()
        isCurrentDevice = (currentDeviceName == device)
        scheduleData : list[DataManager.WaveData] = device.deviceSchedule.scheduleData
        breakCondition = True
        multiselectionMgr = self.timeline.selectionManager
        selectionMark = False
        length = len(scheduleData)
        # 遍历scheduleData中WaveData
        for i in range(0,length):
            waveData: DataManager.WaveData = scheduleData[i]
            selectionMark = False
            if isCurrentDevice:
                for item in multiselectionMgr.GetSelected():
                    label : ModifiedLabels.SelectableLabel = item
                    if label.attachedObject is waveData:
                        selectionMark = True
                if selectionMark:
                    self._PlotWaveData(time,waveData, device, device.deviceName + ':已选中')
                else:
                    self._PlotWaveData(time, waveData, device)
            else:
                self._PlotWaveData(time,waveData,device)
            time = time + waveData.duration

    def RefreshBufferDict(self):
        self.bufferDict = {}
        for device in self.deviceHandler.GetDevices():
            self._AddDeviceBuffer(device,self.bufferDict)

    def ReplotDevicesSynchronously(self):
        self.ClearPlot()
        for device in self.deviceHandler.GetDevices():
            self._PlotDevice(device)

    class PlotThread(QThread):
        def __init__(self,controller):
            self.controller = controller
            super().__init__()
            self.qmut = QMutex()

        def run(self):
            self.qmut.lock()
            print('plot start')
            self.controller.ReplotDevicesSynchronously()
            self.qmut.unlock()

    def ReplotDevicesAsynchronously(self):
        self.ReplotDevicesSynchronously()
        # 多线程会造成无法运行的bug，暂时搁置
        # threadController = self.PlotThread(self)
        # threadController.start(QThread.Priority.LowestPriority)









