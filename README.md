# serial-logger
Command line executable logger of serial data to file.

usage: serial_logger.py [-h] [-f FILENAME] [-p PORT] [--baudrate BAUDRATE] [-b BYTESIZE]<br />
       [--parity PARITY] [-s STOPBITS] [--timeout TIMEOUT] [--xonxoff XONXOFF]<br />
       [--rtscts RTSCTS]
       
optional arguments:<br />
  -h, --help</br >   show this help message and exit<br />
  -f, --filename<br />      ouput filename<br />
  -p, --port<br />   port name, default None. If None the user will be asked to select a port from a list.<br />
  --baudrate<br />   int, default 9600<br />
  -b, --bytesize<br />      int, default = 8<br />
  --parity<br />     Enable parity checking. Possible values: *NONE, EVEN, ODD, MARK, SPACE<br />
  -s, --stopbits<br />      Number of stop bits. Possible values: *1, 1.5, 2<br />
  --timeout<br />    Set a read timeout value.<br />
  --xonxoff<br />    Enable software flow control. Default=False<br />
  --rtscts<br />     Enable hardware (RTS/CTS) flow control. Default=False<br />
