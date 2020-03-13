# serial-logger
Command line executable logger of serial data to file.

usage: serial_logger.py [-h] [-f FILENAME] [-p PORT] [--baudrate BAUDRATE] [-b BYTESIZE]
       [--parity PARITY] [-s STOPBITS] [--timeout TIMEOUT] [--xonxoff XONXOFF]
       [--rtscts RTSCTS]

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        ouput filename
  -p PORT, --port PORT  port name, default None. If None the user will be
                        asked to select a port from a list.
  --baudrate BAUDRATE   int, default 9600
  -b BYTESIZE, --bytesize BYTESIZE
                        int, default = 8
  --parity PARITY       Enable parity checking. Possible values: *NONE, EVEN,
                        ODD, MARK, SPACE
  -s STOPBITS, --stopbits STOPBITS
                        Number of stop bits. Possible values: *1, 1.5, 2
  --timeout TIMEOUT     Set a read timeout value.
  --xonxoff XONXOFF     Enable software flow control. Default=False
  --rtscts RTSCTS       Enable hardware (RTS/CTS) flow control. Default=False
