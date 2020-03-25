#!/usr/bin/env python3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QTextEdit, QComboBox, QPushButton, QLineEdit, QLabel
from PyQt5.QtWidgets import QStatusBar, QAction
import queue as Queue

import sys
import time
import serial

# module import
import utilities as ut

WIN_WIDTH, WIN_HEIGHT = 600, 1000  # Window size
SER_TIMEOUT = 0.01  # Timeout for serial Rx

# # Convert bytes to string
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
        self.text_update.connect(self.append_text)

        self.fnameBox = QLineEdit(self)
        self.fnameBox.setText("log.txt")
        self.fnameBox.setMaxLength(50)

        # Drop-down menus
        self.portSelect = QComboBox(self)
        self.portSelect.addItems(ut.port_options())

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
        self.log_update.connect(self.record)

        self.pause_btn = QPushButton('Pause', self)
        self.pause_btn.clicked.connect(self.pause_log)
        self.pause_btn.resize(self.pause_btn.sizeHint())

        self.stop_btn = QPushButton('Disconnect', self)
        self.stop_btn.clicked.connect(self.stop)
        self.stop_btn.resize(self.stop_btn.sizeHint())

        # Labels
        self.heading1 = QLabel()
        self.heading1.setText("<strong>Serial Port Connction Options<\strong>")
        self.heading2 = QLabel()
        self.heading2.setText("<strong>Logging Options<\strong>")
        self.l1 = QLabel()
        self.l1.setText("Serial Port:")
        self.l2 = QLabel()
        self.l2.setText("Baud Rate:")
        self.l3 = QLabel()
        self.l3.setText("Logfile:       ")

        # Layout
        self.vbox = QVBoxLayout()
        self.hbox0 = QHBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.centralWidget().setLayout(self.vbox)

        self.hbox0.addWidget(self.l1)
        self.hbox0.addWidget(self.portSelect)
        self.hbox0.addWidget(self.l2)
        self.hbox0.addWidget(self.baudSelect)

        self.hbox1.addWidget(self.cnct_btn)
        self.hbox1.addWidget(self.stop_btn)

        self.hbox2.addWidget(self.l3)
        self.hbox2.addWidget(self.fnameBox)
        self.hbox2.addStretch()

        self.hbox3.addWidget(self.record_btn)
        self.hbox3.addWidget(self.pause_btn)

        self.vbox.addWidget(self.textbox)
        self.vbox.addWidget(self.heading1)
        self.vbox.addLayout(self.hbox0)
        self.vbox.addLayout(self.hbox1)
        self.vbox.addWidget(self.heading2)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)

    def connect(self):
        self.portname, _ = self.portSelect.currentText().split('  ')
        self.baudrate = self.baudSelect.currentText()
        self.serth = SerialThread(self.portname, self.baudrate)
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
                                     self.baudrate)
            time.sleep(SER_TIMEOUT*1.2)
            self.ser.flushInput()
        except:
            self.ser = None
        if not self.ser:
            print("Cannot open port")
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
