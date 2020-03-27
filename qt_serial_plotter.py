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
    # send_fig = pyqtSignal(Axes, str, name="send_fig")  # is this needed?

    def __init__(self, *args):
        super(window, self).__init__()

        self.resize(1200, 800)  # Set window size

        self.ser_connectedF = False
        self.recordF = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.plotth = PlotThread()
        self.graph = MplCanvas(self)
        self.plotter = None
        self.plotth = None

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
        self.cnct_btn.clicked.connect(self.update_plot)
        self.cnct_btn.resize(self.cnct_btn.sizeHint())

        self.record_btn = QPushButton('Record', self)
        self.record_btn.clicked.connect(self.record_log)
        self.record_btn.resize(self.record_btn.sizeHint())
        # self.log_update.connect(self.record)

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

        self.l_side.addWidget(self.graph)
        self.l_side.addLayout(self.portsec)
        self.l_side.addLayout(self.cnctsec)
        self.l_side.addLayout(self.filesec)
        self.l_side.addLayout(self.recdsec)
        self.l_side.addStretch()

        self.main.addLayout(self.l_side)
        self.main.addWidget(self.textbox)

        self.centralWidget().setLayout(self.main)

        n_data = 500
        self.xdata = list(range(n_data))
        self.rdata = np.zeros(n_data, dtype=np.float64).tolist()
        self.pdata = np.zeros(n_data, dtype=np.float64).tolist()
        self.ydata = np.zeros(n_data, dtype=np.float64).tolist()

        self._plot_refr = None
        self._plot_refp = None
        self._plot_refy = None

    def update_plot(self):

        # if there is already a thread running, kill it first
        if self.plotth != None and self.plotth.isRunning():
            self.plotth.terminate()

        self.plotter = Plotter()
        self.plotth = QThread()

        # connect signals
        self.send_fig.connect(self.plotter.replot)
        self.plotter.return_fig.connect(self.graph.updata_plot)
        # move to thread and start
        self.plotter.moveToThread(self.plotth)
        self.plotth.start()
        # start the plotting
        self.send_fig.emit(self.graph.axes)

    def connect(self):
        self.portname, _ = self.portSelect.currentText().split('  ')
        self.baudrate = self.baudSelect.currentText()
        self.serth = SerialThread(self.portname, self.baudrate)
        self.serth.start()
        self.ser_connectedF = True
        self.serth.running = True
        self.serth.signal_str.connect(self.display)
        # self.serth.signal_str.connect(self.plot)

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

    # def plot(self, text):
    #     text, _, _ = text.partition('\n')
    #     try:
    #         data = text.split("\t")
    #         [roll, pitch, yaw] = data
    #     except:
    #         [roll, pitch, yaw] = [20, 0, 0]
    #     # Drop off the first y element, append a new one.
    #     self.rdata = self.rdata[1:] + [np.float64(roll)]
    #     self.pdata = self.pdata[1:] + [np.float64(pitch)]
    #     self.ydata = self.ydata[1:] + [np.float64(yaw)]

    #     # Note: we no longer need to clear the axis.
    #     if self._plot_refr is None:
    #         # First time we have no plot reference, so do a normal plot.
    #         # .plot returns a list of line <reference>s, as we're
    #         # only getting one we can take the first element.
    #         plot_refsr = self.graph.axes.plot(self.xdata, self.rdata)
    #         plot_refsp = self.graph.axes.plot(self.xdata, self.pdata)
    #         plot_refsy = self.graph.axes.plot(self.xdata, self.ydata)
    #         self._plot_refr = plot_refsr[0]
    #         self._plot_refp = plot_refsp[0]
    #         self._plot_refy = plot_refsy[0]
    #     else:
    #         # We have a reference, we can use it to update the data for that line.
    #         self._plot_refr.set_ydata(self.rdata)
    #         self._plot_refp.set_ydata(self.pdata)
    #         self._plot_refy.set_ydata(self.ydata)
            

    #     # Trigger the canvas to update and redraw.
    #     self.graph.draw()

    def closeEvent(self, event):  # Window closing, standard Qt syntax
        if self.ser_connectedF:
            self.serth.running = False  # Wait until serial thread terminates
            self.serth.wait()
        sys.exit()


class MplCanvas(FigureCanvasQTAgg):
    send_fig = QtCore.pyqtSignal(axes, str, name="send_fig")

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(MplCanvas, self).__init__(self.fig)

        self.fig = Figure()
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)  # added
        self.axes.set_ylim([-360, 360])

    def updata_plot(self, axes):  # added
        self.axes = axes
        self.draw()


class Plotter(QObject):
    return_fig = QtCore.pyqtSignal(object)
    def __init__(self):
        self._plot_refr = None
        self._plot_refp = None
        self._plot_refy = None

    @pyqtSlot(str)
    def replot(self, text):
        text, _, _ = text.partition('\n')
        try:
            data = text.split("\t")
            [roll, pitch, yaw] = data
        except:
            [roll, pitch, yaw] = [20, 0, 0]
        # Drop off the first y element, append a new one.
        self.rdata = self.rdata[1:] + [np.float64(roll)]
        self.pdata = self.pdata[1:] + [np.float64(pitch)]
        self.ydata = self.ydata[1:] + [np.float64(yaw)]

        # Note: we no longer need to clear the axis.
        if self._plot_refr is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refsr = self.graph.axes.plot(self.xdata, self.rdata)
            plot_refsp = self.graph.axes.plot(self.xdata, self.pdata)
            plot_refsy = self.graph.axes.plot(self.xdata, self.ydata)
            self._plot_refr = plot_refsr[0]
            self._plot_refp = plot_refsp[0]
            self._plot_refy = plot_refsy[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_refr.set_ydata(self.rdata)
            self._plot_refp.set_ydata(self.pdata)
            self._plot_refy.set_ydata(self.ydata)
            

        # Trigger the canvas to update and redraw.
        self.return_fig.emit(data)


class PlotThread(QtCore.QThread):

    def __init__(self):
        self.graph = MplCanvas(self)

    def plot(self, text):
        text, _, _ = text.partition('\n')
        try:
            data = text.split("\t")
            [roll, pitch, yaw] = data
        except:
            [roll, pitch, yaw] = [20, 0, 0]
        # Drop off the first y element, append a new one.
        self.rdata = self.rdata[1:] + [np.float64(roll)]
        self.pdata = self.pdata[1:] + [np.float64(pitch)]
        self.ydata = self.ydata[1:] + [np.float64(yaw)]

        # Note: we no longer need to clear the axis.
        if self._plot_refr is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refsr = self.graph.axes.plot(self.xdata, self.rdata)
            plot_refsp = self.graph.axes.plot(self.xdata, self.pdata)
            plot_refsy = self.graph.axes.plot(self.xdata, self.ydata)
            self._plot_refr = plot_refsr[0]
            self._plot_refp = plot_refsp[0]
            self._plot_refy = plot_refsy[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_refr.set_ydata(self.rdata)
            self._plot_refp.set_ydata(self.pdata)
            self._plot_refy.set_ydata(self.ydata)


        # Trigger the canvas to update and redraw.
        self.graph.draw()


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
