from enum import Enum
from PyQt6 import QtWidgets


class HTMLContent:
    class Color(Enum):
        red = 'red'
        blue = 'blue'
        green = 'green'
        black = 'black'
        brown = 'brown'

    class DisplayType(Enum):
        Normal = 0
        Bold = 1
        Italic = 2

    def __init__(self):
        self._text: str = '<p>'
        self._color = self.Color.black
        self._fontDisplayType = self.DisplayType.Normal

    def Clear(self):
        self._text: str = '<p>'

    def NewLine(self):
        self._text = self._text + '<br>'

    def NewParagraph(self):
        self._text = self._text + '</p><p>'

    def SetColor(self,color: Color):
        self._color = color

    def SetDisplayType(self,type: DisplayType):
        self._fontDisplayType = type

    def AppendText(self,text: str):
        targetStr = text
        targetStr = '<font color=' + self._color.value + '>' + targetStr + '</font>'
        if self._fontDisplayType == self.DisplayType.Normal:
            targetStr = targetStr
        elif self._fontDisplayType == self.DisplayType.Bold:
            targetStr = '<b>' + targetStr + '</b>'
        elif self._fontDisplayType == self.DisplayType.Italic:
            targetStr = '<i>' + targetStr + '</i>'
        self._text = self._text + targetStr

    def ExportText(self) -> str:
        return self._text + '</p>'