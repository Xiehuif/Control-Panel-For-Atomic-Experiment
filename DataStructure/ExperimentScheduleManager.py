import copy
import enum
import json
from abc import ABC, abstractmethod

from PyQt6.QtCore import Qt

import MultiprocessSupport.ExperimentProcess
from DataStructure import LogManager, SerializationManager, DataManager
from DataStructure.PyTree import TreeNode, Tree, NodeData
from DataStructure.PyTreeModelForQt import PyTreeModel


class SchedulerItemType(enum.Enum):
    Imported = 'Imported'
    Derived = 'Derived'


class DisplayHeader(enum.Enum):
    Name = '任务名称'
    Source = '任务来源'
    Depth = '深度'
    ScannedDevice = '扫描设备'
    ScannedIndex = '波形所在索引'
    ScannedParameterType = '扫描参数'
    Value = '值'
    ScheduledMinimumTime = '计划最小用时'
    RunningState = '运行状态'


class ExperimentSchedulerItemDataBase(SerializationManager.Serializable, NodeData):

    def SetRunningState(self, state: MultiprocessSupport.ExperimentProcess.TaskManager.State):
        if isinstance(state, MultiprocessSupport.ExperimentProcess.TaskManager.State):
            self._currentState = state
        else:
            raise TypeError

    def GetRunningStateDescriptionText(self, state: MultiprocessSupport.ExperimentProcess.TaskManager.State):
        if state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Uninitiated:
            return '等待用户操作'
        elif state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Excluded:
            return '不在运行范围内'
        elif state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Running:
            return '运行中'
        elif state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Waiting:
            return '等待运行'
        elif state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Finished:
            return '已完成'
        else:
            return 'UNKNOWN STATE'

    def __init__(self, attachedNode: TreeNode = None, name: str = 'Unknown'):
        SerializationManager.Serializable.__init__(self)
        NodeData.__init__(self, attachedNode)
        self._attachedNode: TreeNode = attachedNode
        self.name = name
        self._currentState = MultiprocessSupport.ExperimentProcess.TaskManager.State.Uninitiated

    def GetDescriptionString(self, header: DisplayHeader) -> str:
        if header == DisplayHeader.RunningState:
            return self.GetRunningStateDescriptionText(self._currentState)
        else:
            return 'UNDEFINED'

    def GetName(self) -> str:
        return self.name

    def SetName(self, name) -> None:
        self.name = name

    @abstractmethod
    def GetType(self) -> SchedulerItemType:
        # 获取Item类型
        pass

    @abstractmethod
    def GetData(self, deviceDatas: dict):
        # 获取总和数据
        pass

    @abstractmethod
    def AppliedItemData(self):
        # 应用数据
        pass


