from abc import ABC, abstractmethod
from enum import Enum
import ParameterAcquireDialog


class GeneratorBase(ABC):

    @abstractmethod
    def GetGeneratorName(self) -> str:
        pass

    @abstractmethod
    def GetGeneratorParameter(self) -> type[Enum]:
        pass

    @abstractmethod
    def ArrayGenerate(self, data):
        pass

    def Activate(self) -> list:
        classList = [self.GetGeneratorParameter()]
        argDialog = ParameterAcquireDialog.AcquireDialog(classList)
        data = argDialog.Activate()
        return self.ArrayGenerate(data)


class GeneratorHandler:

    def __init__(self):
        self._generators = {}

    def GetGeneratorNames(self) -> list[str]:
        names: [str] = []
        for generatorName in self._generators:
            names.append(generatorName)
        return names

    def RegisterGenerator(self, generator: GeneratorBase):
        self._generators.update({generator.GetGeneratorName(): generator})

    def GetGenerator(self) -> list[GeneratorBase]:
        generatorList: list[GeneratorBase] = []
        for deviceName in self._devices:
            deviceList.append(self._devices[deviceName])
        return deviceList

    def GetDevice(self,deviceName:str):
        for existedDeviceName in self._devices:
            if existedDeviceName == deviceName:
                return self._devices.get(deviceName)
        return None

generatorHandlerInstance = GeneratorHandler()
