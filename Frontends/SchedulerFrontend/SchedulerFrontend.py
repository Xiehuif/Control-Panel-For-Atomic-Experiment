from PyQt6 import QtWidgets
from PyQt6.QtGui import QCloseEvent

from DataStructure import LogManager
from DataStructure.PyTree import TreeNode
from Frontends.SchedulerFrontend import SchdulerFrontendForm,SchedulerFrontendButtonBehavior
from ModifiedQWidgets.ExperimentSchedulerWidgets import ItemWidgets, ExperimentItemRunningPanel

class ExperimentScheduler(QtWidgets.QWidget, SchdulerFrontendForm.Ui_SchedulerForm):

    def __init__(self, frontendFinder: dict ,parent = None):
        super().__init__(parent)

        # 初始化变量
        form = SchdulerFrontendForm.Ui_SchedulerForm()
        form.setupUi(self)
        LogManager.Log('Scheduler initialized', LogManager.LogType.Runtime)

        # 控件初始化
        self.itemTable = ItemWidgets.ExperimentScheduleItemTree(form.ExperimentView)
        self.runningPanel = ExperimentItemRunningPanel.RunningPanel(self.itemTable, form.ExecutionProgressBar)

        # 辅助量
        self.copiedItem: list[TreeNode] = []
        self.copiedFromTree = None

        # 多界面入口
        self.frontendFinder = frontendFinder
        self.frontendFinder.update({self.__class__: self})

        # 事件绑定，此处模块导入滞后，防止循环导入造成标识符缺失报错
        from Frontends.SchedulerFrontend.SchedulerMenuBehavior import SchedulerMenuBehavior
        self.itemTable.GetViewWidget().AddMenuCallback(
            lambda item: SchedulerMenuBehavior.MenuEntrance(item, self.itemTable)
        )

        form.ImportFromWavePanelBtn.clicked.connect(
            lambda: SchedulerFrontendButtonBehavior.ImportButtons.ImportFromWavePanel(self.itemTable)
        )

        form.ScanArgBtn.clicked.connect(
            lambda: SchedulerFrontendButtonBehavior.ImportButtons.DeriveFromCurrentItems(self.itemTable, self)
        )

        form.ExportToWavePanelBtn.clicked.connect(
            lambda: SchedulerFrontendButtonBehavior.ExportButtons.ExportToWavePanel(self.itemTable, self.frontendFinder)
        )

        form.InitBtn.clicked.connect(
            lambda: SchedulerFrontendButtonBehavior.RunningButton.ExecutionCurrentItems(self.itemTable, self.runningPanel)
        )

    def closeEvent(self, a0, QCloseEvent=None):
        LogManager.Log('Scheduler hiden', LogManager.LogType.Runtime)
        self.hide()
        a0.ignore()


