# serial-logger

This repository contains both a command line serial logging program and a GUI program with the same functionalitly. The goal of this project is to enable viewing and logging of recieved serial messages while experimenting with PyQt5 based GUI development. Plotting functions are designed to display gyroscope values read from an Arduino Nano 33 IoT.

## cli_serial_logger.py
Command line logger of serial data to file. This code relies heavily on pyserial by Chris Liechti. (https://github.com/pyserial/pyserial)

usage: cli_serial_logger.py [-h] [-f FILENAME] [-p PORT] [--baudrate BAUDRATE] [--bytesize BYTESIZE]<br />
       [--parity PARITY] [--stopbits STOPBITS] [--timeout TIMEOUT] [--xonxoff XONXOFF]<br />
       [--rtscts RTSCTS]
       
### Optional arguments:
  -h, --help            show this help message and exit<br />
  -nl, --no_log         Do not log data to file<br />
  -f FILENAME, --filename FILENAME ouput filename<br />
  -p PORT, --port PORT  port name, default None. If None the user will be asked to select a port from a list.<br />
  --baudrate BAUDRATE   int, default 9600<br />
  --bytesize BYTESIZE   int, default = 8<br />
  --parity PARITY       Enable parity checking. Possible values: *NONE, EVEN, ODD, MARK, SPACE<br />
  --stopbits STOPBITS   Number of stop bits. Possible values: *1, 1.5, 2<br />
  --timeout TIMEOUT     Set a read timeout value.<br />
  -x, --xonxoff         Software flow control flag<br />
  -r, --rtscts          Hardware (RTS/CTS) flow control flag.<br />

  
  ## qt_serial_logger.py
  PyQt5 based serial logger.
  
  ## qt_serial_plotter.py
  PyQt5 based live plotting of serial data. INCOMPLETE.
