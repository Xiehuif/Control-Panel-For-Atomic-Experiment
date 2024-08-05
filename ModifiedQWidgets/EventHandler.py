from PyQt6 import QtGui,QtCore,QtWidgets
from PyQt6.QtWidgets import QWidget,QApplication
import enum
class EventHandlerObject(QtCore.QObject):
    _delegates : dict = None
    _parameters : dict = None
    _infos : dict = None
    _infoActivation = False

    def __init__(self):
        self._delegates = {}
        self._parameters = {}
        self._infos = {}
        super().__init__()

    def ClearBinding(self):
        self._delegates = {}
        self._infos = {}
        self._parameters = {}

    def BindEvent(self : QtWidgets,event : int,func,args = None,info = None):
        self._delegates.update({event: func})
        self._parameters.update({event: args})
        if info is None:
            self._infos.update({event: lambda: 'A event:' + str(event) + ' has triggered somewhere'})
        else:
            self._infos.update({event: info})

    def eventFilter(self, object : QtCore.QObject, event):
        func = self._delegates.get(event.type(), None)
        par = self._parameters.get(event.type(), None)
        info = self._infos.get(event.type(), None)
        if func is None:
            return False
        elif par is None:
            func()
            if self._infoActivation:
                print(info())
            return True
        else:
            func(par())
            if self._infoActivation:
                print(info())
            return True
