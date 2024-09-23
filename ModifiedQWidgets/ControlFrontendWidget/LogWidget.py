from enum import Enum
from PyQt6 import QtWidgets
import CheckSelectionWidget
import HTMLGenerator
import LogManager


class BrowserController:

    class InfoType(Enum):
        File = '文件'
        FunctionName = '函数名'
        Time = '时间'

    def _ReceiveNewLog(self,logRecord: LogManager.LogRecord):
        if self._LogTypeFilter(logRecord.type):
            self._PrintLog(logRecord)

    def _PrintLog(self,logRecord: LogManager.LogRecord):
        self._content.NewParagraph()
        if self._transparency.get(self.InfoType.File):
            self._AddFileInfo(self._content, logRecord)
        if self._transparency.get(self.InfoType.FunctionName):
            self._AddFunctionName(self._content, logRecord)
        if self._transparency.get(self.InfoType.Time):
            self._AddTime(self._content, logRecord)
        self._AddLogContent(self._content, logRecord)
        self._ApplyContent()
        return

    def _ApplyContent(self):
        self._browser.setHtml(self._content.ExportText())

    def _InitializeTransparency(self):
        self._transparency.update({self.InfoType.Time: True})
        self._transparency.update({self.InfoType.FunctionName: True})
        self._transparency.update({self.InfoType.File: True})

    def _InitializeLogTypeCombobox(self, targetCombobox: QtWidgets.QComboBox):
        index = 0
        for item in LogManager.LogType:
            targetCombobox.addItem(item.value)
            index = targetCombobox.findText(item.value)
            targetCombobox.setItemData(index, item)

    def _LogTypeFilter(self, logType: LogManager.LogType):
        currentType = self._logTypeSelector.itemData(self._logTypeSelector.currentIndex())
        if currentType is None:
            return False
        if currentType == LogManager.LogType.Any:
            return True
        else:
            return currentType == logType

    def _ResettingInfoTransparency(self):
        infoExplaination = {}
        for infoType in self.InfoType:
            infoExplaination.update({infoType: infoType.value})
        checkWidget = CheckSelectionWidget.CheckWidget(infoExplaination, '请选择提示内容', self._browser)
        infoSetting = checkWidget.ShowItemCheckDialog()
        self._transparency = infoSetting
        self.RefreshLogDisplay()

    def SetTransparency(self, infoType: InfoType, isVisible: bool):
        self._transparency.update({infoType: isVisible})

    def __init__(self, browser: QtWidgets.QTextBrowser, logTypeCombobox: QtWidgets.QComboBox, transparencyControlBtn: QtWidgets.QPushButton):
        # 显示组件注册
        self._browser = browser
        self._content = HTMLGenerator.HTMLContent()
        # 信息可见度
        self._transparency = {}
        self._transparencySettingBtn = transparencyControlBtn
        self._InitializeTransparency()
        self._transparencySettingBtn.clicked.connect(self._ResettingInfoTransparency)
        # 日志显示类型
        self._logTypeSelector = logTypeCombobox
        self._InitializeLogTypeCombobox(self._logTypeSelector)
        initIndex = self._logTypeSelector.findData(LogManager.LogType.Any)
        self._logTypeSelector.setCurrentIndex(initIndex)
        self._logTypeSelector.currentIndexChanged.connect(self.RefreshLogDisplay)
        # 注册日志显示回调
        LogManager.RegisterCallback(self._ReceiveNewLog)
        # 最后刷新
        self.RefreshLogDisplay()

    def RefreshLogDisplay(self):
        self._content.Clear()
        logData = LogManager.GetLogData()
        logRecords = logData.GetLogRecords(self._logTypeSelector.itemData(self._logTypeSelector.currentIndex()))
        size = len(logRecords)
        for i in range(0,size):
            self._PrintLog(logRecords[i])
        self._ApplyContent()

    @staticmethod
    def _AddFileInfo(HTMLContent: HTMLGenerator.HTMLContent, logRecord: LogManager.LogRecord):
        HTMLContent.NewLine()
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Normal)
        HTMLContent.SetColor(HTMLContent.Color.black)
        HTMLContent.AppendText('Sent from file:')
        for file in logRecord.initiatingObjectFile:
            HTMLContent.NewLine()
            HTMLContent.SetDisplayType(HTMLContent.DisplayType.Normal)
            HTMLContent.AppendText('file ')
            HTMLContent.SetDisplayType(HTMLContent.DisplayType.Bold)
            HTMLContent.AppendText(file)

    @staticmethod
    def _AddFunctionName(HTMLContent: HTMLGenerator.HTMLContent, logRecord: LogManager.LogRecord):
        HTMLContent.NewLine()
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Normal)
        HTMLContent.SetColor(HTMLContent.Color.black)
        HTMLContent.AppendText('In function: ')
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Italic)
        HTMLContent.SetColor(HTMLContent.Color.blue)
        HTMLContent.AppendText(logRecord.initiatingObjectFunctionName)

    @staticmethod
    def _AddTime(HTMLContent: HTMLGenerator.HTMLContent, logRecord: LogManager.LogRecord):
        HTMLContent.NewLine()
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Normal)
        HTMLContent.SetColor(HTMLContent.Color.black)
        HTMLContent.AppendText('Time: ')
        HTMLContent.SetColor(HTMLContent.Color.red)
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Normal)
        HTMLContent.AppendText(logRecord.logTime)

    @staticmethod
    def _AddLogContent(HTMLContent: HTMLGenerator.HTMLContent, logRecord: LogManager.LogRecord):
        HTMLContent.NewLine()
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Italic)
        HTMLContent.SetColor(HTMLContent.Color.blue)
        HTMLContent.AppendText('[{}] '.format(logRecord.type.value))
        HTMLContent.SetDisplayType(HTMLContent.DisplayType.Normal)
        HTMLContent.SetColor(HTMLContent.Color.black)
        HTMLContent.AppendText(logRecord.info)
