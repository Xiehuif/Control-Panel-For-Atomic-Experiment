"""
File IO Support
TO BE DONE...
"""
from PyQt6 import QtCore
from PyQt6.QtCore import QIODevice, QTextStream

import LogManager
import SerializationManager


class SerializableIO:
    """
    读写文件的接口
    不要实例化这个类
    直接调用静态函数即可
    """

    @staticmethod
    def WriteStringToFile(fileDirectory: str, targetStr: str):
        fileDevice = QtCore.QFile(fileDirectory)
        if fileDevice.open(QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text):
            textStream = QTextStream(fileDevice)
            textStream.setEncoding(QtCore.QStringEncoder.Encoding.Utf8)
            textStream << targetStr
            fileDevice.close()
        else:
            LogManager.Log('Can not write in file:' + fileDirectory,LogManager.LogType.Error)

    @staticmethod
    def ReadStringFromFile(fileDirectory: str) -> str:
        fileDevice = QtCore.QFile(fileDirectory)
        targetStr = None
        if fileDevice.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
            textStream = QTextStream(fileDevice)
            textStream.setEncoding(QtCore.QStringEncoder.Encoding.Utf8)
            targetStr = textStream.readAll()
            fileDevice.close()
        return targetStr

