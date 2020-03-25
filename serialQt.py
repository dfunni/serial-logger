import sys
from PyQt5.QtCore import QCoreApplication, Qt, QThread
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction, QMessageBox
from PyQt5.QtWidgets import QCalendarWidget, QFontDialog, QColorDialog, QTextEdit, QFileDialog
from PyQt5.QtWidgets import QCheckBox, QProgressBar, QComboBox, QLabel, QStyleFactory, QLineEdit, QInputDialog
import utilities as ut

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QtTextEdit, QWidget, QApplication, QVLayout


try:
    import Queue
except:
    import queue as Queue
import sys
import time
import serial


class window(QMainWindow):

    def __init__(self):
        super(window, self).__init__()
        self.setGeometry(50, 50, 800, 500)
        self.setWindowTitle('Serial Logger')

        saveFile = QAction('&Save File', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.file_save)

        extractAction = QAction('&Quit', self)
        extractAction.setShortcut('Ctrl+Q')
        extractAction.setStatusTip('exit')
        extractAction.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(saveFile)
        fileMenu.addAction(extractAction)

        ports, descs = ut.port_options()
        self.portSelect = QComboBox(self)
        self.portSelect.addItems(ports)
        self.portSelect.move(50, 300)

        self.textbox = QLineEdit(self)
        self.textbox.move(50, 400)

        # self.port = self.portSelect.currentText()
        # self.ser = ut.connect(self.port)

        self.home()

    def file_save(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File',
                                              options=QFileDialog.DontUseNativeDialog)
        file = open(name, 'w')
        text = self.textEdit.toPlainText()
        file.write(text)
        file.close()

    def home(self):
        cnct_btn = QPushButton('Connect', self)
        cnct_btn.clicked.connect(self.connect)
        cnct_btn.resize(cnct_btn.sizeHint())
        cnct_btn.move(50, 100)

        start_btn = QPushButton('start', self)
        start_btn.clicked.connect(self.log)
        start_btn.resize(start_btn.sizeHint())
        start_btn.move(50, 150)

        stop_btn = QPushButton('stop', self)
        stop_btn.clicked.connect(self.stop_log)
        stop_btn.resize(stop_btn.sizeHint())
        stop_btn.move(50, 200)

        self.show()

    def connect(self):
        self.port = self.portSelect.currentText()
        self.ser = ut.connect(self.port)

    def log(self):
        ut.log('log.txt', self.ser)

    def stop_log(self):
        ut.stop_log(self.ser)

    def close_application(self):
        sys.exit()


if __name__ == "__main__":  # had to add this otherwise app crashed

    def run():
        app = QApplication(sys.argv)
        Gui = window()
        sys.exit(app.exec_())

run()
