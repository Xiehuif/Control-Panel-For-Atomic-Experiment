import json

import LogManager
import SerializationManager
import enum
import copy
import cv2

class WaveData(SerializationManager.Serializable):
    __slots__ = ('type', 'parameter', 'title')
    def CopyFrom(self,waveData):
        self.type = copy.deepcopy(waveData.type)
        self.parameter = copy.deepcopy(waveData.parameter)
        self.title = copy.deepcopy(waveData.title)

    def __init__(self,*args):
        # duration:float,type,parameter,title='default'
        '''
        初始化一个WaveData
        :param args: 若只有一项，则默认为Serialize产生的JSON字符串；如果有三项，按顺序为 类型；参数；标题
        '''
        if len(args) == 3:
            self.type = args[0]
            self.parameter = args[1]
            self.title = args[2]
        elif len(args) == 1:
            jsonString = args[0]
            self.Deserialize(jsonString)
        else:
            self.type = None
            self.parameter = None
            self.title = None
            super().__init__()
            
class DeviceSchedule(SerializationManager.Serializable):
    def __init__(self,device):
        self._device = device
        self.scheduleData: list[WaveData] = []
        super().__init__()

    def Reset(self):
        self.scheduleData: list[WaveData] = []

    def AddWave(self,wave:WaveData):
        self.scheduleData.append(wave)

    def DeleteWave(self,wave:WaveData):
        return self.scheduleData.remove(wave)

    def GetAttachedDevice(self):
        return self._device

class Device(SerializationManager.Serializable):
    def __init__(self,deviceName:str,deviceOutputMode):
        self.deviceName = deviceName
        self.deviceOutputMode = deviceOutputMode
        self.deviceSchedule = DeviceSchedule(self)
        super().__init__()

    def GetPlotMethod(self,waveData:WaveData):
        """
        此方法由不同Device进行重载从而为不同的Device提供波形绘图功能
        :param waveData: 被绘制的波形
        :return: 用于绘制波形的函数
        """
        return lambda: 0

    def GetDuration(self,waveData:WaveData) -> float:
        LogManager.Log('Get Duration ERR:Can\'t find duration \n type is ' + str(waveData.type) + ' \n par : \n' +
              str(waveData.parameter), LogManager.LogType.Error)
        """
        此方法由不同的Device进行重载从而为不同的Device输出不同波形时所需要的时间
        必须重载
        :param waveData: 被评估的波形
        :return: 所用时长
        """
        return 10.0

    def GetOutputModes(self) -> dict:
        outputModes = {}
        for outputModeItem,outputModeValue in self.deviceOutputMode.__members__.items():
            outputName:str = outputModeValue.value[0]
            outputModeDataEnum = outputModeValue
            outputModes.update({outputName: outputModeDataEnum})
        return outputModes

    def Serialize(self,encoder: json.JSONEncoder|None = None) -> str:
        return self.deviceSchedule.Serialize(encoder)

    def Deserialize(self,jsonContext :str|None):
        self.deviceSchedule.Deserialize(jsonContext)
        return

    def DeviceAwake(self):
        '''
        设备唤醒
        :return:
        '''
        return

    def DeviceRun(self):
        '''
        设备运行
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