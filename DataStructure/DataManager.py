import Serialize
import enum
import copy

class WaveData(Serialize.Serializable):
    __slots__ = ('duration', 'type', 'parameter', 'title')
    def CopyFrom(self,waveData):
        self.duration = copy.deepcopy(waveData.duration)
        self.type = copy.deepcopy(waveData.type)
        self.parameter = copy.deepcopy(waveData.parameter)
        self.title = copy.deepcopy(waveData.title)

    def __init__(self,*args):
        # duration:float,type,parameter,title='default'
        if len(args) == 0:
            self.duration = None
            self.type = None
            self.parameter = None
            self.title = None
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
        self._device = device
        self.scheduleData: list[WaveData] = []

    def Reset(self):
        self.scheduleData: list[WaveData] = []

    def AddWave(self,wave:WaveData):
        self.scheduleData.append(wave)

    def DeleteWave(self,wave:WaveData):
        return self.scheduleData.remove(wave)

    def GetAttachedDevice(self):
        return self._device

    def ScheduleSerialization(self) -> list|None:
        length = len(self.scheduleData)
        if length == 0:
            print('null schedule:' + self._device.deviceName)
            return None
        else:
            dataList = []
            for i in range(0,length):
                dataStr = self.scheduleData[i].Serialize()
                dataList.append(dataStr)
            return dataList

    def ScheduleDeserialization(self,dataStrList:list):
        if dataStrList is None:
            self.Reset()
            return
        size = len(dataStrList)
        self.scheduleData: list[WaveData] = []
        for i in range(0,size):
            waveData = WaveData(dataStrList[i])
            self.AddWave(waveData)


class Device:
    def __init__(self,deviceName:str,deviceOutputMode):
        self.deviceName = deviceName
        self.deviceOutputMode = deviceOutputMode
        self.deviceSchedule = DeviceSchedule(self)

    def GetPlotMethod(self,waveData:WaveData):
        """
        此方法由不同Device进行重载从而为不同的Device提供波形绘图功能
        :param waveData: 被绘制的波形
        :return: 用于绘制波形的函数
        """
        return lambda: 0

    def GetDuration(self,waveData:WaveData) -> float:
        """
        此方法由不同的Device进行重载从而预估不同的Device输出不同波形时所需要的时间
        :param waveData: 被评估的波形
        :return: 所用时长
        """
        return 0

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

    def DeviceDeserialization(self,dataStrList:list):
        self.deviceSchedule.ScheduleDeserialization(dataStrList)
        return

    def RunDevice(self):
        '''
        设备运行入口
        :return:
        '''
        return


class DeviceHandler:
    def __init__(self):
        self._devices = {}

    def GetDeviceNames(self) -> list[str]:
        names:[str] = []
        for deviceName in self._devices:
            names.append(deviceName)
        return names

    def RegisterDevice(self,device:Device):
        self._devices.update({device.deviceName:device})

    def GetDevices(self) -> list[Device]:
        deviceList:[Device] = []
        for deviceName in self._devices:
            deviceList.append(self._devices[deviceName])
        return deviceList

    def GetDevice(self,deviceName:str):
        for existedDeviceName in self._devices:
            if existedDeviceName == deviceName:
                return self._devices.get(deviceName)
        return None


deviceHandlerInstance = DeviceHandler()