import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
import LinkListStructure
import ModifiedLabels
import MultiselectionManager
from QSSConstant import QSSPresetting

class WaveBlock:
    # internal methods

    def _ApplyQSS(self,label : ModifiedLabels.SelectableLabel):
        '''
        一个用于应用QSS表的内部函数，在生成Label时使用
        :param label: 被应用样式表的组件
        :return:
        '''
        label.SetQSS(ModifiedLabels.DisplayState.coveredBy, QSSPresetting.CoverBy)
        label.SetQSS(ModifiedLabels.DisplayState.standBy, QSSPresetting.StandBy)
        label.SetQSS(ModifiedLabels.DisplayState.selected, QSSPresetting.Selected)
        label.RefreshDisplay(False)

    def _ApplyText(self,label:ModifiedLabels.SelectableLabel, title: str, detail: list):
        textSet: str = title
        for i in range(0, len(detail)):
            textSet = textSet + '\n' + detail[i]
        label.setWordWrap(False)
        label.setText(textSet)

    def _GetChangeState(self):
        return not self._blockLabel.IsSelected()

    def _ApplyEvent(self,label: ModifiedLabels.SelectableLabel):
        label.eventHandler.BindEvent(QtCore.QEvent.Type.Enter,label.RefreshDisplay,args=lambda: True, info= lambda: 'Enter')
        label.eventHandler.BindEvent(QtCore.QEvent.Type.Leave,label.RefreshDisplay,args=lambda: False,info= lambda: 'Leave')
        label.eventHandler.BindEvent(QtCore.QEvent.Type.MouseButtonRelease,label.SetSelectState,args= self._GetChangeState)

    # public methods
    def ResizeLength(self,length:int):
        '''
        重新定义这个信号的时常
        :param length: 时间长度
        :return:
        '''
        policyControl = QtWidgets.QSizePolicy.Policy
        self.timeScale = length
        selfTimescale = length
        self._blockLabel.setSizePolicy(policyControl.Fixed, policyControl.Expanding)
        widgetSize:QtCore.QSize = self.timeLine.centralWidget.size()
        fullWidth = widgetSize.width()
        fullTimeScale = self.timeLine.GetTimescale()
        selfWidth = selfTimescale / fullTimeScale * fullWidth
        label : ModifiedLabels.SelectableLabel = self._blockLabel
        label.setFixedWidth(int(selfWidth))

    def Clear(self):
        '''
        这个函数只是用来包装一个清空Label的流程
        :return: None
        '''
        if self._blockLabel is not None:
            self.timeLine.selectionManager.Unregister(self._blockLabel)
            self._blockLabel.deleteLater()
            del self._blockLabel

    def GenerateLabel(self) -> ModifiedLabels.SelectableLabel :
        '''
        根据注册的信息返回一个Label控件
        :return:
        '''
        state = False
        if self._blockLabel is not None:
            state = self._blockLabel.IsSelected()
        #清空组件 生成组件 应用缓存的状态
        self.Clear()
        self._blockLabel = ModifiedLabels.SelectableLabel(self.timeLine.centralWidget,self.timeLine.selectionManager,attachedObject=self)
        self._blockLabel.SetSelectState(state)
        #应用文字描述
        self._ApplyText(self._blockLabel,self.title,self._featureDetail)
        #应用样式表
        self._ApplyQSS(self._blockLabel)
        #应用事件
        self._ApplyEvent(self._blockLabel)
        #应用大小
        self.ResizeLength(self.timeScale)
        return self._blockLabel

    def __init__(self,title : str,featureDetail : list,timeline,timeScale:int = 10):
        '''
        初始化一个信号显示块，这个块将显示一段信号的信息
        :param title: 标题
        :param featureDetail: 详细信息，列表的每一个元素占一行
        :param timeline: 所附属的TimelineController
        :param timeScale: 信号总时长
        '''
        self.title = title
        self._featureDetail = featureDetail
        self.timeScale = timeScale
        self._blockLabel:(ModifiedLabels.SelectableLabel or None) = None
        self.timeLine = timeline


class TimelinesController:
    # internal
    def _ClearWidgets(self):
        self.layout.deleteLater()
        self.centralWidget.deleteLater()
        self.scrollArea.deleteLater()

    def _LoadWaveIntoLayout(self,waveBlock : WaveBlock):
        targetLabel = waveBlock.GenerateLabel()
        self.layout.addWidget(targetLabel)
        targetLabel.show()

    def _DeleteSelectedList(self):
        selectedList :list[ModifiedLabels.SelectableLabel] = self.selectionManager.GetSelected()
        blocksNumber = len(selectedList)
        for i in range(0,blocksNumber):
            self.DeleteWave(selectedList.pop().attachedObject)
        self.ShowBlocks()

    # public
    def GetTimescale(self):
        return self.timeScale

    def SetTimescale(self,newTimescale:int):
        self.timeScale = newTimescale


    def RegisterDeleteButton(self,button : QtWidgets.QPushButton):
        button.clicked.connect(self._DeleteSelectedList)

    def __init__(self,scrollArea : QtWidgets.QScrollArea,timeScale:int = 80):
        self.timeScale = timeScale
        self.scrollArea = scrollArea
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollArea.setWidget(self.centralWidget)
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.blockList = LinkListStructure.LinkList()
        self.spacer = QtWidgets.QSpacerItem(1,1,QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Minimum)
        self.selectionManager = MultiselectionManager.SelectionManager()

    def AddWave(self,title : str,featureDetail : list,time:int = 10):
        wave : WaveBlock = WaveBlock(title,featureDetail,self,time)
        self.blockList.SetPointer(self.blockList.GetLength() - 1)
        self.blockList.AppendDataAfterPointer(wave)

    def ShowBlocks(self):
        print('Timeline Refresh its display：\n'
              'Detected Block Number：' + str(self.blockList.GetLength()))
        self.blockList.SetPointer(0)
        self._LoadWaveIntoLayout(self.blockList.GetDataFromPointedNode())
        while self.blockList.PointerMoveForward() :
            self._LoadWaveIntoLayout(self.blockList.GetDataFromPointedNode())
        self.layout.removeItem(self.spacer)
        self.spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.layout.addSpacerItem(self.spacer)

    def DeleteWave(self,block : WaveBlock) -> bool:
        block.Clear()
        return self.blockList.DeleteData(block)




