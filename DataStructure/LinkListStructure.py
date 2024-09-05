class LinkList:
    class _Node:
        _data = None
        _previousNode = None
        _nextNode = None

        def __init__(self,data,previousNode,nextNode):
            self._data = data
            self._previousNode = previousNode
            self._nextNode = nextNode

        def SetPrevious(self,node):
            self._previousNode = node

        def GetPrevious(self):
            return self._previousNode

        def SetNext(self,node):
            self._nextNode = node

        def GetNext(self):
            return self._nextNode

        def GetData(self):
            return self._data

        def __del__(self):
            del self._data


    _length: int = 0
    _head = None
    _tail = None
    _pointer = None

    def __init__(self):
        self._head = None
        self._tail = None
        self._length = 0
        self._pointer = None

    def _InitializationCheck(self,data):
        if self._head is None:
            self._head = self._Node(data,None,None)
            self._tail = self._head
            self._pointer = self._head
            self._length = 1
            return True
        else:
            return False

    def PointerMoveForward(self) -> bool:
        if (self._pointer.GetNext() is None):
            return False
        else:
            self._pointer = self._pointer.GetNext()
            return True

    def PointerMoveBackward(self) -> bool:
        if (self._pointer.GetPrevious() is None):
            return False
        else:
            self._pointer = self._pointer.GetPrevious()
            return True

    def AppendDataAfterPointer(self,data) -> _Node:
        if self._InitializationCheck(data):
            return self._pointer
        else:
            newNode = self._Node(data,self._pointer,self._pointer.GetNext())
            if (self._pointer.GetNext() is not None):
                self._pointer.GetNext().SetPrevious(newNode)
            self._pointer.SetNext(newNode)
            self._length = self._length + 1
            self.PointerMoveForward()
            return newNode

    def _DeleteNode(self,node):
        if node.GetPrevious() is not None:
            node.GetPrevious().SetNext(node.GetNext())
        if node.GetNext() is not None:
            node.GetNext().SetPrevious(node.GetPrevious())
        if node is self._head:
            self._head = node.GetNext()
        if node is self._tail:
            self._tail = node.GetPrevious()
        self._length = self._length - 1


    def DeleteDataAtPointer(self):
        if self._length == 0:
            return False
        elif self._pointer is None:
            print('Using null pointer')
            return False
        else:
            deleted = self._pointer
            self.PointerMoveForward()
            self._DeleteNode(deleted)
            return True

    def GetDataFromPointedNode(self):
        if self._length == 0:
            return None
        return self._pointer.GetData()

    def SetPointer(self,index:int):
        self._pointer = self._head
        if(index < self._length):
            for i in range(0,index):
                self.PointerMoveForward()
            return True
        else:
            return False

    def GetLength(self):
        return self._length

    def DeleteData(self,data) -> bool:
        tempPointer = self._head
        while tempPointer is not None:
            if tempPointer.GetData() is data:
                self._DeleteNode(tempPointer)
                return True
            else:
                tempPointer = tempPointer.GetNext()
        return False



