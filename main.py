# -*- coding: utf-8 -*-

import sys
import os
import time
import glob
import struct
from typing import Type
from serial import Serial
from mgaonline import MgaOnline
from ubxmsg import UbxMsg
from serial.tools import list_ports

def get_port_name() -> str:
  if sys.platform.startswith('win'):
    coms = [port for port, _, hwid in list_ports.comports() if '1546:01A9' in hwid]
    if not coms:
      raise Exception("Can't find a COM port")
    return coms[0]
  elif sys.platform.startswith('linux'):
    pass
  elif sys.platform.startswith('darwin'): # for MacOS
    devs = glob.glob('/dev/tty*usb*')
    if not devs:
      raise Exception("Can't find a device")
    return devs[0]
  raise Exception('Unsupported platform')

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
  token = os.environ['AN_TOKEN']
  lat = os.environ.get('AN_LAT', 0) # deg
  lon = os.environ.get('AN_LON', 90) # deg
  alt = os.environ.get('AN_ALT', 0) # meter unit
  pacc = os.environ.get('AN_PACC', 100) # meter unit 

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
