"""
该文件意在针对不同的数据类型给出一些插值算法，并使得这些插值算法能以非常良好的可读性编写并被程序调用
以便灵活地生成不同的实验参数配置
"""
from enum import Enum

import numpy as np

from DataStructure import ParameterGeneratorsManager


class LinearParameterGenerator(ParameterGeneratorsManager.GeneratorBase):

    """
    这是一个实现在某一区间内线性插值的示例
    """

    class Parameters(Enum):
        """
        定义这个算法所需要的参数
        """
        startValue = ['起始值', float]
        endValue = ['结束值', float]
        interpNumber = ['插值次数', int]
        endPoint = ['输入(N/n)以去除端点', str]

    def AllowedType(self) -> tuple | None:
        """
        这个函数将会报告这个方法支持的类型，如果为None，则不做类型检查
        :return: 类型的tuple
        """
        return int, float

    def GetGeneratorName(self) -> str:
        """
        这个函数返回一个字符串以描述这个算法
        :return: 名称的字符串
        """
        return '线性采样'

    def GetGeneratorParameter(self) -> type[Enum]:
        """
        传入定义参数的类
        :return: 目标类
        """
        return self.Parameters

    def ArrayGenerate(self, data: dict) -> list:
        """
        data是用户传入的参数，key是定义参数的类的item，value是key声明参数的的值
        :param data: 参数
        :return: 生成的参数列表
        """
        # 获取输入，这个阶段将输入的数据全部取出
        startValue = data.get(self.Parameters.startValue)
        endValue = data.get(self.Parameters.endValue)
        interpNumber = data.get(self.Parameters.interpNumber)
        endPoint = data.get(self.Parameters.endPoint)
        # 输入参数化，这个阶段将输入的数据转换为程序参数
        includeEndPoint = not (endPoint == 'N' or endPoint == 'n')
        # 运行算法，创建一个包含所有目标值的数组
        return np.linspace(startValue, endValue, interpNumber, includeEndPoint).tolist()

