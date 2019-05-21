'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import struct


class DataReader:

    def __init__(self, file_data, byte_offset):
        self.file_data = file_data
        self.byte_offset = byte_offset

    def read_byte(self):
        byte = self.file_data[self.byte_offset]
        self.byte_offset += 1
        return byte

    def read_byte_string(self):
        str_len = self.read_byte()
        bytes = bytearray()
        for i in range(0,str_len):
            bytes.append(self.read_byte())
        return bytes.decode("utf-8")

    def read_int16(self):
        bytes = bytearray()
        for i in range(0,2):
            bytes.append(self.read_byte())
        return struct.unpack('<h', bytes)[0]

    def read_int32(self):
        bytes = bytearray()
        for i in range(0,4):
            bytes.append(self.read_byte())
        return struct.unpack('<i', bytes)[0]

    def read_uint32(self):
        bytes = bytearray()
        for i in range(0,4):
            bytes.append(self.read_byte())
        return struct.unpack('<I', bytes)[0]

    def read_float(self):
        bytes = bytearray()
        for i in range(0,4):
            bytes.append(self.read_byte())
        return struct.unpack('<f', bytes)[0]
