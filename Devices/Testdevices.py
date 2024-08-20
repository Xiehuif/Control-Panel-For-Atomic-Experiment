import numpy as np

import DataManager
import enum

from DataManager import WaveData
import numpy

class SineOutputData(enum.Enum):
    Period = ['频率',float]
    Phase = ['初始相位',float]

class SquareOutputData(enum.Enum):
    Period = ['周期',float]
    DutyCycle = ['占空比',float]

class DemoOutput(enum.Enum):
    Sine = ['正弦输出',SineOutputData]
    Square = ['方波输出',SquareOutputData]

class TriangleOutput(enum.Enum):
    Period = ['频率',float]
    DutyCycle = ['占空比',float]
    InitialValue = ['初值',float]

class DemoOutput2(enum.Enum):
    Triangle = ['三角波输出',TriangleOutput]
    Sine = ['正弦输出',SineOutputData]



class test(DataManager.Device):
    def GetPlotMethod(self,waveData:WaveData):
        type = waveData.type
        parameter: dict = waveData.parameter
        if type == SineOutputData:
            period = parameter.get(SineOutputData.Period)
            phase = parameter.get(SineOutputData.Phase)
            return lambda x : numpy.sin(2 * np.pi * period * x + phase)

    def __init__(self):
        output = DemoOutput
        schedule = DataManager.DeviceSchedule(self)
        super().__init__('test1',output,schedule)

class test2(DataManager.Device):
    def __init__(self):
        output = DemoOutput2
        schedule = DataManager.DeviceSchedule(self)
        super().__init__('test2', output, schedule)


DataManager.deviceHandlerInstance.RegisterDevice(test())
DataManager.deviceHandlerInstance.RegisterDevice(test2())