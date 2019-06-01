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
    """ This class is responsible for reading binary data from the GEOM file """


    def __init__(self, filedata):
        self.offset = 0
        self.data = filedata


    def read_byte(self):
        byte = self.data[self.offset]
        self.offset += 1
        return byte


    def read_string(self):
        length = self.read_byte()
        bytes = bytearray()
        for _ in range(length):
            bytes.append(self.read_byte())
        return bytes.decode("utf-8")


    def read_int16(self):
        bytes = bytearray()
        for _ in range(2):
            bytes.append(self.read_byte())
        return struct.unpack('<h', bytes)[0]


    def read_uint16(self):
        bytes = bytearray()
        for _ in range(2):
            bytes.append(self.read_byte())
        return struct.unpack('<H', bytes)[0]


    def read_int32(self):
        bytes = bytearray()
        for _ in range(4):
            bytes.append(self.read_byte())
        return struct.unpack('<i', bytes)[0]


    def read_uint32(self):
        bytes = bytearray()
        for _ in range(4):
            bytes.append(self.read_byte())
        return struct.unpack('<I', bytes)[0]


    def read_int64(self):
        bytes = bytearray()
        for _ in range(8):
            bytes.append(self.read_byte())
        return struct.unpack('<q', bytes)[0]


    def read_uint64(self):
        bytes = bytearray()
        for _ in range(8):
            bytes.append(self.read_byte())
        return struct.unpack('<Q', bytes)[0]


    def read_float(self):
        bytes = bytearray()
        for i in range(0,4):
            bytes.append(self.read_byte())
        return struct.unpack('<f', bytes)[0]
