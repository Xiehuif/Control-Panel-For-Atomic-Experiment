import matplotlib.lines
import numpy as np
from enum import Enum

import PyQt6
from PyQt6 import QtWidgets,QtCore,QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class FunctionPlotBuffer:
    """
    为分段函数提供绘图支持
    """

    class BufferDataType(Enum):
        """
        一个块内正常状态下应持有的的各数据的定义
        """
        function = 'func'
        lowerBound = 'lb'
        upperBound = 'ub'

    def CheckDefinitionDomainByArea(self,lowerXValue:float,higherXValue:float):
        """
        用于检查特定区间是否存在定义，所有区间均视为开区间
        :param lowerXValue:
        :param higherXValue:
        :return: 若无定义返回None，否则返回定义所碰撞的块
        """
        if lowerXValue >= higherXValue:
            print('Invalid')
            return None
        for i in self.bufferList:
            block:dict = i
            lower = block.get(self.BufferDataType.lowerBound)
            upper = block.get(self.BufferDataType.upperBound)
            if not ((lower < upper <= lowerXValue) or (higherXValue <= lower < upper)):
                return block
        return None


    def CheckValueDefinitionDomainByValue(self,xValue:float) -> dict|None:
        """
        用于检查特定值是否存在定义
        :param xValue: 检查的值
        :return: 若无定义，返回None；若有定义，返回定义所在的块
        """
        for i in self.bufferList:
            block:dict = i
            lower = block.get(self.BufferDataType.lowerBound)
            upper = block.get(self.BufferDataType.upperBound)
            if upper > xValue > lower:
                return i
        return None

    def AddBufferBlock(self,function,lowerBound:float,upperBound:float):
        """
        为Buffer添加一个块，这个块在lowerBound和upperBound之间为Buffer提供定义，返回值为function
        :param function: 定义函数
        :param lowerBound: 上界
        :param upperBound: 下界
        :return: None
        """
        if upperBound <= lowerBound:
            print('BUFFER:Invalid Parameter,upperbound lower than lowerBound')
            return
        if self.CheckDefinitionDomainByArea(lowerBound,upperBound) is not None:
            print('BUFFER:Multiple definition')
            return
        block = {}
        block.update({self.BufferDataType.function: function})
        block.update({self.BufferDataType.lowerBound: lowerBound})
        block.update({self.BufferDataType.upperBound: upperBound})
        self.bufferList.append(block)

    def GetValue(self,xValue:float):
        """
        根据写入的块确定Buffer在xValue的值
        :param xValue: 自变量 x
        :return: 因变量 y,若无定义，返回 0
        """
        block = self.CheckValueDefinitionDomainByValue(xValue)
        if block is None:
            return 0
        else:
            return block.get(self.BufferDataType.function)(xValue)

    def GetDefinitionDomainRange(self) -> tuple:
        if len(self.bufferList) == 0:
            return 0,0
        lower = self.bufferList[0].get(self.BufferDataType.lowerBound)
        upper = self.bufferList[0].get(self.BufferDataType.upperBound)
        for i in self.bufferList:
            item:dict = i
            if lower > item.get(self.BufferDataType.lowerBound):
                lower = item.get(self.BufferDataType.lowerBound)
            if upper < item.get(self.BufferDataType.upperBound):
                upper = item.get(self.BufferDataType.upperBound)
        return lower,upper


    def __init__(self):
        self.bufferList: [dict] = []
        return


class PlotWidgetController:
    # entrance
    def __init__(self,parent:QtWidgets.QWidget):
        # init figure
        self.canvas = FigureCanvas()
        self.figure = self.canvas.figure
        self.toolbar = NavigationToolbar(self.canvas)

        # bind qt widget
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolbar)
        parent.setLayout(self.layout)

        # init subplot
        self.subplot = self.figure.add_subplot()

        # data structure
        self.lineList: [matplotlib.lines.Line2D] = []
        self.colorDict = matplotlib.colors.TABLEAU_COLORS
        self.occupiedColor: dict[matplotlib.lines.Line2D] = {}

    # private
    def _GetRandomUnoccupiedColor(self) -> str:
        for color in self.colorDict:
            codeStr: str = color
            if codeStr not in self.occupiedColor.values():
                return codeStr
        return 'black'

    def _DistributeColor(self,line:matplotlib.lines.Line2D):
        color = self._GetRandomUnoccupiedColor()
        self.occupiedColor.update({line:color})
        line.set_color(color)

    def _ExecuteFunction(self, function, x):
        # 调试用接口
        y = function(x)
        return y

    def _GenerateVectorByFunction(self,func,xVector):
        size = xVector.size
        y = []
        for i in range(0,size):
            y.append(func(xVector[i]))
        return np.array(y)

    # public
    def PlotBuffer(self,buffer:FunctionPlotBuffer,title:str = 'default'):
        rangeTuple = buffer.GetDefinitionDomainRange()
        lower = rangeTuple[0]
        upper = rangeTuple[1]
        return self.PlotFunction(buffer.GetValue,lower,upper,label=title)

    def GetSubplot(self):
        return self.subplot

    def SetTitle(self,title:str = 'Title',xAxisTitle:str = 'X Axis',yAxisTitle = 'Y Axis'):
        self.subplot.set_title(title)
        self.subplot.set_xlabel(xAxisTitle)
        self.subplot.set_ylabel(yAxisTitle)

    def PlotFunction(self,y,lowerBound:float,upperBound:float,resolution:int = 1000,label= 'default'):
        #self._ExecuteFunction(y, xValue[i])
        xValue = np.linspace(lowerBound,upperBound,resolution)
        yValue = self._GenerateVectorByFunction(y,xValue)
        return self.PlotPoint(xValue,yValue,label)

    def PlotPoint(self,x:np.ndarray,y:np.ndarray,label= 'default'):
        line = self.subplot.plot(x,y,label=label)
        self._DistributeColor(line[0])
        self.lineList.append(line[0])
        self.Replot()
        return line[0]

    def PlotLegend(self):
        self.subplot.legend()

    def Replot(self):
        self.PlotLegend()
        self.canvas.draw()

    def DeleteLine(self,line:matplotlib.lines.Line2D):
        if line in self.lineList:
            self.lineList.remove(line)
            self.occupiedColor.pop(line)
            line.remove()
            self.Replot()
            return True
        else:
            return False
