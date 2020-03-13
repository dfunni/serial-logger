# serial-logger
Command line executable logger of serial data to file.

usage: serial_logger.py [-h] [-f FILENAME] [-p PORT] [--baudrate BAUDRATE] [-b BYTESIZE]<br />
       [--parity PARITY] [-s STOPBITS] [--timeout TIMEOUT] [--xonxoff XONXOFF]<br />
       [--rtscts RTSCTS]
       
optional arguments:
  -h, --help     show this help message and exit<br />
  -f, --filename ouput filename<br />
  -p, --port     port name, default None. If None the user will be<br />
                 asked to select a port from a list.<br />
  --baudrate     int, default 9600<br />
  -b, --bytesize int, default = 8<br />
  --parity       Enable parity checking. Possible values: *NONE, EVEN,<br />
                        ODD, MARK, SPACE<br />
  -s, --stopbits Number of stop bits. Possible values: *1, 1.5, 2<br />
  --timeout      Set a read timeout value.<br />
  --xonxoff      Enable software flow control. Default=False<br />
  --rtscts       Enable hardware (RTS/CTS) flow control. Default=False<br />
