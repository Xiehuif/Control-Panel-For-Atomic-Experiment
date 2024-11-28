from enum import StrEnum

from PyQt6.QtWidgets import QTreeView, QHeaderView

from ModifiedQWidgets.GeneralWidgets.MenuGenerator import QuickMenu


class ItemView(QTreeView, QuickMenu):

    class MenuItem(StrEnum):
        Delete = '删除'
        Copy = '复制'
        Cut = '剪切'
        Paste = '粘贴'
        SelectLeafItems = '选中所有终端项'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(True)
        self.SetFrontendEditable(True)
        self.SetMenuEnumClass(self.MenuItem)

    def contextMenuEvent(self, *args, **kwargs):
        self.ShowMenu()

    def SetFrontendEditable(self, isEditable: bool):
        header: QHeaderView = self.header()
        if isEditable:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
            return
        else:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            self.setSelectionMode(QTreeView.SelectionMode.NoSelection)
            return

