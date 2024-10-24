"""
File IO Support
TO BE DONE...
"""
from enum import Enum, StrEnum

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QIODevice, QTextStream

from DataStructure import LogManager, SerializationManager


class FileExtensionRule(StrEnum):
    WaveDataFile = 'wvd',
    LogDataFile = 'lgd',
    ExperimentScheduleDataFile = 'esd'


class SerializableIO:

    """
    读写文件的接口
    不要实例化这个类
    直接调用静态成员函数即可
    """

    @staticmethod
    def _GetFilterString(fileDescription: str, fileExtension: FileExtensionRule | None = None):
        if fileExtension is None:
            return '{} (*.*)'.format(fileDescription)
        else:
            return '{} (*.{})'.format(fileDescription, fileExtension.value)

    @classmethod
    def DisplayFileSaveDialog(cls, widgetParent, fileDescription: str, fileExtension: FileExtensionRule | None = None) \
            -> str | None:

        fileDialog = QtWidgets.QFileDialog
        fileFilter = cls._GetFilterString(fileDescription, fileExtension)
        fileDirList = fileDialog.getSaveFileName(widgetParent, '', '', fileFilter)
        if fileDirList is not None and fileDirList[0] != '':
            return fileDirList[0]
        else:
            return None

    @classmethod
    def DisplayFileOpenDialog(cls, widgetParent, fileDescription: str, fileExtension: FileExtensionRule | None = None) \
            -> str | None:

        fileDialog = QtWidgets.QFileDialog
        fileFilter = cls._GetFilterString(fileDescription, fileExtension)
        fileDirList = fileDialog.getOpenFileName(widgetParent, '', '', fileFilter)
        if fileDirList is not None and fileDirList[0] != '':
            return fileDirList[0]
        else:
            return None

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
        if targetStr is None:
            LogManager.Log('SerializableIO Read Err : Can not read string from \'{}\', '
                           'you may have canceled your reading action. Otherwise, there is an exception have occurred.'
                           .format(fileDirectory), LogManager.LogType.Error)
        return targetStr
