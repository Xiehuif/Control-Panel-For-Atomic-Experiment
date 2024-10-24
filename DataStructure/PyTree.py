import copy
import json

from DataStructure import SerializationManager

class NodeData:

    def __init__(self, attachedNode = None):
        self._attachedNode = None

    def SetAttachedNode(self, treeNode):
        self._attachedNode = treeNode

    def GetAttachedNode(self):
        return self._attachedNode

class TreeNode(SerializationManager.Serializable):

    __slots__ = ('_parent', '_data', '_children', '_index', '_tree')

    def DeleteSelf(self):
        self._parent.GetChildren().remove(self)
        temp = []
        for item in self._children:
            temp.append(item)
        for item in temp:
            item.DeleteSelf()

    def GetDepth(self) -> int:
        if self._parent is None:
            return 0
        else:
            return self._parent.GetDepth() + 1

    def __eq__(self, other):
        if isinstance(other, str):
            if self.GetHandler() == other:
                return True
        if isinstance(other, int):
            if self.GetIndex() == other:
                return True
        else:
            return super().__eq__(other)

    def __hash__(self):
        return self.GetHandler().__hash__()

    def SetTree(self, newTree):
        if newTree is self._tree:
            return
        newIndex = newTree.AssignIndex()
        self._tree = newTree
        self._index = newIndex
        for node in self.GetChildren():
            node.SetTree(newTree)

    def GetTree(self):
        """
        获取目标所在的树
        :return: 所在的树
        """
        return self._tree

    def GetIndex(self):
        """
        获取目标的index
        :return: index
        """
        return self._index

    def GetHandler(self) -> str:
        """
        获取目标的handler，同index作用类似，但是是作为hash和判断相等的依据
        :return: handler字符串
        """
        if self._parent is not None:
            return "{}-{}".format(self._parent.GetIndex(), self.GetIndex())
        else:
            return '0'

    def Deserialize(self, jsonContext: str | None):
        super().Deserialize(jsonContext)

    def GetData(self) -> NodeData:
        """
        获取所携带的数据
        :return: data
        """
        return self._data

    def SetData(self, data: NodeData):
        """
        配置所携带的数据
        :param data: 配置的数据
        :return:
        """
        self._data = data
        self._data.SetAttachedNode(self)

    def GetParent(self):
        """
        获取父节点
        :return: 父节点
        """
        return self._parent

    def SetParent(self, parent):
        """
        设定父节点
        :param parent: 父节点
        :return:
        """
        self._parent = parent
        self._parent.GetChildren().append(self)
        if self._parent.GetTree() is not self._tree:
            newTree = parent.GetTree()
            self.SetTree(newTree)

    def GetChildren(self):
        """
        获取子节点
        :return: 子节点列表
        """
        return self._children

    def DeleteChild(self, child):
        """
        删除子节点
        :param child: 子节点
        :return:
        """
        self._children.remove(child)

    def __deepcopy__(self, memodict={}):
        if self in memodict:
            raise RuntimeError('deepcopy of TreeNode found circular copy')
        newTreeNode = TreeNode(None)
        newData = copy.deepcopy(self.GetData())
        newTreeNode.SetData(newData)
        memodict.update({self: True})
        for node in self.GetChildren():
            newChild = copy.deepcopy(node, memodict)
            newChild.SetParent(newTreeNode)
        return newTreeNode


    def __init__(self, tree, parent=None):
        super().__init__()
        if isinstance(tree, Tree):
            self._tree = tree
            self._index = self._tree.AssignIndex()
        elif tree is None:
            self._tree = None
            self._index = -1
        else:
            raise TypeError('arg tree has no type Tree is forbidden')
        self._parent = None
        if parent is None:
            self._parent = None
        elif isinstance(parent, TreeNode):
            self.SetParent(parent)
        else:
            raise TypeError('arg parent has no type TreeNode is forbidden')
        self._children = []
        self._data: SerializationManager.Serializable | None = None


class Tree(SerializationManager.Serializable):

    def __init__(self, jsonContext: str | None = None):
        super().__init__()
        self._assignedIndex: int = 0
        self._root = TreeNode(self)

    def _CollectNodes(self, nodeList: list[TreeNode], targetNode):
        if targetNode in nodeList:
            raise RuntimeError
        nodeList.append(targetNode)
        for node in targetNode.GetChildren():
            self._CollectNodes(nodeList, node)

    def _SearchIndexKernel(self, targetIndex: int, targetNode: TreeNode):
        if targetNode.GetIndex() == targetIndex:
            return targetNode
        else:
            for node in targetNode.GetChildren():
                res = self._SearchIndexKernel(targetIndex, node)
                if res is not None:
                    return res
        return None

    def _SearchDataKernel(self, target, targetNode: TreeNode):
        if targetNode.GetData() == target:
            return targetNode
        else:
            for node in targetNode.GetChildren():
                res = self._SearchDataKernel(target, node)
                if res is not None:
                    return res
        return None

    def GetNodeByIndex(self, index):
        return self._SearchIndexKernel(index, self._root)

    def GetNodeByData(self, data) -> TreeNode | None:
        return self._SearchDataKernel(data, self._root)

    def AssignIndex(self):
        res = self._assignedIndex
        self._assignedIndex += 1
        return res

    def GetNodes(self) -> list[TreeNode]:
        nodeList = []
        self._CollectNodes(nodeList, self._root)
        return nodeList

    def GetRoot(self) -> TreeNode:
        return self._root

    def Serialize(self,encoder:json.JSONEncoder = json.JSONEncoder()) -> str:
        nodeList = self.GetNodes()
        nodeStrDict = {}
        for node in nodeList:
            nodeStr = node.Serialize(encoder)
            nodeHandler = node.GetHandler()
            nodeStrDict.update({nodeHandler: nodeStr})
        finStr = [self._assignedIndex, nodeStrDict]
        return json.dumps(finStr)

    def Deserialize(self, jsonContext :str|None):
        if jsonContext is None:
            return
        else:
            finStr = json.loads(jsonContext)
            nodeStrDict: dict = finStr[1]
            newNodeNumber = len(nodeStrDict)
            newNodeDict = {}

            # 复原节点的index信息和data信息，并维护一以index为key，[node, node.GetParent().GetIndex()]为value的字典
            for nodeHandler in nodeStrDict:

                # 根节点 特殊处理
                if nodeHandler == '0':
                    self._assignedIndex = 0
                    newNode = TreeNode(self)
                    nodeStr = nodeStrDict[nodeHandler]
                    newNode.Deserialize(nodeStr)
                    self._root = newNode
                    nodeTempList = [newNode, -1]
                    newNodeDict.update({0: nodeTempList})
                    continue

                # 其他子节点
                handlerInfo: str = nodeHandler
                args = handlerInfo.split('-')
                parentIndex = int(args[0])
                selfIndex = int(args[1])
                self._assignedIndex = selfIndex
                newNode = TreeNode(self)
                nodeStr = nodeStrDict[nodeHandler]
                newNode.Deserialize(nodeStr)
                nodeTempList = [newNode, parentIndex]
                newNodeDict.update({selfIndex: nodeTempList})

            # 利用之前的Dict恢复节点间亲子关系
            for index in newNodeDict:
                if index == 0:
                    continue
                else:
                    parentTargetIndex = newNodeDict.get(index)[1]
                    currentNode = newNodeDict.get(index)[0]
                    parentNode = newNodeDict.get(parentTargetIndex)[0]
                    currentNode.SetParent(parentNode)

            # 恢复指派index的变量
            self._assignedIndex = int(finStr[0])
