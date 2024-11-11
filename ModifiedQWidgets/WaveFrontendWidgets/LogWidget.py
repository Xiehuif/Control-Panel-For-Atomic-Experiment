from enum import Enum
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, pyqtSignal

import ModifiedQWidgets.GeneralWidgets.CheckSelectionWidget as CheckSelectionWidget
import ModifiedQWidgets.GeneralWidgets.HTMLGenerator as HTMLGenerator
from DataStructure import LogManager


class BrowserController:

    class InfoType(Enum):
        File = '文件'
        FunctionName = '函数名'
        Time = '时间'

    def _ReceiveNewLog(self, logRecord: LogManager.LogRecord):
        if self._LogTypeFilter(logRecord.type):
            self._PrintLog(logRecord)

    class _LoadingLogThread(QThread):

        appendText = pyqtSignal(object)

        def __init__(self, logRecords: list[LogManager.LogRecord], controller):
            super().__init__()
            self._logRecords = logRecords
            self._controller: BrowserController = controller

        def run(self):
            logRecords = self._logRecords
            newContent = HTMLGenerator.HTMLContent()
            for i in range(len(logRecords)):
                self._controller.CreateContent(newContent, logRecords[i])
                if i % 10 == 0:
                    self.appendText.emit(newContent.ExportText())
                    newContent.Clear()
                    self.msleep(100)
                else:
                    newContent.NewParagraph()
            self.appendText.emit(newContent.ExportText())

    def _PrintLog(self, logRecord: LogManager.LogRecord):
        newContent = HTMLGenerator.HTMLContent()
        self.CreateContent(newContent, logRecord)
        self._AppendContent(newContent)
        return

    def CreateContent(self, content: HTMLGenerator.HTMLContent, logRecord: LogManager.LogRecord):
        if self._transparency.get(self.InfoType.File):
            self._AddFileInfo(content, logRecord)
        if self._transparency.get(self.InfoType.FunctionName):
            self._AddFunctionName(content, logRecord)
        if self._transparency.get(self.InfoType.Time):
            self._AddTime(content, logRecord)
        self._AddLogContent(content, logRecord)
        return content

    def _AppendContent(self, HTMLText: HTMLGenerator.HTMLContent):
        self._browser.append(HTMLText.ExportText())

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
        if infoSetting is not None:
            self._transparency = infoSetting
        self.RefreshLogDisplay()

    def SetTransparency(self, infoType: InfoType, isVisible: bool):
        self._transparency.update({infoType: isVisible})

    def __init__(self, browser: QtWidgets.QTextBrowser,
                 logTypeCombobox: QtWidgets.QComboBox, transparencyControlBtn: QtWidgets.QPushButton):
        # 显示组件注册
        self._browser = browser
        # 多线程
        self._refreshThread: BrowserController._LoadingLogThread | None = None
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
        if self._refreshThread is not None:
            self._refreshThread.quit()
        self._browser.clear()
        logData = LogManager.GetLogData()
        logRecords = logData.GetLogRecords(self._logTypeSelector.itemData(self._logTypeSelector.currentIndex()))
        self._refreshThread = self._LoadingLogThread(logRecords, self)
        self._refreshThread.appendText.connect(self._browser.append)
        self._refreshThread.start()

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
