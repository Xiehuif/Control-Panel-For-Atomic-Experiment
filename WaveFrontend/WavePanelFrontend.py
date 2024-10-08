# PRIORITY : Data control
import DataManager
import DevicesImport
import LogManager

# third-party libs or system libs
import sys
import PyQt6
from PyQt6 import QtWidgets

# Modified widgets
import ModifiedLabels
import Timeline
import DeviceSelector
import LogWidget
import TimelinePlotWidget
import SchedulerFrontend

# Widget Support
import WaveFrontendButtonBehavior
import WaveFrontendFileIO
import WavePanelFrontendForm



class WaveFrontend(PyQt6.QtWidgets.QMainWindow):
    def __init__(self, frontendFinder: dict):
        # parent init
        super().__init__()

        # 初始化变量
        form = WavePanelFrontendForm.Ui_MainWindow()
        form.setupUi(self)

        # 控件控制组件生成
        self.logController = LogWidget.BrowserController(form.LogBrowser, form.LogType,
                                                         form.LogInfoTransparencySettingBtn)
        self.selector = DeviceSelector.SelectorController(form.OutputDeviceList, form.WaveTypeList)
        self.deviceHandler = DataManager.deviceHandlerInstance
        self.timeLineController = Timeline.TimelinesController(form.TimeLine, self.selector)
        self.plotController = TimelinePlotWidget.TimelinePlotWidgetController(form.waveView, self.timeLineController)

        # 多界面入口
        self.frontendFinder: dict = frontendFinder
        self.frontendFinder.update({self.__class__: self})

        # 事件绑定
        (self.timeLineController.
         selectionManager.
         BindSelectionChangeEvent(
            lambda:WaveFrontendButtonBehavior.ButtonBehavior.
            ButtonStateCheck(form.DeleteOperationBtn,form.ModifyOperationBtn,
                             form.InsertOperationBtn,self.timeLineController.
                             selectionManager)
        ))

        (form.AddOperationBtn.clicked.connect(
            lambda :WaveFrontendButtonBehavior.ButtonBehavior.AddWaveBlock(self.selector, self.RefreshUI)
        ))

        (form.DeleteOperationBtn.
         clicked.connect(
            lambda :WaveFrontendButtonBehavior.ButtonBehavior.
            DeleteWaveBlock(self.timeLineController.selectionManager, self.selector, self.RefreshUI)
        ))

        (form.ModifyOperationBtn.
         clicked.connect(
            lambda :WaveFrontendButtonBehavior.ButtonBehavior.
            ModifyWaveBlock(self.timeLineController.selectionManager, self.selector, self.RefreshUI)
        ))

        (form.InsertOperationBtn.
         clicked.connect(
            lambda :WaveFrontendButtonBehavior.ButtonBehavior.InsertWaveBlock(
                self.timeLineController.selectionManager, self.selector, self.RefreshUI
            )
        ))

        (form.SchedulerPanelBtn.
         clicked.connect(
            lambda :WaveFrontendButtonBehavior.ButtonBehavior.ShowPanel(
                self.frontendFinder.get(SchedulerFrontend.ExperimentScheduler)
            )
        ))

        (form.WaveFileOpen.triggered.
         connect(lambda: WaveFrontendFileIO.WaveIO.OpenFileAction(self, self.RefreshUI)))

        (form.WaveFileSave.triggered.
         connect(lambda: WaveFrontendFileIO.WaveIO.SaveFileAction(self)))

        (form.LogFileSave.triggered.
         connect(lambda: WaveFrontendFileIO.LogIO.SaveFileAction(LogManager.GetLogData(), self)))

        (form.LogFileOpen.triggered.
         connect(lambda: WaveFrontendFileIO.LogIO.OpenFileAction(LogManager.GetLogData(), self, self.RefreshUI)))

        (form.ApplyTimescaleBtn.
         clicked.connect(lambda: WaveFrontendButtonBehavior.
                         ButtonBehavior.SetTimelineTimescale
        (self, form.TimescaleSetting, self.timeLineController)))

        # 刷新界面
        WaveFrontendButtonBehavior.ButtonBehavior.ButtonStateCheck(
            form.DeleteOperationBtn, form.ModifyOperationBtn,
            form.InsertOperationBtn, self.timeLineController.selectionManager)

    def RefreshUI(self):
        self.logController.RefreshLogDisplay()
        self.timeLineController.ShowBlocks()
        self.plotController.ReplotDevicesAsynchronously()
