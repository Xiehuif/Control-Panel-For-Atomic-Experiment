
from LinkListStructure import LinkList
import enum


class WaveData:
    def __init__(self,duration:float,type,parameter,title='default'):
        self.duration = duration
        self.type = type
        self.parameter = parameter
        self.title = title

class DeviceSchedule:
    def __init__(self,device):
        self.device = device
        self.scheduleData: LinkList = LinkList()

    def AddWave(self,wave:WaveData):
        self.scheduleData.SetPointer(self.scheduleData.GetLength()-1)
        self.scheduleData.AppendDataAfterPointer(wave)

    def DeleteWave(self,wave:WaveData):
        return self.scheduleData.DeleteData(wave)

    def GetAttachedDevice(self):
        return self.device

class Device:
    def __init__(self,deviceName:str,deviceOutputMode,deviceSchedule:DeviceSchedule):
        self.deviceName = deviceName
        self.deviceOutputMode = deviceOutputMode
        self.deviceSchedule = deviceSchedule

    def GetPlotMethod(self,waveData:WaveData):
        return lambda : 0

    def GetOutputModes(self) -> dict:
        outputModes = {}
        for outputModeItem,outputModeValue in self.deviceOutputMode.__members__.items():
            outputName:str = outputModeValue.value[0]
            outputModeDataEnum = outputModeValue.value[1]
            outputModes.update({outputName: outputModeDataEnum})
        return outputModes




class DeviceHandler:
    def __init__(self):
        self.devices = {}
        self.devicesNameList = []

    def RegisterDevice(self,device:Device):
        self.devicesNameList.append(device.deviceName)
        self.devices.update({device.deviceName:device})

    def GetDevices(self) -> list[Device]:
        deviceList:[Device] = []
        for deviceName in self.devices:
            deviceList.append(self.devices[deviceName])
        return deviceList


deviceHandlerInstance = DeviceHandler()