import enum

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import QMenu

from DataStructure import LogManager
from ModifiedQWidgets.GeneralWidgets.MenuGenerator import QuickMenu


class MenuTreeWidget(QtWidgets.QTreeWidget, QuickMenu):

    def __init__(self, **kwargs):
        super().__init__(parent=kwargs.get('parent'))

    def contextMenuEvent(self, *args, **kwargs):
        self.ShowMenu()


class MulticolumnTree:

    def SelectAllLeafItem(self):
        self._frontend.expandAll()
        for item in self._topLevelItems:
            self._SetAllLeafNodeSelected(item)

    def AddMenuCallback(self, callback):
        self._frontend.AddMenuCallback(callback)

    def __init__(self, treeWidget: MenuTreeWidget, headerEnumClass, menuEnumClass):

        """
        此类意在使用一个枚举创造一个列表并用QTreeWidget作为前端显示，枚举的每一项的值都将作为列的表。
        这个列表的每一项可以包含多个允许被QTreeWidget显示的项，并以同枚举一一对应的方式显示

        :param treeWidget: QTreeWidget组件的实例
        :param headerEnumClass: 用以创建对应组件的枚举类（继承Enum），直接传入类的标识符而非实例
        """

        self._columnCount = 0
        self._frontend: MenuTreeWidget = treeWidget
        self._indicatedType = headerEnumClass
        self._columnIndexMap: dict = {}
        self._frontend.SetMenuEnumClass(menuEnumClass)
        self._topLevelItems: list[QtWidgets.QTreeWidgetItem] = []

        # 构建映射关系
        tempHeaderList = []
        for headerItem in headerEnumClass:
            tempHeaderList.append(headerItem)
        self._columnCount = len(tempHeaderList)
        self._frontend.setColumnCount(self._columnCount)
        treeHeader: QtWidgets.QTreeWidgetItem = QtWidgets.QTreeWidgetItem()
        for index in range(self._columnCount):
            headerItem: enum.Enum = tempHeaderList[index]
            treeHeader.setText(index, headerItem.value)
            self._columnIndexMap.update({headerItem: index})
        self._frontend.setHeaderItem(treeHeader)
        self._frontend.setUniformRowHeights(True)

    def _SetAllLeafNodeSelected(self, nodeItem: QtWidgets.QTreeWidgetItem):
        if nodeItem.childCount() != 0:
            for i in range(nodeItem.childCount()):
                self._SetAllLeafNodeSelected(nodeItem.child(i))
        else:
            nodeItem.setSelected(True)

    def _CreateItem(self, data: dict, userData = None) -> QtWidgets.QTreeWidgetItem:
        newTreeItem = QtWidgets.QTreeWidgetItem()
        for item in self._indicatedType:
            columnIndex = self._columnIndexMap.get(item)
            columnText = data.get(item)
            newTreeItem.setText(columnIndex, columnText)
        newTreeItem.setData(0, 0x0100, userData)
        return newTreeItem

    def _CheckDataRule(self, data: dict):
        for indicateEnum in data:
            if not isinstance(indicateEnum, self._indicatedType):
                raise RuntimeError

    def _AddTopLevelItem(self, item: QtWidgets.QTreeWidgetItem):
        self._frontend.addTopLevelItem(item)
        self._topLevelItems.append(item)

    def _AddTopLevelItems(self, items: list[QtWidgets.QTreeWidgetItem]):
        self._frontend.addTopLevelItems(items)
        self._topLevelItems.extend(items)

    def _DeleteTopLevelItem(self, item: QtWidgets.QTreeWidgetItem):
        index = self._frontend.indexOfTopLevelItem(item)
        if index == -1:
            LogManager.Log("No such item in TreeWidget, check again?", LogManager.LogType.Error)
            return False
        self._frontend.takeTopLevelItem(index)
        self._topLevelItems.remove(item)
        return True

    def GetColumnIndex(self, item: enum):
        columnIndex = self._columnIndexMap.get(item)
        return columnIndex

    def InsertItem(self, data: dict, parent: QtWidgets.QTreeWidgetItem = None, userData = None) \
            -> QtWidgets.QTreeWidgetItem:
        """
        向列表中插入一项
        :param data:  依赖的数据，key是指定枚举的实例，value是枚举实例对应的列应显示的字符串
        :param parent: 亲代节点
        :param userData: 用户指定的同该项挂钩的程序数据
        :return: None
        """
        self._CheckDataRule(data)
        item = self._CreateItem(data, userData)
        if parent is None:
            self._AddTopLevelItem(item)
        else:
            parent.addChild(item)
        return item

    def InsertItems(self, packages: list, parent: QtWidgets.QTreeWidgetItem = None) -> list[QtWidgets.QTreeWidgetItem]:
        """
        向列表末尾插入一系列数据
        :param packages: 一系列数据组成的列表，列表的每一个项是一个有两个成员的任意容器iter，iter[0]对应InsertItem的data，iter[1]对应InsertItem的userData
        :return: 返回按顺序被插入的数据中的第一条数据所在的index
        """
        for pack in packages:
            data = pack[0]
            self._CheckDataRule(data)
        itemList = []
        for pack in packages:
            data = pack[0]
            userData = pack[1]
            itemList.append(self._CreateItem(data, userData))
        if parent is not None:
            parent.addChildren(itemList)
        else:
            self._AddTopLevelItems(itemList)
        return itemList

    def DeleteItem(self, item: QtWidgets.QTreeWidgetItem) -> bool:
        if not isinstance(item, QtWidgets.QTreeWidgetItem):
            LogManager.Log('MulticolumnTree: Invalid input for deleted item --- '
                           'type of deleted item is {} but not QTreeWidgetItem'.format(type(item)))
            return False
        parent: QtWidgets.QTreeWidgetItem | None = item.parent()
        if parent is None:
            self._DeleteTopLevelItem(item)
        else:
            index = parent.indexOfChild(item)
            parent.takeChild(index)
            return True

    def SetFrontendEditable(self, isEditable: bool):
        header: QtWidgets.QHeaderView = self._frontend.header()
        if isEditable:
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            self._frontend.setSelectionMode(QtWidgets.QTreeWidget.SelectionMode.ExtendedSelection)
            return
        else:
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
            self._frontend.setSelectionMode(QtWidgets.QTreeWidget.SelectionMode.NoSelection)
            return


    def ClearItems(self):
        self._frontend.clear()
        self._topLevelItems.clear()

    def GetUserData(self, item: QtWidgets.QTreeWidgetItem):
        return item.data(0, 0x0100)

    def GetSelectedItems(self) -> list[QtWidgets.QTreeWidgetItem]:
        """
        获取被选取的各行的第一个Item，注意这些item是QTreeWidgetItem
        :return:
        """
        return self._frontend.selectedItems()


