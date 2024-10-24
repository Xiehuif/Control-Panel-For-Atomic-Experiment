from abc import ABC, abstractmethod
from enum import Enum
import ModifiedQWidgets.GeneralWidgets.ParameterAcquireDialog as ParameterAcquireDialog
from DataStructure.DataManager import ObjectHandler


class GeneratorBase(ABC):

    def AllowedType(self) -> tuple | None:
        return None

    @abstractmethod
    def GetGeneratorName(self) -> str:
        pass

    @abstractmethod
    def GetGeneratorParameter(self) -> type[Enum]:
        pass

    @abstractmethod
    def ArrayGenerate(self, data: dict) -> list:
        pass

    def Activate(self) -> list | None:
        classList = [self.GetGeneratorParameter()]
        argDialog = ParameterAcquireDialog.AcquireDialog(classList)
        data = argDialog.Activate()
        if data is None:
            return None
        else:
            return self.ArrayGenerate(data)

generatorHandlerInstance = ObjectHandler()
import DataStructure.UserEditable