import multiprocessing
from enum import Enum
import ctypes
from time import sleep


class _WorkProcess(multiprocessing.Process):

    """
    用于生成可供执行目标负载的进程
    """

    def __init__(self, targetClass, arg, taskQueue: multiprocessing.Queue, argQueue: multiprocessing.Queue,
                 returnQueue: multiprocessing.Queue,queueLock, closeSig, delSig, resetSig, maxTaskAtOnce: int = 5):
        """
        进程初始化
        :param targetClass: 负载类，我们执行这个类上的方法
        :param taskQueue: 任务队列，按照队列内容依次调用方法
        :param argQueue: 参数队列，任务队列中的方法被调用时，依次取出其中内容作为参数
        :param returnQueue: 返回值队列，任务被处理完成时，将返回值依次送入该队列
        :param queueLock: 队列锁，防止上述队列进程间访问冲突
        :param closeSig: 进程关闭信号，外部可写，被置为真时，所有队列关闭，并且等待执行完成后销毁进程实例
        :param delSig: 进程死亡信号，外部可读，若为真，则线程死亡
        """
        super().__init__()
        self._initArg = arg
        self._tQueue = taskQueue
        self._aQueue = argQueue
        self._retQueue = returnQueue
        self.daemon = True
        self._loadClass = targetClass
        self._loadInstance = None
        self._qLock = queueLock
        self._tBuf = []
        self._aBuf = []
        self._retBuf = []
        self._closeSig = closeSig
        self._delSig = delSig
        self._resetSig = resetSig
        self._maxHoldingTask = maxTaskAtOnce

    def Reset(self):
        self._qLock.acquire()
        while self._tQueue.empty() is not True:
            self._tQueue.get()
        while self._aQueue.empty() is not True:
            self._aQueue.get()
        while self._retQueue.empty() is not True:
            self._retQueue.get()
        self._aBuf.clear()
        self._tBuf.clear()
        self._retBuf.clear()
        self._qLock.release()
        self._resetSig.value = False

    def SetMaxTaskBeforeNextTransfer(self, maxTime: int):
        self._maxHoldingTask = maxTime

    def RunFunc(self, funcName, arg):
        """
        该方法负责运行负载类的方法
        :param funcName: 负载类目标方法的名称
        :param arg: 对应参数列表和执行句柄
        :return: 运行的返回值和执行句柄
        """
        func = getattr(self._loadInstance, funcName)
        handle = arg[0]
        data = arg[1]
        result = func(data)
        return [handle, result]

    def _Uninit(self):
        """
        负载实例析构
        :return:
        """
        del self._loadInstance


    def run(self):
        """
        线程主循环
        :return: 没有返回值
        """
        # 初始化负载类，生成负载实例
        self._loadInstance = self._loadClass(self._initArg)
        # 检验负载实例
        if self._loadInstance is None:
            self._delSig.value = True
            return
        # 主循环
        while self._closeSig.value is False:
            # 检验返回缓存是否为空，如果不是，将返回缓存中的数据全部写入返回值队列，并清空返回值缓存
            if len(self._retBuf) != 0:
                self._qLock.acquire()
                for retList in self._retBuf:
                    self._retQueue.put(retList)
                self._qLock.release()
                self._retBuf.clear()
            # 检验任务队列是否为空，如果不是，取出任务到任务缓存
            if not self._tQueue.empty():
                self._qLock.acquire()
                while not self._tQueue.empty():
                    self._tBuf.append(self._tQueue.get())
                    self._aBuf.append(self._aQueue.get())
                self._qLock.release()
                self._tBuf.reverse()
                self._aBuf.reverse()
            # 检验任务缓存时否为空，如果不是，执行所有任务
            if len(self._tBuf) != 0:
                maxTaskNumber = self._maxHoldingTask
                currentTaskNumber = 0
                while (len(self._tBuf) != 0) and (currentTaskNumber < maxTaskNumber):
                    task = self._tBuf.pop()
                    arg = self._aBuf.pop()
                    ret = self.RunFunc(task, arg)
                    self._retBuf.append(ret)
                    currentTaskNumber += 1
            if self._resetSig.value is True:
                self.Reset()
        self._Uninit()
        self._delSig.value = True
        return




