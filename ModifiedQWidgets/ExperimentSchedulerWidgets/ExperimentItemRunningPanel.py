import cProfile

from PyQt6 import QtWidgets

import MultiprocessSupport.ExperimentProcess
from DataStructure import LogManager
from DataStructure.PyTree import TreeNode
from MultiprocessSupport import *
from DataStructure.ExperimentScheduleManager import ExperimentSchedulerItemDataBase
from ModifiedQWidgets.ExperimentSchedulerWidgets.ItemWidgets import ItemTree


class RunningPanel:

    def __init__(self, itemTree: ItemTree, progressBar: QtWidgets.QProgressBar):
        self._itemTree = itemTree
        self._progressBar = progressBar
        self._indexDict = {}

    def StateChange(self, dataTuple):
        index = dataTuple[0]
        state = dataTuple[1]
        uiItem = self._indexDict.get(index)
        self._itemTree.ChangeRunningState(uiItem, state)

    def TaskFinished(self, dataTuple):
        # 解析数据
        index = dataTuple[0]
        returnValue = dataTuple[1]
        # 返回值处理
        for deviceName in returnValue:
            LogManager.Log('Device:{} return {}'.format(deviceName, returnValue.get(deviceName)))

    def DispatchExperimentItemFromUI(self, items: list[QtWidgets.QTreeWidgetItem]):
        taskManager = MultiprocessSupport.ExperimentProcess.taskManagerInstance
        taskManager.SetStateChangeCallback(self.StateChange)
        taskManager.Reset()
        for item in items:
            nodeItem: TreeNode = self._itemTree.GetUserData(item)
            expItem: ExperimentSchedulerItemDataBase = nodeItem.GetData()
            index = MultiprocessSupport.ExperimentProcess.taskManagerInstance.PutTask(expItem, self.TaskFinished)
            self._indexDict.update({index: item})