class ExperimentSchedulerDerivedItemData(ExperimentSchedulerItemDataBase):

    def GetDescriptionString(self, header: DisplayHeader) -> str:
        """
        对这个Item的数据打表，返回的字符串是对应的描述数据
        :param header: 对应的表头
        :return: 描述数据
        """
        if header == DisplayHeader.Name:
            return self.GetName()
        elif header == DisplayHeader.Depth:
            return str(self.GetAttachedNode().GetDepth())
        elif header == DisplayHeader.Source:
            # NodeData is also an instance of ExperimentSchedulerItemDataBase
            return self.GetAttachedNode().GetParent().GetData().GetName()
        elif header == DisplayHeader.ScannedDevice:
            return self.deviceName
        elif header == DisplayHeader.ScannedIndex:
            return str(self.targetWaveIndex)
        elif header == DisplayHeader.ScannedParameterType:
            return self.targetParameterItem.value[0]
        elif header == DisplayHeader.Value:
            return str(self.appliedValue)
        elif header == DisplayHeader.ScheduledMinimumTime:
            # TODO
            return str(0)
        else:
            return super().GetDescriptionString(header)

    def GetData(self, deviceDatas: dict):
        # 初始化
        deviceDatas.clear()

        # 复原父类数据
        parentItem: ExperimentSchedulerItemDataBase = self.GetAttachedNode().GetParent().GetData()
        parentItem.GetData(deviceDatas)

        # 安装本体
        waveSchedule: DataManager.DeviceSchedule = deviceDatas.get(self._device.deviceName)
        waveData = waveSchedule.GetWaveByIndex(self.targetWaveIndex)
        waveData.parameter.update({self.targetParameterItem: self.appliedValue})
        return deviceDatas

    def AppliedItemData(self):

        # 你需要首先创造其父类所有的环境
        parentItem: ExperimentSchedulerItemDataBase = self.GetAttachedNode().GetParent().GetData()
        parentItem.AppliedItemData()

        # 应用数据
        waveSchedule = self._device.deviceSchedule
        waveData = waveSchedule.GetWaveByIndex(self.targetWaveIndex)
        waveData.parameter.update({self.targetParameterItem: self.appliedValue})
        return

    def GetType(self) -> SchedulerItemType:
        return SchedulerItemType.Derived

    def __init__(self, attachedNode: TreeNode | str | None = None, *args):
        """

        初始化计划项，arg自起始分别是波形序号、指定参数的Enum，受控应用的值、受控的Device

        :param attachedManager: 控制该项的Manager
        :param index: 所控制波形所在设备波形计划的序号
        :param argItem: 用于搜寻被控制参数的Handler
        :param value: 控制的值
        :param device: 所控制的Device

        """
        if len(args) == 0 and isinstance(attachedNode, str):
            # 受Serialize控制
            self.Deserialize(args[0])
        else:
            if attachedNode is not None:
                ExperimentSchedulerItemDataBase.__init__(self, attachedNode)
            else:
                ExperimentSchedulerItemDataBase.__init__(self, None)
            # 获取参数
            index = args[0]
            argItem = args[1]
            value = args[2]
            device: DataManager.Device = args[3]

            # 有效实验参数
            self.targetWaveIndex: int = index
            self.targetParameterItem: enum.Enum = argItem
            self.appliedValue = value
            self.deviceName = device.deviceName

            # 动态链接
            self._device: DataManager.Device | None = DataManager.deviceHandlerInstance.GetObject(self.deviceName)

    def __deepcopy__(self, memodict={}):
        newWaveIndex = copy.deepcopy(self.targetWaveIndex)
        newAppliedValue = copy.deepcopy(self.appliedValue)
        newItem = ExperimentSchedulerDerivedItemData(self.GetAttachedNode(),
                                                     newWaveIndex,
                                                     self.targetParameterItem,
                                                     newAppliedValue,
                                                     DataManager.deviceHandlerInstance.GetObject(self.deviceName)
                                                     )
        newItem.SetName(self.GetName())
        return newItem

    def Deserialize(self, jsonContext: str | None):
        super().Deserialize(jsonContext)
        self._device = DataManager.deviceHandlerInstance.GetObject(self.deviceName)


class ExperimentSchedulerImportedItemData(ExperimentSchedulerItemDataBase):
    
    """
    为实验列表创造一项导入数据，需要一个DeviceHandler，这个数据将作为DerivedItem的派生来源。
    """

    def GetData(self, deviceDatas: dict):
        """
        返回被存储的复制的device数据
        :return: 一个字典，key为各Device的DeviceName，value为各Device实例的schedule
        """
        deviceDatas.clear()
        for device in self._copiedScheduleDict:
            newScheduler = DataManager.DeviceSchedule(device)
            newScheduler.CopyFromSchedule(self._copiedScheduleDict.get(device))
            deviceDatas.update({device.deviceName: newScheduler})
        return deviceDatas

    def GetType(self) -> SchedulerItemType:
        return SchedulerItemType.Imported

    def __init__(self, arg, name='Unknown'):
        """
        手动生成这个类时，arg应该是DeviceHandler

        :param arg: 一个可以被派生出其他实验参数的DeviceHandler
        """
        # devicesData: ObjectHandler
        super().__init__()
        if isinstance(arg, str):
            # 受Serialize控制
            self.Deserialize(arg)
        elif isinstance(arg, DataManager.ObjectHandler):
            # 复制一份完全一致的环境
            devicesData = arg
            self._copiedScheduleDict: dict = {}
            deviceList = devicesData.GetObjects()
            for device in deviceList:
                newSchedule = DataManager.DeviceSchedule(device)
                newSchedule.CopyFromSchedule(device.deviceSchedule)
                self._copiedScheduleDict.update({device: newSchedule})

    def __deepcopy__(self, memodict={}):
        dataDict = {}
        self.GetData(dataDict)
        newObjectHandler = DataManager.ObjectHandler()
        for item in dataDict:
            device: DataManager.Device = DataManager.deviceHandlerInstance.GetObject(item)
            newObjectHandler.RegisterObject(device, device.deviceName)
            device.deviceSchedule.CopyFromSchedule(dataDict.get(item))
        newImportNode = ExperimentSchedulerImportedItemData(newObjectHandler)
        newImportNode.SetName(self.GetName())
        return newImportNode

    def Serialize(self, encoder: json.JSONEncoder = json.JSONEncoder()) -> str:
        dumpedDict = {}
        for device in self._copiedScheduleDict:
            dumpedDict.update({device.deviceName: self._copiedScheduleDict.get(device).Serialize()})
        parameterList = [self.name, dumpedDict]
        return json.dumps(parameterList)

    def Deserialize(self, jsonContext: str | None):
        parameterList = json.loads(jsonContext)
        self.name = str(parameterList[0])
        dumpedDict = parameterList[1]
        self._copiedDeviceHandler = DataManager.ObjectHandler()
        for deviceName in dumpedDict:
            device = DataManager.deviceHandlerInstance.GetObject(deviceName)
            newScheduler = DataManager.DeviceSchedule(device)
            newScheduler.Deserialize(dumpedDict.get(deviceName))
            self._copiedScheduleDict.update({device: newScheduler})

    def AppliedItemData(self):
        devices = DataManager.deviceHandlerInstance.GetObjects()
        for device in devices:
            device.deviceSchedule.CopyFromSchedule(self._copiedScheduleDict.get(device))

    def GetDescriptionString(self, header: DisplayHeader) -> str:
        if header == DisplayHeader.Name:
            return self.GetName()
        elif header == DisplayHeader.Source:
            return 'User'
        elif header == DisplayHeader.Depth:
            return '0'
        elif header == DisplayHeader.ScannedIndex:
            return 'None'
        elif header == DisplayHeader.ScannedDevice:
            return 'Root'
        elif header == DisplayHeader.ScannedParameterType:
            return 'None'
        elif header == DisplayHeader.Value:
            return 'Default'
        elif header == DisplayHeader.ScheduledMinimumTime:
            return '0'
        else:
            return super().GetDescriptionString(header)

