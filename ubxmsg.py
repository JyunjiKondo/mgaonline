# -*- coding: utf-8 -*-

class UbxMsg:
  def __init__(self, cls: int, id: int, payload: list[int]) -> None:
    self.msg = self.add_checksum([0xb5, 0x62, cls, id] + self.length_word(payload) + payload)

  def add_checksum(self, arr: list[int]) -> bytes:
    ck_a = 0
    ck_b = 0
    for b in arr[2:]:
      ck_a = ck_a + b
      ck_b = ck_b + ck_a
    return bytes(arr + [ck_a & 0xff, ck_b & 0xff])

  def length_word(self, payload: list[int]) -> list[int]:
    return [len(payload) & 0xff, len(payload) >> 8]
