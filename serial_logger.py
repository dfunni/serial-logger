#!/usr/bin/env python3
import serial
# import os
import sys
# import subprocess
import time
import argparse
from serial.tools.list_ports import comports


def _ask_for_port():
    """This function was adapted from the pyserial tool miniterm.py."""
    ports = []
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        sys.stderr.write('--- {:2}: {:20} {!r}\n'.format(n, port, desc))
        ports.append(port)

    port = input('Press Ctrl+C to exit\n--- Enter port index or name:')
    try:
        index = int(port) - 1
        if not 0 <= index < len(ports):
            sys.stderr.write('--- Invalid index!\n')
            sys.exit(1)
            # continue
    except ValueError:
        print(f"ValueError: invalid input")
        sys.exit(1)
    else:
        port = ports[index]
#            _activate_port(port)
    return port


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


def main(filename, port, baudrate,  bytesize=8, parity="NONE",  stopbits=1,
         timeout=None, xonxoff=False,  rtscts=False):
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
    ser = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout,
                        xonxoff, rtscts)
    ser.baudrate = baudrate
    ser.flushInput()

    while True:
        try:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
            with open(filename, "a") as f:
                line = str(time.time()) + '\t' + decoded_bytes
                print(line)
                line += '\n'
                f.write(line)
                f.close()
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            ser.close()
            break


if __name__ == "__main__":

    description = """Simple read from serial port and saves to text file.\n"""

    parser = argparse.ArgumentParser(description)

    parser.add_argument('-f', '--filename', type=str, help='ouput filename',
                        default='log.txt')
    parser.add_argument('-p', '--port', type=str,
                        help="""port name, default None. If None the user will
                        be asked to select a port from a list.""", 
                        default=None)
    parser.add_argument('--baudrate', type=int, help='int, default 9600',
                        default=9600)
    parser.add_argument('--bytesize', type=int, 
                        help='int, default = 8', 
                        default=8)
    parser.add_argument('--parity', type=str,
                        help="""Enable parity checking. Possible values:
                        *NONE, 
                        EVEN, 
                        ODD,
                        MARK, 
                        SPACE""",
                        default='NONE')
    parser.add_argument('--stopbits', type=float,
                        help="""Number of stop bits. Possible values:
                        *1, 1.5, 2""",
                        default=1)
    parser.add_argument('--timeout', type=float,
                        help="Set a read timeout value.",
                        default=None)
    parser.add_argument('--xonxoff', type=bool,
                        help="Enable software flow control. Default=False",
                        default=False)
    parser.add_argument('--rtscts', type=bool,
                        help="""Enable hardware (RTS/CTS) flow control.
                        Default=False""",
                        default=False)

    args = parser.parse_args()

    parity_map = {'NONE': serial.PARITY_NONE,
                  'EVEN': serial.PARITY_EVEN,
                  'ODD': serial.PARITY_ODD,
                  'MARK': serial.PARITY_MARK,
                  'SPACE': serial.PARITY_SPACE}

    args.parity = parity_map[args.parity]

    if args.port is None:
        args.port = _ask_for_port()

    main(args.filename, args.port, args.baudrate, args.bytesize,
         args.parity, args.stopbits, args.timeout, args.xonxoff,
         args.rtscts)
