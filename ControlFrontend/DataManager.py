from LinkListStructure import LinkList
import enum


class WaveData:
    def __init__(self,duration:float,type,parameter):
        self.duration = duration
        self.type = type
        self.parameter = parameter


class DeviceSchedule:
    def __init__(self,device):
        self.device = device
        self.schedule = LinkList()

    def AddWave(self,wave:WaveData):
        self.schedule.SetPointer(self.schedule.GetLength()-1)
        self.schedule.AppendDataAfterPointer(wave)

    def DeleteWave(self,wave:WaveData):
        return self.schedule.DeleteData(wave)