#!/usr/bin/env python3
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLayoutItem
from PyQt5.QtWidgets import QTextEdit, QComboBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QLabel, QStatusBar, QAction
from PyQt5 import QtSerialPort
import queue as Queue

import os
import sys
import time
from serial.tools.list_ports import comports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Main widget
class Window(QMainWindow):

    def __init__(self, *args):
        super(Window, self).__init__()

        self.resize(1200, 800)  # Set window size

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.ser = None

        # Menu bar
        self.statusBar = QStatusBar()

        self.quitAction = QAction('&Quit', self)
        self.quitAction.setShortcut('Ctrl+Q')
        self.quitAction.setStatusTip('exit')
        self.quitAction.triggered.connect(self.closeEvent)

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.quitAction)
        self.editMenu = self.mainMenu.addMenu('&Edit')

        # Text boxes
        self.display_box = QTextEdit(self)
        self.display_box.setReadOnly(True)

        self.fname_box = QLineEdit(self)
        self.fname_box.setText("log.txt")
        self.fname_box.setMaxLength(100)

        # Drop-down menus
        self.portSelect = QComboBox(self)
        self.update_ports()

        self.baudSelect = QComboBox(self)
        baud_list = [9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
        baud_list = [str(baud) for baud in baud_list]
        self.baudSelect.addItems(baud_list)

        # Buttons
        self.connect_btn = QPushButton(text="Run", 
                                       checkable=True,
                                       toggled=self.on_toggled)

        self.refresh_btn = QPushButton(text="Refresh",
                                       clicked=self.update_ports)

        self.delete_btn = QPushButton(text="Delete Log",
                                      clicked=self.delete_log)

        self.open_btn = QPushButton(text="Open Log",
                                    clicked=self.open_log)

        self.plot_btn = QPushButton(text="Plot Log",
                                    clicked=self.plot_log)

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
        self.l3.setText("Logfile:")

        # Layout
        self.main = QHBoxLayout()  # main layout
        self.left_lay = QVBoxLayout() 
        self.port_lay = QHBoxLayout()
        self.baud_lay = QHBoxLayout()
        self.file_lay = QHBoxLayout()
        self.cnct_lay = QHBoxLayout()

        self.port_lay.addWidget(self.l1)
        self.port_lay.addWidget(self.portSelect)
        self.port_lay.addWidget(self.refresh_btn)
        self.baud_lay.addWidget(self.l2)
        self.baud_lay.addWidget(self.baudSelect)
        self.file_lay.addWidget(self.l3)
        self.file_lay.addWidget(self.fname_box)
        self.file_lay.addWidget(self.open_btn)
        self.file_lay.addWidget(self.delete_btn)
        self.cnct_lay.addWidget(self.connect_btn)

        self.left_lay.addLayout(self.port_lay)
        self.left_lay.addLayout(self.baud_lay)
        self.left_lay.addLayout(self.file_lay)
        self.left_lay.addSpacing(20)
        self.left_lay.addLayout(self.cnct_lay)
        self.left_lay.addSpacing(20)
        self.left_lay.addWidget(self.plot_btn)
        self.left_lay.addStretch()

        self.main.addLayout(self.left_lay)
        self.main.addWidget(self.display_box)
        self.centralWidget().setLayout(self.main)

    def connect(self):
        self.portname, _ = self.portSelect.currentText().split('  ')
        self.baudrate = self.baudSelect.currentText()
        self.ser = QtSerialPort.QSerialPort(self.portname,
                                            baudRate=self.baudrate,
                                            readyRead=self.receive)

    def update_ports(self):
        """ This function was adapted from the pyserial tool miniterm.py."""
        ports = []
        for port, desc, _ in sorted(comports()):
            ports.append(f'{port}  {desc}')  # double space delimited
        self.portSelect.clear()
        self.portSelect.addItems(ports)

    def delete_log(self):
        self.filename = self.fname_box.text()
        cmd = f'rm {self.filename}'
        os.system(cmd)

    def open_log(self):
        self.filename = self.fname_box.text()
        cmd = f'vim {self.filename}'
        os.system(cmd)

    def plot_log(self):
        # r = []
        # p = []
        # y = []
        self.filename = self.fname_box.text()
        df = pd.read_csv(self.filename, sep='\t',
                         lineterminator='\n',
                         names=['t', 'r', 'p', 'y'])
        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.dropna()
        plt.scatter(df['t'], df['r'], label='roll', marker='.')
        plt.scatter(df['t'], df['p'], label='pitch', marker='.')
        plt.scatter(df['t'], df['y'], label='yaw', marker='.')
        plt.legend()
        plt.show()

    @QtCore.pyqtSlot()
    def receive(self):
        while self.ser.canReadLine():
            text = self.ser.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.display_box.append(text)
            line = f"{str(time.time())}\t{text}\n"  # append timestamp
            with open(self.filename, "a") as f:
                f.write(line)
                f.close()

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.connect_btn.setText("Stop" if checked else "Run")
        if checked:
            self.connect()
            self.filename = self.fname_box.text()
            if not self.ser.isOpen():
                if not self.ser.open(QtCore.QIODevice.ReadWrite):
                    self.connect_btn.setChecked(False)
        else:
            self.ser.close()

    def closeEvent(self, event):  # Window closing, standard Qt syntax
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.setWindowTitle('PyQT Serial Terminal')
    w.show()
    sys.exit(app.exec_())
