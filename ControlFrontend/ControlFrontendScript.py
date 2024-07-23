import PyQt6
import ControlPanel
import sys

class ControlFrontEnd(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        form = ControlPanel.Ui_MainWindow()
        form.setupUi(self)


if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    panel = ControlFrontEnd()
    panel.show()
    sys.exit(app.exec())


