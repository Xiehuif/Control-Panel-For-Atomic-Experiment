# program entrance

import Devices
import sys

import PyQt6

from Frontends.SchedulerFrontend import SchedulerFrontend
from Frontends.WaveFrontend.WavePanelFrontend import WaveFrontend
import MultiprocessSupport.ExperimentProcess
# release only

if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    frontendFinder = {}

    # 线程模块初始化
    MultiprocessSupport.ExperimentProcess.InitiateInstance()

    # 创建组件
    wavePanel = WaveFrontend(frontendFinder)
    scheduler = SchedulerFrontend.ExperimentScheduler(frontendFinder)

    # 执行
    wavePanel.show()
    exitValue = app.exec()
    sys.exit(exitValue)


# debug only
import MultiprocessSupport.ExperimentProcess
from time import sleep
# if __name__ == '__main__':
    # multiControl = MultiprocessSupport.ExperimentProcess.ControlProxy()
    # multiControl.RunDevices()
    # multiControl.WaitForDone()

