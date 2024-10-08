import enum
import json
from abc import ABC, abstractmethod

import SerializationManager
import DataManager
from PyTree import TreeNode, Tree


class SchedulerItemType(enum.Enum):
    Imported = 'Imported'
    Derived = 'Derived'


class ExperimentSchedulerItemDataBase(ABC, SerializationManager.Serializable):

    def __init__(self, attachedNode: TreeNode = None):
        super().__init__()
        self._attachedNode: TreeNode = attachedNode

    def GetAttachedNode(self):
        return self._attachedNode

    def SetAttachedNode(self, attachedNode: TreeNode):
        self._attachedNode = attachedNode

    @abstractmethod
    def GetType(self) -> SchedulerItemType:
        # 获取Item类型
        pass

    @abstractmethod
    def GetData(self, deviceDatas: dict):
        # 获取总和数据
        pass

    def AppliedItemData(self):
        # 应用数据
        pass


class ExperimentSchedulerDerivedItemData(ExperimentSchedulerItemDataBase):

    def GetData(self, deviceDatas: dict):
        # 初始化
        deviceDatas.clear()

        # 复原父类数据
        parentItem: ExperimentSchedulerItemDataBase = self.GetAttachedNode().GetParent().GetData()
        parentItem.GetData(deviceDatas)

        # 安装本体
        waveSchedule: DataManager.DeviceSchedule = deviceDatas.get(self._device)
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

    def __init__(self, attachedNode: TreeNode, *args):
        """

        初始化计划项

        :param attachedManager: 控制该项的Manager
        :param index: 所控制波形所在设备波形计划的序号
        :param argItem: 用于搜寻被控制参数的Handler
        :param value: 控制的值
        :param parentHandler: 其父计划项所对应的Handler
        :param device: 所控制的Device

        """
        super(ExperimentSchedulerItemDataBase).__init__(attachedNode)
        if len(args) == 1 and isinstance(args[0], str):
            # 受Serialize控制
            self.Deserialize(args[0])
        else:
            # 获取参数
            index = args[0]
            argItem = args[1]
            value = args[2]
            device: DataManager.Device = args[4]

            # 有效实验参数
            self.targetWaveIndex: int = index
            self.targetParameterItem: enum.Enum = argItem
            self.appliedValue = value
            self.deviceName = device.deviceName

            # 动态链接
            self._device: DataManager.Device | None = DataManager.deviceHandlerInstance.GetObject(self.deviceName)

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
        :return: 一个字典，key为各Device实例，value为各Device实例下
        """
        deviceDatas.clear()
        for device in self._copiedScheduleDict:
            newScheduler = DataManager.DeviceSchedule()
            newScheduler.CopyFromSchedule(self._copiedScheduleDict.get(device))
            deviceDatas.update({device: newScheduler})
        return deviceDatas

    def GetType(self) -> SchedulerItemType:
        return SchedulerItemType.Imported

    def __init__(self, arg):
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

    def Serialize(self, encoder: json.JSONEncoder = json.JSONEncoder()) -> str:
        dumpedDict = {}
        for device in self._copiedScheduleDict:
            dumpedDict.update({device.deviceName: self._copiedScheduleDict.get(device).Serialize()})
        return json.dumps(dumpedDict)

    def Deserialize(self, jsonContext: str | None):
        dumpedDict = json.loads(jsonContext)
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

class SchedulerItemManager(SerializationManager.Serializable):

    def __init__(self, jsonContext: str | None = None):
        self.treeDict: dict = {}

    def ImportRootItem(self, item: ExperimentSchedulerImportedItemData) -> TreeNode:
        newTree = Tree()
        self.treeDict.update({item: newTree})
        newTree.GetNodeByIndex(0).SetData(item)
        return newTree.GetNodeByIndex(0)

    def ImportDerivedItem(self, parentItem: ExperimentSchedulerItemDataBase,
                          newItem: ExperimentSchedulerDerivedItemData):
        parentNode = parentItem.GetAttachedNode()
        currentNode = TreeNode(parentNode.GetTree(), parentNode)
        currentNode.SetData(newItem)

    def _StackItems(self, node: TreeNode, targetList: list):
        targetList.append(node.GetData())
        for childNode in node.GetChildren():
            self._StackItems(childNode, targetList)

    def GenerateSortedItemList(self) -> list[ExperimentSchedulerItemDataBase]:
        targetList = []
        for item in self.treeDict:
            root = self.treeDict.get(item).GetRoot()
            self._StackItems(root, targetList)
        return targetList






