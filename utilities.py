#!/usr/bin/env python3
import serial
# import os
import sys
# import subprocess
import time
from serial.tools.list_ports import comports


def port_options():
    """This function was adapted from the pyserial tool miniterm.py."""
    ports = []
    descs = []
    index = []
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        sys.stderr.write('--- {:2}: {:20} {!r}\n'.format(n, port, desc))
        ports.append(port)
        descs.append(desc)
        index.append(n)

    return ports, descs


# def _activate_port(port):
#    """This function ensures serial port is activated in linux."""
#    port_permissions = subprocess.check_output('ls -la ' + port,
#                                               shell=True)[7:10].decode('utf-8')
#    if port_permissions == '---':
#        cmd = 'sudo chmod 664 ' + port
#        print("Port needs to be enabled...")
#        print('running command: ' + cmd)
#        os.system(cmd)
#    print("Port open!")

def stop_log(ser):
    ser.close()


def connect(port, baudrate=9600,  bytesize=8, parity="NONE",  stopbits=1,
            timeout=None, xonxoff=False,  rtscts=False):
    """ Connects to serial port"""
    parity_map = {'NONE': serial.PARITY_NONE,
                  'EVEN': serial.PARITY_EVEN,
                  'ODD': serial.PARITY_ODD,
                  'MARK': serial.PARITY_MARK,
                  'SPACE': serial.PARITY_SPACE}
    parity = parity_map[parity]

    ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout,
                        xonxoff, rtscts)

    print(f'connected to {ser.name}')

    # ser_bytes = ser.readline()
    # decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
    # print(decoded_bytes)

    return ser


def log(filename, ser):
    """This is the main function of this program, logs data recieved over
    serial bus as ascii text.

    Keyword arguments:
    filename -- the ouptut filename
    port     -- serial port for connection
    baudrate -- baudrate of serial port
    bytesize -- size of a byte
    parity   -- parity checking, options: NONE, EVEN, ODD, MARK, SPACE
    stopbits -- number of stop bits
    timeout  -- read timeout in seconds
    xonxoff  -- enable software flow control
    rtcts    -- enable hardware flow control
    """

    ser.flushInput()

    while True:
        try:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
            with open(filename, "a") as f:
                line = str(time.time()) + '\t' + decoded_bytes
                # print(line)
                line += '\n'
                f.write(line)
                f.close()
        except KeyboardInterrupt:
            stop_log(ser)