class ProcessController:

    __slots__ = ('_taskQ','_retQ','_argQ','_process','_retBuf','_taskState','_qLock','_closeInitSig'
                 ,'_closeFinishedSig', '_blockadeTask', '_resetSig')

    class TaskState(Enum):
        Waiting = 0
        Finished = 1
        Nonexistent = 2

    class ProcessState(Enum):
        Running = 0
        Closing = 1
        Closed = 2

    def __init__(self, baseClass, initializeArg):

        self._taskQ = multiprocessing.Queue()
        self._retQ = multiprocessing.Queue()
        self._argQ = multiprocessing.Queue()
        self._qLock = multiprocessing.Lock()

        self._closeInitSig = multiprocessing.Value(ctypes.c_bool, False)
        self._closeFinishedSig = multiprocessing.Value(ctypes.c_bool, False)
        self._resetSig = multiprocessing.Value(ctypes.c_bool, False)

        self._process = _WorkProcess(baseClass, initializeArg, self._taskQ, self._argQ, self._retQ, self._qLock, self._closeInitSig
                                     , self._closeFinishedSig, self._resetSig)

        self._blockadeTask = False
        self._retBuf: dict = {}
        self._taskState: dict = {}
        self._process.start()

    def _RefreshTasks(self):
        self._qLock.acquire()
        while not self._retQ.empty():
            buf = self._retQ.get()
            handle = buf[0]
            data = buf[1]
            self._retBuf.update({handle: data})
            self._taskState.update({handle: self.TaskState.Finished})
        self._qLock.release()
        return

    def FindReturnValue(self, handle: str):
        self._RefreshTasks()
        if self._taskState.get(handle) is None:
            return self.TaskState.Nonexistent
        elif self._taskState.get(handle) == self.TaskState.Waiting:
            return self.TaskState.Waiting
        else:
            return self._retBuf.get(handle)

    def IsFinished(self, handle: str) -> bool:
        self._RefreshTasks()
        return (self._taskState.get(handle) == self.TaskState.Finished)

    def WaitForDone(self,handle: None|str = None):
        if handle is None:
            cond = True
            while cond:
                check = True
                self._RefreshTasks()
                for task in self._taskState:
                    check = (check and (self._taskState.get(task) == self.TaskState.Finished))
                if not check:
                    continue
                else:
                    cond = False
            return self.TaskState.Finished
        else:
            if handle in self._taskState:
                while not self._taskState.get(handle) == self.TaskState.Finished:
                    self._RefreshTasks()
                return self.TaskState.Finished
            else:
                return self.TaskState.Nonexistent


    def CallFunction(self, funcName, arg, handle: str):
        """
        该方法将调用进程所绑定的类的函数
        :param funcName: 函数名
        :param arg: 参数
        :param handle: 对应任务的handle，用以获得返回值
        :return: 返回是否将任务
        """
        if self._blockadeTask:
            return False
        self._taskState.update({handle: self.TaskState.Waiting})
        pipeArg = [handle, arg]
        self._qLock.acquire()
        self._argQ.put(pipeArg)
        self._taskQ.put(funcName)
        self._qLock.release()
        return True

    def EndProcess(self):
        """
        终止进程，注意这个方法是一个同步方法，该方法将阻塞该方法的调用线程直到本进程结束所有任务并且进入系统回收流程
        :return:
        """
        self._blockadeTask = True
        self._closeInitSig.value = True
        self._process.join()
        print(self._closeFinishedSig.value)

    def GetProcessState(self) -> ProcessState:

        """
        获取进程状态，进程要么处于已关闭状态(Closed)，要么正在准备结束最后的任务以实现关闭(Closing)，要么正在正常运行(Running)
        :return: ProcessState，一个Enum类型，其中的成员Closed、Closing、Running对应含义如上
        """

        if self._closeFinishedSig:
            return self.ProcessState.Closed
        elif self._closeInitSig and not self._closeFinishedSig:
            return self.ProcessState.Closing
        else:
            return self.ProcessState.Running

    def ResetProcess(self):
        self._resetSig.value = True
        self._taskState.clear()
        self._retBuf.clear()
        while self._resetSig.value is not False:
            sleep(0.01)

    def IsResetting(self) -> bool:
        """
        返回重置过程是否进行中
        :return: bool
        """
        return self._resetSig.value

