import copy
from enum import Enum, IntEnum, StrEnum

from PyQt6 import QtWidgets

import MultiprocessSupport.ExperimentProcess
from DataStructure import DataManager, ExperimentScheduleManager, LogManager, ParameterGeneratorsManager
import ModifiedQWidgets.GeneralWidgets.EditableTableWidget as EditableTableWidget
import ModifiedQWidgets.GeneralWidgets.ParameterAcquireDialog as ParameterAcquireDialog
from DataStructure.PyTree import TreeNode, Tree


class ItemTree(EditableTableWidget.MulticolumnTree):

    def _GenerateWidgetItemData(self, item: ExperimentScheduleManager.ExperimentSchedulerItemDataBase) -> dict:
        """
        依照类型生成表格数据

        :param item: 实验数据项
        :return: WidgetItem所需的data参数
        """
        data = None
        if isinstance(item, ExperimentScheduleManager.ExperimentSchedulerDerivedItemData):
            itemName = item.GetName()
            source = item.GetAttachedNode().GetParent().GetData().GetName()
            depth = item.GetAttachedNode().GetDepth()
            scannedDevice = item.deviceName
            scannedIndex = item.targetWaveIndex
            scannedType = item.targetParameterItem.value[0]
            value = item.appliedValue
            time = 0
            # time = GetTime()
            data = {
                self.ColumnHead.Name: itemName,
                self.ColumnHead.Source: source,
                self.ColumnHead.Depth: str(depth),
                self.ColumnHead.ScannedDevice: scannedDevice,
                self.ColumnHead.ScannedIndex: str(scannedIndex),
                self.ColumnHead.ScannedParameterType: scannedType,
                self.ColumnHead.Value: str(value),
                self.ColumnHead.ScheduledMinimumTime: str(time)
            }
        elif isinstance(item, ExperimentScheduleManager.ExperimentSchedulerImportedItemData):
            name = item.GetName()
            data = {
                self.ColumnHead.Name: name,
                self.ColumnHead.Source: 'User',
                self.ColumnHead.Depth: '0',
                self.ColumnHead.ScannedDevice: 'Root',
                self.ColumnHead.ScannedIndex: 'None',
                self.ColumnHead.ScannedParameterType: 'None',
                self.ColumnHead.Value: 'Default',
                self.ColumnHead.ScheduledMinimumTime: '0'
                # TODO: self.ColumnHead.ScheduledMinimumTime: str(GetTime())
            }
        else:
            raise TypeError('Unexpected type of item when try to generate widget data in ItemTree')
        return data

    def ChangeRunningState(self, item: QtWidgets.QTreeWidgetItem,
                           state: MultiprocessSupport.ExperimentProcess.TaskManager.State):
        index = self.GetColumnIndex(self.ColumnHead.RunningState)
        respondText = None
        if state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Uninitiated:
            respondText = '等待用户操作'
        if state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Excluded:
            respondText = '不在运行范围内'
        if state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Running:
            respondText = '运行中'
        if state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Waiting:
            respondText = '等待运行'
        if state == MultiprocessSupport.ExperimentProcess.TaskManager.State.Finished:
            respondText = '已完成'
        item.setText(index, respondText)

    class MenuItem(StrEnum):
        Delete = '删除'
        Copy = '复制'
        Cut = '剪切'
        Paste = '粘贴'
        SelectLeafItems = '选中所有终端项'

    class ColumnHead(Enum):
        Name = '任务名称'
        Source = '任务来源'
        Depth = '深度'
        ScannedDevice = '扫描设备'
        ScannedIndex = '波形所在索引'
        ScannedParameterType = '扫描参数'
        Value = '值'
        ScheduledMinimumTime = '计划最小用时'
        RunningState = '运行状态'

    def __init__(self, treeWidget: EditableTableWidget.MenuTreeWidget):
        super().__init__(treeWidget, self.ColumnHead, self.MenuItem)
        self._itemsManager = ExperimentScheduleManager.SchedulerItemManager()
        self._itemsMap: dict = {}
        self.SetLayoutPolicyToAdaptContent()

    def ImportRootItem(self, rootItem: ExperimentScheduleManager.ExperimentSchedulerImportedItemData):
        item = rootItem
        data = self._GenerateWidgetItemData(rootItem)
        newNode = self._itemsManager.ImportRootItem(item)
        item.SetAttachedNode(newNode)
        newTreeWidgetItem = self.InsertItem(data, None, newNode)
        self._itemsMap.update({newNode: newTreeWidgetItem})

    def InsertDerivedItems(self, parentNode: TreeNode, items: list[ExperimentScheduleManager.ExperimentSchedulerDerivedItemData]):
        for item in items:
            copiedItem = copy.deepcopy(item)
            newNode = self._itemsManager.ImportDerivedItem(parentNode, copiedItem)
            data = self._GenerateWidgetItemData(copiedItem)
            newTreeWidgetItem = self.InsertItem(data, self._itemsMap.get(newNode.GetParent()), newNode)
            self._itemsMap.update({newNode: newTreeWidgetItem})

    def GetTreeWidgetItemByTreeNode(self, treeNode: TreeNode) -> QtWidgets.QTreeWidgetItem:
        return self._itemsMap.get(treeNode)

    def ExportDataByString(self) -> str:
        return self._itemsManager.Serialize()

    def ImportDataByString(self, dataStr):
        self._itemsManager.Deserialize(dataStr)
        treeList: list[Tree] = self._itemsManager.GetTrees()
        for tree in treeList:
            rootNode = tree.GetRoot()
            self._RetrieveWidgetItems(rootNode)

    def _RetrieveWidgetItems(self, node: TreeNode):
        # 先应用自身数据
        expItem: ExperimentScheduleManager.ExperimentSchedulerItemDataBase = node.GetData()
        data = self._GenerateWidgetItemData(expItem)
        newTreeWidgetItem = self.InsertItem(data, self._itemsMap.get(node.GetParent()), node)
        # 更新映射
        self._itemsMap.update({node: newTreeWidgetItem})
        # 对子节点更新
        for childNode in node.GetChildren():
            self._RetrieveWidgetItems(childNode)

    def InsertDerivedNodes(self, parentNode: TreeNode, nodes: list[TreeNode]):
        for node in nodes:
            # 复制节点，获取数据
            copiedNode = copy.deepcopy(node)
            # 应用TreeNode数据间关系
            copiedNode.SetParent(parentNode)
            # 生成UI控件数据
            self._RetrieveWidgetItems(copiedNode)

    def DeleteItem(self, item: QtWidgets.QTreeWidgetItem) -> bool:
        widgetItem = item
        treeNode: TreeNode = self.GetUserData(item)
        widgetFlag = super().DeleteItem(widgetItem)
        treeFlag = self._itemsManager.DeleteItem(treeNode.GetData())
        self._UnbindNode(treeNode)
        if treeFlag and widgetFlag:
            return True
        elif treeFlag is True:
            LogManager.Log('ItemTree: this content exist in Qt widget but not exist in backend, you might check '
                           'how this report be printed', LogManager.LogType.Error)
            return False
        elif widgetFlag is True:
            LogManager.Log('ItemTree: this content exist in Qt widget but not exist in backend, you might check '
                           'how this report be printed', LogManager.LogType.Error)
            return False
        elif (not treeFlag) and (not widgetFlag):
            LogManager.Log('ItemTree: this content does not exist in neither Qt widget nor backend, you might '
                           'check how this report be printed', LogManager.LogType.Error)
            return False

    def _UnbindNode(self, node: TreeNode):
        try:
            self._itemsMap.pop(node)
        except KeyError as e:
            LogManager.Log('Remove item err: remove an node that is not existed', LogManager.LogType.Error)

