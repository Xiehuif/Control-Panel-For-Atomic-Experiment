
from LinkListStructure import LinkList
import Serialize
import enum


class WaveData(Serialize.Serializable):
    def __init__(self,*args):
        # duration:float,type,parameter,title='default'
        if len(args) == 4:
            self.duration = args[0]
            self.type = args[1]
            self.parameter = args[2]
            self.title = args[3]
        if len(args) == 1:
            jsonString = args[0]
            self.Deserialize(jsonString)

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