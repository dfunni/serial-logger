#!/usr/bin/env python3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QTextEdit, QComboBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QStatusBar, QAction
import queue as Queue

import sys
import time
import serial

# module import
import utilities as ut

WIN_WIDTH, WIN_HEIGHT = 684, 400  # Window size
SER_TIMEOUT = 0.1  # Timeout for serial Rx
baudrate = 9600  # Default baud rate


# Convert a string to bytes
def str_bytes(s):
    return s.encode('latin-1')


# Convert bytes to string
def bytes_str(d):
    return d if type(d) is str else "".join([chr(b) for b in d])


# Display incoming serial data
def display(s):
    sys.stdout.write(s)


# Main widget
class window(QMainWindow):
    text_update = QtCore.pyqtSignal(str)
    log_update = QtCore.pyqtSignal(str)

    def __init__(self, *args):
        super(window, self).__init__()

        self.resize(WIN_WIDTH, WIN_HEIGHT)  # Set window size
        sys.stdout = self  # Redirect sys.stdout to self

        self.ser_initF = False
        self.ser_connectedF = False
        self.recordF = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.extractAction = QAction('&Quit', self)
        self.extractAction.setShortcut('Ctrl+Q')
        self.extractAction.setStatusTip('exit')
        self.extractAction.triggered.connect(self.closeEvent)

        self.statusBar = QStatusBar()

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.extractAction)

        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)
        self.text_update.connect(self.append_text)

        self.portSelect = QComboBox(self)
        self.portSelect.addItems(ut.port_options())

        self.fnameBox = QLineEdit(self)
        self.fnameBox.setText("log.txt")
        self.fnameBox.setMaxLength(50)

        self.cnct_btn = QPushButton('Connect', self)
        self.cnct_btn.clicked.connect(self.connect)
        self.cnct_btn.resize(self.cnct_btn.sizeHint())

        self.record_btn = QPushButton('Record', self)
        self.record_btn.clicked.connect(self.record_log)
        self.record_btn.resize(self.record_btn.sizeHint())
        self.log_update.connect(self.record)

        self.pause_btn = QPushButton('Pause', self)
        self.pause_btn.clicked.connect(self.pause_log)
        self.pause_btn.resize(self.pause_btn.sizeHint())

        self.stop_btn = QPushButton('Stop', self)
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.resize(self.stop_btn.sizeHint())

        self.vbox = QVBoxLayout()
        self.hbox0 = QHBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.centralWidget().setLayout(self.vbox)

        self.vbox.addWidget(self.textbox)
        self.hbox0.addWidget(self.portSelect)
        self.hbox0.addWidget(self.cnct_btn)
        self.hbox0.addWidget(self.stop_btn)
        self.hbox1.addWidget(self.fnameBox)
        self.hbox1.addStretch()
        self.hbox1.addWidget(self.record_btn)
        self.hbox1.addWidget(self.pause_btn)

        self.vbox.addLayout(self.hbox0)
        self.vbox.addLayout(self.hbox1)

    def init_serth(self):
        self.portname, _ = self.portSelect.currentText().split('  ')
        # Start serial thread
        self.serth = SerialThread(self.portname, baudrate)
        self.ser_initF = True

    def connect(self):
        if not self.ser_initF:
            self.init_serth()
        self.serth.running = True
        self.ser_connectedF = True
        self.serth.start()

    def record_log(self):
        if not self.ser_connectedF or not self.serth.running:
            self.connect()
        self.filename = self.fnameBox.text()
        self.serth.record = True
        self.recordF = True

    def pause_log(self):
        self.recordF = False

    def stop(self):
        self.serth.running = False
        self.serth.exit()

    def write(self, text):  # Handle sys.stdout.write: update display
        # Send signal to synchronise call with main thread
        self.text_update.emit(text)
        if self.recordF:
            self.log_update.emit(text)

    def append_text(self, text):  # Text display update handler
        cur = self.textbox.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)  # Move cursor to end of text
        s = str(text)
        while s:
            head, sep, s = s.partition("\n")  # Split line at LF
            cur.insertText(head)  # Insert text at cursor
        self.textbox.setTextCursor(cur)  # Update visible cursor

    def record(self, text):
        line = f"{str(time.time())}\t{text}"
        # print(line)
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
    # Initialise with serial port details
    def __init__(self, portname, baudrate):
        super(SerialThread, self).__init__()
        self.portname = portname
        self.baudrate = baudrate
        self.txq = Queue.Queue()
        self.running = True
        # self.record = False

    def ser_in(self, s):  # Write incoming serial data to screen
        display(s)

    def run(self):                          # Run serial reader thread
        # print(f"Opening {self.portname} at {self.baudrate} baud")
        try:
            self.ser = serial.Serial(self.portname,
                                     self.baudrate,
                                     timeout=SER_TIMEOUT)
            time.sleep(SER_TIMEOUT*1.2)
            self.ser.flushInput()
        except:
            self.ser = None
        if not self.ser:
            print("Can't open port")
            self.running = False
        while self.running:
            try:
                # s = self.ser.read(self.ser.in_waiting or 1)
                s = self.ser.readline()
                if s:  # Get data from serial port
                    self.ser_in(bytes_str(s))  # ..and convert to string
            except:
                self.running = False
                break
        if self.ser:  # Close serial port when thread finished
            self.ser.close()
            self.ser = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = window()
    w.setWindowTitle('PyQT Serial Terminal')
    w.show()
    sys.exit(app.exec_())
