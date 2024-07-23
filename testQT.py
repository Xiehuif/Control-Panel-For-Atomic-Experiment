import sys
from PyQt6.QtWidgets import QWidget, QApplication
import MainWindow
import SubWindow
class TestMainWidget(QWidget):
    def ShowWindow(self,windowForCalled):
        windowForCalled.show()
        return

    def __init__(self,window):
        super().__init__()
        self.subWindow = window
        self.formStyle = MainWindow.Ui_Form()
        self.formStyle.setupUi(self)
        self.formStyle.pushButton.clicked.connect(lambda: print("clicked"))
        self.formStyle.pushButton_2.clicked.connect(window.show)


class TestSubWidget(QWidget):
    def __init__(self):
        super().__init__()
        formStyle = SubWindow.Ui_Form()
        formStyle.setupUi(self)

app = QApplication(sys.argv)
subWindow = TestSubWidget()
window = TestMainWidget(subWindow)
window.show()
sys.exit(app.exec())


