#  Copyright 2022 by Benjamin J. Land (a.k.a. BenLand100)
#
#  This file is part of Simpy.
#
#  Simpy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Simpy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Simpy.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from . import gruvbox
import re

block_start = re.compile(r':\s*(#.*)*$')
indent = re.compile(r'^(\s+)')

class TextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.setFont(QFont('Monospace',13))
        self.installEventFilter(self)
        self.setLineWrapMode(False)


    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)

        return tc.selectedText()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Tab:
            self.textCursor().insertText('    ')
            return
        elif e.key() == Qt.Key_Return:
            c = self.textCursor()
            c.movePosition(QTextCursor.StartOfLine);   
            while c.positionInBlock() > 0:
                c.movePosition(QTextCursor.Up);
            line = c.block().text()
            if m := indent.search(line):
                prefix = m.group(1)
            else:
                prefix = ''
            if m := block_start.search(line):
                prefix += '    '
            self.textCursor().insertText(f'\n{prefix}')
            return

        super(TextEdit, self).keyPressEvent(e)

class NumberBar(QWidget):
    def __init__(self, parent = None):
        super(NumberBar, self).__init__(parent)
        self.editor = parent
        layout = QVBoxLayout()
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_on_scroll)
        self.update_width('1')
        self.setFont(QFont('Monospace',13))

    def update_on_scroll(self, rect, scroll):
        if self.isVisible():
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update()

    def update_width(self, string):
        width = max(30,self.fontMetrics().width(str(string)) + 8)
        if self.width() != width:
            self.setFixedWidth(width)

    def paintEvent(self, event):
        if self.isVisible():
            block = self.editor.firstVisibleBlock()
            height = self.fontMetrics().height()
            number = block.blockNumber()
            painter = QPainter(self)
            pen = painter.pen()
            painter.setPen(QPen(gruvbox.gray))
            painter.drawLine(event.rect().width() - 1, 0, event.rect().width() - 1, event.rect().height() - 1)
            painter.setPen(pen)
            font = painter.font()

            current_block = self.editor.textCursor().block().blockNumber() + 1

            condition = True
            while block.isValid() and condition:
                block_geometry = self.editor.blockBoundingGeometry(block)
                offset = self.editor.contentOffset()
                block_top = block_geometry.translated(offset).top()
                number += 1

                rect = QRect(0, block_top + 2, self.width() - 5, height)

                if number == current_block:
                    font.setBold(True)
                else:
                    font.setBold(False)

                painter.setFont(font)
                painter.drawText(rect, Qt.AlignRight, '%i'%number)

                if block_top > event.rect().bottom():
                    condition = False

                block = block.next()

            painter.end()
