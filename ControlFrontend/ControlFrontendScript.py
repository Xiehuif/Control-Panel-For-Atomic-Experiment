import PyQt6
import ControlPanel
import sys
import DataManager
import ModifiedLabels
import Testdevices
import TimelinePlotWidget
import DeviceSelector
class ControlFrontEnd(PyQt6.QtWidgets.QMainWindow):
    testNumber = 0
    def __init__(self):
        super().__init__()
        form = ControlPanel.Ui_MainWindow()
        import Timeline
        form.setupUi(self)
        form.AddOperationBtn.clicked.connect(self.AddBlcokTest)
        form.DeleteOperationBtn.clicked.connect(self.DeleteBlockTest)
        self.selector = DeviceSelector.SelectorController(form.OutputDeviceList, form.WaveTypeList)
        self.timeLineController = Timeline.TimelinesController(form.TimeLine, self.selector)
        self.plotController = TimelinePlotWidget.TimelinePlotWidgetController(form.waveView,self.timeLineController)

    def RefreshUI(self):
        self.timeLineController.ShowBlocks()
        self.plotController.ReplotDevicesAsynchronously()

    def AddBlcokTest(self):
        title = 'test block' + str(self.testNumber)
        self.testNumber = self.testNumber + 1
        waveData = DataManager.WaveData(10, None, 'None')
        self.selector.ShowParameterPanel(waveData,self.Insert)

    def Insert(self, waveData: DataManager.WaveData):
        self.selector.GetCurrentDevice().deviceSchedule.AddWave(waveData)
        self.RefreshUI()

    def DeleteBlockTest(self):
        deletedWaveLabel:list[ModifiedLabels.SelectableLabel] = self.timeLineController.selectionManager.GetSelected()
        while len(deletedWaveLabel) != 0:
            deletedWave: DataManager.WaveData = deletedWaveLabel.pop().attachedObject
            self.selector.GetCurrentDevice().deviceSchedule.DeleteWave(deletedWave)
        self.RefreshUI()





if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = ControlFrontEnd()
    panel.show()
    sys.exit(app.exec())


