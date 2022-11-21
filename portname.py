# -*- coding: utf-8 -*-

import sys
import glob
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