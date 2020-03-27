#!/usr/bin/env python3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QTextEdit, QComboBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QLabel, QStatusBar, QAction
import queue as Queue

import sys
import time
import serial
import random
import numpy as np
from serial.tools.list_ports import comports

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure


def bytes_str(d):
    ''' Convert bytes to string'''
    return d if type(d) is str else "".join([chr(b) for b in d])


def port_options():
    """ This function was adapted from the pyserial tool miniterm.py."""
    ports = []
    for port, desc, _ in sorted(comports()):
        ports.append(f'{port}  {desc}')  # double space delimited

    return ports


# Main widget
class Window(QMainWindow):

    def __init__(self, *args):
        super(Window, self).__init__()

        self.resize(1200, 800)  # Set window size

        self.ser_connectedF = False
        self.recordF = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Menu bar
        self.statusBar = QStatusBar()

        self.extractAction = QAction('&Quit', self)
        self.extractAction.setShortcut('Ctrl+Q')
        self.extractAction.setStatusTip('exit')
        self.extractAction.triggered.connect(self.closeEvent)

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.extractAction)

        # Text boxes
        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)
        # self.text_update.connect(self.append_text)

        self.fnameBox = QLineEdit(self)
        self.fnameBox.setText("log.txt")
        self.fnameBox.setMaxLength(50)

        # Drop-down menus
        self.portSelect = QComboBox(self)
        self.portSelect.addItems(port_options())

        self.baudSelect = QComboBox(self)
        baud_list = [9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
        baud_list = [str(baud) for baud in baud_list]
        self.baudSelect.addItems(baud_list)

        # Buttons
        self.cnct_btn = QPushButton('Connect', self)
        self.cnct_btn.clicked.connect(self.connect)
        self.cnct_btn.resize(self.cnct_btn.sizeHint())

        self.record_btn = QPushButton('Record', self)
        self.record_btn.clicked.connect(self.record_log)
        self.record_btn.resize(self.record_btn.sizeHint())

        self.pause_btn = QPushButton('Pause', self)
        self.pause_btn.clicked.connect(self.pause_log)
        self.pause_btn.resize(self.pause_btn.sizeHint())

        self.stop_btn = QPushButton('Disconnect', self)
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.resize(self.stop_btn.sizeHint())

        # Labels
        self.heading1 = QLabel()
        self.heading1.setText("<b>Serial Port Connction Options<\b>")
        self.heading2 = QLabel()
        self.heading2.setText("<b>Logging Options<\b>")
        self.l1 = QLabel()
        self.l1.setText("Serial Port:")
        self.l2 = QLabel()
        self.l2.setText("Baud Rate:")
        self.l3 = QLabel()
        self.l3.setText("Logfile:       ")

        # Layout
        self.main = QHBoxLayout()  # main layout
        self.l_side = QVBoxLayout() 
        self.portsec = QHBoxLayout()
        self.cnctsec = QHBoxLayout()
        self.filesec = QHBoxLayout()
        self.recdsec = QHBoxLayout()

        self.portsec.addWidget(self.l1)
        self.portsec.addWidget(self.portSelect)
        self.portsec.addWidget(self.l2)
        self.portsec.addWidget(self.baudSelect)

        self.cnctsec.addWidget(self.cnct_btn)
        self.cnctsec.addWidget(self.stop_btn)

        self.filesec.addWidget(self.l3)
        self.filesec.addWidget(self.fnameBox)
        self.filesec.addStretch()

        self.recdsec.addWidget(self.record_btn)
        self.recdsec.addWidget(self.pause_btn)

        self.l_side.addLayout(self.portsec)
        self.l_side.addLayout(self.cnctsec)
        self.l_side.addLayout(self.filesec)
        self.l_side.addLayout(self.recdsec)
        self.l_side.addStretch()

        self.main.addLayout(self.l_side)
        self.main.addWidget(self.textbox)

        self.centralWidget().setLayout(self.main)

    def connect(self):
        self.portname, _ = self.portSelect.currentText().split('  ')
        self.baudrate = self.baudSelect.currentText()
        self.serth = SerialThread(self.portname, self.baudrate)
        self.serth.start()
        self.ser_connectedF = True
        self.serth.running = True
        self.serth.signal_str.connect(self.display)

    def record_log(self):
        if not self.ser_connectedF or not self.serth.running:
            self.connect()
        self.filename = self.fnameBox.text()
        self.recordF = True
        self.serth.signal_str.connect(self.record)

    def pause_log(self):
        self.recordF = False

    def stop(self):
        self.serth.running = False
        self.serth.exit()

    def display(self, text):  # Text display update handler
        cur = self.textbox.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)  # Move cursor to end of text
        text, _, _ = text.partition('\n')
        cur.insertText(text)
        self.textbox.setTextCursor(cur)  # Update visible cursor

    def record(self, text):
        line = f"{str(time.time())}\t{text}"  # append timestamp
        with open(self.filename, "a") as f:
            f.write(line)
            f.close()

    def closeEvent(self, event):  # Window closing, standard Qt syntax
        if self.ser_connectedF:
            self.serth.running = False  # Wait until serial thread terminates
            self.serth.wait()
        sys.exit()


# Thread to handle incoming &amp; outgoing serial data
class SerialThread(QtCore.QThread):
    signal_str = QtCore.pyqtSignal(str)

    # Initialise with serial port details
    def __init__(self, portname, baudrate):
        super(SerialThread, self).__init__()
        self.portname = portname
        self.baudrate = baudrate
        self.txq = Queue.Queue()
        self.running = True

    def run(self):                          # Run serial reader thread
        self.ser = serial.Serial(self.portname, self.baudrate, timeout=0.1)
        self.ser.flushInput()
        if not self.ser:
            print("Cannot open port")
            self.running = False
        while self.running:
            try:
                s = self.ser.readline()
                # time.sleep(.1)
                if s:  # Get data from serial port
                    self.signal_str.emit(bytes_str(s))
            except:
                self.running = False
                break
        if self.ser:  # Close serial port when thread finished
            self.ser.close()
            self.ser = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.setWindowTitle('PyQT Serial Terminal')
    w.show()
    sys.exit(app.exec_())
