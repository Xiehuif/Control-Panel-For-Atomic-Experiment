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

    def ScheduleSerialization(self) -> list|None:
        self.scheduleData.SetPointer(0)
        if self.scheduleData.GetDataFromPointedNode() is None:
            print('null schedule:' + self.device.deviceName)
            return None
        else:
            dataList = []
            dataStr = self.scheduleData.GetDataFromPointedNode().Serialize()
            dataList.append(dataStr)
            while self.scheduleData.PointerMoveForward():
                dataStr = self.scheduleData.GetDataFromPointedNode().Serialize()
                dataList.append(dataStr)
            return dataList

    def ScheduleDeserialization(self,dataStrList:list):
        size = len(dataStrList)
        self.scheduleData = LinkList()
        self.scheduleData.SetPointer(0)
        for i in range(0,size):
            waveData = WaveData(dataStrList[i])
            self.AddWave(waveData)


class Device:
    def __init__(self,deviceName:str,deviceOutputMode):
        self.deviceName = deviceName
        self.deviceOutputMode = deviceOutputMode
        self.deviceSchedule = DeviceSchedule(self)

    def GetPlotMethod(self,waveData:WaveData):
        return lambda : 0

    def GetOutputModes(self) -> dict:
        outputModes = {}
        for outputModeItem,outputModeValue in self.deviceOutputMode.__members__.items():
            outputName:str = outputModeValue.value[0]
            outputModeDataEnum = outputModeValue
            outputModes.update({outputName: outputModeDataEnum})
        return outputModes

    def DeviceSerialization(self) -> dict:
        scheduleStrList = self.deviceSchedule.ScheduleSerialization()
        targetDict = {}
        targetDict.update({self.deviceName: scheduleStrList})
        return targetDict


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

    def GetDevice(self,deviceName:str):
        for existedDeviceName in self.devices:
            if existedDeviceName == deviceName:
                return self.devices.get(deviceName)
        return None


deviceHandlerInstance = DeviceHandler()