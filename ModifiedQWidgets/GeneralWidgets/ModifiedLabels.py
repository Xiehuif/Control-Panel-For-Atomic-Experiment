
from PyQt6 import   QtWidgets
from PyQt6.QtWidgets import QWidget
import EventHandler
import  enum
from MultiselectionManager import SelectionManager

class InteractableLabel(QtWidgets.QLabel):

    # 为QT的Label控件提供响应其他事件的操作

    eventHandler: (EventHandler or None) = None


    def __init__(self,parent : QWidget):
        super().__init__(parent)
        print('Handler Online')
        self.setMouseTracking(True)
        self.eventHandler = EventHandler.EventHandlerObject()
        self.installEventFilter(self.eventHandler)

class DisplayState(enum.Enum):
    standBy = 'StandBy'
    coveredBy = 'coveredBy'
    selected = 'selected'

class SelectableLabel(InteractableLabel):

    # 基于InteractableLabel制作的可供用于多选菜单的Label

    QSSContainer: dict = {}
    selectionManager: (SelectionManager or None) = None

    def __init__(self,parent : QWidget, manager: SelectionManager,attachedObject):
        super().__init__(parent)
        self.selectionManager = manager
        self.attachedObject = attachedObject
        manager.Register(self)

    def SetQSS(self,displayType: DisplayState,qss: str):
        self.QSSContainer.update({displayType: qss})

    def RefreshDisplay(self,isCovered: bool):
        if isCovered:
            self.setStyleSheet(self.QSSContainer.get(DisplayState.coveredBy))
        elif self.IsSelected():
            self.setStyleSheet(self.QSSContainer.get(DisplayState.selected))
        else:
            self.setStyleSheet(self.QSSContainer.get(DisplayState.standBy))

    def IsSelected(self):
        return self.selectionManager.IsSelected(self)

    def SetSelectState(self,state: bool):
        self.selectionManager.SetSelect(self,state)