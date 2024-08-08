import PyQt6
import ControlPanel
import sys
import DataManager
import ModifiedLabels


class ControlFrontEnd(PyQt6.QtWidgets.QMainWindow):
    testNumber = 0
    def __init__(self):
        super().__init__()
        form = ControlPanel.Ui_MainWindow()
        import Timeline
        form.setupUi(self)
        self.testDevice = DataManager.DeviceSchedule('test')
        self.timeLineController = Timeline.TimelinesController(form.TimeLine,self.testDevice)
        form.AddOperationBtn.clicked.connect(self.AddBlcokTest)
        form.DeleteOperationBtn.clicked.connect(self.DeleteBlockTest)


    def AddBlcokTest(self):
        title = 'test block' + str(self.testNumber)
        self.testNumber = self.testNumber + 1
        self.testDevice.AddWave(DataManager.WaveData(10,title,'None'))
        self.timeLineController.ShowBlocks()

    def DeleteBlockTest(self):
        deletedWaveLabel:list[ModifiedLabels.SelectableLabel] = self.timeLineController.selectionManager.GetSelected()
        while len(deletedWaveLabel) != 0:
            deletedWave: DataManager.WaveData = deletedWaveLabel.pop().attachedObject
            self.testDevice.DeleteWave(deletedWave)
        self.timeLineController.ShowBlocks()





if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = ControlFrontEnd()
    panel.show()
    sys.exit(app.exec())