class SchedulerItemManager(SerializationManager.Serializable, PyTreeModel):

    # 刷新
    def Clear(self):
        self.treeList.clear()

    # Serializable 重载
    def Serialize(self, encoder:json.JSONEncoder = json.JSONEncoder()) -> str:
        dataList = []
        for index in range(len(self.treeList)):
            tree: Tree = self.treeList[index]
            treeString = tree.Serialize()
            dataList.append(treeString)
        dataString = json.dumps(dataList)
        return dataString

    def Deserialize(self, jsonContext :str|None):
        self.Clear()
        dataList = json.loads(jsonContext)
        for index in range(len(dataList)):
            tree: Tree = Tree()
            tree.Deserialize(dataList[index])
            self.treeList.append(tree)

    # 数据关联
    def RegisterModelDisplay(self, headerEnum: type[enum.Enum], dataCallback):
        PyTreeModel.__init__(self, lambda: self.treeList, headerEnum, dataCallback)

    def GetTrees(self):
        newList = []
        for tree in self.treeList:
            newList.append(tree)
        return newList

    def __init__(self, jsonContext: str | None = None):
        self.treeList: list = []

    def ImportTree(self, tree: Tree):
        self.treeList.append(tree)

    def ImportRootItem(self, item: ExperimentSchedulerImportedItemData) -> TreeNode:
        newTree = Tree()
        self.treeList.append(newTree)
        newNode = newTree.GetNodeByIndex(0)
        newNode.SetData(item)
        return newTree.GetNodeByIndex(0)

    def ImportDerivedItem(self, parentNode: TreeNode, newItem: ExperimentSchedulerDerivedItemData) -> TreeNode:
        currentNode = TreeNode(parentNode.GetTree(), parentNode)
        currentNode.SetData(newItem)
        newItem.SetAttachedNode(currentNode)
        return currentNode

    def DeleteItem(self, item):
        returnFlag = False
        targetTree = item.GetAttachedNode().GetTree()
        if isinstance(item, ExperimentSchedulerImportedItemData):
            try:
                self.treeList.remove(targetTree)
                returnFlag = True
            except ValueError:
                LogManager.Log("SchedulerItemMGR: No such root item in SchedulerMGR can be deleted",
                               LogManager.LogType.Error)
                returnFlag = False
        if isinstance(item, ExperimentSchedulerDerivedItemData):
            targetNode = item.GetAttachedNode()
            parentNode = targetNode.GetParent()
            children = parentNode.GetChildren()
            try:
                children.remove(targetNode)
                returnFlag = True
            except ValueError:
                LogManager.Log("SchedulerItemMGR: No such root item in SchedulerMGR can be deleted",
                               LogManager.LogType.Error)
                returnFlag = False
        return returnFlag





