from PyQt6 import QtWidgets,QtCore,QtGui


class CheckWidget(QtWidgets.QDialog):

    def __init__(self, checkItems: dict, explainationText: str = '请选择', parent: QtWidgets.QWidget = None):
        self.dialogParent = parent
        self.items = checkItems
        self.explainationText = explainationText
        self._check = False
        super().__init__(parent)

    def _CreateLayout(self, itemCheckBoxDict: dict) -> QtWidgets.QBoxLayout:
        # 主布局
        mainLayout = QtWidgets.QVBoxLayout()
        # 说明文本
        explainationLabel = QtWidgets.QLabel()
        explainationLabel.setText(self.explainationText)
        mainLayout.addWidget(explainationLabel)
        for item in self.items:
            # 每项文本
            itemText: str = self.items.get(item)
            # 每项选框
            itemCheckBox = QtWidgets.QCheckBox()
            #布局
            mainLayout.addWidget(itemCheckBox)
            # 为选框注册文本与数据关系
            itemCheckBox.setText(itemText)
            itemCheckBox.setChecked(True)
            itemCheckBoxDict.update({item: itemCheckBox})
        return mainLayout

    def _CancelButtonClicked(self):
        self._check = False
        self.close()

    def _CheckButtonClicked(self):
        self._check = True
        self.close()

    def ShowItemCheckDialog(self) -> dict|None:
        itemCheckBoxes = {}
        # 生成词条布局
        mainLayout = self._CreateLayout(itemCheckBoxes)
        # 生成操作按钮
        checkButton = QtWidgets.QPushButton()
        checkButton.setText('确认')
        checkButton.clicked.connect(self._CheckButtonClicked)
        cancelButton = QtWidgets.QPushButton()
        cancelButton.setText('取消')
        cancelButton.clicked.connect(self._CancelButtonClicked)
        # 向layout中添加
        mainLayout.addWidget(checkButton)
        mainLayout.addWidget(cancelButton)
        # 注册layout
        self.setLayout(mainLayout)
        self.setSizeGripEnabled(False)
        self.exec()
        if self._check is False:
            return None
        inputResult = {}
        for item in itemCheckBoxes:
            itemCheckBox: QtWidgets.QCheckBox = itemCheckBoxes.get(item)
            inputResult.update({item: (itemCheckBox.isChecked())})
        return inputResult
