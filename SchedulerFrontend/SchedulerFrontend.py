from PyQt6 import QtWidgets

import LogManager
import SchdulerFrontendForm
import SchedulerFrontendButtonBehavior
import ItemWidgets
import WavePanelFrontend


class ExperimentScheduler(QtWidgets.QWidget, SchdulerFrontendForm.Ui_SchedulerForm):

    def __init__(self, frontendFinder: dict ,parent = None):
        super().__init__(parent)

        # 初始化变量
        form = SchdulerFrontendForm.Ui_SchedulerForm()
        form.setupUi(self)
        LogManager.Log('Scheduler initialized', LogManager.LogType.Runtime)

        # 控件初始化
        self.itemTable = ItemWidgets.ItemTree(form.ScheduleTree)

        # 多界面入口
        self.frontendFinder = frontendFinder
        self.frontendFinder.update({self.__class__: self})

        # 事件绑定
        form.ImportFromWavePanelBtn.clicked.connect(
            lambda: SchedulerFrontendButtonBehavior.ImportButtons.ImportFromWavePanel(self.itemTable)
        )

        form.ExportToWavePanelBtn.clicked.connect(
            lambda: SchedulerFrontendButtonBehavior.ExportButtons.ExportToWavePanel(self.itemTable, self.frontendFinder)
        )



    def closeEvent(self, a0, QCloseEvent=None):
        LogManager.Log('Scheduler hiden', LogManager.LogType.Runtime)
        self.hide()
        a0.ignore()


