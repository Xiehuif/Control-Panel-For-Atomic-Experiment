import matplotlib.lines
import numpy as np
from enum import Enum

import PyQt6
from PyQt6 import QtWidgets,QtCore,QtGui
from PyQt6.QtCore import QThread,QThreadPool,QRunnable
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtcairo import FigureCanvasQTCairo as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.legend_handler import HandlerTuple
import cProfile
import LogManager

matplotlib.rcParams['font.family'] = 'SimHei'  # 或其他支持中文的字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
matplotlib.use('qtcairo')
LogManager.Log(matplotlib.get_backend())


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
        :param lowerXValue: 区间下界
        :param higherXValue: 区间上界
        :return: 若无定义返回None，否则返回定义所碰撞的块
        """
        if lowerXValue >= higherXValue:
            LogManager.Log('Invalid X value: lower x gt. higher x', LogManager.LogType.Error)
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
        self.groupDict: dict[str] = {}
        self.colorDict = matplotlib.colors.TABLEAU_COLORS
        self.occupiedColor: dict[str] = {}
        self.threadPool = QThreadPool.globalInstance()
        self._breakPoints = {}

        # performance analysis (be used only for debugging or optimization)

    # private
    def _GenerateVectorByFunctionSyn(self,func,xVector):
        size = xVector.size
        y = []
        for i in range(0,size):
            y.append(func(xVector[i]))
        return np.array(y)

    def _RegisterGroup(self,line:matplotlib.lines.Line2D,groupName:str):
        if groupName not in self.groupDict:
            self.groupDict.update({groupName: []})
        self.groupDict.get(groupName).append(line)

    def _GetRandomUnoccupiedColor(self) -> str:
        for color in self.colorDict:
            codeStr: str = color
            if codeStr not in self.occupiedColor.values():
                return codeStr
        return 'black'

    def _ExecuteFunction(self, function, x):
        # 调试用接口
        y = function(x)
        return y

    class _FunctionComputationThread(QRunnable):
        def __init__(self,func,xVector,yVector,indexStart,indexEnd):
            self.func = func
            self.xVector = xVector
            self.indexStart = indexStart
            self.indexEnd = indexEnd
            self.yVector = yVector
            super().__init__()

        def run(self):
            for i in range(self.indexStart,self.indexEnd):
                self.yVector[i] = self.func(self.xVector[i])

    def _GenerateVectorByFunction(self,func,xVector,threadNumber = 16):
        size = xVector.size
        y = [0]*size
        computationSizeOfEachThread = int(size / threadNumber)
        residualTask = size - (computationSizeOfEachThread * threadNumber)
        for i in range(0,threadNumber):
            if i == threadNumber - 1:
                thread = self._FunctionComputationThread(func,xVector,y,i * computationSizeOfEachThread,
                                                         (i+1) * computationSizeOfEachThread + residualTask)
                self.threadPool.start(thread)
            else:
                thread = self._FunctionComputationThread(func,xVector,y,i * computationSizeOfEachThread,
                                                         (i+1) * computationSizeOfEachThread)
                self.threadPool.start(thread)
        self.threadPool.waitForDone()
        return np.array(y)

    def _GetBreakPoint(self,groupName: str) -> tuple|None:
        if groupName in self._breakPoints:
            return self._breakPoints.get(groupName)
        else:
            return None

    def _SetBreakPoint(self,groupName: str,breakPoint: tuple):
        self._breakPoints.update({groupName: breakPoint})

    # public
    def GetColor(self,groupName:str):
        if groupName in self.occupiedColor:
            return self.occupiedColor.get(groupName)
        else:
            color = self._GetRandomUnoccupiedColor()
            self.occupiedColor.update({groupName: color})
            return color

    def ShowLegend(self):
        lineList = []
        titleList = []
        for title in self.groupDict:
            lineGroup = self.groupDict.get(title)
            lineGroupTuple = tuple(lineGroup)
            lineList.append(lineGroupTuple)
            titleList.append(title)
        self.subplot.legend(lineList, titleList, numpoints=1, handler_map={tuple: HandlerTuple(None)}, loc='upper right')

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

    def PlotFunction(self,y,lowerBound:float,upperBound:float,resolutionRate:int = 50,label= 'default',breakPointGroupName = None):
        #self._ExecuteFunction(y, xValue[i])
        resolution = int((upperBound - lowerBound) * resolutionRate)
        xValue = np.linspace(lowerBound,upperBound,resolution)
        yValue = self._GenerateVectorByFunction(y,xValue)
        return self.PlotPoint(xValue,yValue,label,breakPointGroupName)

    def PlotPoint(self,x:np.ndarray,y:np.ndarray,label= 'default',breakPointGroupName = None):
        if breakPointGroupName is None:
            breakPointGroupName = label
        color = self.GetColor(label)
        breakPoint = self._GetBreakPoint(breakPointGroupName)
        plotX = None
        plotY = None
        if breakPoint is not None:
            plotX = np.hstack((breakPoint[0], x))
            plotY = np.hstack((breakPoint[1], y))
        else:
            plotX = x
            plotY = y
        newBreakPoint = (plotX[plotX.size - 1],plotY[plotY.size - 1])
        self._SetBreakPoint(breakPointGroupName,newBreakPoint)
        line = self.subplot.plot(plotX,plotY,label=label,color=color)
        self._RegisterGroup(line[0],label)
        return line[0]

    def ClearPlot(self):
        groupNameList = []
        for groupName in self.groupDict:
            groupNameList.append(groupName)
        for groupName in groupNameList:
            self.DeleteGroup(groupName)
        groupNameList.clear()
        for groupName in self._breakPoints:
            groupNameList.append(groupName)
        for groupName in groupNameList:
            self._breakPoints.pop(groupName)

    def DrawPlot(self):
        self.ShowLegend()
        self.canvas.draw()

    def DeleteGroup(self,groupName:str):
        if groupName in self.groupDict:
            lineList = self.groupDict.pop(groupName)
            for item in lineList:
                line:matplotlib.lines.Line2D = item
                line.remove()
        if groupName in self.occupiedColor:
            self.occupiedColor.pop(groupName)
        if groupName in self._breakPoints:
            self._breakPoints.pop(groupName)

