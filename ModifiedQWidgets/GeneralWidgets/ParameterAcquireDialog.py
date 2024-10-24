from PyQt6 import QtWidgets
from DataStructure import DataManager
from enum import Enum


class AcquireDialog(QtWidgets.QDialog):
    """

    本类用于产生创建参数的Dialog，并返回对应的参数

    """

    def __init__(self, dataEnumClasses: list[type[Enum]], presetting: dict[Enum] = None):
        # 传入参数
        self._dataEnumClasses: list[type[Enum]] = dataEnumClasses
        self._presetting = presetting
        # 数据维护
        self._result: dict[Enum] | None = None
        self._editLineCollector: dict[QtWidgets.QLineEdit] = {}
        self._checkState: bool = False

    def Activate(self) -> dict[Enum] | None:
        """
        这是这一Dialog的唯一入口，调用这个函数将启动参数的输入流程
        :return: 如果输入流程正常结束，返回参数的输入结果，结果是一个dict，key是Clarification的Enum，见下方定义，value是参数的值；
                 如果输入流程被中断，返回Enum
        """
        super().__init__(None)
        self._SetWidgetUI()
        self._result = None
        self.exec()
        return self._result

    def _GetDataClarifications(self) -> list:
        """
        根据指示收集所有必要的数据声明
        :return: 返回一个列表，每一项是一个Enum，对应一条参数，Enum的value是一个列表，value列表第一项是这个参数的名称，
                 第二项是参数的数据类型，数据类型将会用于检查输入的合法性并确保后续利用这个数据的操作符合程序设定
        """
        '''
        # original
        dataEnum = self.waveData.type
        dataClarifications = []
        dataClarifications.append(self.titleItem)
        for clarificationName,clarification in dataEnum.value[1].__members__.items():
            dataClarifications.append(clarification)
        return dataClarifications
        '''
        dataClarifications = []
        for enumClass in self._dataEnumClasses:
            for enumItem in enumClass:
                dataClarifications.append(enumItem)
        return dataClarifications

    def _CreateItemUI(self, clarification: Enum, collector: dict[QtWidgets.QLineEdit]) -> QtWidgets.QHBoxLayout:
        '''
        为每一条参数，在dialog内创建一行来寻求用户输入
        :param clarification: 每一条参数的声明，每个声明是一个enum，定义见_GetDataClarification
        :param collector: 用于收集用户输入的QLineEdit控件，一个字典，key为QLineEdit控件，value为对应的clarification
        :return: 返回一个实现该条参数收集的水平布局控件
        '''
        # 声明水平布局
        itemLayout = QtWidgets.QHBoxLayout()
        # 获取参数的名称
        name = clarification.value[0] + ':'
        # 添加控件，实现布局： 布局目标 --> 参数名称: [输入框]
        itemLayout.addWidget(QtWidgets.QLabel(name))
        editLine = QtWidgets.QLineEdit()
        itemLayout.addWidget(editLine)
        # 如果已有数据，读入
        if self._presetting is not None:
            editLine.setText(str(self._presetting.get(clarification)))
        # 向collector添加需要收集的数据，格式如函数注释
        collector.update({editLine: clarification})
        return itemLayout

    def _SetWidgetUI(self) -> dict[QtWidgets.QLineEdit]:
        '''
        根据_GetDataClarification的收集结果产生窗口
        :return: 一个字典，key是对应参数的输入控件，value是参数声明的enum，详细格式见_GetDataClarification
        '''
        # 确定UI布局控制目标和控制参数
        widget = self
        dataClarifications = self._GetDataClarifications()
        # 声明返回值
        dataCollector: dict[QtWidgets.QLineEdit] = self._editLineCollector
        # 主垂直布局声明
        mainLayout = QtWidgets.QVBoxLayout()
        widget.setLayout(mainLayout)
        # 读取声明，创建每一条参数的控件布局，并将其添加到主垂直布局中
        # 注意到dataCollector此时也收集了所有QEditLine和参数声明Enum的对应关系
        for clarification in dataClarifications:
            mainLayout.addLayout(self._CreateItemUI(clarification, dataCollector))
        # 声明操作按钮
        checkButton = QtWidgets.QPushButton('确认')
        cancelButton = QtWidgets.QPushButton('取消')
        # 向布局中添加按钮
        mainLayout.addWidget(checkButton)
        mainLayout.addWidget(cancelButton)
        # 绑定按钮事件
        checkButton.clicked.connect(self._Check)
        cancelButton.clicked.connect(self._Cancel)
        return dataCollector

    def _Check(self):
        '''
        处理用户按下确定按钮后的事件
        :return: 这是事件回调，没有返回值
        '''
        self._result = {}
        # 对每一个控件做数据收集
        for targetEditLine in self._editLineCollector:
            # 获取对应目标参数的用户输入，名称和数据类型
            inputContent: str = targetEditLine.text()
            clarification: Enum = self._editLineCollector.get(targetEditLine)
            name: str = clarification.value[0]
            type = clarification.value[1]
            # 声明参数的值
            parameterValue = None
            # 尝试类型转换
            try:
                parameterValue = type(inputContent)
            except Exception as e:
                closeButton = QtWidgets.QMessageBox.StandardButton.Close
                result = self.ParameterConvertErrorDialog(name, inputContent, str(type), e, closeButton)
                if result == closeButton:
                    self._result = None
                    return
            self._result.update({clarification: parameterValue})
        self._checkState = True
        self.close()

    @staticmethod
    def ParameterConvertErrorDialog(dialog, parameterName: str, content: str, type: str, exception: Exception,
                                     closeButton: QtWidgets.QPushButton) -> QtWidgets.QPushButton:

        """
        报错窗口，当尝试将用户输入转换为对应的参数出错时，提供提示

        :param parameterName: 参数名称
        :param content: 用户输入内容
        :param type: 参数被设定的类型
        :param closeButton: 关闭按钮
        :return: 返回按钮状态
        """
        title = '参数错误'
        message: str = ('在处理参数： ' + parameterName
                        + ' 时,读取到值为：' + content + '，无法转换类型到： '
                        + type
                        + ' ，错误类型为{}，请检查格式是否匹配'.format(exception))
        result = QtWidgets.QMessageBox.critical(dialog, title, message, closeButton)
        return result

    def _Cancel(self):
        """
        取消的事件的回调
        :return: 事件回调，无返回值
        """
        self._checkState = False
        self._result = None
        self.close()


