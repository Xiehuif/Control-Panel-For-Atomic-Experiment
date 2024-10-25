from PyQt6 import QtWidgets

import MultiprocessSupport
from DataStructure import DataManager, ExperimentScheduleManager
import ModifiedQWidgets.ExperimentSchedulerWidgets.ItemWidgets as ItemWidgets
from ModifiedQWidgets.ExperimentSchedulerWidgets import ExperimentItemRunningPanel
from Frontends.WaveFrontend import WavePanelFrontend
from DataStructure.PyTree import TreeNode

class ImportButtons:

    @staticmethod
    def ImportFromWavePanel(itemTree: ItemWidgets.ItemTree):
        nameDialog = QtWidgets.QInputDialog()
        outputList = nameDialog.getText(None, '名称', '请确定一个名称')
        if not outputList[1]:
            return
        name = outputList[0]
        rootItem = ExperimentScheduleManager.ExperimentSchedulerImportedItemData(DataManager.deviceHandlerInstance)
        rootItem.SetName(name)
        itemTree.ImportRootItem(rootItem)

    @staticmethod
    def DeriveFromCurrentItems(itemTree: ItemWidgets.ItemTree, widget = None):
        # 获得被选中选项
        selectedList = itemTree.GetSelectedItems()
        selectedTreeNodes = []
        targetTree = None
        # 是否为空，若是，暂停流程
        if len(selectedList) == 0:
            title = '拒绝操作'
            message: str = '没有选择任何目标'
            closeButton = QtWidgets.QMessageBox.StandardButton.Close
            result = QtWidgets.QMessageBox.warning(None, title, message, closeButton)
            return
        # 对每一项检查是否有根节点
        for item in selectedList:
            itemTreeNode: TreeNode = itemTree.GetUserData(item)
            if targetTree is None:
                targetTree = itemTreeNode.GetTree()
            elif targetTree is not itemTreeNode.GetTree():
                title = '拒绝操作'
                message: str = '不能对用户导入的不同节点或这些节点的子节点进行统一的派生子节点的操作'
                closeButton = QtWidgets.QMessageBox.StandardButton.Close
                result = QtWidgets.QMessageBox.critical(None, title, message, closeButton)
                return
            selectedTreeNodes.append(itemTreeNode)
        # 获取根节点及其所存储的数据
        rootItem: ExperimentScheduleManager.ExperimentSchedulerImportedItemData = targetTree.GetRoot().GetData()
        copiedData = {}
        rootItem.GetData(copiedData)
        # 名称输入
        deriveWidget = ItemWidgets.ItemDeriveWidget(copiedData, widget)
        nameDialog = QtWidgets.QInputDialog()
        outputList = nameDialog.getText(None, '名称', '请确定一个名称')
        # 检验输入是否为空或者被用户取消
        if not outputList[1]:
            return
        name = outputList[0]
        # 获取用户界面模块和插值算法导出的实验数据项
        returnValue: list[ExperimentScheduleManager.ExperimentSchedulerDerivedItemData] = deriveWidget.Activate()
        # 检验导出是否为空，或者被用户取消
        if returnValue is None:
            return
        # 应用输入的名称
        for item in returnValue:
            item.SetName(name)
        # 将所有数据项导入到系统
        for parentNode in selectedTreeNodes:
            itemTree.InsertDerivedItems(parentNode, returnValue)


class ExportButtons:

    @staticmethod
    def ExportToWavePanel(itemTree: ItemWidgets.ItemTree, frontendFinder: dict):
        # 获得被选中选项
        selectedList = itemTree.GetSelectedItems()
        if len(selectedList) != 1:
            # 不合法数据
            return
        # 注意结构： 列表项目所绑定数据是Node类型，Node类型携带数据是目标的Item，Item及其父类所携带的数据应用到DataManager
        # 的handlerInstance后重新刷新WavePanel才完成导出
        exportedTableItem: QtWidgets.QTreeWidgetItem = selectedList[0]
        exportedNode: TreeNode = itemTree.GetUserData(exportedTableItem)
        exportedExperimentItem: ExperimentScheduleManager.ExperimentSchedulerItemDataBase = exportedNode.GetData()
        exportedExperimentItem.AppliedItemData()
        waveFrontend: WavePanelFrontend.WaveFrontend = frontendFinder.get(WavePanelFrontend.WaveFrontend)
        waveFrontend.RefreshUI()

class RunningButton:

    @staticmethod
    def ExecutionCurrentItems(itemTree: ItemWidgets.ItemTree, runningPanel: ExperimentItemRunningPanel.RunningPanel):
        selectedItems = itemTree.GetSelectedItems()
        itemTree.SetFrontendEditable(False)
        runningPanel.DispatchExperimentItemFromUI(selectedItems)
        taskManager = MultiprocessSupport.ExperimentProcess.taskManagerInstance
        taskManager.RunTasks(lambda :itemTree.SetFrontendEditable(True))



