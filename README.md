# serial-logger
Command line executable logger of serial data to file. This code relies heavily on pyserial by Chris Liechti. (https://github.com/pyserial/pyserial)

usage: serial_logger.py [-h] [-f FILENAME] [-p PORT] [--baudrate BAUDRATE] [--bytesize BYTESIZE]<br />
       [--parity PARITY] [--stopbits STOPBITS] [--timeout TIMEOUT] [--xonxoff XONXOFF]<br />
       [--rtscts RTSCTS]
       
## Optional arguments:
  -h, --help :       show help message and exit<br />
  -f, --filename :   str, ouput filename (default=serial_log.txt)<br />
  -p, --port :       str, port name, if None the user will be asked to select a port from a list (default None)<br />
  --baudrate :       int (default 9600)<br />
  --bytesize :       int (default = 8)<br />
  --parity :         str, enable parity checking. Possible values: NONE, EVEN, ODD, MARK, SPACE (default="NONE")<br />
  --stopbits :       float, number of stop bits. Possible values: 1, 1.5, 2, (default=1)<br />
  --timeout :        float, set a read timeout value (default=None)<br />
  --xonxoff :        bool, enable software flow control (default=False)<br />
  --rtscts :         bool, enable hardware (RTS/CTS) flow control (default=False)<br />
