from enum import Enum

from PyQt6 import QtWidgets

import EditableTableWidget
import ExperimentScheduleManager
from PyTree import TreeNode


class ItemTree(EditableTableWidget.MulticolumnTree):

    class ColumnHead(Enum):
        Name = '任务名称'
        Source = '任务来源'
        Depth = '深度'
        ScannedDevice = '扫描设备'
        ScannedParameterType = '扫描参数'
        Value = '值'
        ScheduledMinimumTime = '计划最小用时'

    def __init__(self, treeWidget: QtWidgets.QTreeWidget):
        super().__init__(treeWidget, self.ColumnHead)
        self._itemsManager = ExperimentScheduleManager.SchedulerItemManager()
        self._itemsMap: dict = {}

    def ImportItem(self, item: ExperimentScheduleManager.ExperimentSchedulerImportedItemData):
        nameDialog = QtWidgets.QInputDialog()
        outputList = nameDialog.getText(None, '名称', '请确定一个名称')
        if not outputList[1]:
            return
        name = outputList[0]
        data = {
            self.ColumnHead.Name: name,
            self.ColumnHead.Source: 'User',
            self.ColumnHead.Depth: '0',
            self.ColumnHead.ScannedDevice: 'Root',
            self.ColumnHead.ScannedParameterType: 'Root',
            self.ColumnHead.Value: 'Default',
            self.ColumnHead.ScheduledMinimumTime: '0'
            # TODO: self.ColumnHead.ScheduledMinimumTime: GetTime()
        }
        newNode = self._itemsManager.ImportRootItem(item)
        item.SetAttachedNode(newNode)
        newTreeWidgetItem = self.InsertItem(data, None, newNode)
        self._itemsMap.update({newNode: newTreeWidgetItem})


class DerivedItemWidget(QtWidgets.QDialog):

    def __init__(self, copiedDeviceDatas, parentNode: TreeNode, parentWidget = None):
        """
        给定一个数据，以问询需要导出的items
        :param copiedDeviceDatas: 一个字典，key是Device的实例，value是对应Device的DeviceSchedule的复制实例
        """
        # 主窗口
        super().__init__(parentWidget)
        self.setWindowTitle('设置扫描参数')
        self._vLayout = QtWidgets.QVBoxLayout()
        self._devicesBoxList: QtWidgets.QComboBox = QtWidgets.QComboBox(None)
        self._waveBoxList: QtWidgets.QComboBox = QtWidgets.QComboBox(None)
        self._parameterItemBoxList: QtWidgets.QComboBox = QtWidgets.QComboBox(None)
        self._generateValueType: QtWidgets.QComboBox = QtWidgets.QComboBox(None)

        self._copiedDatas = copiedDeviceDatas
        self._deviceNameList = []
        for device in copiedDeviceDatas:
            self._deviceList.append(device.deviceName)











