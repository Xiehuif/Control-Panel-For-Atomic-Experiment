import copy
from enum import Enum, IntEnum
from multiprocessing import Queue
from time import sleep

from PyQt6.QtCore import QThread, QMutex, pyqtSignal, Qt

import DataStructure.DataManager
import MultiprocessSupport.MultiprocessKernel
from collections import deque

from DataStructure import LogManager
from DataStructure.ExperimentScheduleManager import ExperimentSchedulerItemDataBase
import cProfile

class ProcessServer:

    """线程服务类，用于操作Device，实例化于实验操作的守护进程"""

    def __init__(self, logQueue):
        self.processDeviceHandler = DataStructure.DataManager.ObjectHandler()
        self._logQueue = logQueue
        LogManager.RegisterCallback(self.LogPiper)
        LogManager.Log('Log system in exp. process has already online', LogManager.LogType.Experiment)
        return

    def InitializeDevice(self, object):
        """
        初始化，注册设备
        :param object: list对象，有目前所有设备的类名
        :return: None
        """
        for className in object:
            newDevice: DataStructure.DataManager.Device = className()
            self.processDeviceHandler.RegisterObject(newDevice, newDevice.deviceName)
            newDevice.DeviceAwake()

    def RefreshSchdule(self, scheduleDict: dict):
        """
        传入参数
        :param scheduleDict: deviceName作为key，DeviceSchedule作为value
        :return: None
        """
        for deviceName in scheduleDict:
            LogManager.Log('deviceName:{} detected by process'.format(deviceName), LogManager.LogType.Runtime)
            localDevice: DataStructure.DataManager.Device = self.processDeviceHandler.GetObject(deviceName)
            remoteDeviceSchedule: DataStructure.DataManager.DeviceSchedule = scheduleDict.get(deviceName)
            localDevice.deviceSchedule.CopyFromSchedule(remoteDeviceSchedule)

    def Run(self, nullArg):
        """
        启动程序
        :return:
        """
        returnDict = {}
        for device in self.processDeviceHandler.GetObjects():
            returnValue = device.DeviceRun()
            returnDict.update({device.deviceName: returnValue})
        return returnDict

    def LogPiper(self, logRecord):
        self._logQueue.put(logRecord)


class ControlProxy:

    """ 实验操作守护进程的操作代理，实例化于主线程，实例化后启动实验操作的守护进程 """

    class LogProxy(QThread):

        transferLog = pyqtSignal(object)

        def __init__(self, logQueue: Queue):
            super().__init__()
            self._logQueue = logQueue

        def run(self):
            while True:
                self.sleep(1)
                if not self._logQueue.empty():
                    while not self._logQueue.empty():
                        self.transferLog.emit(self._logQueue.get())

    def __init__(self):
        # 获取设备列表
        deviceList = DataStructure.DataManager.deviceHandlerInstance.GetObjects()
        deviceClassList = []
        for device in deviceList:
            deviceType = type(device)
            deviceClassList.append(deviceType)
        # 声明多线程
        self._logQueue: Queue = Queue()
        self._processController = MultiprocessSupport.MultiprocessKernel.ProcessController(ProcessServer,
                                                                                           self._logQueue)
        self._logProxy = self.LogProxy(self._logQueue)
        # 配置多线程
        self._logProxy.transferLog.connect(LogManager.LogByLogRecord)
        self._logProxy.start(QThread.Priority.LowestPriority)
        self._processController.CallFunction(ProcessServer.InitializeDevice.__name__, deviceClassList, "init")
        self._processController.WaitForDone()
        LogManager.Log('Control Proxy Successfully open exp. process', LogManager.LogType.Runtime)

    def ImportSchedule(self, scheduleDict: dict):
        self._processController.CallFunction(ProcessServer.RefreshSchdule.__name__, scheduleDict, 'importData')
        self._processController.WaitForDone()

    def RunDevices(self):
        self._processController.CallFunction(ProcessServer.Run.__name__, None, 'deviceRun')
        self._processController.WaitForDone()
        return self._processController.FindReturnValue('deviceRun')

    def WaitForDone(self):
        self._processController.WaitForDone()

    def Reset(self):
        self._processController.ResetProcess()

    def IsResetting(self):
        return self._processController.IsResetting()

    def WaitReset(self):
        while True:
            if not self.IsResetting():
                return


