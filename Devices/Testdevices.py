import numpy as np

import DataManager
import enum

import LogManager
from DataManager import WaveData
import numpy

class SineOutputData(enum.Enum):
    Period = ['频率',float]
    Phase = ['初始相位',float]
    Duration = ['时长',float]

class SquareOutputData(enum.Enum):
    Period = ['周期',float]
    DutyCycle = ['占空比',float]
    Duration = ['时长',float]

class DemoOutput(enum.Enum):
    Sine = ['正弦输出',SineOutputData]
    Square = ['方波输出',SquareOutputData]

def SquareWaveValue(time,period,dutyCycle):
    if (time % period) < period * dutyCycle:
        return 1
    else:
        return 0


class test(DataManager.Device):
    def GetDuration(self,waveData:WaveData) -> float:
        parameter: dict = waveData.parameter
        duration = 0.0
        if waveData.type == DemoOutput.Sine:
            duration = parameter.get(DemoOutput.Sine.value[1].Duration)
        elif waveData.type == DemoOutput.Square:
            duration = parameter.get(DemoOutput.Square.value[1].Duration)
        else:
            super().GetDuration(waveData)
        return duration

    def GetPlotMethod(self,waveData:WaveData):
        type = waveData.type
        parameter: dict = waveData.parameter
        if type == DemoOutput.Sine:
            period = parameter.get(SineOutputData.Period)
            phase = parameter.get(SineOutputData.Phase)
            return lambda x : numpy.sin(2 * np.pi * period * x + phase)
        if type == DemoOutput.Square:
            period = parameter.get(SquareOutputData.Period)
            dutyCycle = parameter.get(SquareOutputData.DutyCycle)
            return lambda x:SquareWaveValue(x,period,dutyCycle)
        else:
            return super().GetPlotMethod(waveData)

    def __init__(self):
        output = DemoOutput
        super().__init__('test1',output)

    def DeviceAwake(self):
        LogManager.Log('设备已唤醒...' + self.deviceName)

    def DeviceRun(self):
        LogManager.Log('设备正运行...' + self.deviceName)

DataManager.deviceHandlerInstance.RegisterObject(test())