from enum import Enum

import PyQt6
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QVariant

from DataStructure.PyTree import *
from DataStructure import ExperimentScheduleManager

class PyTreeModel(QAbstractItemModel):

    def __init__(self, getTreesCallback, headerEnum, getDataCallback):
        """
        初始化
        :param getTreesCallback: 获取Tree列表的回调
        :param headerEnum: 获取header的Enum
        :param getDataCallback: 获取列表数据的回调，headerEnum的成员是key，而内容是value
        """
        super().__init__(None)
        self._getTrees = getTreesCallback
        self._headerEnum: type[Enum] = headerEnum
        self._dataCallback = getDataCallback
        self._colCount = 0
        self._colIndexDict = {}
        for enumItem in self._headerEnum:
            self._colIndexDict.update({self._colCount: enumItem})
            self._colCount += 1
        self._nodeIndexDict: dict = {}

    def _IsRoot(self, parent):
        parentIndex: None | QModelIndex = parent
        if parentIndex is None:
            return True
        elif parentIndex.isValid():
            return False
        else:
            return True

    def _WriteBuffer(self, node: TreeNode, column: int, value: str):
        targetStringDict = self._CheckBuffer(node)
        headerItem = self._colIndexDict.get(column)
        targetStringDict.update({headerItem: value})

    # 行列数据

    def columnCount(self, parent=None, *args, **kwargs):
        return self._colCount

    def rowCount(self, parent=None, *args, **kwargs):
        isRoot = self._IsRoot(parent)
        if isRoot:
            rC = len(self._getTrees())
            return rC
        else:
            parentIndex: None | QModelIndex = parent
            treeNode: TreeNode = parentIndex.internalPointer()
            rC = len(treeNode.GetChildren())
            return rC

    # 获取索引

    def hasChildren(self, parent=None, *args, **kwargs):
        if parent is None:
            return (len(self._getTrees()) != 0)
        elif not parent.isValid():
            return (len(self._getTrees()) != 0)
        else:
            parentIndex: QModelIndex = parent
            parentNode: TreeNode = parentIndex.internalPointer()
            return len(parentNode.GetChildren()) != 0

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
        isRoot = self._IsRoot(parent)
        if parent is None:
            parent = QModelIndex()
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
    def setData(self, index, value, role=None):
        treeIndex: None | QModelIndex = index
        if treeIndex is None:
            return False
        if not treeIndex.isValid():
            return False
        targetTreeNode: TreeNode = treeIndex.internalPointer()
        if targetTreeNode is None:
            raise ValueError('Node doesn\'t exist')
        if role == PyQt6.QtCore.Qt.ItemDataRole.DisplayRole:
            self._WriteBuffer(targetTreeNode, treeIndex.column(), value)
            self.dataChanged.emit(index, index, role)
        elif role == PyQt6.QtCore.Qt.ItemDataRole.UserRole:
            targetTreeNode.SetData(value)
            self.dataChanged.emit(index, index, role)
        else:
            return False

    def data(self, index, role=None):
        treeIndex: None | QModelIndex = index
        if treeIndex is None:
            return QVariant()
        if not treeIndex.isValid():
            return QVariant
        targetTreeNode: TreeNode = treeIndex.internalPointer()
        if role == PyQt6.QtCore.Qt.ItemDataRole.DisplayRole:
            return self._dataCallback(targetTreeNode, self._colIndexDict.get(treeIndex.column()))
        if role == PyQt6.QtCore.Qt.ItemDataRole.UserRole:
            return targetTreeNode.GetData()
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return 0
        return PyQt6.QtCore.Qt.ItemFlag.ItemIsEnabled | PyQt6.QtCore.Qt.ItemFlag.ItemIsSelectable

    # 表头展示

    def headerData(self, section, orientation, role=None):
        if orientation == PyQt6.QtCore.Qt.Orientation.Horizontal and role == PyQt6.QtCore.Qt.ItemDataRole.DisplayRole:
            return self._colIndexDict.get(section).value
        else:
            return QVariant()


