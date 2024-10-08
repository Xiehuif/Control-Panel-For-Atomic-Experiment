# program entrance
import sys

import PyQt6

import SchedulerFrontend
from WavePanelFrontend import WaveFrontend

if __name__ == '__main__':
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    frontendFinder = {}

    # 创建组件
    wavePanel = WaveFrontend(frontendFinder)
    scheduler = SchedulerFrontend.ExperimentScheduler(frontendFinder)

    wavePanel.show()
    exitValue = app.exec()
    sys.exit(exitValue)