# third-party libs or system libs
from PyQt6 import QtWidgets,QtCore,QtGui
from artiq.experiment import *

import DataManager
import DeviceSelector
import LogManager
import ModifiedLabels
import MultiselectionManager
import Timeline
import TimelinePlotWidget


class ButtonBehavior:

    @staticmethod
    def SetTimelineTimescale(parent, timeScaleEdit, timeLineController):
        newTimescale = timeScaleEdit.value()
        if newTimescale > 0:
            timeLineController.SetTimescale(newTimescale)
            timeLineController.ShowBlocks()
        else:
            closeButton = QtWidgets.QMessageBox.StandardButton.Close
            title = '参数错误'
            message: str = '必须为正'
            result = QtWidgets.QMessageBox.critical(parent, title, message, closeButton)

    @staticmethod
    def ButtonStateCheck(delBtn, modBtn, insBtn, selectionManager):
        selectionMgr = selectionManager
        # del btn
        if len(selectionMgr.GetSelected()) == 0:
            delBtn.setEnabled(False)
        else:
            delBtn.setEnabled(True)
        # ins btn
        if len(selectionMgr.GetSelected()) != 1:
            modBtn.setEnabled(False)
            insBtn.setEnabled(False)
        else:
            modBtn.setEnabled(True)
            insBtn.setEnabled(True)

    @staticmethod
    def AddWaveBlock(selector, refreshUICallback):
        waveData = DataManager.WaveData()
        selector.ShowParameterPanel(waveData, lambda: selector.GetCurrentDevice().deviceSchedule.AddWave(waveData))
        refreshUICallback()

    @staticmethod
    def DeleteWaveBlock(selectionManager: MultiselectionManager.SelectionManager,
                        selector: DeviceSelector.SelectorController, refreshCallBack):
        deletedWaveLabel:list[ModifiedLabels.SelectableLabel] = selectionManager.GetSelected()
        while len(deletedWaveLabel) != 0:
            deletedWave: DataManager.WaveData = deletedWaveLabel.pop().attachedObject
            selector.GetCurrentDevice().deviceSchedule.DeleteWave(deletedWave)
        refreshCallBack()

    @staticmethod
    def _InsertWaveData(targetDevice: DataManager.Device,
                       selectedWaveData: DataManager.WaveData, newWaveData: DataManager.WaveData, refreshCallback):
        index = targetDevice.deviceSchedule.scheduleData.index(selectedWaveData)
        targetDevice.deviceSchedule.scheduleData.insert(index, newWaveData)
        refreshCallback()

    @staticmethod
    def InsertWaveBlock(selectionManager, selector, refreshCallback):
        selectedWaveLabels = selectionManager.GetSelected()
        if len(selectedWaveLabels) != 1:
            return
        selectedWaveData: DataManager.WaveData = selectedWaveLabels[0].attachedObject
        newWaveData: DataManager.WaveData = DataManager.WaveData()
        selector.ShowParameterPanel(newWaveData,
                                    lambda: ButtonBehavior._InsertWaveData(
                                        selector.GetCurrentDevice(),selectedWaveData, newWaveData, refreshCallback
                                    ))

    @staticmethod
    def InitiateDevice():
        for device in DataManager.deviceHandlerInstance.GetObjects():
            device.DeviceAwake()
        for device in DataManager.deviceHandlerInstance.GetObjects():
            device.DeviceRun()

    @staticmethod
    def ModifyWaveBlock(selectionManager: MultiselectionManager.SelectionManager,
                        selector: DeviceSelector.SelectorController,
                        refreshCallback):
        selectedWaveLabels = selectionManager.GetSelected()
        if len(selectedWaveLabels) != 1:
            return
        selectedWaveData = selectedWaveLabels[0].attachedObject
        newWaveData = DataManager.WaveData()
        newWaveData.CopyFrom(selectedWaveData)
        selector.ShowParameterPanel(newWaveData, lambda :selectedWaveData.CopyFrom(newWaveData))
        refreshCallback()

    @staticmethod
    def ShowPanel(panel: QtWidgets.QWidget):
        if panel.isVisible():
            LogManager.Log("Panel has already been opened", LogManager.LogType.Runtime)
            return
        else:
            panel.show()


