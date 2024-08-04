import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
import LinkListStructure


class WaveBlock:


    def GetLabelObject(self) -> QtWidgets.QLabel:
        return self._blockLabel

    def GenerateLabel(self) -> QtWidgets.QLabel :
        self._blockLabel.deleteLater()
        self._blockLabel = QtWidgets.QLabel()
        self._blockLabel.size = self.size
        textSet : str = self.title
        policyControl = QtWidgets.QSizePolicy.Policy
        self._blockLabel.setSizePolicy(policyControl.Expanding, policyControl.Expanding)
        for i in range(0, len(self._featureDetail)):
            textSet = textSet + '\n' + self._featureDetail[i]
        self._blockLabel.setWordWrap(False)
        self._blockLabel.setText(textSet)
        return self._blockLabel

    def ShowLabel(self):
        self.GetLabelObject().show()

    def __init__(self,title : str,featureDetail : list,size : QtCore.QSize = None):
        self.title = title
        self._featureDetail = featureDetail
        self.size = size
        self._blockLabel = QtWidgets.QLabel()
        self.GenerateLabel()

    def GetSize(self) -> QtCore.QSize:
        return self._blockLabel.size()

    def OnClicked(self):
        pass
        # To be done : respond click

    def Modify(self):
        pass
        # To be done : respond move(if necessary)


class TimelinesContorller:


    def _ClearWidgets(self):
        self.layout.deleteLater()
        self.centralWidget.deleteLater()
        self.scrollArea.deleteLater()

    def __init__(self,scrollArea : QtWidgets.QScrollArea):
        self.scrollArea = scrollArea
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.scrollArea.setWidget(self.centralWidget)
        self.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.blockList = LinkListStructure.LinkList()
        self.spacer = QtWidgets.QSpacerItem(1,1,QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Minimum)

    def AddWave(self,title : str,featureDetail : list):
        wave : WaveBlock = WaveBlock(title,featureDetail)
        self.blockList.SetPointer(self.blockList.GetLength())
        self.blockList.AppendDataAfterPointer(wave)

    def _LoadWaveIntoLayout(self,waveBlock : WaveBlock):
        self.layout.addWidget(waveBlock.GenerateLabel())
        waveBlock.ShowLabel()

    def ShowBlocks(self):
        self.blockList.SetPointer(0)
        self._LoadWaveIntoLayout(self.blockList.GetDataFromPointedNode())
        while self.blockList.PointerMoveForward() :
            self._LoadWaveIntoLayout(self.blockList.GetDataFromPointedNode())
        self.layout.removeItem(self.spacer)
        self.spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.layout.addSpacerItem(self.spacer)

    def DeleteWave(self):
        pass
        # To be done

