#!/usr/bin/env python3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QTextEdit, QComboBox, QPushButton, QLineEdit, QAction
from PyQt5.QtWidgets import QStatusBar
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
class window(QWidget):
    text_update = QtCore.pyqtSignal(str)

    def __init__(self, *args):
        super(window, self).__init__()

        self.resize(WIN_WIDTH, WIN_HEIGHT)  # Set window size

        extractAction = QAction('&Quit', self)
        extractAction.setShortcut('Ctrl+Q')
        extractAction.setStatusTip('exit')
        extractAction.triggered.connect(self.close_application)

        self.statusBar = QStatusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)

        self.textbox = QTextEdit(self)
        self.textbox.setReadOnly(True)
        self.text_update.connect(self.append_text)

        ports, descs = ut.port_options()
        self.portSelect = QComboBox(self)
        self.portSelect.addItems(ports)

        self.fnameBox = QLineEdit(self)
        self.fnameBox.setText("log.txt")
        self.fnameBox.setMaxLength(50)

        cnct_btn = QPushButton('Connect', self)
        cnct_btn.clicked.connect(self.connect)
        cnct_btn.resize(cnct_btn.sizeHint())

        record_btn = QPushButton('Record', self)
        record_btn.clicked.connect(self.record_log)
        record_btn.resize(record_btn.sizeHint())

        pause_btn = QPushButton('Pause', self)
        pause_btn.clicked.connect(self.pause_log)
        pause_btn.resize(pause_btn.sizeHint())

        stop_btn = QPushButton('Stop', self)
        stop_btn.clicked.connect(self.stop)
        stop_btn.resize(stop_btn.sizeHint())

        vbox = QVBoxLayout()
        hbox0 = QHBoxLayout()
        hbox1 = QHBoxLayout()
        # hbox2 = QHBoxLayout()

        # self.setLayout(layout)
        vbox.addWidget(self.textbox)
        sys.stdout = self  # Redirect sys.stdout to self
        hbox0.addWidget(self.portSelect)
        hbox0.addWidget(cnct_btn)
        hbox0.addWidget(stop_btn)
        hbox1.addWidget(self.fnameBox)
        hbox1.addStretch()
        hbox1.addWidget(record_btn)
        hbox1.addWidget(pause_btn)

        vbox.addLayout(hbox0)
        vbox.addLayout(hbox1)
        self.setLayout(vbox)

    def connect(self):
        self.portname = self.portSelect.currentText()
        # Start serial thread
        self.serth = SerialThread(self.portname, baudrate)
        self.serth.start()

    def record_log(self):
        self.filename = self.fnameBox.text()

    def pause_log(self):
        pass

    def stop(self):
        self.serth.running = False
        self.serth.exit()

    def write(self, text):  # Handle sys.stdout.write: update display
        # Send signal to synchronise call with main thread
        self.text_update.emit(text)

    def append_text(self, text):  # Text display update handler
        cur = self.textbox.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)  # Move cursor to end of text
        s = str(text)
        while s:
            head, sep, s = s.partition("\n")  # Split line at LF
            cur.insertText(head)  # Insert text at cursor
        self.textbox.setTextCursor(cur)  # Update visible cursor

    def close_event(self, event):  # Window closing
        self.serth.running = False  # Wait until serial thread terminates
        self.serth.wait()

    def close_application(self):
        self.close_event()
        sys.exit(app.exec_())


# Thread to handle incoming &amp; outgoing serial data
class SerialThread(QtCore.QThread):
    # Initialise with serial port details
    def __init__(self, portname, baudrate):
        super(SerialThread, self).__init__()
        self.portname, self.baudrate = portname, baudrate
        self.txq = Queue.Queue()
        self.running = True

    def ser_in(self, s):  # Write incoming serial data to screen
        display(s)

    def run(self):                          # Run serial reader thread
        print(f"Opening {self.portname} at {self.baudrate} baud")
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
                s = self.ser.read(self.ser.in_waiting or 1)
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
