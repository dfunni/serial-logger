#!/usr/bin/env python3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QTextEdit, QWidget, QApplication, QVBoxLayout, QComboBox, QPushButton, QHBoxLayout

try:
    import Queue
except:
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
class MyWidget(QWidget):
    text_update = QtCore.pyqtSignal(str)

    def __init__(self, *args): 
        super(MyWidget, self).__init__()

        self.textbox = QTextEdit(self)
        font = QtGui.QFont()
        font.setFamily("Courier New")  # Monospaced font
        font.setPointSize(12)
        self.textbox.setFont(font)
        self.text_update.connect(self.append_text)  # Connect text update to handler

        ports, descs = ut.port_options()
        self.portSelect = QComboBox(self)
        self.portSelect.addItems(ports)

        cnct_btn = QPushButton('Connect', self)
        cnct_btn.clicked.connect(self.connect)
        cnct_btn.resize(cnct_btn.sizeHint())

        stop_btn = QPushButton('stop', self)
        stop_btn.clicked.connect(self.stop)
        stop_btn.resize(stop_btn.sizeHint())

        layout = QVBoxLayout()
        self.resize(WIN_WIDTH, WIN_HEIGHT)  # Set window size
        self.setLayout(layout)
        layout.addWidget(self.textbox)
        sys.stdout = self  # Redirect sys.stdout to self
        layout.addWidget(self.portSelect)
        layout.addWidget(cnct_btn)
        layout.addWidget(stop_btn)

    def connect(self):
        self.portname = self.portSelect.currentText()
        self.serth = SerialThread(self.portname, baudrate)  # Start serial thread
        self.serth.start()

    def stop(self):
        self.serth.running = False
        self.serth.exit()

    def write(self, text):  # Handle sys.stdout.write: update display
        self.text_update.emit(text)  # Send signal to synchronise call with main thread

    def append_text(self, text):  # Text display update handler
        cur = self.textbox.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)  # Move cursor to end of text
        s = str(text)
        while s:
            head, sep, s = s.partition("\n")  # Split line at LF
            cur.insertText(head)  # Insert text at cursor
        self.textbox.setTextCursor(cur)  # Update visible cursor

    def closeEvent(self, event):  # Window closing
        self.serth.running = False  # Wait until serial thread terminates
        self.serth.wait()


# Thread to handle incoming &amp; outgoing serial data
class SerialThread(QtCore.QThread):
    def __init__(self, portname, baudrate):  # Initialise with serial port details
        super(SerialThread, self).__init__()
        self.portname, self.baudrate = portname, baudrate
        self.txq = Queue.Queue()
        self.running = True

    def ser_in(self, s):  # Write incoming serial data to screen
        display(s)

    def run(self):                          # Run serial reader thread
        print(f"Opening {self.portname} at {self.baudrate} baud")
              # "(hex display)" if hexmode else ""))
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
    w = MyWidget()
    w.setWindowTitle('PyQT Serial Terminal')
    w.show()
    sys.exit(app.exec_())