class TaskRunningThread(QThread):
    """
    与实验操作守护进程通信的主进程内线程
    """

    logOutput = pyqtSignal(object)
    runCallback = pyqtSignal(object)
    stateChange = pyqtSignal(object)

    class RunningState(IntEnum):
        WaitingForStart = 0
        Running = 1
        Pausing = 2
        Paused = 3
        Stopping = 4
        Stopped = 5
        Continuing = 6

    def __init__(self, taskDeque, length, proxy):
        super().__init__(None)
        self._taskDeque = taskDeque
        self._length = length
        self._runningState = self.RunningState.WaitingForStart
        self._pauseFlag = False
        self._stopFlag = False
        self._remoteControlLock = QMutex()
        self._proxy: ControlProxy = proxy

    def SetPause(self):
        self._remoteControlLock.lock()
        if self._runningState != self.RunningState.Running:
            self._remoteControlLock.unlock()
            return False
        self._pauseFlag = True
        self._runningState = self._runningState.Pausing
        self._remoteControlLock.unlock()
        return True

    def SetStop(self):
        self._remoteControlLock.lock()
        if self._runningState == (self.RunningState.WaitingForStart | self._runningState.Pausing | self._runningState.Continuing | self._runningState.Stopping):
            self._remoteControlLock.unlock()
            return
        self._stopFlag = True
        self._runningState = self.RunningState.Stopping
        self._remoteControlLock.unlock()

    def GetRunningState(self):
        self._remoteControlLock.lock()
        copiedState = copy.deepcopy(self._runningState)
        self._remoteControlLock.unlock()
        return copiedState

    def Start(self):
        if self._runningState == self._runningState.WaitingForStart:
            self.start()
        else:
            return

    def _DeviceLoad(self, loadSchedule):
        # self.logOutput.emit('Reset proxy for exp.')
        # self._proxy.Reset()
        # self._proxy.WaitReset()
        # self.logOutput.emit('Resetting finished')
        # self.logOutput.emit('Import schedule')
        self._proxy.ImportSchedule(loadSchedule)
        # self.logOutput.emit('Schedule imported')
        # self.logOutput.emit('Running')
        returnValue = self._proxy.RunDevices()
        # self.logOutput.emit('Finished')
        return returnValue

    def _Uninit(self):
        # self.logOutput.emit('Experiment stop process initiated')
        self._runningState = self.RunningState.Stopped
        # self.logOutput.emit('Experiment has been stopped')
        return

    def run(self):
        self.logOutput.emit('Experiment Run, loaded length:{}'.format(self._length))
        for i in range(self._length):
            self.stateChange.emit((i, TaskManager.State.Waiting))
        for i in range(self._length):
            # 检查线程工作状态
            # self.logOutput.emit('Current task number:{}'.format(i))
            self._remoteControlLock.lock()
            # self.logOutput.emit('Experiment State:{}'.format(self._runningState.name))
            if self._runningState == self.RunningState.Pausing:
                # self.logOutput.emit('Experiment pause')
                self._runningState = self.RunningState.Paused
                self._remoteControlLock.unlock()
                while True:
                    sleep(1)
                    self._remoteControlLock.lock()
                    if self._runningState == self.RunningState.Continuing:
                        # self.logOutput.emit('Experiment is trying to continue from being paused')
                        self._runningState = self.RunningState.Running
                        self._remoteControlLock.unlock()
                        break
                    elif self._runningState == self.RunningState.Stopping:
                        # self.logOutput.emit('Experiment is trying to stop from being paused')
                        self._remoteControlLock.unlock()
                        break
                    else:
                        self._remoteControlLock.unlock()
            else:
                self._remoteControlLock.unlock()
            self._remoteControlLock.lock()
            if self._runningState == self.RunningState.Stopping:
                # self.logOutput.emit('Experiment is stopping')
                self._Uninit()
                self._remoteControlLock.unlock()
                return
            else:
                self._remoteControlLock.unlock()
            # 获取数据
            taskData = self._taskDeque.popleft()
            taskIndex = taskData[0]
            schedule = taskData[1]
            # self.stateChange.emit((taskIndex, TaskManager.State.Running))
            # self.logOutput.emit('Experiment index:{} is started'.format(taskIndex))
            # 分配负载
            returnValue = self._DeviceLoad(schedule)
            # self.logOutput.emit('Experiment index:{} is finished'.format(taskIndex))
            self.stateChange.emit((taskIndex, TaskManager.State.Finished))
            self.runCallback.emit((taskIndex, returnValue))

class TaskManager:

    """
    用于向实验守护进程中实现各种功能的控制器，封装了通信线程和进程代理
    """

    class State(IntEnum):
        Waiting = 0
        Running = 1
        Finished = 2
        Uninitiated = 3
        Excluded = 4

    def __init__(self):
        # 工作线程控制器
        self._controller = ControlProxy()
        # 任务队列
        self._taskDeque = deque()
        # 回调查询字典
        self._callbackDict = {}
        # 状态回调
        self._stateCallback = None
        # 维护变量
        self._indexAssigned = 0
        self._taskThread = None

    def SetStateChangeCallback(self, callback):
        self._stateCallback = callback

    def StateChange(self, index: int, state: State):
        if self._stateCallback is None:
            return
        data = (index, state)
        self._stateCallback(data)

    def Reset(self):
        # 重置本地队列，任务运行时，实验进程将会被托管线程重置，因而无需关心托管线程
        self._taskDeque.clear()
        self._callbackDict.clear()
        self._indexAssigned = 0
        self._taskThread = None

    def PutTask(self, item: ExperimentSchedulerItemDataBase, callback) -> int:
        # 加长
        index = self._indexAssigned
        self._indexAssigned += 1
        # 置入数据
        data = {}
        item.GetData(data)
        dataTuple = (index, data)
        self._taskDeque.append(dataTuple)
        # 置入回调
        self._callbackDict.update({index: callback})
        # 返回index
        return index

    def RunTasks(self, callback = None):
        # 产生线程，注入依赖
        self._taskThread = TaskRunningThread(self._taskDeque, self._indexAssigned, self._controller)
        if self._stateCallback is not None:
            self._taskThread.stateChange.connect(self._stateCallback, type=Qt.ConnectionType.BlockingQueuedConnection)
        self._taskThread.logOutput.connect(lambda string: LogManager.Log(string, LogManager.LogType.Runtime), type=Qt.ConnectionType.BlockingQueuedConnection)
        self._taskThread.runCallback.connect(lambda dataTuple: (self._callbackDict.get(dataTuple[0]))(dataTuple), type=Qt.ConnectionType.BlockingQueuedConnection)
        if callback is not None:
            self._taskThread.finished.connect(callback)
        # 线程启动
        self._taskThread.Start()

    def Pause(self):
        # TODO
        pass

    def Continue(self):
        # TODO
        pass

    def Stop(self):
        # TODO
        pass

taskManagerInstance: TaskManager | None = None

def InitiateInstance():
    MultiprocessSupport.ExperimentProcess.taskManagerInstance = TaskManager()
    return
