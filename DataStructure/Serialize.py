import enum
import json
import sys


class Serializable:
    def __init__(self,jsonContext: str|None = None):
        self.Deserialize(jsonContext)

    def Deserialize(self, jsonContext :str|None):
        if jsonContext is None:
            return
        dataDict = json.loads(jsonContext)
        print(dataDict)
        for varName in dataDict:
            self.__setattr__(varName,self.FromStringListToVarible(dataDict.get(varName)))
        return

    def ConvertObjectToVaribleStringList(self,var) -> list[str]|None:
        """
        通过重写该函数为更多类型提供序列化能力，返回的列表应有两个对象，第一个对象是仅含有一个字符串类型参数的，作为var类型的实例化函数名称
        然后另一个对象是实例化所需的字符串参数
        :param var:序列化目标
        :return: 字符串列表
        """
        return None

    @staticmethod
    def FromStringListToVarible(stringList):
        moduleStr = stringList[0]
        classStr = stringList[1]
        methodStr = stringList[2]
        argObj = stringList[3]
        targetModule = sys.modules.get(moduleStr)
        targetClass = targetModule.__getattribute__(classStr)
        targetMethod = getattr(targetClass,methodStr)
        obj = targetMethod(argObj)
        return obj

    @staticmethod
    def FromStringListToBuiltinIterable(argObj:list):
        res = []
        load:list = argObj[3]
        sizeNum = len(load)
        for i in range(0,sizeNum):
            obj = Serializable.FromStringListToVarible(load[i])
            res.append(obj)
        return res

    @staticmethod
    def FromStringListToBuiltinIterablelist(argObj):
        return Serializable.FromStringListToBuiltinIterable(argObj)

    @staticmethod
    def FromStringListToBuiltinIterableset(argObj):
        return set(Serializable.FromStringListToBuiltinIterable(argObj))

    @staticmethod
    def FromStringListToBuiltinIterabletuple(argObj):
        return tuple(Serializable.FromStringListToBuiltinIterable(argObj))

    @staticmethod
    def FromStringListToBuiltinDict(argObj:list):
        res = {}
        load:dict = argObj[3]
        for keyStringList in load:
            valueStringList = load.get(keyStringList)
            key = Serializable.FromStringListToVarible(keyStringList)
            value = Serializable.FromStringListToVarible(valueStringList)
            res.update({key:value})
        return res





    def FromVaribleToStringList(self, var):
        varList = []
        varList.append(type(var).__module__)
        varList.append(type(var).__name__)
        if type(var).__module__ == 'builtins':
            varList.append('__call__')
            if isinstance(var, (list, tuple, set)):
                varList[0] = self.__module__
                varList[1] = 'Serializable'
                varList[2] = self.FromStringListToBuiltinIterable.__name__ + type(var).__name__
                varContent = list(var)
                contentList = []
                size = len(varContent)
                for i in range(0,size):
                    contentList.append(self.FromVaribleToStringList(varContent[i]))
                varList.append(contentList)
                return varList
            if isinstance(var, (int, float, str, bool)):
                varList.append(str(var))
                return varList
            if isinstance(var, dict):
                varList[0] = self.__module__
                varList[1] = 'Serializable'
                varList[2] = self.FromStringListToBuiltinDict.__name__
                varContent = list(var)
                contentDict = {}
                for key in var:
                    keyList = self.FromVaribleToStringList(key)
                    valueList = self.FromVaribleToStringList(var.get(key))
                    contentDict.update({keyList: valueList})
                varList.append(contentDict)
                return varList
        if isinstance(var,Serializable):
            varList.append('__call__')
            varList.append(var.Serialize())
            return varList
        if isinstance(var,enum.Enum):
            varList.append('__getitem__')
            varList.append(var.name)
            return varList
        customVarList = self.ConvertObjectToVaribleStringList(var)
        if customVarList is None:
            print('Serializable : can\'t convert ' + type(var).__name__)
            return ['None']
        if isinstance(customVarList,list) and len(customVarList) == 2:
            varList.append(customVarList[0])
            varList.append(customVarList[1])
        else:
            print('Serializable : can\'t convert ' + type(var).__name__)
            return ['None']



    def Serialize(self,encoder:json.JSONEncoder = json.JSONEncoder()) -> str:
        varList = self.GetVaribleName()
        jsonStr = 'null'
        varDict = {}
        for varName in varList:
            varValue = getattr(self,varName)
            varDict.update({varName: self.FromVaribleToStringList(varValue)})
        jsonStr = json.dumps(varDict)
        return jsonStr

    def GetVaribleName(self) -> list[str]:
        fullMemberList = dir(self)
        varibleMemberList = []
        for member in fullMemberList:
            if not (member.startswith('_') or type(self.__getattribute__(member)).__name__ == 'method'):
                varibleMemberList.append(member)
        return varibleMemberList
