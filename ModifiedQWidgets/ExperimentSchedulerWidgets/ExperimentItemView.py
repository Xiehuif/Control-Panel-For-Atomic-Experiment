from PyQt6.QtWidgets import QTreeView, QHeaderView


class ItemView(QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(True)
        self.SetFrontendEditable(True)

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

