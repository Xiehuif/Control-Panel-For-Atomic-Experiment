from enum import Enum

import PyQt6.QtCore.Qt
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QVariant

from DataStructure.PyTree import *
from DataStructure import ExperimentScheduleManager

class ExperimentModel(QAbstractItemModel):

    def __init__(self, getTreesCallback, headerEnum, getDataCallback):
        super().__init__(None)
        self._getTrees = getTreesCallback
        self._headerEnum: type[Enum] = headerEnum
        self._dataCallback = getDataCallback
        self._colCount = 0
        self._colIndexDict = {}
        for enumItem in self._headerEnum:
            self._colIndexDict.update({self._colCount: enumItem})
            self._colCount += 1

    def _isRoot(self, parent):
        parentIndex: None | QModelIndex = parent
        if parentIndex is None:
            return True
        elif parentIndex.isValid():
            return False
        else:
            return True

    # 行列数据

    def columnCount(self, parent=None, *args, **kwargs):
        return self._colCount

    def rowCount(self, parent=None, *args, **kwargs):
        isRoot = self._isRoot(parent)
        if isRoot:
            return len(self._getTrees())
        else:
            parentIndex: None | QModelIndex = parent
            treeNode: TreeNode = parentIndex.internalPointer()
            return len(treeNode.GetChildren())

    # 获取索引

    def parent(self, child=None):
        if child is None:
            return QModelIndex()
        else:
            childIndex: QModelIndex = child
            if not childIndex.isValid():
                return QModelIndex()
            else:
                childNode: TreeNode = childIndex.internalPointer()
                parentNode: TreeNode = childNode.GetParent()
                # 当前节点已经是根节点
                if parentNode is None:
                    return QModelIndex()
                # 父节点是根节点
                if parentNode.GetParent() is None:
                    treeList: list[Tree] = self._getTrees()
                    for i in range(len(treeList)):
                        if treeList[i].GetRoot() is parentNode:
                            return self.createIndex(i, 0, parentNode)
                # 父节点不是根节点
                else:
                    grandparentNode = parentNode.GetParent()
                    parentIndex = grandparentNode.GetChildren().index(parentNode)
                    return self.createIndex(parentIndex, 0, parentNode)


    def index(self, row, column, parent=None, *args, **kwargs):
        isRoot = self._isRoot(parent)
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if isRoot:
            treeItems: list[Tree] = self._getTrees()
            rootNode: TreeNode = treeItems[row].GetRoot()
            return self.createIndex(row, column, rootNode)
        else:
            parentIndex: None | QModelIndex = parent
            parentNode: TreeNode = parentIndex.internalPointer()
            return self.createIndex(row, column, parentNode.GetChildren()[row])

    # 数据操作

    def data(self, index, role=None):
        treeIndex: None | QModelIndex = index
        if treeIndex is None:
            return QVariant()
        if not treeIndex.isValid():
            return QVariant
        targetTreeNode: TreeNode = treeIndex.internalPointer()
        if role == PyQt6.QtCore.Qt.ItemDataRole.DisplayRole:
            targetStringDict: dict = self._dataCallback(targetTreeNode)
            targetEnum = self._colIndexDict.get(treeIndex.column())
            return targetStringDict.get(targetEnum)
        if role == PyQt6.QtCore.Qt.ItemDataRole.UserRole:
            return targetTreeNode.GetData()
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return 0
        return PyQt6.QtCore.Qt.ItemFlag.ItemIsEnabled | PyQt6.QtCore.Qt.ItemFlag.ItemIsSelectable

    # 表头展示

    def headerData(self, section, orientation, role=None):



