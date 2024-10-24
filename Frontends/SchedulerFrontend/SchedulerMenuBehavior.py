import copy

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTreeWidgetItem

from DataStructure import ExperimentScheduleManager, LogManager
from Frontends.SchedulerFrontend import SchedulerFrontend
from ModifiedQWidgets.ExperimentSchedulerWidgets.ItemWidgets import ItemTree
from DataStructure.PyTree import TreeNode, Tree

class SchedulerMenuBehavior:

    @staticmethod
    def _CrossTreeOpration(parentWidget) -> bool:
        msgBox = QtWidgets.QMessageBox()
        clickedButton = msgBox.question(parentWidget, '潜在的数据不匹配',
                                        '你正在跨越根节点实行数据间的迁移操作，注意各项数据并不依靠'
                                        '波形的名字匹配，而是依靠其在队列中的顺序匹配，因此由于根节点内所要操作的目标波形可能发'
                                        '生改变，你可能需要在迁移完成后确认信息完好无误，是否继续？')
        if clickedButton is msgBox.StandardButton.Yes:
            return True
        else:
            return False

    @staticmethod
    def _EditRootItem(parentWidget):
        dialog = QtWidgets.QMessageBox()
        dialog.warning(parentWidget, '拒绝访问根对象', '根对象只能删除，或经由文件、波形界面导入，其余操作一概无效')

    @staticmethod
    def _CopyAction(parentWidget: SchedulerFrontend.ExperimentScheduler) -> tuple | None:
        """
        根据被选中的项，将这些项绑定的TreeNode复制出来
        :param parentWidget: 目标Controller的Manager Widget
        :return: 返回复制结果
        """
        # 变量声明，目标控制器，被选项，和缓存变量
        itemTree = parentWidget.itemTable
        selectedItems = itemTree.GetSelectedItems()
        target = []
        treeImportedFlag = False
        copiedFromTree = None
        # 复制流程
        for item in selectedItems:
            # 获取目标TreeNode
            treeNode: TreeNode = itemTree.GetUserData(item)
            # 验证是否来自同一个Tree对象，若不是则提醒用户是否打断复制流程
            if (copiedFromTree is None) and (treeImportedFlag is False):
                copiedFromTree = treeNode.GetTree()
                treeImportedFlag = True
            elif copiedFromTree is not treeNode.GetTree():
                response = SchedulerMenuBehavior._CrossTreeOpration(parentWidget)
                if not response:
                    return None
                else:
                    copiedFromTree = None
            # 验证是否复制了根节点，若有根节点则打断复制流程并告知用户
            if isinstance(treeNode.GetData(), ExperimentScheduleManager.ExperimentSchedulerImportedItemData):
                LogManager.Log('Refuse to copy imported experiment data', LogManager.LogType.Runtime)
                SchedulerMenuBehavior._EditRootItem(parentWidget)
                return None
            # 通过检验，向缓存中添加复制的节点
            else:
                target.append(copy.deepcopy(treeNode))
        # 完成复制流程，打包输出
        return copiedFromTree, target

    @staticmethod
    def DeleteSelectedItems(itemTree: ItemTree):
        selectedItems = itemTree.GetSelectedItems()
        for item in selectedItems:
            itemTree.DeleteItem(item)

    @staticmethod
    def CopySelectedItems(parentWidget: SchedulerFrontend.ExperimentScheduler):
        # 获取复制结果
        dataTuple = SchedulerMenuBehavior._CopyAction(parentWidget)
        # 解包
        copiedFromTree = dataTuple[0]
        target = dataTuple[1]
        # 验证结果
        if target is None:
            return
        # 应用结果
        parentWidget.copiedItem = target
        parentWidget.copiedFromTree = copiedFromTree

    @staticmethod
    def SliceSelectedItems(parentWidget: SchedulerFrontend.ExperimentScheduler):
        # 获取复制结果
        dataTuple = SchedulerMenuBehavior._CopyAction(parentWidget)
        # 解包
        copiedFromTree = dataTuple[0]
        target = dataTuple[1]
        # 验证结果
        if target is None:
            return
        # 应用结果
        parentWidget.copiedItem = target
        parentWidget.copiedItem = copiedFromTree
        # 获取被选项
        itemTree = parentWidget.itemTable
        selectedItems = itemTree.GetSelectedItems()
        # 删除这些项
        for item in selectedItems:
            itemTree.DeleteItem(item)

    @staticmethod
    def PasteCopiedItems(parentWidget: SchedulerFrontend.ExperimentScheduler):
        """
        粘贴操作
        :param parentWidget: 父控件
        :return: None
        """
        # 2024/10/19: 功能有误
        # 检查粘贴板
        if parentWidget.copiedItem is None:
            return
        # 局部变量声明
        itemTree = parentWidget.itemTable
        parentNodes = []
        crossTreeWarningFlag = False
        targetTree = parentWidget.copiedFromTree
        # 检验粘贴板内容是否来自同一个根节点
        if targetTree is None and crossTreeWarningFlag is False:
            response = SchedulerMenuBehavior._CrossTreeOpration(parentWidget)
            if not response:
                return
            else:
                crossTreeWarningFlag = True
        # 获取被选项，并验证是否是同一根节点
        for selectedItem in itemTree.GetSelectedItems():
            parentNodeToBeAdded: TreeNode = itemTree.GetUserData(selectedItem)
            if (parentNodeToBeAdded.GetTree() is not targetTree) and (crossTreeWarningFlag is False):
                response = SchedulerMenuBehavior._CrossTreeOpration(parentWidget)
                if not response:
                    return
                else:
                    crossTreeWarningFlag = True
            parentNodes.append(parentNodeToBeAdded)
        # 克隆粘贴板内容，并应用到所有所选WidgetItem对应的TreeNode
        newNodes = copy.deepcopy(parentWidget.copiedItem)
        for parentNode in parentNodes:
            itemTree.InsertDerivedNodes(parentNode, newNodes)

    @staticmethod
    def SelectLeafItems(parentWidget: SchedulerFrontend.ExperimentScheduler):
        parentWidget.itemTable.SelectAllLeafItem()

    @staticmethod
    def MenuEntrance(menuItem: ItemTree.MenuItem, schedulerWidget):
        LogManager.Log('SchedulerMenuBehavior got callback menu item:{}'.format(menuItem), LogManager.LogType.Runtime)
        if menuItem == ItemTree.MenuItem.Delete:
            itemTree = schedulerWidget.itemTable
            SchedulerMenuBehavior.DeleteSelectedItems(itemTree)
        elif menuItem == ItemTree.MenuItem.Copy:
            SchedulerMenuBehavior.CopySelectedItems(schedulerWidget)
        elif menuItem == ItemTree.MenuItem.Cut:
            SchedulerMenuBehavior.SliceSelectedItems(schedulerWidget)
        elif menuItem == ItemTree.MenuItem.Paste:
            SchedulerMenuBehavior.PasteCopiedItems(schedulerWidget)
        elif menuItem == ItemTree.MenuItem.SelectLeafItems:
            SchedulerMenuBehavior.SelectLeafItems(schedulerWidget)
        else:
            LogManager.Log('SchedulerMenuBehavior: Invalid return value -- contacting your software maintainer.', LogManager.LogType.Error)
            return

