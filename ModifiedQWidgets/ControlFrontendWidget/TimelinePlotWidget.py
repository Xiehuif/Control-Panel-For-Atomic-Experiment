from PyQt6 import QtWidgets

import PlotWidget
import Timeline
import DataManager
import matplotlib
class TimelinePlotWidgetController(PlotWidget.PlotWidgetController):
    def __init__(self,timelinePlotWidget:QtWidgets.QWidget,timeline:Timeline.TimelinesController):
        super().__init__(timelinePlotWidget)
        self.timeline = timeline
        self.timeline.selectionManager.BindSelectionChangeEvent(self.ReplotDevices)
        self.deviceHandler = DataManager.deviceHandlerInstance
        self.bufferDict = {}
        self.plotLines = []

    def _AddDeviceBuffer(self,device:DataManager.Device,bufferDict:dict):
        selectedDevice = self.timeline.deviceSelector.GetCurrentDevice()
        selectedLabel = self.timeline.selectionManager.GetSelected()
        deviceScheduleData = device.deviceSchedule.scheduleData
        deviceScheduleData.SetPointer(0)
        timeRecord = 0.0
        cycleCondition = True
        if device == selectedDevice:
            # 分类 区分高亮和普通
            highlightBuffer = PlotWidget.FunctionPlotBuffer()
            normalBuffer = PlotWidget.FunctionPlotBuffer()
            bufferDict.update({-1 : highlightBuffer})
            bufferDict.update({device.deviceName:normalBuffer})
            while deviceScheduleData.GetDataFromPointedNode() is not None and cycleCondition:
                targetData : DataManager.WaveData = deviceScheduleData.GetDataFromPointedNode()
                func = device.GetPlotMethod(targetData)
                isSelected = False
                for label in selectedLabel:
                    isSelected = (label.attachedObject == targetData)
                if isSelected:
                    highlightBuffer.AddBufferBlock(func,timeRecord,timeRecord + targetData.duration)
                else:
                    normalBuffer.AddBufferBlock(func,timeRecord,timeRecord + targetData.duration)
                timeRecord = timeRecord + targetData.duration
                cycleCondition = deviceScheduleData.PointerMoveForward()
        else:
            buffer = PlotWidget.FunctionPlotBuffer()
            bufferDict.update({device.deviceName:buffer})
            while deviceScheduleData.GetDataFromPointedNode() is not None and cycleCondition:
                targetData : DataManager.WaveData = deviceScheduleData.GetDataFromPointedNode()
                func = device.GetPlotMethod(targetData)
                buffer.AddBufferBlock(func,timeRecord,timeRecord + targetData.duration)
                timeRecord = timeRecord + targetData.duration
                cycleCondition = deviceScheduleData.PointerMoveForward()

    def RefreshBufferDict(self):
        self.bufferDict = {}
        for device in self.deviceHandler.GetDevices():
            self._AddDeviceBuffer(device,self.bufferDict)

    def ReplotDevices(self):
        for line in self.plotLines:
            self.DeleteLine(line)
        currentDeviceName = self.timeline.deviceSelector.GetCurrentDevice().deviceName
        itemDeviceName = 'None'
        self.RefreshBufferDict()
        for i in self.bufferDict:
            if i == -1:
                itemDeviceName = currentDeviceName + ':被选取'
            else:
                itemDeviceName = i
            buffer = self.bufferDict[i]
            line = self.PlotBuffer(buffer,itemDeviceName)
            self.plotLines.append(line)








