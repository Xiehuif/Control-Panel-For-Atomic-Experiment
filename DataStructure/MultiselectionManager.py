class SelectionManager:
    def __init__(self):
        self._target: list = []
        self._selected: list = []

    def IsSelected(self,target) -> bool:
        if target in self._selected:
            return True
        else:
            return False

    def GetSelected(self) -> list:
        return self._selected

    def SetSelect(self,target,value : bool) -> bool:
        if target not in self._target:
            return False
        if value:
            return self._Select(target)
        else:
            return self._Unselect(target)

    def Clear(self):
        self._selected.clear()
        self._target.clear()

    def GetMember(self) -> list:
        return self._target

    def Register(self,target):
        self._target.append(target)

    def Unregister(self,target):
        if target in self._selected:
            self._selected.remove(target)
        self._target.remove(target)

    def _Unselect(self, target) -> bool:
        if self.IsSelected(target):
            self._selected.remove(target)
            return True
        else:
            return False

    def _Select(self,target) -> bool:
        if self.IsSelected(target):
            return False
        else:
            self._selected.append(target)
            return True