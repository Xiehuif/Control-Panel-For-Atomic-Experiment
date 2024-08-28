# 依赖项,根据需要添加
import numpy as np
import DataManager
from enum import Enum
from DataManager import WaveData

# 定义不同输出类型波形所需各项数据，注意格式: 数据集合 = ['数据名称',数据类型]
class SineOutputData(Enum):
    Period = ['频率',float]
    Phase = ['初始相位',float]
    Amplitude = ['振幅',float]

class SquareOutputData(Enum):
    Period = ['频率', float]
    InitialTime = ['初始时间', float]
    DutyCycle = ['占空比', float]
    HigherPeak = ['最大值', float]
    LowerPeak = ['最小值',float]

# 将定义好的数据注册到一个Enum表内，每一行都是一个输出类型，注意格式： 输出 = ['输出名称',数据集合]
class DemoOutput(Enum):
    Sine = ['正弦输出',SineOutputData]
    Square = ['方波输出',SquareOutputData]

# 新建设备类
class DemoDevice(DataManager.Device):

    # 初始化设备，注意参数格式

    def __init__(self):
        # 第一个参数是设备显示及索引的名称，注意设备的类名可以重复，但是这一显示及索引的名称在所有存在的设备里必须是唯一的
        # 这个用于显示或索引的名称可以是中文，但是不推荐，中文可能带来性能或兼容性问题
        # 第二个参数是上面先定义好的参数表
        super().__init__('demo',DemoOutput)

    # 这个函数定义了波形图如何绘制，针对不同类型的波形需要返回一个绘制函数
    # 对于一个波形而言，他的最左端自变量为0
    # 最右端自变量等于其 duration （持续时间）
    # 经由这个关系，返回给出0 - duration期间内波型对每一个t对应的函数值的函数

    def GetPlotMethod(self,waveData:WaveData):
        type = waveData.type
        parameter: dict = waveData.parameter
        if type == DemoOutput.Sine:
            period = parameter.get(SineOutputData.Period)
            phase = parameter.get(SineOutputData.Phase)
            amp = parameter.get(SineOutputData.Amplitude)
            # 直接返回 A sin(2 \pi T + \phi)
            return lambda x: amp * np.sin(2 * np.pi * period * x + phase)
        if type == DemoOutput.Square:
            period = parameter.get(SquareOutputData.Period)
            higherPeak = parameter.get(SquareOutputData.HigherPeak)
            lowerPeak = parameter.get(SquareOutputData.LowerPeak)
            initialTime = parameter.get(SquareOutputData.InitialTime)
            dutyCycle = parameter.get(SquareOutputData.DutyCycle)
            # 这个有更复杂的逻辑，另外写一个函数
            return lambda x: self.SquareWaveValue(x, period, higherPeak, lowerPeak, initialTime, dutyCycle)
        else:
            return super().GetPlotMethod(waveData)

    def SquareWaveValue(timeValue,period,higherPeak,lowerPeak,initialTime,dutyCycle):
        if ((timeValue + initialTime) % period < period * dutyCycle):
            return higherPeak
        else:
            return lowerPeak

# 注册设备
DataManager.deviceHandlerInstance.RegisterDevice(DemoDevice())

# 在DevicesImport中Import该文件以使该设备生效