import inspect
import time
from enum import Enum
from DataStructure import SerializationManager
import datetime

class LogType(Enum):
    Info = 'Info'
    Error = 'Error'
    Runtime = 'Runtime'
    Any = 'Any'
    Experiment = 'Experiment'

class LogRecord(SerializationManager.Serializable):

    _timeFormat = '%Y-%m-%d %H:%M:%S'
    def __init__(self, jsonContext = None):
        self.initiatingObjectFile = []
        self.initiatingObjectFunctionName: str = 'null function'
        self.info: str = 'null str'
        self.type: LogType = LogType.Any
        self.logTime: str = datetime.datetime.now().strftime(self._timeFormat)
        super().__init__()
        if jsonContext is not None:
            self.Deserialize(jsonContext)

    def SetTime(self,dateTime:datetime.datetime):
        self.logTime = dateTime.strftime(self._timeFormat)

    def SetInfo(self,info: str):
        self.info = info

    def SetType(self,logType: LogType):
        self.type = logType

    def SetInitiatingFunction(self,targetFunction):
        self.initiatingObjectFunctionName = targetFunction

    def AddFileName(self,fileName: str):
        self.initiatingObjectFile.append(fileName)

    def __str__(self):
        targetStr = '\n Sent from file:'
        for i in range(0,len(self.initiatingObjectFile)):
            targetStr = targetStr + '\n' + 'file ' + self.initiatingObjectFile[i]
        targetStr = targetStr + '\n' + 'In function: ' + self.initiatingObjectFunctionName
        targetStr = targetStr + '\n' + 'Time:' + self.logTime
        targetStr = targetStr + '\n' + '[' + self.type.name + ']:' + self.info
        return targetStr

    def __gt__(self, other):
        if type(other) == type(self):
            otherTime = datetime.datetime.strptime(other.logTime,self._timeFormat)
            selfTime = datetime.datetime.strptime(self.logTime,self._timeFormat)
            return selfTime > otherTime
        else:
            return self > other

    def __lt__(self, other):
        if type(other) == type(self):
            otherTime = datetime.datetime.strptime(other.logTime,self._timeFormat)
            selfTime = datetime.datetime.strptime(self.logTime,self._timeFormat)
            return selfTime < otherTime
        else:
            return self < other

class LogData(SerializationManager.Serializable):
    def __init__(self):
        self.logContentDict = {}
        for logType in LogType:
            self.logContentDict.update({logType :[]})
        super().__init__()

    def SendLog(self, logRecord: LogRecord):
        targetDict = self.logContentDict.get(logRecord.type)
        targetDict.append(logRecord)

    def GetLogRecords(self,logType: LogType = LogType.Any):
        targetLogList = []
        if logType == LogType.Any:
            for targetType in self.logContentDict:
                for logRecord in self.logContentDict.get(targetType):
                    targetLogList.append(logRecord)
        else:
            targetLogList = self.logContentDict.get(logType)
        targetLogList.sort()
        return targetLogList

class _ExperimentLogHandler:
    def __init__(self):
        self.logData = LogData()
        self._callbacks = []

    def SendLog(self, logRecord: LogRecord):
        for callback in self._callbacks:
            callback(logRecord)
        self.logData.SendLog(logRecord)

    def RegisterCallback(self, callback):
        self._callbacks.append(callback)

    def Log(self, log: str, type: LogType = LogType.Any):
        logRecord = LogRecord()
        logRecord.SetType(type)
        logRecord.SetTime(datetime.datetime.now())
        logRecord.SetInfo(log)
        runtimeStack = inspect.stack()
        stackLength = len(runtimeStack)
        for i in range(2,stackLength):
            if runtimeStack[i].filename.startswith('<'):
                continue
            logRecord.AddFileName(runtimeStack[i].filename + ' line ' + str(runtimeStack[i].lineno))
        logRecord.SetInitiatingFunction(runtimeStack[2].function)
        print(logRecord)
        for callback in self._callbacks:
            callback(logRecord)
        self.logData.SendLog(logRecord)


_experimentLogHandler = _ExperimentLogHandler()

def RegisterCallback(callback):
    _experimentLogHandler.RegisterCallback(callback)

def LogByLogRecord(logRecord: LogRecord):
    _experimentLogHandler.SendLog(logRecord)

def GetLogData():
    return _experimentLogHandler.logData

def Log(info: str, logType: LogType = LogType.Any):
    _experimentLogHandler.Log(info, logType)
