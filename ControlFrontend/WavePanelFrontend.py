# PRIORITY
import DataManager
import DevicesImport

# third-party libs or system libs
import sys

import PyQt6
from PyQt6 import QtWidgets

# Data control
import DeviceSelector
import LogWidget
import ModifiedLabels
import Timeline
# Modified widgets
import TimelinePlotWidget
# Widget Connect
import WaveFrontendButtonBehavior
import WaveFrontendFileIO
import WavePanel


class WaveFrontend(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        # parent init
        super().__init__()

        # 初始化变量
        form = WavePanel.Ui_MainWindow()
        form.setupUi(self)

        # 控件控制
        self.logController = LogWidget.BrowserController(form.LogBrowser, form.LogType,
                                                         form.LogInfoTransparencySettingBtn)
        self.selector = DeviceSelector.SelectorController(form.OutputDeviceList, form.WaveTypeList)
        self.deviceHandler = DataManager.deviceHandlerInstance
        self.timeLineController = Timeline.TimelinesController(form.TimeLine, self.selector)
        self.plotController = TimelinePlotWidget.TimelinePlotWidgetController(form.waveView, self.timeLineController)

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
            lambda :WaveFrontendButtonBehavior.ButtonBehavior.AddWaveBlock(self.selector,self.RefreshUI)
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

        (form.ExecuteOperationBtn.
         clicked.connect(WaveFrontendButtonBehavior.ButtonBehavior.InitiateDevice))

        (form.Open.triggered.
         connect(lambda: WaveFrontendFileIO.WaveIO.OpenFileAction(self, self.RefreshUI)))

        (form.Save.triggered.
         connect(lambda: WaveFrontendFileIO.WaveIO.SaveFileAction(self)))

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

# program entrance
if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = WaveFrontend()
    panel.show()
    exitValue = app.exec()
    sys.exit(exitValue)