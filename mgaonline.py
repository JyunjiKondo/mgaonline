# -*- coding: utf-8 -*-

import os
import urllib.request
import struct
from ubxmsg import UbxMsg

class MgaOnline:
  HOSTS :list[str] = [
    'https://online-live1.services.u-blox.com',
    'https://online-live2.services.u-blox.com'
  ]

  def __init__(self, token: str, lat: str, lon: str, alt: str, pacc: str) -> None:
    self.off = 0
    for h in self.HOSTS:
      url = f'{h}/GetOnlineData.ashx?' + \
        'gnss=gps,qzss,bds,gal;datatype=eph,alm;filteronpos;' + \
        f'token={token};lat={lat};lon={lon};alt={alt};pacc={pacc};'

      try:
        with urllib.request.urlopen(url) as response:
          self.data = response.read()
      except urllib.error.URLError as e:
        print(e.reason)
      else:
        break
    else:
      raise Exception("Can't access AssistNow service")

  def __iter__(self):
    return self

  def __next__(self) -> bytes:
    if self.off >= len(self.data):
      raise StopIteration()
    mes = struct.unpack_from('HBBHB', self.data, self.off)
    assert mes[0] == 0x62b5, f'Invalid header: {mes[0]}'
    length = mes[3]
    start = self.off
    self.off += 6 + length + 2
    return self.data[start:self.off]
