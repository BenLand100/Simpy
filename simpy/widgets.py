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
deindent = re.compile(r'^ {0,4}')

highlight_syms_left = {
    '{':'}',
    '[':']',
    '(':')',
    '[':']'
}
highlight_syms_right = {
    l:r for r,l in highlight_syms_left.items()
}

class TextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)
        self.setFont(QFont('Monospace',13))
        self.installEventFilter(self)
        self.setLineWrapMode(False)
        self.cursorPositionChanged.connect(self.cursor_changed)
        
    def paintEvent(self,event):
        super().paintEvent(event)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)

        return tc.selectedText()

    def highlight_braces_from(self,pos,char,left):
        c_0 = self.textCursor()
        c_0.setPosition(pos-1)
        c_0.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
        extra = QTextEdit.ExtraSelection()
        extra.format.setBackground(gruvbox.neutral_blue);
        extra.format.setForeground(gruvbox.neutral_red);
        extra.cursor = c_0;
        extra_selection = [extra]
        
        match = highlight_syms_left[char] if left else highlight_syms_right[char]
        c_1 = self.textCursor()
        c_1.setPosition(pos)
        c_1.movePosition(QTextCursor.StartOfBlock)
        search_pos = pos-c_1.position()-1
        search_txt = c_1.block().text()
        found = False
        if left:
            search_pos = search_pos + 1
        else:
            search_pos = search_pos - 1
        depth = 0
        while not found:
            for i in (range(search_pos,len(search_txt)) if left else range(search_pos,-1,-1)):
                if search_txt[i] == char:
                    depth = depth+1
                elif search_txt[i] == match:
                    if depth <= 0:
                        c_1.setPosition(i+c_1.position())
                        c_1.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor)
                        extra = QTextEdit.ExtraSelection()
                        extra.format.setBackground(gruvbox.neutral_blue);
                        extra.format.setForeground(gruvbox.neutral_red);
                        extra.cursor = c_1;
                        extra_selection.append(extra)
                        found = True
                        break
                    else:
                        depth = depth-1
            else:
                if left:
                    if c_1.blockNumber() == self.blockCount()-1:
                        break
                    c_1.movePosition(QTextCursor.NextBlock)
                else:
                    if c_1.blockNumber() == 0:
                        break
                    c_1.movePosition(QTextCursor.PreviousBlock)
                search_txt = c_1.block().text()
                search_pos = 0 if left else len(search_txt)-1
        self.setExtraSelections(extra_selection)

    def cursor_changed(self):
        c = self.textCursor()
        txt = c.block().text()
        if len(txt) == 0:
            return
        pos = c.positionInBlock()-1
        if pos >= 0 and pos < len(txt):
            pre = txt[pos]
            if pre in highlight_syms_left:
                self.highlight_braces_from(c.position(),pre,True)
                return
            if pre in highlight_syms_right:
                self.highlight_braces_from(c.position(),pre,False)
                return
        if pos+1 < len(txt):
            post = txt[pos+1]
            c.movePosition(QTextCursor.Right)
            if post in highlight_syms_left:
                self.highlight_braces_from(c.position(),post,True)
                return
            if post in highlight_syms_right:
                self.highlight_braces_from(c.position(),post,False)
                return
        self.setExtraSelections([])
            

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Tab:
            c = self.textCursor()
            if c.hasSelection():
                start,end = c.selectionStart(),c.selectionEnd()
                c.setPosition(end)
                c.movePosition(QTextCursor.StartOfBlock)
                e_block = c.blockNumber()
                c.setPosition(start)
                c.movePosition(QTextCursor.StartOfBlock)
                while True:
                    c.insertText('    ')
                    if c.blockNumber() == e_block:
                        break;
                    c.movePosition(QTextCursor.NextBlock)
            else:
                c.insertText('    ')
            return
        elif e.key() == Qt.Key_Backtab:
            c = self.textCursor()
            if c.hasSelection():
                start,end = c.selectionStart(),c.selectionEnd()
                c.setPosition(end)
                c.movePosition(QTextCursor.StartOfBlock)
                e_block = c.blockNumber()
                c.setPosition(start)
                c.movePosition(QTextCursor.StartOfBlock)
                while True:
                    text = c.block().text()
                    if (m := deindent.search(text)):
                        remove = len(m.group(0))
                        c.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,remove)
                        c.removeSelectedText()
                    if c.blockNumber() == e_block:
                        break;
                    c.movePosition(QTextCursor.NextBlock)
            else:
                c.movePosition(QTextCursor.StartOfBlock)
                text = c.block().text()
                if (m := deindent.search(text)):
                    remove = len(m.group(0))
                    c.movePosition(QTextCursor.Right,QTextCursor.KeepAnchor,remove)
                    c.removeSelectedText()
            return
        elif e.key() == Qt.Key_Return:
            c = self.textCursor()
            c.movePosition(QTextCursor.StartOfBlock);
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

                rect = QRect(0, int(block_top + 2), int(self.width() - 5), int(height))

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
