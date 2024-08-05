import PyQt6
import ControlPanel
import sys

class ControlFrontEnd(PyQt6.QtWidgets.QMainWindow):
    testNumber = 0
    def __init__(self):
        super().__init__()
        form = ControlPanel.Ui_MainWindow()
        import Timeline
        form.setupUi(self)

        self.timeLineController = Timeline.TimelinesController(form.TimeLine)
        form.AddOperationBtn.clicked.connect(self.AddBlcokTest)
        self.timeLineController.RegisterDeleteButton(form.DeleteOperationBtn)


    def AddBlcokTest(self):
        title = 'test block' + str(self.testNumber)
        self.testNumber = self.testNumber + 1
        descriptionTest = ['this should work','sample: Time = 1ms']
        self.timeLineController.AddWave(title,descriptionTest)
        self.timeLineController.ShowBlocks()




if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = ControlFrontEnd()
    panel.show()
    sys.exit(app.exec())


