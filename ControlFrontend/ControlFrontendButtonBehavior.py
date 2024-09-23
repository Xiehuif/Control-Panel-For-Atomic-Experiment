# third-party libs or system libs
from PyQt6 import QtWidgets,QtCore,QtGui
from artiq.experiment import *

import DataManager
import DeviceSelector
import Timeline
import TimelinePlotWidget


class ButtonBehavior:

    def __init__(self):
        self.selector = None
        self.timeLineController = None
        self.plotController = None
        self.deviceHandler = DataManager.deviceHandlerInstance

    def SetDeviceSelector(self,selector: DeviceSelector.SelectorController):
        self.selector = selector

    def SetTimelineController(self, controller: Timeline.TimelinesController):
        self.timeLineController = controller
        controller.selectionManager.BindSelectionChangeEvent(self.ButtonStateCheck)
        self.ButtonStateCheck()

    def SetTimelinePlotController(self, plotController: TimelinePlotWidget.TimelinePlotWidgetController):
        self.plotController = plotController


