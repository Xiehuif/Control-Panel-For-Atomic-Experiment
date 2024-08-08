import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
import LinkListStructure
import ModifiedLabels
import MultiselectionManager
from QSSConstant import QSSPresetting
import DataManager


class WaveBlock:
    # internal methods

    def _ApplyQSS(self, label: ModifiedLabels.SelectableLabel):
        '''
        一个用于应用QSS表的内部函数，在生成Label时使用
        :param label: 被应用样式表的组件
        :return:
        '''
        label.SetQSS(ModifiedLabels.DisplayState.coveredBy, QSSPresetting.CoverBy)
        label.SetQSS(ModifiedLabels.DisplayState.standBy, QSSPresetting.StandBy)
        label.SetQSS(ModifiedLabels.DisplayState.selected, QSSPresetting.Selected)
        label.RefreshDisplay(False)

    def _ApplyText(self, label: ModifiedLabels.SelectableLabel, title: str, duration: str, detail: str):
        textSet: str = title + '\n'
        textSet = textSet + duration + '\n'
        textSet = textSet + detail + '\n'
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
    def ResizeLength(self, length: float):
        '''
        重新定义这个信号的时常
        :param length: 时间长度
        :return:
        '''
        policyControl = QtWidgets.QSizePolicy.Policy
        self.timeScale = length
        selfTimescale = length
        self._blockLabel.setSizePolicy(policyControl.Fixed, policyControl.Expanding)
        widgetSize: QtCore.QSize = self.timeLine.scrollArea.size()
        fullWidth = widgetSize.width()
        fullTimeScale = self.timeLine.GetTimescale()
        selfWidth = selfTimescale / fullTimeScale * fullWidth
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
        self._ApplyText(self._blockLabel, self.title, self.duration, self.detail)
        #应用样式表
        self._ApplyQSS(self._blockLabel)
        #应用事件
        self._ApplyEvent(self._blockLabel)
        #应用大小
        self.ResizeLength(self.waveData.duration)
        return self._blockLabel

    def __init__(self, waveData: DataManager.WaveData, timeline):
        '''
        以Label形式显示一段信号
        :param waveData: 被显示的信号输出模块
        '''
        self.waveData = waveData
        self.title = str(waveData.type)
        self.duration = str(waveData.duration)
        self.detail = str(waveData.parameter)
        self._blockLabel: (ModifiedLabels.SelectableLabel or None) = None
        self.timeLine = timeline


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
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.layout.addSpacerItem(self.spacer)

    def _ClearWidget(self):
        while len(self.blockList) != 0:
            self.blockList.pop().Clear()
        self.selectionManager.Clear()

    def _LoadWaveIntoLayout(self, waveData: DataManager.WaveData):
        waveBlock = WaveBlock(waveData,self)
        self.blockList.append(waveBlock)
        targetLabel = waveBlock.GenerateLabel()
        self.layout.addWidget(targetLabel)
        targetLabel.show()

    # public
    def GetTimescale(self):
        return self.timeScale

    def SetTimescale(self, newTimescale: int):
        self.timeScale = newTimescale

    def __init__(self, scrollArea: QtWidgets.QScrollArea,schedule: DataManager.DeviceSchedule, timeScale: float = 80):
        # 显示属性
        self.timeScale = timeScale
        self.scrollArea = scrollArea
        self._InitializeWidget()

        # 操作逻辑
        self.blockList: list[WaveBlock] = []
        self._schedule: DataManager.DeviceSchedule = schedule
        self._scheduleData = schedule.schedule
        self.selectionManager = MultiselectionManager.SelectionManager()

    def SetSchedule(self, newSchedule: DataManager.DeviceSchedule):
        self._schedule.schedule.SetPointer(0)
        self._ClearWidget()
        self._schedule = newSchedule
        self.blockList = []
        self.ShowBlocks()

    def GetSchedule(self) -> DataManager.DeviceSchedule:
        return self._schedule

    def ShowBlocks(self):
        self._ClearWidget()
        print('Timeline Refresh its display：\n'
              'Detected Block Number：' + str(self._scheduleData.GetLength()))
        self._scheduleData.SetPointer(0)
        if self._scheduleData.GetDataFromPointedNode() is None:
            print('Timeline null')
            return
        self._LoadWaveIntoLayout(self._scheduleData.GetDataFromPointedNode())
        while self._scheduleData.PointerMoveForward():
            self._LoadWaveIntoLayout(self._scheduleData.GetDataFromPointedNode())
        self._ResetSpacer()
