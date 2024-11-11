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
        # self._text: str = '<p>'
        self._textList = ['<p>']
        self._color = self.Color.black
        self._fontDisplayType = self.DisplayType.Normal

    def _GetOriginalText(self):
        return ''.join(self._textList)

    def _SetOriginalText(self, html):
        self._textList.clear()
        self._textList.append(html)

    def Clear(self):
        self._textList = ['<p>']

    def NewLine(self):
        self._textList.append('<br>')

    def NewParagraph(self):
        self._textList.append('</p><p>')

    def SetColor(self,color: Color):
        self._color = color

    def SetDisplayType(self,type: DisplayType):
        self._fontDisplayType = type

    def AppendText(self,text: str):
        targetStr = text
        # 关键字转换
        targetStr = targetStr.replace('<', ' &lt; ')
        targetStr = targetStr.replace('>', ' &gt; ')
        # 字符转换
        targetStr = targetStr.replace('\n', '<br>')
        # targetStr = '<font color=' + self._color.value + '>' + targetStr + '</font>'
        # self._textList.extend(('<font color=', self._color.value, '>', targetStr, '</font>'))
        if self._fontDisplayType == self.DisplayType.Normal:
            self._textList.extend(('<font color=', self._color.value, '>', targetStr, '</font>'))
        elif self._fontDisplayType == self.DisplayType.Bold:
            # targetStr = '<b>' + targetStr + '</b>'
            self._textList.extend(('<b>', '<font color=', self._color.value, '>', targetStr, '</font>', '</b>'))
        elif self._fontDisplayType == self.DisplayType.Italic:
            # targetStr = '<i>' + targetStr + '</i>'
            self._textList.extend(('<i>', '<font color=', self._color.value, '>', targetStr, '</font>', '</i>'))

    def ExportText(self) -> str:
        return ''.join(self._textList) + '</p>'

    def Join(self, content):
        newHTMLContent = HTMLContent()
        newHTMLContent._SetOriginalText(self.ExportText() + content._GetOriginalText())
        return newHTMLContent