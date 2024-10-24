import enum

from PyQt6.QtGui import QCursor, QAction
from PyQt6.QtWidgets import QMenu

from DataStructure import LogManager


class QuickMenu:

    def __init__(self):
        self._menu = QMenu()
        self._menuCallback = []
        self._enumClass: type[enum.Enum] | None = None

    def ShowMenu(self):
        cursor = QCursor()
        self._AppliedMenuItems()
        self._menu.exec(cursor.pos())

    def MenuBinding(self, context: str, item):
        newAction = QAction()
        newAction.setText(context)
        newAction.setData(item)
        self._menu.addAction(newAction)
        newAction.triggered.connect(lambda: self._ActionClicked(newAction))

    def _AppliedMenuItems(self):
        self._menu.clear()
        for item in self._enumClass:
            self.MenuBinding(item.value, item)

    def SetMenuEnumClass(self, enumClass: type[enum.Enum]):
        self._enumClass = enumClass

    def _ActionClicked(self, action: QAction):
        item = action.data()
        name = action.text()
        LogManager.Log('Action:{} was clicked and emitted item is:{}'.format(name, item)
                       , LogManager.LogType.Runtime)
        self.ClickMenu(item)

    def AddMenuCallback(self, callback):
        self._menuCallback.append(callback)

    def ClickMenu(self, item):
        for callback in self._menuCallback:
            callback(item)