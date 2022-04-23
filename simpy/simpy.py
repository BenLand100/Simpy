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
from .widgets import *
from .syntax import *
import os
import signal
import sys
import re

iconsize = QSize(16, 16)

stylesheet = ''
  
default_script = '#/usr/bin/python3\n\nif __name__ == \'__main__\':\n    print(\'Hello World!\')'

class Simpy(QMainWindow):
    def __init__(self, parent = None):
        super(Simpy, self).__init__(parent)
        
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon.fromTheme('applications-python'))

        self.app_path = QFileInfo.path(QFileInfo(QCoreApplication.arguments()[0]))
        
        self.lineLabel = QLabel('[:]')
        self.statusBar().addPermanentWidget(self.lineLabel)
        self.statusBar().setStyleSheet(stylesheet)
        
        self.settings = QSettings('Simpy', 'Simpy')

        self.editor = TextEdit()
        self.editor.setStyleSheet(stylesheet)
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.context_menu_requested)
        self.editor.cursorPositionChanged.connect(self.cursor_changed)
        self.editor.document().modificationChanged.connect(self.setWindowModified)
        self.cursor = QTextCursor()
        self.editor.setTextCursor(self.cursor)
        
        self.terminal = QTextEdit()
        self.terminal.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.terminal.setMinimumHeight(30)
        self.terminal.setStyleSheet(stylesheet)
        
        self.numbers = NumberBar(self.editor)
        
        self.highlighter = Highlighter(self.editor.document())
        
        self.newAct = QAction('&New', self, shortcut=QKeySequence.New, statusTip='New File', triggered=self.handle_new)
        self.openAct = QAction('&Open', self, shortcut=QKeySequence.Open, statusTip='Open File', triggered=self.handle_open)
        self.saveAct = QAction('&Save', self, shortcut=QKeySequence.Save, statusTip='Save File', triggered=self.handle_save)
        self.saveAsAct = QAction('&Save as ...', self, shortcut=QKeySequence.SaveAs, statusTip='Save File As', triggered=self.handle_save_as)
        self.exitAct = QAction('Exit', self, shortcut=QKeySequence.Quit, statusTip='Exit', triggered=self.handle_quit)
        self.runAct = QAction(QIcon.fromTheme('play'), '&Run', self, shortcut='Ctrl+R', statusTip='Run Program', triggered=self.handle_run)
        self.haltAct = QAction(QIcon.fromTheme('stop'), '&Halt', self, shortcut='Ctrl+H', statusTip='Halt Program', triggered=self.handle_halt)
        
        bar=self.menuBar()
        bar.setStyleSheet(stylesheet)
        self.filemenu=bar.addMenu('File')
        self.filemenu.setStyleSheet(stylesheet)
        self.filemenu.addAction(self.newAct)
        self.filemenu.addAction(self.openAct)
        self.filemenu.addAction(self.saveAct)
        self.filemenu.addAction(self.saveAsAct)
        self.filemenu.addSeparator()
        self.filemenu.addAction(self.exitAct)
        
        editmenu = bar.addMenu('Edit')
        editmenu.setStyleSheet(stylesheet)
        editmenu.addAction(QAction(QIcon.fromTheme('edit-undo'), 'Undo', self, triggered = self.editor.undo, shortcut = 'Ctrl+z'))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-redo'), 'Redo', self, triggered = self.editor.redo, shortcut = 'Shift+Ctrl+z'))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon.fromTheme('edit-copy'), 'Copy', self, triggered = self.editor.copy, shortcut = 'Ctrl+c'))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-cut'), 'Cut', self, triggered = self.editor.cut, shortcut = 'Ctrl+x'))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-paste'), 'Paste', self, triggered = self.editor.paste, shortcut = 'Ctrl+v'))
        editmenu.addAction(QAction(QIcon.fromTheme('edit-delete'), 'Delete', self, triggered = self.editor.cut, shortcut = 'Del'))
        editmenu.addSeparator()
        editmenu.addAction(QAction(QIcon.fromTheme('edit-select-all'), 'Select All', self, triggered = self.editor.selectAll, shortcut = 'Ctrl+a'))
        
        programmenu = bar.addMenu('Program')
        programmenu.setStyleSheet(stylesheet)
        programmenu.addAction(self.runAct)
        programmenu.addAction(self.haltAct)
                
        toolbar = self.addToolBar('Program')
        toolbar.setStyleSheet(stylesheet)
        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        toolbar.setIconSize(QSize(iconsize))
        toolbar.setMovable(True)
        toolbar.setAllowedAreas(Qt.AllToolBarAreas)
        toolbar.addAction(self.runAct)
        toolbar.addAction(self.haltAct)
        
        splitter = QSplitter(Qt.Vertical)
        layoutH = QHBoxLayout()
        layoutH.addWidget(self.numbers)
        layoutH.addWidget(self.editor)
        dummy = QWidget(self)
        dummy.setLayout(layoutH)
        splitter.addWidget(dummy)
        splitter.addWidget(self.terminal)
        splitter.setStretchFactor(0, 2)
        self.setCentralWidget(splitter)
        self.editor.setFocus()
        
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.data_ready)
        self.process.started.connect(lambda: self.log('Starting subprocess'))
        self.process.finished.connect(lambda: self.log(f'Subprocess terminated ({self.process.exitCode()})'))

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, 'Systray', 'No system tray found.')
        else:
            self.trayIcon = QSystemTrayIcon(self)
            self.trayIcon.setIcon(QIcon.fromTheme('applications-python'))
            self.trayIconMenu = QMenu(self)
            self.trayIconMenu.addAction(self.runAct)
            self.trayIconMenu.addAction(self.haltAct)
            self.trayIconMenu.addAction(QAction(QIcon.fromTheme('application-exit'),'Exit', self, triggered=self.handle_quit))
            self.trayIcon.setContextMenu(self.trayIconMenu)
            self.trayIcon.show()
        
        self.load_settings()
        self.editor.clear()
        self.editor.setPlainText(default_script)
        self.set_filename('')
        self.set_modified(False)
        self.editor.moveCursor(self.cursor.End)
        self.editor.setFocus()
        self.setWindowTitle('Simpy - [unsaved][*]')
        self.status('Welcome to Simpy!')
        
        
    def status(self,msg):
        self.statusBar().showMessage(msg)
        
    def log(self,msg):
        self.terminal.moveCursor(self.cursor.End)
        self.terminal.append(msg)
        self.terminal.moveCursor(self.cursor.End)
        self.terminal.ensureCursorVisible()

    def clear_log(self):
        self.terminal.setText('')

    def cursor_changed(self):
        line = self.editor.textCursor().blockNumber() + 1
        pos = self.editor.textCursor().positionInBlock()
        self.lineLabel.setText(f'[{line}:{pos}]')

    def data_ready(self):
        out = str(self.process.readAll(), encoding = 'utf8').rstrip()
        self.log(out)    

    def get_line_number(self):
        self.editor.moveCursor(self.cursor.StartOfLine)
        linenumber = self.editor.textCursor().blockNumber() + 1
        return linenumber
            
    def handle_new(self):
        if self.maybe_save():
            self.editor.clear()
            self.editor.setPlainText(default_script)
            self.set_filename('')
            self.set_modified(False)
            self.editor.moveCursor(self.cursor.End)
            self.log('New Program Ceated')
            self.editor.setFocus()
            self.setWindowTitle('Simpy - [unsaved][*]')
            
    def open_file(self, path=None):
        if path:
            inFile = QFile(path)
            if inFile.open(QFile.ReadWrite | QFile.Text):
                text = inFile.readAll()
                text = str(text, encoding = 'utf8')
                self.editor.setPlainText(text.replace('\t', '    '))
                self.set_modified(False)
                self.set_filename(path)
                self.editor.setFocus()
                self.log(f'File Opened: {path}')

    def handle_open(self, path=None):
        if self.maybe_save():
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), 'Python Files (*.py);; all Files (*)')
            if path:
                self.open_file(path)
            
    def handle_save(self):
        if (self.filename != ''):
            file = QFile(self.filename)
            if not file.open( QFile.WriteOnly | QFile.Text):
                QMessageBox.warning(self, 'Error',  'Cannot write file %s:\n%s.' % (self.filename, file.errorString()))
                return

            outstr = QTextStream(file)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            file_data = self.editor.toPlainText()
            outstr << file_data
            QApplication.restoreOverrideCursor()                
            self.set_modified(False)
            self.setWindowTitle(f'Simpy - {self.filename}[*]')
            self.log(f'File Saved: {self.filename}')
            self.set_filename(self.filename)
            self.editor.setFocus()
        else:
            self.handle_save_as()
    
    def handle_save_as(self):
        fn, _ = QFileDialog.getSaveFileName(self, 'Save as...', self.filename, 'Python files (*.py)')

        if not fn:
            self.log('File save aborted.')
            return False

        lfn = fn.lower()
        if not lfn.endswith('.py'):
            fn += '.py'

        self.set_filename(fn)
        return self.handle_save()
        
    def maybe_save(self):
        if not self.is_modified():
            return True

        ret = QMessageBox.question(self, 'Message',
                '<h4><p>The program was modified.</p>\n<p>Save changes?</p></h4>',
                QMessageBox.Yes | QMessageBox.Discard | QMessageBox.Cancel)

        if ret == QMessageBox.Yes:
            if self.filename == '':
                self.handle_save_as()
                return False
            else:
                self.handle_save()
                return True

        if ret == QMessageBox.Cancel:
            return False

        return True   
    
    def handle_halt(self):
        self.status('Halting onging process')
        if self.process.state() != QProcess.ProcessState.NotRunning:
            os.kill(self.process.processId(),signal.SIGINT)
        
    def handle_run(self):
        if self.editor.toPlainText() == '':
            self.status('Nothing to run!')
            return
        if self.filename:
            if self.is_modified():
                self.status('Executing ' + self.filename)
                self.handle_save()
                self.execute()
            else:
                self.status('Executing ' + self.filename)
                self.execute()
        else:
            self.handle_save()
            if self.filename:
                self.handle_run()
            else:
                self.log('Must save before running!')
            
    def execute(self, cmd='python3'):
        dname = os.getcwd()
        self.log('CWD='+dname)
        QProcess().execute('cd "' + dname + '"')
        self.process.start(cmd,['-u',self.filename])
        
    def goto_line(self, line):
        linecursor = QTextCursor(self.editor.document().findBlockByLineNumber(line-1))
        self.editor.moveCursor(QTextCursor.End)
        self.editor.setTextCursor(linecursor)
        
    def handle_quit(self):
        if self.maybe_save():
            app.quit()

    def set_numbers_visible(self, value=True):
        self.numbers.setVisible(value)

    def document(self):
        return self.editor.document
        
    def is_modified(self):
        return self.editor.document().isModified()

    def set_modified(self, modified):
        self.editor.document().setModified(modified)

    def set_linewrap_mode(self, mode):
        self.editor.setLineWrapMode(mode)

    def clear(self):
        self.editor.clear()
        
    def set_filename(self, filename):
        if (dirname := os.path.dirname(filename)) != '':
            os.chdir(dirname)
        self.filename = os.path.basename(filename)
        if self.filename:
            self.setWindowTitle(f'Simpy - {self.filename}[*]')
        else:
            self.setWindowTitle('Simpy - [unsaved][*]')
        
    def load_settings(self):
        if self.settings.value('pos') != '':
            pos = self.settings.value('pos', QPoint(200, 200))
            self.move(pos)
        if self.settings.value('size') != '':
            size = self.settings.value('size', QSize(400, 400))
            self.resize(size)

    def save_settings(self):
        self.settings.setValue('pos', self.pos())
        self.settings.setValue('size', self.size())

    def context_menu_requested(self,point):
        cmenu = QMenu()
        cmenu = self.editor.createStandardContextMenu()
        cmenu.exec_(self.editor.mapToGlobal(point)) 
        
    ### Override some QMainWindow functions
        
    def closeEvent(self, e):
        self.save_settings()
        if self.maybe_save():
            e.accept()
        else:
            e.ignore()
            
    def paintEvent(self, event):
        '''
        #Gotta figure out a better color for line highlight, if kept
        highlighted_line = QTextEdit.ExtraSelection()
        highlighted_line.format.setBackground(gruvbox.gray)
        highlighted_line.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
        highlighted_line.cursor = self.editor.textCursor()
        highlighted_line.cursor.clearSelection()
        '''
        self.editor.setExtraSelections([])
