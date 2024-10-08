from PyQt6 import QtWidgets

import DataManager
import ExperimentScheduleManager
import ItemWidgets
import WavePanelFrontend
from PyTree import TreeNode

class ImportButtons:

    @staticmethod
    def ImportFromWavePanel(itemTree: ItemWidgets.ItemTree):
        importedExperimentItem = ExperimentScheduleManager.ExperimentSchedulerImportedItemData(DataManager.deviceHandlerInstance)
        itemTree.ImportItem(importedExperimentItem)


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
        exportedNode = itemTree.GetUserData(exportedTableItem)
        exportedExperimentItem: ExperimentScheduleManager.ExperimentSchedulerItemDataBase = exportedNode.GetData()
        exportedExperimentItem.AppliedItemData()
        waveFrontend: WavePanelFrontend.WaveFrontend = frontendFinder.get(WavePanelFrontend.WaveFrontend)
        waveFrontend.RefreshUI()