'''
2024/10/13

LOG:
为了扫描参数，实现导出关系，从而给出一个ItemDeriveWidget是一个很合理的做法
但是这个类本身既整合了UI又整合了后端数据处理，我不清楚这是不是在给自己以后埋雷
但是目前也无法预测，这个UI逻辑是否会被复用，或许这是一个稍微简单的处理方法，如果不需要复用的话
或许一个更好的方案是把这个类的UI整合到ParameterAcquireDialog类里面，然后在此类中聚合
'''

class ItemDeriveWidget(QtWidgets.QDialog):


    class _SelectableItems(StrEnum):
        Device = '目标设备：'
        WaveIndex = '目标波形：'
        WaveParameter = '目标参数：'
        IsGenerated = '生成方式：'

    def _AddTitledComboBox(self, vLayout: QtWidgets.QVBoxLayout, title: str) -> QtWidgets.QComboBox:
        comboBox = QtWidgets.QComboBox(None)
        labelTitle = QtWidgets.QLabel()
        labelTitle.setText(title)
        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(labelTitle)
        hLayout.addWidget(comboBox)
        vLayout.addLayout(hLayout)
        return comboBox

    def _SetMainComboBox(self, widgetsDict: dict) -> QtWidgets.QVBoxLayout:
        # 控件
        _vLayout = QtWidgets.QVBoxLayout()
        for item in self._SelectableItems:
            newComboBox = self._AddTitledComboBox(_vLayout, item)
            widgetsDict.update({item: newComboBox})
        self.setLayout(_vLayout)
        return _vLayout

    def _SetValueItem(self, mainLayout: QtWidgets.QVBoxLayout, hLayout: QtWidgets.QHBoxLayout):
        hLayout.addWidget(QtWidgets.QLabel('值：'))
        valueBox = QtWidgets.QLineEdit()
        hLayout.addWidget(valueBox)
        mainLayout.addLayout(hLayout)
        return valueBox

    def _SetButtonItem(self, mainLayout: QtWidgets.QVBoxLayout):
        checkButton = QtWidgets.QPushButton()
        checkButton.setText('确定')
        cancelButton = QtWidgets.QPushButton()
        cancelButton.setText('取消')
        checkButton.clicked.connect(self._Check)
        cancelButton.clicked.connect(self._Cancel)
        mainLayout.addWidget(checkButton)
        mainLayout.addWidget(cancelButton)

    def _GenerateComboBoxItems(self, targetSelectableItem: _SelectableItems, itemNameList: list, itemDataList: list):
        targetComboBox: QtWidgets.QComboBox = self._widgetsDict.get(targetSelectableItem)
        targetComboBox.clear()
        targetComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
        targetComboBox.setCurrentIndex(-1)
        if len(itemNameList) != len(itemDataList):
            LogManager.Log('ItemDeriveWidget: Unmatched list length in generate combo box items',
                           LogManager.LogType.Error)
            return
        length = len(itemDataList)
        for index in range(length):
            itemString = itemNameList[index]
            itemData = itemDataList[index]
            targetComboBox.addItem(itemString)
            targetComboBox.setItemData(index, itemData, 100)
            index += 1

    def _GetCurrentData(self, targetSelectableItem: _SelectableItems):
        targetBox: QtWidgets.QComboBox = self._widgetsDict.get(targetSelectableItem)
        return targetBox.currentData(100)

    def _RefreshDeviceComboBoxData(self):
        deviceNameList = self._copiedDeviceDatas.keys()
        itemNames = []
        itemDatas = []
        for deviceName in deviceNameList:
            device = DataManager.deviceHandlerInstance.GetObject(deviceName)
            itemNames.append(device.deviceName)
            itemDatas.append(device)
        self._GenerateComboBoxItems(self._SelectableItems.Device, itemNames, itemDatas)
        self._RefreshWaveComboBoxData()

    def _RefreshWaveComboBoxData(self):
        targetDevice: DataManager.Device = self._GetCurrentData(self._SelectableItems.Device)
        if targetDevice is None:
            return
        targetSchedule: DataManager.DeviceSchedule = self._copiedDeviceDatas.get(targetDevice.deviceName)
        itemNames = []
        itemDatas = []
        for wave in targetSchedule.scheduleData:
            itemNames.append(wave.title)
            itemDatas.append(wave)
        self._GenerateComboBoxItems(self._SelectableItems.WaveIndex, itemNames, itemDatas)
        self._RefreshArgComboBoxData()

    def _RefreshArgComboBoxData(self):
        waveData: DataManager.WaveData = self._GetCurrentData(self._SelectableItems.WaveIndex)
        if waveData is None:
            return
        itemNames = []
        itemDatas = []
        for item in waveData.parameter:
            itemNames.append(item.value[0])
            itemDatas.append(item)
        self._GenerateComboBoxItems(self._SelectableItems.WaveParameter, itemNames, itemDatas)
        self._RefreshGeneratorComboBoxData()

    def _RefreshGeneratorComboBoxData(self):
        argTypeEnum = self._GetCurrentData(self._SelectableItems.WaveParameter)
        methods: list[ParameterGeneratorsManager.GeneratorBase] = ParameterGeneratorsManager.generatorHandlerInstance.GetObjects()
        itemNames = []
        itemDatas = []
        if argTypeEnum is None:
            return
        argType = argTypeEnum.value[1]
        for method in methods:
            allowType: tuple = method.AllowedType()
            if allowType is None or argType in allowType:
                itemNames.append(method.GetGeneratorName())
                itemDatas.append(method)
        itemNames.append('值')
        itemDatas.append(0)
        self._GenerateComboBoxItems(self._SelectableItems.IsGenerated, itemNames, itemDatas)
        self._ShowValueLayout()

    def _ShowValueLayout(self):
        methodBox: QtWidgets.QComboBox = self._widgetsDict.get(self._SelectableItems.IsGenerated)
        if methodBox.itemData(methodBox.currentIndex(), 100) == 0:
            self._valueBox.setEnabled(True)
        else:
            self._valueBox.setEnabled(False)

    def _Check(self):
        self._returnValue = []
        # 辅助数据初始化
        wave: DataManager.WaveData = self._GetCurrentData(self._SelectableItems.WaveIndex)
        device = self._GetCurrentData(self._SelectableItems.Device)
        schedule: DataManager.DeviceSchedule = self._copiedDeviceDatas.get(device.deviceName)
        index = schedule.GetIndexOfWave(wave)
        argType = self._GetCurrentData(self._SelectableItems.WaveParameter)
        method = self._GetCurrentData(self._SelectableItems.IsGenerated)
        for item in wave, device, argType, method:
            if item is None:
                return
        # 参数生成
        collectValueObject = []
        if method == 0:
            # 手动输入，捕获参数
            valueStr = self._valueBox.text()
            collectValueObject.append(valueStr)
        else:
            # 由特定方法生成
            generateMethod: ParameterGeneratorsManager.GeneratorBase = method
            collectValueObject = generateMethod.Activate()
        # 参数类型转换
        if collectValueObject is None or len(collectValueObject) == 0:
            self._returnValue = None
            return
        availableValue = []
        argTypeClass = argType.value[1]
        value = None
        for item in collectValueObject:
            try:
                value = argTypeClass(item)
            except Exception as e:
                closeButton = QtWidgets.QMessageBox.StandardButton.Close
                res = ParameterAcquireDialog.AcquireDialog.ParameterConvertErrorDialog(self, wave.title, valueStr,
                                                                                       argTypeClass, e, closeButton)
                if res == closeButton:
                    self._returnValue = None
                    return
            availableValue.append(value)
        for itemValue in availableValue:
            expItem = ExperimentScheduleManager.ExperimentSchedulerDerivedItemData(None, index,
                                                                                   argType, itemValue, device)
            self._returnValue.append(expItem)
        self.close()

    def _Cancel(self):
        self._returnValue = None
        self.close()

    def __init__(self, copiedDeviceDatas, parentWidget = None):

        """
        给定一个数据，以问询需要导出的items
        :param copiedDeviceDatas: 一个字典，key是Device的DeviceName，value是对应Device的DeviceSchedule的复制实例
        :param parentNodes: 一个列表，所有预备导出的节点的父节点
        :param parentWidget: 父控件
        """

        # 主窗口UI
        super().__init__(parentWidget)
        self.setWindowTitle('设置扫描参数')
        self._widgetsDict = {}
        self._mainLayout = self._SetMainComboBox(self._widgetsDict)
        self._valueLayout = QtWidgets.QHBoxLayout()
        self._valueBox: QtWidgets.QLineEdit = self._SetValueItem(self._mainLayout, self._valueLayout)
        self._SetButtonItem(self._mainLayout)
        self._copiedDeviceDatas: dict = copiedDeviceDatas
        self._parentWidget = parentWidget

        # ComboBox逻辑
        self._returnValue = None

        # 绑定设备与波形ComboBox关联
        targetComboBox: QtWidgets.QComboBox = self._widgetsDict.get(self._SelectableItems.Device)
        targetComboBox.currentIndexChanged.connect(self._RefreshWaveComboBoxData)

        # 绑定波形与参数ComboBox关联
        targetComboBox = self._widgetsDict.get(self._SelectableItems.WaveIndex)
        targetComboBox.currentIndexChanged.connect(self._RefreshArgComboBoxData)

        # 绑定参数与生成方法ComboBox关联
        targetComboBox = self._widgetsDict.get(self._SelectableItems.WaveParameter)
        targetComboBox.currentIndexChanged.connect(self._RefreshGeneratorComboBoxData)

        # 绑定生成方法与值布局关联
        targetComboBox = self._widgetsDict.get(self._SelectableItems.IsGenerated)
        targetComboBox.currentIndexChanged.connect(self._ShowValueLayout)

        # 初始化
        self._RefreshDeviceComboBoxData()

    def Activate(self) -> list[ExperimentScheduleManager.ExperimentSchedulerDerivedItemData]:
        self.exec()
        return self._returnValue



