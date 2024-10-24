from PyQt6 import QtCore, QtWidgets

from DataStructure import LogManager, MultiselectionManager, DataManager
import ModifiedQWidgets.GeneralWidgets.ModifiedLabels as ModifiedLabels
from ModifiedQWidgets.WaveFrontendWidgets.QSSConstant import QSSWaveBlockPresetting
from ModifiedQWidgets.WaveFrontendWidgets import DeviceSelector

class WaveBlock:
    # internal methods

    def _ApplyQSS(self, label: ModifiedLabels.SelectableLabel):
        """
        一个用于应用QSS表的内部函数，在生成Label时使用
        :param label: 被应用样式表的组件
        :return:
        """
        label.SetQSS(ModifiedLabels.DisplayState.coveredBy, QSSWaveBlockPresetting.CoverBy)
        label.SetQSS(ModifiedLabels.DisplayState.standBy, QSSWaveBlockPresetting.StandBy)
        label.SetQSS(ModifiedLabels.DisplayState.selected, QSSWaveBlockPresetting.Selected)
        label.RefreshDisplay(False)

    def _ApplyText(self, label: ModifiedLabels.SelectableLabel, title: str, duration: str, detail: str, index: int):
        textSet: str = title + '\n'
        textSet = textSet + '序号:{}'.format(index) + '\n'
        textSet = textSet + duration + '\n'
        textSet = textSet + detail
        label.setWordWrap(False)
        label.setText(textSet)

    def _GetChangeState(self):
        return not self._blockLabel.IsSelected()

    def _ApplyEvent(self, label: ModifiedLabels.SelectableLabel):
        label.eventHandler.BindEvent(QtCore.QEvent.Type.Enter, label.RefreshDisplay, args=lambda: True,
                                     info=lambda: 'Enter')
        label.eventHandler.BindEvent(QtCore.QEvent.Type.Leave, label.RefreshDisplay, args=lambda: False,
                                     info=lambda: 'Leave')
        label.eventHandler.BindEvent(QtCore.QEvent.Type.MouseButtonRelease, label.SetSelectState,
                                     args=self._GetChangeState)

    # public methods
    def ResizeLength(self, length: float,minimunSizeRatio: float = 0.1):

        """
        重新定义这个Label的长度
        :param length: 时间长度
        :param minimunSizeRatio: 每一个时间块所占最小比例
        :return:
        """

        # 控件伸缩规则 纵向宽度可延伸 横向长度固定
        policyControl = QtWidgets.QSizePolicy.Policy
        self._blockLabel.setSizePolicy(policyControl.Fixed, policyControl.Expanding)
        # 时间条控件尺寸获取
        widgetSize: QtCore.QSize = self.timeLine.scrollArea.size()
        # 计算所需长度比例
        fullWidth = widgetSize.width()
        selfTimescale = length
        fullTimeScale = self.timeLine.GetTimescale()
        sizeRatio = selfTimescale / fullTimeScale
        # 检查是否符合最小比例要求
        if minimunSizeRatio > sizeRatio:
            sizeRatio = minimunSizeRatio
        # 计算像素级别尺寸
        selfWidth = sizeRatio * fullWidth
        # 应用到当前label
        label: ModifiedLabels.SelectableLabel = self._blockLabel
        label.setFixedWidth(int(selfWidth))

    def Clear(self):
        '''
        清空Label
        :return: None
        '''
        if self._blockLabel is not None:
            self.timeLine.selectionManager.Unregister(self._blockLabel)
            self._blockLabel.deleteLater()
            del self._blockLabel

    def GenerateLabel(self) -> ModifiedLabels.SelectableLabel:
        '''
        根据注册的信息返回一个Label控件
        :return: 目标Label
        '''
        state = False
        if self._blockLabel is not None:
            state = self._blockLabel.IsSelected()
        #清空组件 生成组件 应用缓存的状态
        self.Clear()
        self._blockLabel = ModifiedLabels.SelectableLabel(self.timeLine.centralWidget, self.timeLine.selectionManager,
                                                          self.waveData)
        self._blockLabel.SetSelectState(state)
        #应用文字描述
        self._ApplyText(self._blockLabel, self.title, str(self.duration), self.detail, self.index)
        #应用样式表
        self._ApplyQSS(self._blockLabel)
        #应用事件
        self._ApplyEvent(self._blockLabel)
        #应用大小
        self.ResizeLength(self.duration)
        return self._blockLabel

    __slots__ = ('waveData', 'title', 'detail', 'duration', '_blockLabel', 'timeLine', 'index')

    def __init__(self, waveData: DataManager.WaveData, timeline, duration, index):
        '''
        以Label形式显示一段信号
        :param waveData: 被显示的信号输出模块
        '''
        self.waveData = waveData
        self.title = waveData.title
        self.duration = duration
        self.detail = str(waveData.type.value[0])
        self._blockLabel: (ModifiedLabels.SelectableLabel or None) = None
        self.timeLine = timeline
        self.index = index


class TimelinesController:
    # internal
    def _ResetSpacer(self):
        self.layout.removeItem(self.spacer)
        self.spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.layout.addSpacerItem(self.spacer)

    def _InitializeWidget(self):
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollArea.setWidget(self.centralWidget)
        self.centralWidget.setStyleSheet('background-color:white;')
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.layout.setSpacing(0)
        self.spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.layout.addSpacerItem(self.spacer)

    def _ClearWidget(self):
        while len(self.blockList) != 0:
            self.blockList.pop().Clear()
        self.selectionManager.Clear()

    def _LoadWaveIntoLayout(self, waveData: DataManager.WaveData, index: int = -1):
        waveBlock = WaveBlock(waveData,self,self.deviceSelector.GetCurrentDevice().GetDuration(waveData), index)
        self.blockList.append(waveBlock)
        targetLabel = waveBlock.GenerateLabel()
        self.layout.addWidget(targetLabel)
        targetLabel.show()

    # public
    def GetTimescale(self):
        return self.timeScale

    def SetTimescale(self, newTimescale: int):
        self.timeScale = newTimescale

    def __init__(self, scrollArea: QtWidgets.QScrollArea, selector: DeviceSelector.SelectorController, timeScale: float = 80):
        # 显示属性
        self.timeScale = timeScale
        self.scrollArea = scrollArea
        self._InitializeWidget()

        # 数据接口
        self.blockList: list[WaveBlock] = []
        self.deviceSelector = selector
        self._scheduleData: list[DataManager.WaveData] = selector.GetCurrentDevice().deviceSchedule.scheduleData
        self.selectionManager = MultiselectionManager.SelectionManager()

        #绑定刷新
        self.deviceSelector.deviceQList.currentItemChanged.connect(self.ShowBlocks)

    def ShowBlocks(self):
        # 获取当前时间表
        self._scheduleData: list[DataManager.WaveData] = self.deviceSelector.GetCurrentDevice().deviceSchedule.scheduleData
        self._ClearWidget()
        self.blockList = []
        length = len(self._scheduleData)
        # 添加Label
        LogManager.Log('Timeline Refresh its display：\n'
              'Detected Block Number：' + str(length))
        if length == 0:
            LogManager.Log('Timeline null')
            return
        for i in range(0, length):
            self._LoadWaveIntoLayout(self._scheduleData[i], i)
        self._ResetSpacer()
