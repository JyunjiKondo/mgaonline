# -*- coding: utf-8 -*-

"""Usage:
    mgaonline <token> <lat> <lon> <alt> <pacc>

Options:
    <token>
    <lat>   : in degree
    <lon>   : in degree
    <alt>   : in meter
    <pacc>  : position accuracy in meter
"""

import os
import time
import struct
from typing import Type
from serial import Serial
from mgaonline import MgaOnline
from ubxmsg import UbxMsg
from docopt import docopt
from portname import get_port_name

def wait_for_ack(ser: Type[Serial]) -> None:
  r = ser.read_until(b'\xb5') # wait for UBX preamble sync char1
  mes = struct.unpack('=BBBH', ser.read(5)) # read sync char2, class, id and length
  if mes[1] != 0x05 or mes[2] != 0x01:
    raise Exception('No ACK received')

MGA_ACK_INFO_STR :list[str] = [
  'The receiver accepted the data',
  'The receiver does not know the time so it cannot use the data',
  'The message version is not supported by the receiver',
  'The message size does not match the message version',
  'The message data could not be stored to the database',
  'The receiver is not ready to use the message data',
  'The message type is unknown'
]

def wait_for_mga_ack(ser: Type[Serial]) -> None:
  r = ser.read_until(b'\xb5') # wait for UBX preamble sync char1
  mes = struct.unpack('=BBBHBBB', ser.read(8)) # read sync char2, class, id, length, type, version and infoCode
  if mes[1] != 0x13 or mes[2] != 0x60:
    raise Exception("No MGA-ACK received")
  if mes[4] != 0x01:
    print(f'The message was not used by the receiver. {MGA_ACK_INFO_STR[mes[6]]}.')

if __name__ == '__main__':
  args = docopt(__doc__)
  token = args['<token>']
  lat = args['<lat>']
  lon = args['<lon>']
  alt = args['<alt>']
  pacc = args['<pacc>']

  rst_msg = UbxMsg(0x06, 0x04, [0xff, 0xff, 0x02, 0x00]).msg
  ackaiding_msg = UbxMsg(0x06, 0x8a, [0x00, 0x01, 0x00, 0x00, 0x25, 0x00, 0x11, 0x10, 0x01]).msg

  with Serial(port=get_port_name(), baudrate=38400, timeout=5) as ser:
    print("> " + rst_msg.hex())
    ser.write(rst_msg) # cold start
    time.sleep(1) # wait 1 sec
    print("> " + ackaiding_msg.hex())
    ser.write(ackaiding_msg) # enable acknowledge assistance input messages
    wait_for_ack(ser)
    for m in MgaOnline(token, lat, lon, alt, pacc):
      print("> " + m.hex())
      ser.write(m) # send a message
      wait_for_mga_ack(ser)
