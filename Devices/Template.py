# 依赖项,根据需要添加
import numpy as np
import DataManager
from enum import Enum

# 定义输出波形所需各项数据，注意格式: ['名称',数据类型]
class SineOutputData(Enum):
    Period = ['频率',float]
    Phase = ['初始相位',float]
    Amplitude = ['振幅',float]

class SquareOutputData(Enum):
    Period = ['频率', float]
    InitialTime = ['初始时间', float]
    HigherPeak = ['最大值', float]
    LowerPeak = ['最小值',float]

# 将定义好的数据注册到一个Enum表内，每一行是对应的波形类型和对应的
class DemoOutput(Enum):
    Sine = ['正弦输出',SineOutputData]
    Square = ['方波输出',SquareOutputData]

def SquareWaveValue(time,period,dutyCycle):
    if (time % period) < period * dutyCycle:
        return 1
    else:
        return 0


class test(DataManager.Device):
    def GetPlotMethod(self,waveData:WaveData):
        type = waveData.type
        parameter: dict = waveData.parameter
        if type == SineOutputData:
            period = parameter.get(SineOutputData.Period)
            phase = parameter.get(SineOutputData.Phase)
            return lambda x : numpy.sin(2 * np.pi * period * x + phase)
        if type == SquareOutputData:
            period = parameter.get(SquareOutputData.Period)
            dutyCycle = parameter.get(SquareOutputData.DutyCycle)
            return lambda x:SquareWaveValue(x,period,dutyCycle)
        else:
            return super().GetPlotMethod(waveData)


    def __init__(self):
        output = DemoOutput
        schedule = DataManager.DeviceSchedule(self)
        super().__init__('test1',output,schedule)

class test2(DataManager.Device):
    def __init__(self):
        output = DemoOutput2
        schedule = DataManager.DeviceSchedule(self)
        super().__init__('test2', output, schedule)

    def GetPlotMethod(self,waveData:WaveData):
        type = waveData.type
        parameter: dict = waveData.parameter
        if type == SineOutputData:
            period = parameter.get(SineOutputData.Period)
            phase = parameter.get(SineOutputData.Phase)
            return lambda x : numpy.sin(2 * np.pi * period * x + phase)
        else:
            return super().GetPlotMethod(waveData)


DataManager.deviceHandlerInstance.RegisterDevice(test())
DataManager.deviceHandlerInstance.RegisterDevice(test2())